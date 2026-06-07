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


CONCRETE_WIDTH_TYPES = {
    1: "uint8",
    2: "uint16",
    4: "uint32",
    8: "uint64",
}


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _field_length(field: Dict[str, Any]) -> int | None:
    length = field.get("length")
    if length is not None:
        return int(length)
    start = field.get("start")
    end = field.get("end")
    if start is None or end is None:
        return None
    return int(end) - int(start)


def _infer_export_encoding(field: Dict[str, Any]) -> str | None:
    attributes = field.get("attributes") if isinstance(field.get("attributes"), dict) else {}
    encoding = field.get("encoding_type") or attributes.get("encoding_type") or attributes.get("encoding")
    if encoding:
        return str(encoding)
    length = _field_length(field)
    if length is None:
        return None
    base = CONCRETE_WIDTH_TYPES.get(length)
    if not base:
        return "bytes" if length > 4 else None
    endian = field.get("endian")
    if length in (2, 4, 8) and endian in {"big", "little"}:
        return f"{base}_{'be' if endian == 'big' else 'le'}"
    return base


def _normalize_export_field(field: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(field)
    attributes = normalized.get("attributes") if isinstance(normalized.get("attributes"), dict) else {}
    attributes = dict(attributes)

    if "semantic_role" not in attributes:
        role = normalized.get("semantic_role")
        if role:
            attributes["semantic_role"] = role

    original_type = normalized.get("field_type")
    encoding = _infer_export_encoding(normalized)
    if original_type and "inferred_role_label" not in attributes:
        attributes["inferred_role_label"] = original_type
    if encoding:
        normalized["field_type"] = encoding
        normalized["encoding_type"] = encoding
        attributes["encoding_type"] = encoding
        attributes.setdefault("encoding", encoding)

    normalized["attributes"] = attributes
    return normalized


def _normalize_protocol_field_types(protocol_model: Dict[str, Any]) -> Dict[str, Any]:
    model = dict(protocol_model)
    families = []
    for family in model.get("families", []) or []:
        family_copy = dict(family)
        family_copy["field_hypotheses"] = [
            _normalize_export_field(field)
            for field in family_copy.get("field_hypotheses", []) or []
            if isinstance(field, dict)
        ]
        families.append(family_copy)
    model["families"] = families
    return model


def _refresh_refined_framing(refined_protocol_model: Dict[str, Any], base_protocol_model: Dict[str, Any]) -> Dict[str, Any]:
    refreshed = dict(refined_protocol_model)
    base_metadata = base_protocol_model.get("metadata") if isinstance(base_protocol_model.get("metadata"), dict) else {}
    refined_metadata = refreshed.get("metadata") if isinstance(refreshed.get("metadata"), dict) else {}
    refined_metadata = dict(refined_metadata)
    if "framing_global_summary" in base_metadata:
        refined_metadata["framing_global_summary"] = base_metadata["framing_global_summary"]
    refreshed["metadata"] = refined_metadata

    base_by_family = {
        str(family.get("family_id")): family
        for family in base_protocol_model.get("families", []) or []
        if isinstance(family, dict)
    }
    families = []
    for family in refreshed.get("families", []) or []:
        if not isinstance(family, dict):
            continue
        family_copy = dict(family)
        base_family = base_by_family.get(str(family_copy.get("family_id"))) or {}
        if "framing_summary" in base_family:
            family_copy["framing_summary"] = base_family["framing_summary"]
        families.append(family_copy)
    refreshed["families"] = families
    return refreshed


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
    predicted_protocol = _normalize_protocol_field_types(protocol_model)
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
        refined = _normalize_protocol_field_types(_refresh_refined_framing(refined_protocol_model, predicted_protocol))
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
    parser.add_argument("output_json", help="Output evaluation input JSON conforming to assets/schema/evaluation_input.schema.json")
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
