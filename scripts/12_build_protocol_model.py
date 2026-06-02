#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import fields as dataclass_fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.model.schema import FamilyFeatureSummary, FamilyModel, FamilyRelation, FamilySemanticSummary, FieldHypothesis, ProtocolModel, Segment
from protocol_re.utils.logging import setup_stage_logging


def _build_relation(edge: dict) -> FamilyRelation:
    """Construct a FamilyRelation from a stage-10 edge dict, tolerating extra keys.

    Stage 10 emits ``relation_confidence``; the schema field is ``confidence``.
    Unknown keys are dropped so the model stays forward-compatible with new
    relation metrics added upstream.
    """
    edge = dict(edge)
    if "relation_confidence" in edge and "confidence" not in edge:
        edge["confidence"] = edge.pop("relation_confidence")
    valid = {f.name for f in dataclass_fields(FamilyRelation)}
    return FamilyRelation(**{k: v for k, v in edge.items() if k in valid})


def _build_field_hypothesis(field: dict) -> FieldHypothesis:
    """Construct a FieldHypothesis while preserving upstream field extensions.

    LLM semantic labeling can annotate field hypotheses with top-level
    ``semantic_*`` keys. The protocol model schema keeps those extension values
    under ``attributes``, so fold unsupported keys there before constructing the
    dataclass.
    """
    payload = dict(field)
    attributes = payload.get("attributes") if isinstance(payload.get("attributes"), dict) else {}
    attributes = dict(attributes)

    for key in ("semantic_role", "semantic_confidence", "semantic_evidence"):
        if key in payload and key not in attributes:
            attributes[key] = payload[key]

    valid = {f.name for f in dataclass_fields(FieldHypothesis)}
    extras = {key: value for key, value in payload.items() if key not in valid}
    if extras:
        existing_extras = attributes.get("upstream_extras")
        if isinstance(existing_extras, dict):
            attributes["upstream_extras"] = {**existing_extras, **extras}
        else:
            attributes["upstream_extras"] = extras

    payload["attributes"] = attributes
    return FieldHypothesis(**{key: value for key, value in payload.items() if key in valid})


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble a protocol-model JSON document from inferred family summaries.")
    parser.add_argument("family_json", help="Output from 07_infer_boundaries.py")
    parser.add_argument("output_json", help="Protocol model output path")
    parser.add_argument("--features-json", help="Optional family feature JSON from 06_extract_features.py")
    parser.add_argument("--keywords-json", help="Optional keyword/subformat JSON from 09_infer_keywords.py")
    parser.add_argument("--relations-json", help="Optional output from 10_infer_relations.py")
    parser.add_argument("--semantics-json", help="Optional output from 11_infer_semantics.py")
    parser.add_argument("--framing-json", help="Optional framing hypotheses from 05_infer_framing.py")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("12_build_protocol_model", Path(args.log_dir))

    logger.info("Building protocol model from family summaries")
    logger.decision(
        decision="Assembling protocol model",
        reason="Combining all inference artifacts",
        has_features=args.features_json is not None,
        has_keywords=args.keywords_json is not None,
        has_relations=args.relations_json is not None,
        has_semantics=args.semantics_json is not None,
        has_framing=args.framing_json is not None,
    )

    with logger.stage("load_family_data"):
        logger.info(f"Loading family data from {args.family_json}")
        with open(args.family_json, "r", encoding="utf-8") as handle:
            family_data = json.load(handle)
        logger.metric("families_loaded", len(family_data), "families")

    with logger.stage("load_optional_artifacts"):
        features_payload = {}
        if args.features_json:
            logger.info(f"Loading features from {args.features_json}")
            with open(args.features_json, "r", encoding="utf-8") as handle:
                features_payload = json.load(handle)
            logger.metric("families_with_features", len(features_payload), "families")

        keywords_payload = {}
        if args.keywords_json:
            logger.info(f"Loading keywords from {args.keywords_json}")
            with open(args.keywords_json, "r", encoding="utf-8") as handle:
                keywords_payload = json.load(handle)
            logger.metric("families_with_keywords", len(keywords_payload), "families")

        relations_payload = {"family_edges": [], "role_hints": {}}
        if args.relations_json:
            logger.info(f"Loading relations from {args.relations_json}")
            with open(args.relations_json, "r", encoding="utf-8") as handle:
                relations_payload = json.load(handle)
            logger.metric("relations_loaded", len(relations_payload.get("family_edges", [])), "relations")

        semantics_payload = {}
        if args.semantics_json:
            logger.info(f"Loading semantics from {args.semantics_json}")
            with open(args.semantics_json, "r", encoding="utf-8") as handle:
                semantics_payload = json.load(handle)
            logger.metric("families_with_semantics", len(semantics_payload), "families")

        framing_payload = {"families": {}, "global": {}}
        if args.framing_json:
            logger.info(f"Loading framing from {args.framing_json}")
            with open(args.framing_json, "r", encoding="utf-8") as handle:
                framing_payload = json.load(handle)
            logger.metric("families_with_framing", len(framing_payload.get("families", {})), "families")

    with logger.stage("build_family_models"):
        families = []
        for family_id, details in family_data.items():
            with logger.context(family_id=family_id):
                segments = [Segment(**segment) for segment in details.get("segments", [])]
                field_hypotheses = [_build_field_hypothesis(field) for field in details.get("field_hypotheses", [])]
                feature_summary = features_payload.get(family_id)
                keyword_summary = keywords_payload.get(family_id)
                framing_summary = (framing_payload.get("families") or {}).get(family_id)
                role_hint = relations_payload.get("role_hints", {}).get(family_id, {})
                semantic_summary = semantics_payload.get(family_id)
                related_families = []
                for edge in relations_payload.get("family_edges", []):
                    if edge["request_family_id"] == family_id:
                        related_families.append(edge["response_family_id"])
                    elif edge["response_family_id"] == family_id:
                        related_families.append(edge["request_family_id"])
                families.append(
                    FamilyModel(
                        family_id=family_id,
                        role=role_hint.get("role_hint", "unknown"),
                        message_count=details.get("message_count", 0),
                        template=details.get("template", ""),
                        segments=segments,
                        field_hypotheses=field_hypotheses,
                        feature_summary=FamilyFeatureSummary(**feature_summary) if feature_summary else None,
                        semantic_summary=FamilySemanticSummary(**semantic_summary) if semantic_summary else None,
                        keyword_summary=keyword_summary,
                        framing_summary=framing_summary,
                        related_families=sorted(set(related_families)),
                        evidence={
                            "source": args.family_json,
                            "keyword_evidence_source": args.keywords_json if keyword_summary else None,
                            "framing_evidence_source": args.framing_json if framing_summary else None,
                            **role_hint,
                        },
                    )
                )

        logger.metric("family_models_built", len(families), "families")

    with logger.stage("build_protocol_model"):
        relations = [_build_relation(edge) for edge in relations_payload.get("family_edges", [])]

        model = ProtocolModel(
            families=families,
            relations=relations,
            metadata={
                # "source_family_summary": args.family_json,
                # "source_feature_summary": args.features_json,
                # "source_keyword_summary": args.keywords_json,
                # "source_framing_summary": args.framing_json,
                # "source_relations_summary": args.relations_json,
                # "source_semantics_summary": args.semantics_json,
                "framing_global_summary": framing_payload.get("global", {}),
                # "notes": "Initial auto-generated protocol model assembled from family summaries.",
            },
        )

        logger.metric("total_families", len(families), "families")
        logger.metric("total_relations", len(relations), "relations")

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(model.to_dict(), handle, indent=2)
        logger.info(f"Wrote protocol model to {args.output_json}")

    print(f"[+] Wrote protocol model with {len(families)} families to {args.output_json}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
