#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.corpus.request_response_pairing import pair_request_response_messages
from protocol_re.model.schema import FamilyAssignment


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer likely request/response message pairs inside each session.")
    parser.add_argument("input_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("output_json", help="Output JSON file for pair hypotheses")
    parser.add_argument("--assignments-json", help="Optional family assignment JSON from 04_discover_families.py")
    parser.add_argument("--min-score", type=float, default=1.5, help="Minimum pairing score")
    parser.add_argument("--max-index-gap", type=int, default=3, help="Maximum forward search window within a session")
    args = parser.parse_args()

    records = load_corpus_jsonl(args.input_jsonl)
    assignments = None
    if args.assignments_json:
        with open(args.assignments_json, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        assignments = [FamilyAssignment(**item) for item in payload["assignments"]]
    pairs = pair_request_response_messages(
        records,
        assignments=assignments,
        min_score=args.min_score,
        max_index_gap=args.max_index_gap,
    )

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump([pair.to_dict() for pair in pairs], handle, indent=2)

    print(f"[+] Wrote {len(pairs)} request/response pair hypotheses to {args.output_json}")


if __name__ == "__main__":
    main()
