#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.corpus.request_response_pairing import pair_request_response_messages
from protocol_re.model.schema import FamilyAssignment
from protocol_re.utils.logging import setup_stage_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer likely request/response message pairs inside each session.")
    parser.add_argument("input_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("output_json", help="Output JSON file for pair hypotheses")
    parser.add_argument("--assignments-json", help="Optional family assignment JSON from 04_discover_families.py")
    parser.add_argument("--min-score", type=float, default=1.5, help="Minimum pairing score")
    parser.add_argument("--max-index-gap", type=int, default=3, help="Maximum forward search window within a session")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("08_pair_requests_responses", Path(args.log_dir))

    logger.info(f"Loading messages from {args.input_jsonl}")
    logger.decision(
        decision="Request/response pairing configuration",
        reason="User configuration",
        min_score=args.min_score,
        max_index_gap=args.max_index_gap,
    )

    with logger.stage("load_corpus"):
        records = load_corpus_jsonl(args.input_jsonl)
        logger.metric("message_count", len(records), "messages")

    with logger.stage("load_assignments"):
        assignments = None
        if args.assignments_json:
            logger.info(f"Loading family assignments from {args.assignments_json}")
            with open(args.assignments_json, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            assignments = [FamilyAssignment(**item) for item in payload["assignments"]]
            logger.metric("assignments_loaded", len(assignments), "assignments")
        else:
            logger.info("No assignments provided, using heuristic pairing")

    with logger.stage("pair_messages"):
        pairs = pair_request_response_messages(
            records,
            assignments=assignments,
            min_score=args.min_score,
            max_index_gap=args.max_index_gap,
        )
        logger.metric("pairs_found", len(pairs), "pairs")
        logger.info(f"Found {len(pairs)} request/response pairs")

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump([pair.to_dict() for pair in pairs], handle, indent=2)
        logger.info(f"Wrote pairs to {args.output_json}")

    print(f"[+] Wrote {len(pairs)} request/response pair hypotheses to {args.output_json}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
