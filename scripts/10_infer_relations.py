#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.model.schema import FamilyAssignment, PairRecord
from protocol_re.inference.request_response_relations import summarize_family_relations


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize request-response relations between discovered message families.")
    parser.add_argument("input_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("assignments_json", help="Output from 04_discover_families.py")
    parser.add_argument("pairs_json", help="Output from 07_pair_requests_responses.py")
    parser.add_argument("output_json", help="Output JSON file for inferred family relations")
    parser.add_argument("--min-echo-support", type=float, default=0.9)
    parser.add_argument("--min-length-support", type=float, default=0.9)
    parser.add_argument("--min-edge-pairs", type=int, default=2, help="Minimum pair count for a family relation edge.")
    parser.add_argument("--min-edge-lift", type=float, default=1.0, help="Minimum lift over family base rates for a relation edge.")
    parser.add_argument("--max-response-families-per-request", type=int, default=5, help="Top response-family candidates to keep per request family.")
    parser.add_argument("--allow-self-relations", action="store_true", help="Keep same-family request/response candidate edges.")
    args = parser.parse_args()

    records = load_corpus_jsonl(args.input_jsonl)
    with open(args.assignments_json, "r", encoding="utf-8") as handle:
        assignments_payload = json.load(handle)
    with open(args.pairs_json, "r", encoding="utf-8") as handle:
        pairs_payload = json.load(handle)

    assignments = [FamilyAssignment(**item) for item in assignments_payload["assignments"]]
    pairs = [PairRecord(**item) for item in pairs_payload]
    summary = summarize_family_relations(
        records,
        pairs,
        assignments,
        min_echo_support=args.min_echo_support,
        min_length_support=args.min_length_support,
        min_edge_pairs=args.min_edge_pairs,
        min_edge_lift=args.min_edge_lift,
        max_response_families_per_request=args.max_response_families_per_request,
        allow_self_relations=args.allow_self_relations,
    )

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print(f"[+] Wrote {len(summary['family_edges'])} family relation summaries to {args.output_json}")


if __name__ == "__main__":
    main()
