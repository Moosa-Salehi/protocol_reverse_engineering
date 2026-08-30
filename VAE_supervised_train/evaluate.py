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
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from VAE_supervised_train.common import parse_protocols, seed_everything
from VAE_supervised_train.data import MessageFamilyDataset
from VAE_supervised_train.metrics import clustering_metrics, run_hdbscan
from VAE_supervised_train.model import load_checkpoint


@torch.inference_mode()
def embed_dataset(model, dataset, device, batch_size: int, progress: bool = False) -> np.ndarray:
    output = np.zeros((len(dataset), model.latent_dim), dtype=np.float32)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    batches = tqdm(loader, desc="Embedding validation", unit="batch", leave=False,
                   disable=not progress, dynamic_ncols=True)
    for byte_ids, mask, _, indexes in batches:
        mu, _ = model.encode(byte_ids.to(device), mask.to(device))
        output[indexes.numpy()] = mu.cpu().numpy()
    return output


def evaluate_embeddings(dataset, embeddings: np.ndarray, min_cluster_size: int = 5,
                        min_samples: int | None = None, epsilon: float = 0.0,
                        protocol_parameters: dict[str, dict] | None = None) -> dict:
    per_protocol, aggregate_truth, aggregate_predicted = {}, [], []
    cluster_offset = 0
    protocols = sorted({row["protocol_id"] for row in dataset.rows})
    selected_parameters = {}
    for protocol in protocols:
        indexes = np.asarray([i for i, row in enumerate(dataset.rows) if row["protocol_id"] == protocol])
        truth_keys = [dataset.rows[i]["trusted_family_id"] for i in indexes]
        mapping = {key: number for number, key in enumerate(sorted(set(truth_keys)))}
        truth = np.asarray([mapping[key] for key in truth_keys])
        parameters = (protocol_parameters or {}).get(protocol, {})
        protocol_min_cluster_size = int(parameters.get("min_cluster_size", min_cluster_size))
        protocol_min_samples = parameters.get("min_samples", min_samples)
        protocol_epsilon = float(parameters.get("cluster_selection_epsilon", epsilon))
        predicted = run_hdbscan(embeddings[indexes], protocol_min_cluster_size,
                                protocol_min_samples, protocol_epsilon)
        per_protocol[protocol] = clustering_metrics(truth, predicted)
        selected_parameters[protocol] = {
            "min_cluster_size": protocol_min_cluster_size,
            "min_samples": protocol_min_samples,
            "cluster_selection_epsilon": protocol_epsilon,
        }
        aggregate_truth.extend(f"{protocol}:{key}" for key in truth_keys)
        aggregate_predicted.extend([-1 if value < 0 else cluster_offset + int(value) for value in predicted])
        cluster_offset += max(0, len(set(predicted.tolist()) - {-1}))
    global_mapping = {key: number for number, key in enumerate(sorted(set(aggregate_truth)))}
    overall = clustering_metrics(np.asarray([global_mapping[x] for x in aggregate_truth]), np.asarray(aggregate_predicted))
    return {"per_protocol": per_protocol, "overall": overall,
            "hdbscan_per_protocol": selected_parameters}


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate supervised VAE embeddings with per-protocol HDBSCAN.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--protocols", default="all")
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--min-confidence", type=float, default=0.9)
    parser.add_argument("--min-family-support", type=int, default=1)
    parser.add_argument("--min-cluster-size", type=int, default=5)
    parser.add_argument("--min-samples", type=int)
    parser.add_argument("--cluster-selection-epsilon", type=float, default=0.0)
    parser.add_argument("--use-checkpoint-hdbscan", action=argparse.BooleanOptionalAction, default=True,
                        help="Use per-protocol HDBSCAN settings saved with a revised trainer checkpoint.")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    seed_everything(args.seed)
    model, checkpoint = load_checkpoint(args.checkpoint, args.device)
    dataset = MessageFamilyDataset(args.dataset, parse_protocols(args.protocols), model.max_len,
                                   args.min_confidence, args.min_family_support)
    if not dataset.rows:
        raise SystemExit("No eligible records selected")
    embeddings = embed_dataset(model, dataset, args.device, args.batch_size, progress=True)
    saved_parameters = None
    if args.use_checkpoint_hdbscan:
        saved_parameters = (checkpoint.get("metrics") or {}).get("hdbscan_per_protocol")
    report = evaluate_embeddings(dataset, embeddings, args.min_cluster_size, args.min_samples,
                                 args.cluster_selection_epsilon, saved_parameters)
    report["checkpoint"] = str(args.checkpoint)
    report["checkpoint_epoch"] = checkpoint.get("epoch")
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
