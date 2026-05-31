#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.llm.refinement import collect_llm_patches, refine_protocol_model, refinement_delta_summary
from protocol_re.utils.logging import setup_stage_logging


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_json_optional(path: str | None) -> Dict[str, Any] | None:
    if not path:
        return None
    candidate = Path(path)
    if not candidate.is_file():
        return None
    return _load_json(path)


def _write_json(path: str, payload: Dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and apply evidence-gated LLM RFC 6902 patches to produce a refined protocol model."
    )
    parser.add_argument("protocol_model_json", help="Input base protocol model, normally data/10_protocol_model.json")
    parser.add_argument("llm_analysis_json", help="Input LLM analysis artifact from scripts/15_analyze_with_llm.py")
    parser.add_argument("refined_model_json", help="Output refined protocol model, normally data/10_protocol_model.refined.json")
    parser.add_argument("--evidence-json", default="data/12_llm_evidence.json", help="Evidence bundle used for support gating")
    parser.add_argument("--schema-json", default="schema/protocol_model.schema.json", help="Protocol model JSON schema")
    parser.add_argument("--patches-out", default="data/13_llm_patches.json", help="Output collected patch artifact")
    parser.add_argument(
        "--validation-out",
        default="data/13_llm_patch_validation.json",
        help="Output accepted/rejected patch validation artifact",
    )
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("15b_apply_llm_refinement", Path(args.log_dir))

    logger.info("Applying LLM refinement patches to protocol model")

    with logger.stage("load_data"):
        logger.info(f"Loading protocol model from {args.protocol_model_json}")
        model = _load_json(args.protocol_model_json)
        logger.metric("families_in_model", len(model.get('families', [])), "families")

        logger.info(f"Loading LLM analysis from {args.llm_analysis_json}")
        analysis = _load_json(args.llm_analysis_json)

        evidence = _load_json_optional(args.evidence_json)
        if evidence:
            logger.info(f"Loaded evidence from {args.evidence_json}")

        schema = _load_json_optional(args.schema_json)
        if schema:
            logger.info(f"Loaded schema from {args.schema_json}")

    with logger.stage("collect_patches"):
        patch_bundle = collect_llm_patches(analysis)
        logger.metric("patches_collected", len(patch_bundle.get('patches', [])), "patches")

    with logger.stage("apply_refinement"):
        refined, validation = refine_protocol_model(model, patch_bundle, evidence=evidence, schema=schema)
        validation["delta_summary"] = refinement_delta_summary(model, refined)
        validation["source_protocol_model"] = args.protocol_model_json
        validation["source_llm_analysis"] = args.llm_analysis_json
        validation["source_evidence"] = args.evidence_json

        logger.metric("patches_accepted", validation['accepted_patch_count'], "patches")
        logger.metric("patches_rejected", validation['rejected_patch_count'], "patches")
        logger.decision(
            decision=f"Applied {validation['accepted_patch_count']} patches",
            reason=f"Evidence-gated validation, rejected {validation['rejected_patch_count']}",
            acceptance_rate=validation['accepted_patch_count'] / len(patch_bundle.get('patches', [])) if patch_bundle.get('patches') else 0
        )

    with logger.stage("write_output"):
        _write_json(args.patches_out, patch_bundle)
        logger.info(f"Wrote patches to {args.patches_out}")

        _write_json(args.validation_out, validation)
        logger.info(f"Wrote validation to {args.validation_out}")

        _write_json(args.refined_model_json, refined)
        logger.info(f"Wrote refined model to {args.refined_model_json}")

    print(
        "[+] LLM refinement applied: "
        f"{validation['accepted_patch_count']} accepted, {validation['rejected_patch_count']} rejected; "
        f"wrote {args.refined_model_json}"
    )

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
