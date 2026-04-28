#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from protocol_re.corpus.message_corpus import iter_corpus_jsonl
from protocol_re.features.extraction import stream_feature_artifacts
from protocol_re.model.schema import FamilyAssignment


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract reusable per-message and per-family feature artifacts from the canonical corpus.")
    parser.add_argument("input_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("output_dir", help="Directory for feature artifacts")
    parser.add_argument("--assignments-json", help="Optional family assignment JSON from 05_discover_families.py")
    parser.add_argument("--include-unassigned", action="store_true", help="Include records without a family assignment")
    args = parser.parse_args()

    assignments = None
    if args.assignments_json:
        with open(args.assignments_json, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        assignments = [FamilyAssignment(**item) for item in payload["assignments"]]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    message_path = output_dir / "message_features.jsonl"
    family_path = output_dir / "family_features.json"

    with open(message_path, "w", encoding="utf-8") as handle:
        family_features = stream_feature_artifacts(
            iter_corpus_jsonl(args.input_jsonl),
            handle,
            assignments=assignments,
            include_unassigned=args.include_unassigned,
        )

    with open(family_path, "w", encoding="utf-8") as handle:
        json.dump(family_features, handle, indent=2)

    message_count = sum(item["message_count"] for item in family_features.values())
    print(f"[+] Wrote {message_count} assigned message feature records to {message_path}")
    print(f"[+] Wrote {len(family_features)} family feature records to {family_path}")


if __name__ == "__main__":
    main()
