#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.evaluation.reporting import build_evaluation_report
from protocol_re.utils.logging import setup_stage_logging


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build evaluation metrics for the protocol reverse-engineering pipeline.")
    parser.add_argument("messages_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("assignments_json", help="Family assignment JSON from 04_discover_families.py")
    parser.add_argument("families_json", help="Family boundary JSON from 07_infer_boundaries.py")
    parser.add_argument("pairs_json", help="Request/response pair JSON from 08_pair_requests_responses.py")
    parser.add_argument("relations_json", help="Relation JSON from 10_infer_relations.py")
    parser.add_argument("output_json", help="Output evaluation report JSON")
    parser.add_argument("--semantics-json", help="Optional semantic summary JSON from 11_infer_semantics.py")
    parser.add_argument("--framing-json", help="Optional framing summary JSON from 05_infer_framing.py")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("13_evaluate_pipeline", Path(args.log_dir))

    logger.info("Building evaluation report for pipeline")

    with logger.stage("load_data"):
        logger.info(f"Loading messages from {args.messages_jsonl}")
        records = load_corpus_jsonl(args.messages_jsonl)
        logger.metric("message_count", len(records), "messages")

        logger.info(f"Loading assignments from {args.assignments_json}")
        assignments_payload = _load_json(args.assignments_json)

        logger.info(f"Loading families from {args.families_json}")
        families_payload = _load_json(args.families_json)

        logger.info(f"Loading pairs from {args.pairs_json}")
        pairs_payload = _load_json(args.pairs_json)

        logger.info(f"Loading relations from {args.relations_json}")
        relations_payload = _load_json(args.relations_json)

        semantics_payload = _load_json(args.semantics_json) if args.semantics_json else {}
        framing_payload = _load_json(args.framing_json) if args.framing_json else {}

        if args.semantics_json:
            logger.info(f"Loading semantics from {args.semantics_json}")
        if args.framing_json:
            logger.info(f"Loading framing from {args.framing_json}")

    with logger.stage("build_evaluation_report"):
        report = build_evaluation_report(
            records=records,
            assignments_payload=assignments_payload,
            families_payload=families_payload,
            pairs_payload=pairs_payload,
            relations_payload=relations_payload,
            semantics_payload=semantics_payload,
            framing_payload=framing_payload,
        )

        # Log key metrics from report
        if "coverage" in report:
            coverage = report["coverage"]
            logger.metric("corpus_coverage", coverage.get("corpus_coverage_ratio", 0), "ratio")
            logger.metric("clustering_sample_ratio", coverage.get("clustering_sample_ratio", 0), "ratio")

        if "clustering" in report:
            clustering = report["clustering"]
            logger.metric("families_discovered", clustering.get("family_count", 0), "families")

        if "pairing" in report:
            pairing = report["pairing"]
            logger.metric("pairs_found", pairing.get("pair_count", 0), "pairs")

    diagnostic_summary = ((report.get("diagnostics") or {}).get("summary") or {})
    warning_count = diagnostic_summary.get('warning_family_count', 0)

    if warning_count > 0:
        logger.warning(f"Clustering diagnostic warnings for {warning_count} families")

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
        logger.info(f"Wrote evaluation report to {args.output_json}")

    print(f"[+] Wrote evaluation report to {args.output_json}")
    if diagnostic_summary:
        print(f"[+] Clustering diagnostic warning families: {warning_count}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
