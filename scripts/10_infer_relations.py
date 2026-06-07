#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.model.schema import FamilyAssignment, PairRecord
from protocol_re.inference.request_response_relations import summarize_family_relations
from protocol_re.utils.logging import setup_stage_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize request-response relations between discovered message families.")
    parser.add_argument("input_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("assignments_json", help="Output from 04_discover_families.py")
    parser.add_argument("pairs_json", help="Output from 08_pair_requests_responses.py")
    parser.add_argument("output_json", help="Output JSON file for inferred family relations")
    parser.add_argument("--min-echo-support", type=float, default=0.8, help="Minimum support threshold for echo field detection (default: 0.8)")
    parser.add_argument("--min-length-support", type=float, default=0.75, help="Minimum support threshold for length relation detection (default: 0.75)")
    parser.add_argument("--min-edge-pairs", type=int, default=2, help="Minimum pair count for a family relation edge.")
    parser.add_argument("--min-edge-lift", type=float, default=1.0, help="Minimum lift over family base rates for a relation edge.")
    parser.add_argument("--max-response-families-per-request", type=int, default=5, help="Top response-family candidates to keep per request family.")
    parser.add_argument("--allow-self-relations", action="store_true", help="Keep same-family request/response candidate edges.")
    parser.add_argument("--min-relation-confidence", type=float, default=0.7, help="Minimum confidence threshold for keeping a relation (default: 0.7)")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("10_infer_relations", Path(args.log_dir))

    logger.info("Inferring family relations from request/response pairs")
    logger.decision(
        decision="Relation inference configuration",
        reason="User configuration",
        min_echo_support=args.min_echo_support,
        min_length_support=args.min_length_support,
        min_edge_pairs=args.min_edge_pairs,
        min_relation_confidence=args.min_relation_confidence,
    )

    with logger.stage("load_corpus"):
        records = load_corpus_jsonl(args.input_jsonl)
        logger.metric("message_count", len(records), "messages")

    with logger.stage("load_assignments_and_pairs"):
        logger.info(f"Loading assignments from {args.assignments_json}")
        with open(args.assignments_json, "r", encoding="utf-8") as handle:
            assignments_payload = json.load(handle)

        logger.info(f"Loading pairs from {args.pairs_json}")
        with open(args.pairs_json, "r", encoding="utf-8") as handle:
            pairs_payload = json.load(handle)

        assignments = [FamilyAssignment(**item) for item in assignments_payload["assignments"]]
        pairs = [PairRecord(**item) for item in pairs_payload]

        logger.metric("assignments_loaded", len(assignments), "assignments")
        logger.metric("pairs_loaded", len(pairs), "pairs")

    with logger.stage("summarize_relations"):
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
            min_relation_confidence=args.min_relation_confidence,
        )

        logger.metric("relations_found", len(summary['family_edges']), "relations")
        logger.metric("families_with_roles", len(summary.get('role_hints', {})), "families")

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        logger.info(f"Wrote relations to {args.output_json}")

    print(f"[+] Wrote {len(summary['family_edges'])} family relation summaries to {args.output_json}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
