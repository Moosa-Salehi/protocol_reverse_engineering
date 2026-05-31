#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.utils.logging import setup_stage_logging


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _ground_truth_placeholder(protocol_name: str) -> Dict[str, Any]:
    return {
        "protocol_name": protocol_name,
        "message_types": [],
        "relations": [],
    }


def build_evaluation_model_data(
    protocol_model: Dict[str, Any],
    evaluation: Dict[str, Any],
    llm_analysis: Dict[str, Any],
    refined_protocol_model: Dict[str, Any] | None = None,
    patch_validation: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    predicted_protocol = dict(protocol_model)
    predicted_protocol["llm_analysis"] = llm_analysis

    metadata = dict(predicted_protocol.get("metadata", {}) or {})
    metadata["pipeline_evaluation"] = evaluation
    metadata["evaluation_model_data_created_at"] = datetime.now(timezone.utc).isoformat()
    predicted_protocol["metadata"] = metadata

    output = {
        "predicted_protocol": predicted_protocol,
        "ground_truth_protocol": _ground_truth_placeholder(str(predicted_protocol.get("protocol_name", "unknown-industrial-protocol"))),
        "metadata": {
            "artifact_type": "protocol_re_evaluation_model_data",
            "source_protocol_model": "10_protocol_model.json",
            "source_pipeline_evaluation": "11_evaluation.json",
            "source_llm_analysis": "13_llm_analysis.json",
        },
    }
    if refined_protocol_model:
        refined = dict(refined_protocol_model)
        refined["llm_analysis"] = llm_analysis
        refined_metadata = dict(refined.get("metadata", {}) or {})
        refined_metadata["pipeline_evaluation"] = evaluation
        if patch_validation:
            refined_metadata["llm_patch_validation"] = patch_validation
        refined["metadata"] = refined_metadata
        output["base_predicted_protocol"] = predicted_protocol
        output["refined_predicted_protocol"] = refined
        output["predicted_protocol"] = refined
        output["metadata"]["source_refined_protocol_model"] = "10_protocol_model.refined.json"
        output["metadata"]["source_llm_patch_validation"] = "13_llm_patch_validation.json"
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare final evaluation input data from pipeline protocol model artifacts.")
    parser.add_argument("protocol_model_json", help="Input protocol model JSON from stage 12")
    parser.add_argument("evaluation_json", help="Input pipeline evaluation JSON from stage 13")
    parser.add_argument("llm_analysis_json", help="Input LLM analysis JSON from stage 15")
    parser.add_argument("output_json", help="Output evaluation input JSON conforming to schema/evaluation_input.schema.json")
    parser.add_argument("--refined-protocol-model-json", help="Optional refined model JSON from stage 15b")
    parser.add_argument("--patch-validation-json", help="Optional patch validation JSON from stage 15b")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("16_prepare_evaluation_data", Path(args.log_dir))

    logger.info("Preparing evaluation model data")

    with logger.stage("load_data"):
        logger.info(f"Loading protocol model from {args.protocol_model_json}")
        protocol_model = _load_json(args.protocol_model_json)

        logger.info(f"Loading evaluation from {args.evaluation_json}")
        evaluation = _load_json(args.evaluation_json)

        logger.info(f"Loading LLM analysis from {args.llm_analysis_json}")
        llm_analysis = _load_json(args.llm_analysis_json)

        refined_protocol_model = None
        if args.refined_protocol_model_json:
            logger.info(f"Loading refined model from {args.refined_protocol_model_json}")
            refined_protocol_model = _load_json(args.refined_protocol_model_json)

        patch_validation = None
        if args.patch_validation_json:
            logger.info(f"Loading patch validation from {args.patch_validation_json}")
            patch_validation = _load_json(args.patch_validation_json)

    with logger.stage("build_evaluation_data"):
        output = build_evaluation_model_data(
            protocol_model,
            evaluation,
            llm_analysis,
            refined_protocol_model,
            patch_validation,
        )
        logger.metric("families_in_output", len(output.get("predicted_protocol", {}).get("families", [])), "families")

    with logger.stage("write_output"):
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(output, handle, indent=2, ensure_ascii=False)
        logger.info(f"Wrote evaluation data to {output_path}")

    print(f"[+] Wrote evaluation model data to {output_path}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
