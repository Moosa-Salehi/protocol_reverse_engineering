#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.evaluation.reporting import build_evaluation_report


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build evaluation metrics for the protocol reverse-engineering pipeline.")
    parser.add_argument("messages_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("assignments_json", help="Family assignment JSON from 04_discover_families.py")
    parser.add_argument("families_json", help="Family boundary JSON from 06_infer_boundaries.py")
    parser.add_argument("pairs_json", help="Request/response pair JSON from 07_pair_requests_responses.py")
    parser.add_argument("relations_json", help="Relation JSON from 10_infer_relations.py")
    parser.add_argument("output_json", help="Output evaluation report JSON")
    parser.add_argument("--semantics-json", help="Optional semantic summary JSON from 11_infer_semantics.py")
    args = parser.parse_args()

    semantics_payload = _load_json(args.semantics_json) if args.semantics_json else {}
    report = build_evaluation_report(
        records=load_corpus_jsonl(args.messages_jsonl),
        assignments_payload=_load_json(args.assignments_json),
        families_payload=_load_json(args.families_json),
        pairs_payload=_load_json(args.pairs_json),
        relations_payload=_load_json(args.relations_json),
        semantics_payload=semantics_payload,
    )

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print(f"[+] Wrote evaluation report to {args.output_json}")


if __name__ == "__main__":
    main()
