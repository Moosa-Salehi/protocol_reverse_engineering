#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import warnings
import statistics
from collections import Counter
from pathlib import Path

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))

# PyTorch requires this to make CUDA matrix operations deterministic. It must be set
# before the first CUDA operation and avoids repeated CuBLAS determinism warnings.
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

if "--show-warnings" not in sys.argv:
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings(
        "ignore",
        message=r"Deterministic behavior was enabled.*CuBLAS.*",
        category=UserWarning,
    )

import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader
from tqdm.auto import tqdm
from sklearn.preprocessing import StandardScaler

from VAE_supervised_train.common import parse_protocols, seed_everything
from VAE_supervised_train.data import FamilyBalancedBatchSampler, MessageFamilyDataset
from VAE_supervised_train.evaluate import embed_dataset, evaluate_embeddings
from VAE_supervised_train.losses import (batch_hard_triplet, centroid_loss, collapse_loss,
                                         supervised_contrastive, vae_kl)
from VAE_supervised_train.metrics import checkpoint_key, clustering_metrics, run_hdbscan
from VAE_supervised_train.model import (SupervisedVAE, load_training_checkpoint,
                                        save_checkpoint, save_training_checkpoint)


def aggregate_validation(report: dict) -> dict:
    metrics = report["overall"].copy()
    protocols = list(report["per_protocol"].values())
    metrics["family_count_error"] = sum(item["family_count_error"] for item in protocols)
    total = sum(item["message_count"] for item in protocols)
    for name in ("weighted_cluster_impurity", "merged_family_rate", "fragmented_family_rate", "noise_fraction"):
        metrics[name] = sum(item[name] * item["message_count"] for item in protocols) / max(1, total)
    return metrics


def tune_hdbscan(dataset, embeddings: np.ndarray, sizes: list[int], samples: list[int | None],
                 epsilons: list[float], progress: bool = True,
                 size_fractions: list[float] | None = None, two_stage: bool = False):
    parameters = {}
    protocols = sorted({row["protocol_id"] for row in dataset.rows})
    protocol_progress = tqdm(protocols, desc="HDBSCAN tuning", unit="protocol", leave=False,
                             disable=not progress, dynamic_ncols=True)
    for protocol in protocol_progress:
        protocol_progress.set_postfix_str(protocol)
        indexes = [i for i, row in enumerate(dataset.rows) if row["protocol_id"] == protocol]
        protocol_data = MessageFamilyDataset.from_rows([dataset.rows[i] for i in indexes], dataset.max_len)
        protocol_embeddings = embeddings[np.asarray(indexes)]
        scaled_embeddings = StandardScaler().fit_transform(protocol_embeddings)
        truth_keys = [row["trusted_family_id"] for row in protocol_data.rows]
        truth_mapping = {key: number for number, key in enumerate(sorted(set(truth_keys)))}
        truth = np.asarray([truth_mapping[key] for key in truth_keys])
        protocol_sizes = set(sizes)
        for fraction in size_fractions or []:
            protocol_sizes.add(max(2, int(round(len(indexes) * fraction))))
        protocol_sizes = sorted({min(size, len(indexes)) for size in protocol_sizes if len(indexes) >= 2})
        best = None
        if two_stage:
            search = [(size, samples[0], epsilon) for size in protocol_sizes for epsilon in epsilons]
        else:
            search = [(size, sample_count, epsilon) for size in protocol_sizes
                      for sample_count in samples for epsilon in epsilons]
        for size, sample_count, epsilon in search:
            predicted = run_hdbscan(scaled_embeddings, size, sample_count, epsilon, standardized=True)
            metrics = clustering_metrics(truth, predicted)
            candidate = (checkpoint_key(metrics), size, sample_count, epsilon)
            if best is None or candidate[0] < best[0]:
                best = candidate
        if two_stage:
            winning_size = best[1]
            for sample_count in samples[1:]:
                for epsilon in epsilons:
                    predicted = run_hdbscan(scaled_embeddings, winning_size, sample_count, epsilon,
                                            standardized=True)
                    metrics = clustering_metrics(truth, predicted)
                    candidate = (checkpoint_key(metrics), winning_size, sample_count, epsilon)
                    if best is None or candidate[0] < best[0]:
                        best = candidate
        parameters[protocol] = {"min_cluster_size": best[1], "min_samples": best[2],
                                "cluster_selection_epsilon": best[3]}
    report = evaluate_embeddings(dataset, embeddings, protocol_parameters=parameters)
    values = list(parameters.values())
    protocol_counts = Counter(row["protocol_id"] for row in dataset.rows)
    non_null_samples = [item["min_samples"] for item in values if item["min_samples"] is not None]
    report["hdbscan_global"] = {
        "min_cluster_size": max(2, int(statistics.median(item["min_cluster_size"] for item in values))),
        "min_cluster_size_fraction": float(statistics.median(
            item["min_cluster_size"] / max(1, protocol_counts[protocol])
            for protocol, item in parameters.items()
        )),
        "min_samples": int(statistics.median(non_null_samples)) if non_null_samples else None,
        "cluster_selection_epsilon": float(statistics.median(
            item["cluster_selection_epsilon"] for item in values
        )),
        "selection": "median_of_protocol_tuned_parameters",
    }
    return report, aggregate_validation(report)


