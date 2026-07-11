"""
Enhanced semantic field labeling with protocol-agnostic inference.

This module integrates evidence from multiple sources (framing, features,
relations, keywords) to infer semantic roles for protocol fields.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilySemanticSummary
from protocol_re.inference.field_semantics import (
    SemanticHypothesis,
    infer_discriminator_fields,
    infer_length_fields,
    infer_transaction_id_fields,
    infer_counter_fields,
    infer_address_fields,
    infer_body_value_fields,
    infer_status_fields,
    infer_payload_fields,
    infer_checksum_fields,
    infer_constant_fields,
    _infer_encoding_type,
)
from protocol_re.inference.semantic_patterns import (
    resolve_conflicting_hypotheses,
    propagate_semantic_labels_across_families,
    detect_common_protocol_patterns,
)


def _field_key(field: Dict[str, object]) -> Tuple[int, int]:
    return (int(field.get("start", 0)), int(field.get("length", 0)))


def _covers(field: Dict[str, object], start: int, width: int) -> bool:
    field_start = int(field.get("start", 0))
    field_len = int(field.get("length", 0))
    field_end = field_start + field_len
    return field_start <= start and (start + width) <= field_end


def _best_covering_field(fields: Sequence[Dict[str, object]], start: int, width: int) -> Optional[Dict[str, object]]:
    candidates = [field for field in fields if _covers(field, start, width)]
    if not candidates:
        return None
    candidates.sort(key=lambda field: (int(field.get("length", 0)), int(field.get("start", 0))))
    return candidates[0]


def summarize_semantics(
    family_data: Dict[str, object],
    relations_payload: Dict[str, object],
    framing_data: Optional[Dict[str, object]] = None,
    features_data: Optional[Dict[str, object]] = None,
    keywords_data: Optional[Dict[str, object]] = None,
) -> Dict[str, object]:
    """
    Enhanced semantic labeling with protocol-agnostic inference.

    Args:
        family_data: Family boundary data from stage 07
        relations_payload: Relation data from stage 10
        framing_data: Optional framing data from stage 05
        features_data: Optional feature data from stage 06
        keywords_data: Optional keyword/discriminator data from stage 09

    Returns:
        Dictionary mapping family_id to semantic summary
    """
    role_hints = relations_payload.get("role_hints", {}) or {}
    family_edges = relations_payload.get("family_edges", []) or []
    semantics: Dict[str, object] = {}

    # Build edge lookup tables
    edges_by_request: Dict[str, List[Dict[str, object]]] = {}
    edges_by_response: Dict[str, List[Dict[str, object]]] = {}
    for edge in family_edges:
        edges_by_request.setdefault(edge["request_family_id"], []).append(edge)
        edges_by_response.setdefault(edge["response_family_id"], []).append(edge)

    # Extract framing data by family
    framing_by_family = {}
    if framing_data:
        framing_by_family = framing_data.get("families", {}) or {}

    # Extract feature data by family
    features_by_family = features_data or {}

    # Extract keyword data by family
    keywords_by_family = {}
    if keywords_data:
        for family_id, kw_data in keywords_data.items():
            keywords_by_family[family_id] = kw_data

    # First pass: collect all semantic hypotheses per family
    all_family_hypotheses: Dict[str, List[SemanticHypothesis]] = {}

    for family_id, details in family_data.items():
        fields = list(details.get("field_hypotheses", []))
        role_hint = role_hints.get(family_id, {})
        role = role_hint.get("role_hint", "unknown")

        # Get evidence sources for this family
        framing_summary = framing_by_family.get(family_id)
        feature_summary = features_by_family.get(family_id)
        keyword_summary = keywords_by_family.get(family_id)
        relation_edges = edges_by_request.get(family_id, [])

        # Run semantic inference functions
        hypotheses: List[SemanticHypothesis] = []

        # 1. Discriminator/opcode fields
        hypotheses.extend(infer_discriminator_fields(
            fields, framing_summary, keyword_summary, feature_summary
        ))

        # 2. Length fields
        hypotheses.extend(infer_length_fields(
            fields, framing_summary, None
        ))

        # 3. Transaction ID fields
        hypotheses.extend(infer_transaction_id_fields(
            fields, relation_edges, framing_summary, feature_summary
        ))

        # 4. Counter/sequence fields
        hypotheses.extend(infer_counter_fields(
            fields, framing_summary, feature_summary
        ))

        # 5. Address fields
        hypotheses.extend(infer_address_fields(
            fields, feature_summary
        ))

        hypotheses.extend(infer_body_value_fields(
            fields, framing_summary, role
        ))

        # 6. Status fields (response only)
        hypotheses.extend(infer_status_fields(
            fields, role, feature_summary
        ))

        # 7. Payload fields
        hypotheses.extend(infer_payload_fields(
            fields, framing_summary, feature_summary
        ))

        # 8. Checksum fields
        hypotheses.extend(infer_checksum_fields(
            fields, None
        ))

        # 9. Constant/reserved fields
        hypotheses.extend(infer_constant_fields(
            fields, feature_summary
        ))

        # Add legacy relation-based labels (for backward compatibility)
        hypotheses.extend(_legacy_relation_labels(
            fields, edges_by_request.get(family_id, []), edges_by_response.get(family_id, [])
        ))

        all_family_hypotheses[family_id] = hypotheses

    # Second pass: propagate labels across families
    all_family_hypotheses = propagate_semantic_labels_across_families(
        all_family_hypotheses,
        min_family_count=3,
        confidence_boost=0.1,
    )

    # Third pass: resolve conflicts and build final output
    for family_id, hypotheses in all_family_hypotheses.items():
        role_hint = role_hints.get(family_id, {})
        role = role_hint.get("role_hint", "unknown")
        req_like = float(role_hint.get("request_like_pairs", 0))
        resp_like = float(role_hint.get("response_like_pairs", 0))
        total_like = req_like + resp_like
        role_conf = max(req_like, resp_like) / total_like if total_like > 0 else 0.0

        # Resolve conflicts and filter by confidence
        resolved_hypotheses = resolve_conflicting_hypotheses(
            hypotheses,
            max_hypotheses_per_field=3,
            min_confidence=0.5,
        )

        # Convert to field_labels format
        field_labels = [hyp.to_dict() for hyp in resolved_hypotheses]

        # Generate notes
        notes = []
        for edge in edges_by_response.get(family_id, []):
            if edge.get("echo_fields"):
                notes.append(
                    f"Echoes request fields from {edge['request_family_id']} with up to {len(edge['echo_fields'])} strong offset matches."
                )
            if edge.get("length_relations"):
                notes.append(
                    f"Response size is tied to request fields from {edge['request_family_id']}."
                )

        # Detect common patterns
        patterns = detect_common_protocol_patterns(resolved_hypotheses)
        if patterns["pattern_confidence"] > 0.5:
            pattern_desc = []
            if patterns["has_transaction_id"]:
                pattern_desc.append("transaction ID")
            if patterns["has_length_field"]:
                pattern_desc.append("length field")
            if patterns["has_discriminator"]:
                pattern_desc.append("discriminator")
            if pattern_desc:
                notes.append(f"Detected common protocol pattern: {', '.join(pattern_desc)}")

        semantics[family_id] = FamilySemanticSummary(
            family_id=family_id,
            role=role,
            confidence=round(role_conf, 4),
            field_labels=field_labels,
            notes=notes[:10],
        ).to_dict()

    return semantics


def _legacy_relation_labels(
    fields: List[Dict[str, object]],
    request_edges: List[Dict[str, object]],
    response_edges: List[Dict[str, object]],
) -> List[SemanticHypothesis]:
    """
    Generate legacy relation-based labels for backward compatibility.

    These labels are added in addition to the new semantic inference:
    - echoed_request_field
    - transaction_or_correlation_id (from echo)
    - response_size_selector
    """
    hypotheses: List[SemanticHypothesis] = []

    # Process request edges (this family is the request)
    for edge in request_edges:
        # Echo fields
        for echo in edge.get("echo_fields", []):
            field = _best_covering_field(fields, int(echo["request_offset"]), int(echo["width"]))
            if field is None:
                continue

            start = int(field["start"])
            length = int(field["length"])

            # Add echoed_request_field label
            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="echoed_request_field",
                confidence=float(echo.get("support", 0.0)),
                evidence={
                    "response_family_id": edge["response_family_id"],
                    "response_offset": echo["response_offset"],
                    "support": echo.get("support", 0.0),
                },
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

            # Add transaction_or_correlation_id if 2 or 4 bytes
            if length in (2, 4):
                hypotheses.append(SemanticHypothesis(
                    field_start=start,
                    field_length=length,
                    semantic_role="transaction_or_correlation_id",
                    confidence=min(0.99, 0.55 + 0.4 * float(echo.get("support", 0.0))),
                    evidence={
                        "response_family_id": edge["response_family_id"],
                        "echo_support": echo.get("support", 0.0),
                    },
                    encoding_type=_infer_encoding_type(length, field.get("endian")),
                ))

        # Length relations
        for rel in edge.get("length_relations", []):
            field = _best_covering_field(fields, int(rel["request_offset"]), int(rel["width"]))
            if field is None:
                continue

            start = int(field["start"])
            length = int(field["length"])

            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="response_size_selector",
                confidence=float(rel.get("support", 0.0)),
                evidence={
                    "relation_type": rel.get("relation_type"),
                    "response_family_id": edge["response_family_id"],
                    "support": rel.get("support", 0.0),
                },
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

    return hypotheses
