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
    )

    payload = {
        "assignments": [assignment.to_dict() for assignment in result.assignments],
        "labels": result.labels,
        "sample_size": result.sample_size,
        "feature_shape": list(result.feature_shape),
    }
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print(f"[+] Wrote {len(result.assignments)} family assignments to {args.output_json}")


if __name__ == "__main__":
    main()
