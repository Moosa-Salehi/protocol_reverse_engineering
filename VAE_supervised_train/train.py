#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader

from VAE_supervised_train.common import parse_protocols, seed_everything
from VAE_supervised_train.data import FamilyBalancedBatchSampler, MessageFamilyDataset
from VAE_supervised_train.evaluate import embed_dataset, evaluate_embeddings
from VAE_supervised_train.losses import (batch_hard_triplet, centroid_loss, collapse_loss,
                                         supervised_contrastive, vae_kl)
from VAE_supervised_train.metrics import checkpoint_key
from VAE_supervised_train.model import SupervisedVAE, save_checkpoint


def aggregate_validation(report: dict) -> dict:
    metrics = report["overall"].copy()
    protocols = list(report["per_protocol"].values())
    metrics["family_count_error"] = sum(item["family_count_error"] for item in protocols)
    total = sum(item["message_count"] for item in protocols)
    for name in ("weighted_cluster_impurity", "merged_family_rate", "fragmented_family_rate", "noise_fraction"):
        metrics[name] = sum(item[name] * item["message_count"] for item in protocols) / max(1, total)
    return metrics


def tune_hdbscan(dataset, embeddings: np.ndarray, sizes: list[int], samples: list[int | None], epsilons: list[float]):
    best = None
    for size in sizes:
        for sample_count in samples:
            for epsilon in epsilons:
                report = evaluate_embeddings(dataset, embeddings, size, sample_count, epsilon)
                metrics = aggregate_validation(report)
                candidate = (checkpoint_key(metrics), report, metrics)
                if best is None or candidate[0] < best[0]:
                    best = candidate
    return best[1], best[2]


def parse_optional_ints(value: str) -> list[int | None]:
    return [None if item.strip().lower() in {"none", "auto"} else int(item) for item in value.split(",")]


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a supervised VAE solely for message-family clustering.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("VAE_supervised_train/checkpoints/best.pth"))
    parser.add_argument("--metrics", type=Path, default=Path("VAE_supervised_train/checkpoints/metrics.jsonl"))
    parser.add_argument("--metrics-format", choices=("jsonl", "json"), default="jsonl")
    parser.add_argument("--train-protocols", default="all")
    parser.add_argument("--validation-protocols", default=None,
                        help="Defaults to the training protocols. Data is not split; all selected records are used.")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--patience", type=int, default=12)
    parser.add_argument("--validate-every", type=int, default=2)
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
    parser.add_argument("--hdbscan-min-cluster-sizes", default="3,5,8,12")
    parser.add_argument("--hdbscan-min-samples", default="none,1,3,5")
    parser.add_argument("--hdbscan-epsilons", default="0.0")
    parser.add_argument("--validation-batch-size", type=int, default=512)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--no-mixed-precision", action="store_true")
    args = parser.parse_args()
    seed_everything(args.seed)
    train_protocols = parse_protocols(args.train_protocols)
    validation_protocols = parse_protocols(args.validation_protocols) if args.validation_protocols else train_protocols
    train_data = MessageFamilyDataset(args.dataset, train_protocols, args.max_len,
                                      args.min_confidence, args.min_family_support)
    validation_data = MessageFamilyDataset(args.dataset, validation_protocols, args.max_len,
                                           args.min_confidence, 1)
    if len(train_data.key_to_label) < 2:
        raise SystemExit("Training requires at least two eligible protocol-local families")
    sampler = FamilyBalancedBatchSampler(train_data.labels, args.families_per_batch,
                                         args.examples_per_family, args.batches_per_epoch, args.seed)
    loader = DataLoader(train_data, batch_sampler=sampler, num_workers=0,
                        pin_memory=args.device.startswith("cuda"))
    model = SupervisedVAE(args.max_len, args.latent_dim).to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    amp_enabled = args.device.startswith("cuda") and not args.no_mixed_precision
    scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.metrics.parent.mkdir(parents=True, exist_ok=True)
    best_key, stale = None, 0
    sizes = [int(x) for x in args.hdbscan_min_cluster_sizes.split(",")]
    samples = parse_optional_ints(args.hdbscan_min_samples)
    epsilons = [float(x) for x in args.hdbscan_epsilons.split(",")]
    config = vars(args).copy()
    config = {key: str(value) if isinstance(value, Path) else value for key, value in config.items()}
    metric_rows = []
    with args.metrics.open("w", encoding="utf-8") as metric_file:
        for epoch in range(1, args.epochs + 1):
            sampler.set_epoch(epoch)
            model.train()
            sums = {name: 0.0 for name in ("total", "supcon", "triplet", "compact", "separation", "collapse", "kl", "reconstruction")}
            for byte_ids, mask, labels, _ in loader:
                byte_ids, mask, labels = byte_ids.to(args.device), mask.to(args.device), labels.to(args.device)
                optimizer.zero_grad(set_to_none=True)
                with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=amp_enabled):
                    reconstruction, mu, logvar = model(byte_ids, mask)
                    supcon = supervised_contrastive(mu, labels, args.temperature)
                    triplet = batch_hard_triplet(mu, labels, args.triplet_margin)
                    compact, separation = centroid_loss(mu, labels, args.centroid_margin)
                    collapse = collapse_loss(mu)
                    kl = vae_kl(mu, logvar)
                    valid = mask.bool()
                    recon = F.cross_entropy(reconstruction[valid], byte_ids[valid]) if args.reconstruction_weight else mu.sum() * 0.0
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
            row = {"epoch": epoch, "train": {key: value / len(loader) for key, value in sums.items()}}
            if epoch % args.validate_every == 0 or epoch == args.epochs:
                model.eval()
                embeddings = embed_dataset(model, validation_data, args.device, args.validation_batch_size)
                report, selection = tune_hdbscan(validation_data, embeddings, sizes, samples, epsilons)
                row["validation"] = report
                key = checkpoint_key(selection)
                if best_key is None or key < best_key:
                    best_key, stale = key, 0
                    save_checkpoint(str(args.output), model, config, report, epoch)
                else:
                    stale += 1
                row["checkpoint_key"] = key
                row["best"] = key == best_key
            metric_rows.append(row)
            if args.metrics_format == "jsonl":
                metric_file.write(json.dumps(row, sort_keys=True) + "\n")
                metric_file.flush()
            else:
                metric_file.seek(0)
                json.dump(metric_rows, metric_file, indent=2, sort_keys=True)
                metric_file.truncate()
                metric_file.flush()
            print(json.dumps(row, sort_keys=True))
            if stale >= args.patience:
                break


if __name__ == "__main__":
    main()