def model_cache_signature(model) -> str:
    digest = hashlib.sha256()
    for name, parameter in model.state_dict().items():
        flat = parameter.detach().reshape(-1)
        digest.update(name.encode("utf-8"))
        digest.update(str(tuple(parameter.shape)).encode("ascii"))
        digest.update(flat[:16].cpu().numpy().tobytes())
        digest.update(str(float(flat.float().sum().cpu())).encode("ascii"))
    return digest.hexdigest()


def cached_embeddings(model, dataset, device: str, batch_size: int, cache_path: Path,
                      progress: bool) -> np.ndarray:
    metadata_path = cache_path.with_suffix(cache_path.suffix + ".json")
    signature = {"model": model_cache_signature(model), "records": len(dataset),
                 "latent_dim": model.latent_dim, "max_len": model.max_len}
    if cache_path.exists():
        cached_metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else None
        if cached_metadata == signature:
            cached = np.load(cache_path, mmap_mode="r")
            expected = (len(dataset), model.latent_dim)
            if cached.shape == expected:
                tqdm.write(f"Reusing full embedding cache: {cache_path}")
                return np.asarray(cached)
        tqdm.write(f"Replacing stale full embedding cache: {cache_path}")
    embeddings = embed_dataset(model, dataset, device, batch_size, progress=progress)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = cache_path.with_suffix(cache_path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.save(handle, embeddings)
    temporary.replace(cache_path)
    metadata_path.write_text(json.dumps(signature, sort_keys=True), encoding="utf-8")
    return embeddings


def parse_optional_ints(value: str) -> list[int | None]:
    return [None if item.strip().lower() in {"none", "auto"} else int(item) for item in value.split(",")]


def describe_device(device_name: str, amp_enabled: bool) -> str:
    device = torch.device(device_name)
    if device.type == "cuda":
        if not torch.cuda.is_available():
            raise SystemExit(f"CUDA device requested ({device_name}), but torch.cuda.is_available() is false")
        index = device.index if device.index is not None else torch.cuda.current_device()
        properties = torch.cuda.get_device_properties(index)
        memory_gib = properties.total_memory / (1024 ** 3)
        capability = torch.cuda.get_device_capability(index)
        return (f"Device: CUDA GPU {index} - {properties.name} | CUDA {torch.version.cuda} | "
                f"compute capability {capability[0]}.{capability[1]} | {memory_gib:.1f} GiB | "
                f"mixed precision: {'enabled' if amp_enabled else 'disabled'}")
    return (f"Device: CPU | threads: {torch.get_num_threads()} | "
            f"mixed precision: disabled")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a supervised VAE solely for message-family clustering.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("VAE_supervised_train/checkpoints/best_v3.pth"))
    parser.add_argument("--metrics", type=Path, default=Path("VAE_supervised_train/checkpoints/metrics_v3.jsonl"))
    parser.add_argument("--metrics-format", choices=("jsonl", "json"), default="jsonl")
    parser.add_argument("--train-protocols", default="all")
    parser.add_argument("--validation-protocols", default=None,
                        help="Defaults to the training protocols. Data is not split; all selected records are used.")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--patience", type=int, default=6,
                        help="Number of validation rounds without improvement before stopping.")
    parser.add_argument("--validate-every", type=int, default=5)
    parser.add_argument("--latent-dim", type=int, default=32)
    parser.add_argument("--max-len", type=int, default=256)
    parser.add_argument("--families-per-batch", type=int, default=16)
    parser.add_argument("--examples-per-family", type=int, default=4)
    parser.add_argument("--batches-per-epoch", type=int)
    parser.add_argument("--min-family-support", type=int, default=2)
    parser.add_argument("--min-confidence", type=float, default=0.9)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--gradient-clip", type=float, default=5.0)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--triplet-margin", type=float, default=0.3)
    parser.add_argument("--centroid-margin", type=float, default=0.8)
    parser.add_argument("--supcon-weight", type=float, default=1.0)
    parser.add_argument("--triplet-weight", type=float, default=0.5)
    parser.add_argument("--compactness-weight", type=float, default=0.05)
    parser.add_argument("--separation-weight", type=float, default=0.25)
    parser.add_argument("--collapse-weight", type=float, default=0.1)
    parser.add_argument("--kl-weight", type=float, default=1e-3)
    parser.add_argument("--reconstruction-weight", type=float, default=0.0)
    parser.add_argument("--hdbscan-min-cluster-sizes", default="12,25,50,100,250")
    parser.add_argument("--hdbscan-min-samples", default="none,1,5")
    parser.add_argument("--hdbscan-epsilons", default="0.0")
    parser.add_argument("--full-hdbscan-min-cluster-sizes", default="25,50,100,250,500,1000,2500,5000")
    parser.add_argument("--full-hdbscan-size-fractions", default="0.0005,0.001,0.0025,0.005,0.01,0.025")
    parser.add_argument("--full-hdbscan-min-samples", default="none,1,5")
    parser.add_argument("--full-hdbscan-epsilons", default="0.0")
    parser.add_argument("--validation-batch-size", type=int, default=512)
    parser.add_argument("--validation-max-per-family", type=int, default=256,
                        help="Deterministic validation cap per trusted family; zero disables it.")
    parser.add_argument("--validation-max-per-protocol", type=int, default=10000,
                        help="Deterministic validation cap per protocol; zero disables it.")
    parser.add_argument("--full-validation-on-best", action=argparse.BooleanOptionalAction, default=True,
                        help="Retune HDBSCAN on the full corpus for each subset-best candidate (default: enabled).")
    parser.add_argument("--full-embedding-cache-dir", type=Path,
                        default=Path("VAE_supervised_train/checkpoints/full_embedding_cache"))
    parser.add_argument("--latest", type=Path,
                        help="Resumable checkpoint path; defaults to latest_v3.pth beside --output.")
    parser.add_argument("--resume", type=Path,
                        help="Resume model, optimizer, scaler, epoch, and early-stopping state from --latest output.")
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--no-mixed-precision", action="store_true")
    parser.add_argument("--show-warnings", action="store_true",
                        help="Show deprecation and future warnings hidden by default.")
    parser.add_argument("--no-progress", action="store_true", help="Disable tqdm progress bars.")
    args = parser.parse_args()
    seed_everything(args.seed)
    manifest_path = args.dataset.with_suffix(".manifest.json")
    if not manifest_path.exists():
        raise SystemExit(f"Dataset manifest not found: {manifest_path}")
    dataset_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if dataset_manifest.get("payload_source") != "tshark_transport_or_l2_payload":
        raise SystemExit(
            "Dataset uses the legacy dissector-level payload representation. "
            "Rebuild it with VAE_supervised_train/build_dataset.py before training."
        )
    train_protocols = parse_protocols(args.train_protocols)
    validation_protocols = parse_protocols(args.validation_protocols) if args.validation_protocols else train_protocols
    train_data = MessageFamilyDataset(args.dataset, train_protocols, args.max_len,
                                      args.min_confidence, args.min_family_support)
    full_validation_data = MessageFamilyDataset(args.dataset, validation_protocols, args.max_len,
                                                args.min_confidence, 1)
    validation_data = full_validation_data.stratified_subset(
        args.validation_max_per_family, args.validation_max_per_protocol, args.seed
    )
    if len(train_data.key_to_label) < 2:
        raise SystemExit("Training requires at least two eligible protocol-local families")
    sampler = FamilyBalancedBatchSampler(train_data.labels, args.families_per_batch,
                                         args.examples_per_family, args.batches_per_epoch, args.seed)
    loader = DataLoader(train_data, batch_sampler=sampler, num_workers=args.num_workers,
                        pin_memory=args.device.startswith("cuda"))
    amp_enabled = args.device.startswith("cuda") and not args.no_mixed_precision
    tqdm.write(describe_device(args.device, amp_enabled))
    tqdm.write(f"Deterministic mode: enabled | CUBLAS_WORKSPACE_CONFIG="
               f"{os.environ['CUBLAS_WORKSPACE_CONFIG']}")
    model = SupervisedVAE(args.max_len, args.latent_dim).to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    latest_path = args.latest or args.output.with_name("latest_v3.pth")
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    best_key, subset_best_key, best_metrics, stale, start_epoch = None, None, None, 0, 1
    sizes = [int(x) for x in args.hdbscan_min_cluster_sizes.split(",")]
    samples = parse_optional_ints(args.hdbscan_min_samples)
    epsilons = [float(x) for x in args.hdbscan_epsilons.split(",")]
    full_sizes = [int(x) for x in args.full_hdbscan_min_cluster_sizes.split(",")]
    full_fractions = [float(x) for x in args.full_hdbscan_size_fractions.split(",")]
    full_samples = parse_optional_ints(args.full_hdbscan_min_samples)
    full_epsilons = [float(x) for x in args.full_hdbscan_epsilons.split(",")]
    config = vars(args).copy()
    config = {key: str(value) if isinstance(value, Path) else value for key, value in config.items()}
    if args.resume:
        resumed = load_training_checkpoint(str(args.resume), model, optimizer, scaler, args.device)
        start_epoch = int(resumed["epoch"]) + 1
        if resumed.get("selection_scope") == "full_corpus":
            best_key = tuple(resumed["best_key"]) if resumed.get("best_key") is not None else None
            subset_best_key = tuple(resumed["subset_best_key"]) if resumed.get("subset_best_key") is not None else None
            best_metrics = resumed.get("best_metrics")
            stale = int(resumed.get("stale", 0))
        else:
            tqdm.write("Legacy resume checkpoint detected; clustering selection state will restart using full-corpus metrics.")
        tqdm.write(f"Resumed {args.resume} at epoch {start_epoch} (stale validations: {stale})")
    tqdm.write(f"Training records: {len(train_data):,} | validation subset: {len(validation_data):,} "
               f"| full validation: {len(full_validation_data):,} | families: {len(validation_data.key_to_label)}")
    metric_rows = []
    metrics_mode = "a" if args.resume and args.metrics_format == "jsonl" else "w"
    with args.metrics.open(metrics_mode, encoding="utf-8") as metric_file:
        epoch_progress = tqdm(range(start_epoch, args.epochs + 1), desc="Training", unit="epoch",
                              disable=args.no_progress, dynamic_ncols=True)
        for epoch in epoch_progress:
            sampler.set_epoch(epoch)
            model.train()
            sums = {name: 0.0 for name in ("total", "supcon", "triplet", "compact", "separation", "collapse", "kl", "reconstruction")}
            batch_progress = tqdm(loader, desc=f"Epoch {epoch}/{args.epochs}", unit="batch", leave=False,
                                  disable=args.no_progress, dynamic_ncols=True)
            for batch_number, (byte_ids, mask, labels, _) in enumerate(batch_progress, start=1):
                byte_ids, mask, labels = byte_ids.to(args.device), mask.to(args.device), labels.to(args.device)
                optimizer.zero_grad(set_to_none=True)
                with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp_enabled):
                    if args.reconstruction_weight > 0:
                        reconstruction, mu, logvar = model(byte_ids, mask)
                    else:
                        reconstruction = None
                        mu, logvar = model.encode(byte_ids, mask)
                    supcon = supervised_contrastive(mu, labels, args.temperature)
                    triplet = batch_hard_triplet(mu, labels, args.triplet_margin)
                    compact, separation = centroid_loss(mu, labels, args.centroid_margin)
                    collapse = collapse_loss(mu)
                    kl = vae_kl(mu, logvar)
                    if reconstruction is not None:
                        valid = mask.bool()
                        recon = F.cross_entropy(reconstruction[valid], byte_ids[valid])
                    else:
                        recon = mu.sum() * 0.0
                    total = (args.supcon_weight * supcon + args.triplet_weight * triplet +
                             args.compactness_weight * compact + args.separation_weight * separation +
                             args.collapse_weight * collapse + args.kl_weight * kl + args.reconstruction_weight * recon)
                scaler.scale(total).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.gradient_clip)
                scaler.step(optimizer)
                scaler.update()
                for name, value in (("total", total), ("supcon", supcon), ("triplet", triplet),
                                    ("compact", compact), ("separation", separation), ("collapse", collapse),
                                    ("kl", kl), ("reconstruction", recon)):
                    sums[name] += float(value.detach())
                if batch_number == 1 or batch_number % 25 == 0:
                    batch_progress.set_postfix(loss=f"{sums['total'] / batch_number:.4f}")
            row = {"epoch": epoch, "train": {key: value / len(loader) for key, value in sums.items()}}
            if epoch % args.validate_every == 0 or epoch == args.epochs:
                epoch_progress.set_description(f"Validating epoch {epoch}")
                model.eval()
                embeddings = embed_dataset(model, validation_data, args.device, args.validation_batch_size,
                                           progress=not args.no_progress)
                report, selection = tune_hdbscan(validation_data, embeddings, sizes, samples, epsilons,
                                                 not args.no_progress)
                report["validation_scope"] = "stratified_subset"
                report["validation_record_count"] = len(validation_data)
                row["validation"] = report
                subset_key = checkpoint_key(selection)
                row["subset_checkpoint_key"] = subset_key
                if subset_best_key is None or subset_key < subset_best_key:
                    subset_best_key = subset_key
                    if args.full_validation_on_best:
                        cache_path = args.full_embedding_cache_dir / f"epoch_{epoch:05d}.npy"
                        full_embeddings = cached_embeddings(
                            model, full_validation_data, args.device, args.validation_batch_size,
                            cache_path, progress=not args.no_progress
                        )
                        full_report, full_selection = tune_hdbscan(
                            full_validation_data, full_embeddings, full_sizes, full_samples,
                            full_epsilons, not args.no_progress, full_fractions, two_stage=True
                        )
                        full_report["validation_scope"] = "full_corpus_retuned"
                        full_report["validation_record_count"] = len(full_validation_data)
                        full_report["embedding_cache"] = str(cache_path)
                        key = checkpoint_key(full_selection)
                        row["full_validation"] = full_report
                    else:
                        full_report, key = report, subset_key
                    if best_key is None or key < best_key:
                        best_key, best_metrics, stale = key, full_report, 0
                        save_checkpoint(str(args.output), model, config, full_report, epoch)
                        row["best"] = True
                    else:
                        stale += 1
                        row["best"] = False
                else:
                    stale += 1
                    key = best_key
                row["checkpoint_key"] = key
                row.setdefault("best", False)
            metric_rows.append(row)
            if args.metrics_format == "jsonl":
                metric_file.write(json.dumps(row, sort_keys=True) + "\n")
                metric_file.flush()
            else:
                metric_file.seek(0)
                json.dump(metric_rows, metric_file, indent=2, sort_keys=True)
                metric_file.truncate()
                metric_file.flush()
            train_loss = row["train"]["total"]
            if "checkpoint_key" in row:
                key = row["checkpoint_key"]
                status = "best" if row["best"] else f"stale={stale}/{args.patience}"
                tqdm.write(f"Epoch {epoch}: loss={train_loss:.4f}, count_error={key[0]}, "
                           f"impurity={key[1]:.6f}, noise={key[3]:.3f} ({status})")
            else:
                tqdm.write(f"Epoch {epoch}: loss={train_loss:.4f}")
            epoch_progress.set_description("Training")
            epoch_progress.set_postfix(loss=f"{train_loss:.4f}", best_count_error=(best_key or ("-",))[0])
            save_training_checkpoint(str(latest_path), model, optimizer, scaler, config, epoch,
                                     best_key, subset_best_key, stale, best_metrics)
            if stale >= args.patience:
                break


if __name__ == "__main__":
    main()
