#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.clustering.family_discovery import discover_families
from protocol_re.corpus.message_corpus import load_corpus_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover message families from the canonical corpus.")
    parser.add_argument("input_jsonl")
    parser.add_argument("output_json")
    parser.add_argument("--method", choices=["dbscan", "hdbscan"], default="hdbscan")
    parser.add_argument("--sample-size", type=int, default=100000)
    parser.add_argument("--pca-components", type=int, default=32)
    parser.add_argument("--dbscan-eps", type=float, default=40.0)
    parser.add_argument("--dbscan-min-samples", type=int, default=5)
    parser.add_argument("--hdbscan-min-cluster-size", type=int, default=50)
    parser.add_argument("--feature-mode", choices=["raw_bytes", "structural", "neural", "hybrid"], default="raw_bytes")
    parser.add_argument("--neural-model-path", default="industrial_encoder_only.pth")
    parser.add_argument("--latent-cache-path")
    parser.add_argument("--neural-batch-size", type=int, default=256)
    args = parser.parse_args()

    records = load_corpus_jsonl(args.input_jsonl)
    result = discover_families(
        records,
        method=args.method,
        sample_size=args.sample_size,
        pca_components=args.pca_components,
        dbscan_eps=args.dbscan_eps,
        dbscan_min_samples=args.dbscan_min_samples,
        hdbscan_min_cluster_size=args.hdbscan_min_cluster_size,
        feature_mode=args.feature_mode,
        neural_model_path=args.neural_model_path,
        latent_cache_path=args.latent_cache_path,
        neural_batch_size=args.neural_batch_size,
    )
    requested_sample = args.sample_size if args.sample_size is not None else len(records)
    assignment_strategy = (
        "full_corpus_clustering"
        if result.sample_size >= len(records)
        else "sample_unique_then_duplicate_and_centroid_propagation"
    )

    payload = {
        "assignments": [assignment.to_dict() for assignment in result.assignments],
        "labels": result.labels,
        "sample_size": result.sample_size,
        "assigned_message_count": len(result.assignments),
        "total_message_count": len(records),
        "requested_sample_size": requested_sample,
        "assignment_strategy": assignment_strategy,
        "feature_shape": list(result.feature_shape),
        "diagnostics": result.diagnostics or {},
        "metadata": {
            "feature_mode": result.feature_mode,
            "requested_feature_mode": result.requested_feature_mode,
            "neural_model": result.neural_model,
            "latent_dim": result.latent_dim,
            "latent_cache": result.latent_cache,
            "symbolic_feature_count": result.symbolic_feature_count,
            "fallback_reason": result.fallback_reason,
        },
    }
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    family_count = len({assignment.family_id for assignment in result.assignments})
    print(f"[+] Discovered {family_count} families")
    print(f"[+] Wrote {len(result.assignments)} family assignments to {args.output_json}")


if __name__ == "__main__":
    main()
