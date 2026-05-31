#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.export.llm_evidence import build_llm_evidence_bundle
from protocol_re.utils.logging import setup_stage_logging


def _load_optional_json(path: str | None):
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a compact per-family evidence bundle for downstream LLM analysis.")
    parser.add_argument("protocol_model_json", help="Input protocol model JSON from 12_build_protocol_model.py")
    parser.add_argument("output_json", help="Output compact evidence bundle JSON")
    parser.add_argument("--evaluation-json", help="Optional evaluation report JSON from 13_evaluate_pipeline.py")
    parser.add_argument("--family-limit", type=int, default=30, help="Optional maximum number of largest families to include")
    parser.add_argument("--relation-limit", type=int, default=8, help="Max global relation summaries to retain")
    parser.add_argument("--field-limit", type=int, default=8, help="Max field/semantic hypotheses to retain per family and global candidate type")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON; omitted by default to keep LLM evidence compact")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("14_export_llm_evidence", Path(args.log_dir))

    logger.info("Exporting LLM evidence bundle")
    logger.decision(
        decision="LLM evidence export configuration",
        reason="User configuration",
        family_limit=args.family_limit,
        relation_limit=args.relation_limit,
        field_limit=args.field_limit,
        pretty_print=args.pretty,
    )

    with logger.stage("load_protocol_model"):
        logger.info(f"Loading protocol model from {args.protocol_model_json}")
        with open(args.protocol_model_json, "r", encoding="utf-8") as handle:
            model = json.load(handle)
        logger.metric("families_in_model", len(model.get("families", [])), "families")

    with logger.stage("load_evaluation"):
        evaluation = _load_optional_json(args.evaluation_json)
        if evaluation:
            logger.info(f"Loaded evaluation from {args.evaluation_json}")

    with logger.stage("build_evidence_bundle"):
        bundle = build_llm_evidence_bundle(
            model,
            evaluation=evaluation,
            family_limit=args.family_limit,
            relation_limit=args.relation_limit,
            field_limit=args.field_limit,
        )
        logger.metric("families_in_bundle", len(bundle['families']), "families")
        logger.metric("relations_in_bundle", len(bundle.get('global_relations', [])), "relations")

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            if args.pretty:
                json.dump(bundle, handle, indent=2)
            else:
                json.dump(bundle, handle, separators=(",", ":"))
        logger.info(f"Wrote LLM evidence bundle to {args.output_json}")

    print(f"[+] Wrote LLM evidence bundle with {len(bundle['families'])} families to {args.output_json}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
