#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json

from protocol_re.model.schema import FamilyFeatureSummary, FamilyModel, FamilyRelation, FamilySemanticSummary, FieldHypothesis, ProtocolModel, Segment


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble a protocol-model JSON document from inferred family summaries.")
    parser.add_argument("family_json", help="Output from 06_infer_boundaries.py")
    parser.add_argument("output_json", help="Protocol model output path")
    parser.add_argument("--features-json", help="Optional family feature JSON from 05_extract_features.py")
    parser.add_argument("--keywords-json", help="Optional keyword/subformat JSON from 08_infer_keywords.py")
    parser.add_argument("--relations-json", help="Optional output from 10_infer_relations.py")
    parser.add_argument("--semantics-json", help="Optional output from 11_infer_semantics.py")
    args = parser.parse_args()

    with open(args.family_json, "r", encoding="utf-8") as handle:
        family_data = json.load(handle)

    features_payload = {}
    if args.features_json:
        with open(args.features_json, "r", encoding="utf-8") as handle:
            features_payload = json.load(handle)

    keywords_payload = {}
    if args.keywords_json:
        with open(args.keywords_json, "r", encoding="utf-8") as handle:
            keywords_payload = json.load(handle)

    relations_payload = {"family_edges": [], "role_hints": {}}
    if args.relations_json:
        with open(args.relations_json, "r", encoding="utf-8") as handle:
            relations_payload = json.load(handle)
    semantics_payload = {}
    if args.semantics_json:
        with open(args.semantics_json, "r", encoding="utf-8") as handle:
            semantics_payload = json.load(handle)

    families = []
    for family_id, details in family_data.items():
        segments = [Segment(**segment) for segment in details.get("segments", [])]
        field_hypotheses = [FieldHypothesis(**field) for field in details.get("field_hypotheses", [])]
        feature_summary = features_payload.get(family_id)
        keyword_summary = keywords_payload.get(family_id)
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
                related_families=sorted(set(related_families)),
                evidence={
                    "source": args.family_json,
                    "keyword_evidence_source": args.keywords_json if keyword_summary else None,
                    **role_hint,
                },
            )
        )

    relations = [FamilyRelation(**edge) for edge in relations_payload.get("family_edges", [])]

    model = ProtocolModel(
        families=families,
        relations=relations,
        metadata={
            "source_family_summary": args.family_json,
            "source_feature_summary": args.features_json,
            "source_keyword_summary": args.keywords_json,
            "source_relations_summary": args.relations_json,
            "source_semantics_summary": args.semantics_json,
            "notes": "Initial auto-generated protocol model assembled from family summaries.",
        },
    )

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(model.to_dict(), handle, indent=2)

    print(f"[+] Wrote protocol model with {len(families)} families to {args.output_json}")


if __name__ == "__main__":
    main()
