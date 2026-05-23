#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.corpus.message_corpus import iter_corpus_jsonl
from protocol_re.features.extraction import stream_feature_artifacts
from protocol_re.model.schema import FamilyAssignment


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract reusable per-family feature artifacts from the canonical corpus.")
    parser.add_argument("input_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("output", help="output family features json")
    parser.add_argument("--assignments-json", help="Optional family assignment JSON from 04_discover_families.py")
    parser.add_argument("--include-unassigned", action="store_true", help="Include records without a family assignment")
    parser.add_argument("--feature-mode", choices=["raw_bytes", "structural", "neural", "hybrid"], default=None, help="Clustering feature mode metadata passthrough")
    parser.add_argument("--neural-model-path", default=None, help="Optional neural model path metadata passthrough")
    parser.add_argument("--latent-cache-path", default=None, help="Optional latent cache path metadata passthrough")
    parser.add_argument("--neural-batch-size", type=int, default=256, help="Optional neural batch size metadata passthrough")
    args = parser.parse_args()

    assignments = None
    if args.assignments_json:
        with open(args.assignments_json, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        assignments = [FamilyAssignment(**item) for item in payload["assignments"]]

    family_path = args.output

    family_features = stream_feature_artifacts(
        iter_corpus_jsonl(args.input_jsonl),
        assignments=assignments,
        include_unassigned=args.include_unassigned,
    )

    with open(family_path, "w", encoding="utf-8") as handle:
        json.dump(family_features, handle, indent=2)

    message_count = sum(item["message_count"] for item in family_features.values())
    print(f"[+] Processed {message_count} assigned messages")
    print(f"[+] Wrote {len(family_features)} family feature records to {family_path}")


if __name__ == "__main__":
    main()
