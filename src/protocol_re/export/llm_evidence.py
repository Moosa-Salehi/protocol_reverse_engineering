from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional




def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _top_items(items: Iterable[Dict[str, Any]], limit: int, score_key: str = "confidence") -> List[Dict[str, Any]]:
    return sorted(
        list(items),
        key=lambda item: (-_as_float(item.get(score_key, 0.0)), _as_int(item.get("start", 0))),
    )[:limit]


def _template_digest(template: str, max_tokens: int = 32) -> Dict[str, Any]:
    tokens = template.split() if template else []
    return {
        "byte_length": len(tokens),
        "prefix": " ".join(tokens[:max_tokens]),
        "truncated": len(tokens) > max_tokens,
    }


def _trim_object(item: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    return {key: item.get(key) for key in keys if key in item}


def _compact_field(field: Dict[str, Any]) -> Dict[str, Any]:
    start = _as_int(field.get("start", 0))
    length = _as_int(field.get("length", 0))
    evidence = field.get("evidence", {}) or {}
    result = {
        "start": start,
        "end": start + max(0, length),
        "length": length,
        "label": field.get("field_type") or field.get("label") or "unknown",
        "confidence": round(_as_float(field.get("confidence", 0.0)), 6),
    }
    if field.get("endian"):
        result["endian"] = field.get("endian")
    if evidence:
        result["evidence"] = _trim_object(
            evidence,
            [
                "reason",
                "feature_source",
                "entropy_mean",
                "unique_ratio_mean",
                "coverage_mean",
                "support",
                "relation_type",
                "echo_support",
            ],
        )
    return result


def _compact_label(label: Dict[str, Any]) -> Dict[str, Any]:
    start = _as_int(label.get("start", 0))
    length = _as_int(label.get("length", 0))
    return {
        "start": start,
        "end": start + max(0, length),
        "length": length,
        "label": label.get("label", "unknown"),
        "confidence": round(_as_float(label.get("confidence", 0.0)), 6),
    }


def _compact_segment(segment: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "start": _as_int(segment.get("start", 0)),
        "end": _as_int(segment.get("end", 0)),
        "kind": segment.get("kind", "unknown"),
        "confidence": round(_as_float(segment.get("confidence", 0.0)), 6),
    }


def _compact_feature_summary(feature_summary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not feature_summary:
        return {}

    motif_stats = feature_summary.get("motif_stats", {}) or {}
    structure_stats = feature_summary.get("structure_stats", {}) or {}

    return {
        "motifs": {
            "repetition_ratio": motif_stats.get("messages_with_repetition_ratio"),
            "top": (motif_stats.get("top_motifs", []) or [])[:5],
            "wide": (motif_stats.get("wide_repeated_motifs", []) or [])[:5],
        },
        "structure": {
            "length_profile": structure_stats.get("length_profile", {}),
            "trailing_block": structure_stats.get("trailing_block_stats", {}),
        },
    }


def _compact_relation(relation: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "request_family_id": relation.get("request_family_id"),
        "response_family_id": relation.get("response_family_id"),
        "pair_count": relation.get("pair_count"),
        "avg_pair_score": relation.get("avg_pair_score"),
        "avg_latency_ms": relation.get("avg_latency_ms"),
        "echo_fields": (relation.get("echo_fields", []) or [])[:3],
        "length_relations": (relation.get("length_relations", []) or [])[:3],
    }


def _top_relations(model: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    relations = sorted(
        model.get("relations", []) or [],
        key=lambda item: (-_as_int(item.get("pair_count", 0)), -_as_float(item.get("avg_pair_score", 0.0))),
    )
    return [_compact_relation(relation) for relation in relations[:limit]]


def _compact_evaluation(evaluation: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not evaluation:
        return {}

    corpus = evaluation.get("corpus", {}) or {}
    clustering = evaluation.get("clustering", {}) or {}
    boundaries = evaluation.get("boundaries", {}) or {}
    pairs = evaluation.get("pairs", {}) or {}
    relations = evaluation.get("relations", {}) or {}
    semantics = evaluation.get("semantics", {}) or {}

    return {
        "corpus": {
            "message_count": corpus.get("message_count"),
            "session_count": corpus.get("session_count"),
            "payload_length": corpus.get("payload_length", {}),
            "direction_counts": corpus.get("direction_counts", {}),
        },
        "clustering": {
            "assignment_coverage_ratio": clustering.get("assignment_coverage_ratio"),
            "family_count": clustering.get("family_count"),
            "noise_count": clustering.get("noise_count"),
            "cluster_size_distribution": clustering.get("cluster_size_distribution", {}),
        },
        "boundaries": {
            "parseable_family_ratio": boundaries.get("parseable_family_ratio"),
            "parseable_family_count": boundaries.get("parseable_family_count"),
            "field_confidence_distribution": boundaries.get("field_confidence_distribution", {}),
            "segment_confidence_distribution": boundaries.get("segment_confidence_distribution", {}),
        },
        "pairs": {
            "pair_count": pairs.get("pair_count"),
            "score_distribution": pairs.get("score_distribution", {}),
            "direction_unknown_pair_ratio": pairs.get("direction_unknown_pair_ratio"),
        },
        "relations": {
            "edge_count": relations.get("edge_count"),
            "avg_pair_score_distribution": relations.get("avg_pair_score_distribution", {}),
            "edges_with_echo_fields": relations.get("edges_with_echo_fields"),
            "edges_with_length_relations": relations.get("edges_with_length_relations"),
            "role_hint_counts": relations.get("role_hint_counts", {}),
        },
        "semantics": {
            "semantic_coverage_ratio": semantics.get("semantic_coverage_ratio"),
            "semantic_family_count": semantics.get("semantic_family_count"),
            "role_counts": semantics.get("role_counts", {}),
            "top_field_labels": (semantics.get("top_field_labels", []) or [])[:10],
        },
    }


def _family_confidence_notes(family: Dict[str, Any]) -> List[str]:
    notes: List[str] = []
    semantic = family.get("semantic_summary") or {}
    features = family.get("feature_summary") or {}
    length_profile = ((features.get("structure_stats") or {}).get("length_profile") or {}).get("kind")
    if length_profile:
        notes.append(f"Length profile is {length_profile}.")
    if semantic.get("confidence") is not None:
        notes.append(f"Semantic role confidence is {semantic.get('confidence')}.")
    fields = family.get("field_hypotheses", []) or []
    if fields:
        high_conf = sum(1 for field in fields if _as_float(field.get("confidence", 0.0)) >= 0.8)
        notes.append(f"{high_conf}/{len(fields)} field hypotheses have confidence >= 0.8.")
    if family.get("related_families"):
        notes.append(f"Has {len(family.get('related_families', []))} related family links.")
    return notes


def _compact_family(family: Dict[str, Any], field_limit: int) -> Dict[str, Any]:
    semantic_summary = family.get("semantic_summary") or {}
    feature_summary = family.get("feature_summary") or {}
    segments = family.get("segments", []) or []
    fields = family.get("field_hypotheses", []) or []
    labels = semantic_summary.get("field_labels", []) or []

    return {
        "family_id": family.get("family_id"),
        "role": family.get("role", "unknown"),
        "message_count": family.get("message_count", 0),
        "template": _template_digest(family.get("template", "")),
        "related_family_ids": family.get("related_families", [])[:10],
        "segments": [_compact_segment(segment) for segment in sorted(segments, key=lambda item: (_as_int(item.get("start", 0)), _as_int(item.get("end", 0))))[:12]],
        "fields": [_compact_field(field) for field in _top_items(fields, field_limit)],
        "semantic_labels": [_compact_label(label) for label in _top_items(labels, field_limit)],
        "features": _compact_feature_summary(feature_summary),
        "confidence_notes": _family_confidence_notes(family),
    }


def _global_candidates(families: List[Dict[str, Any]], field_limit: int) -> Dict[str, Any]:
    length_candidates: List[Dict[str, Any]] = []
    opcode_candidates: List[Dict[str, Any]] = []
    constants: List[Dict[str, Any]] = []
    low_confidence: List[Dict[str, Any]] = []

    for family in families:
        family_id = family.get("family_id")
        for field in family.get("field_hypotheses", []) or []:
            field_type = str(field.get("field_type", "unknown"))
            compact = _compact_field(field)
            compact["family_id"] = family_id
            if "length" in field_type:
                length_candidates.append(compact)
            elif field_type in {"keyword", "opcode", "function", "selector"} or "keyword" in field_type:
                opcode_candidates.append(compact)
            elif "constant" in field_type or field_type == "fixed":
                constants.append(compact)
            if _as_float(field.get("confidence", 0.0)) < 0.55:
                low_confidence.append({**compact, "reason": "low field confidence"})

    return {
        "length_candidates": _top_items(length_candidates, field_limit),
        "opcode_candidates": _top_items(opcode_candidates, field_limit),
        "constants": _top_items(constants, field_limit),
        "low_confidence_areas": _top_items(low_confidence, field_limit),
    }


def _coverage(bundle: Dict[str, Any]) -> Dict[str, Any]:
    optional_sections = [
        "evaluation",
        "families",
        "relations",
        "global_hypotheses.length_candidates",
        "global_hypotheses.opcode_candidates",
        "global_hypotheses.constants",
        "global_hypotheses.low_confidence_areas",
    ]
    filled: List[str] = []
    missing: List[str] = []
    for section in optional_sections:
        value: Any = bundle
        for part in section.split("."):
            value = value.get(part, {}) if isinstance(value, dict) else {}
        if value:
            filled.append(section)
        else:
            missing.append(section)
    return {
        "filled_sections": filled,
        "missing_sections": missing,
        "completeness_score": round(len(filled) / len(optional_sections), 6) if optional_sections else 1.0,
    }


def build_llm_evidence_bundle(
    model: Dict[str, Any],
    evaluation: Optional[Dict[str, Any]] = None,
    family_limit: Optional[int] = None,
    relation_limit: int = 8,
    field_limit: int = 8,
) -> Dict[str, Any]:
    families = sorted(
        model.get("families", []) or [],
        key=lambda item: (-_as_int(item.get("message_count", 0)), str(item.get("family_id", ""))),
    )
    if family_limit is not None:
        families = families[:family_limit]

    relations = _top_relations(model, relation_limit)
    candidates = _global_candidates(families, field_limit)
    bundle = {
        "protocol": {
            "name": model.get("protocol_name", "unknown-industrial-protocol"),
        },
        "source": {
            "total_families_in_model": len(model.get("families", []) or []),
            "families_in_bundle": len(families),
            "total_relations_in_model": len(model.get("relations", []) or []),
            "relations_in_bundle": len(relations),
            "limits": {
                "family_limit": family_limit,
                "field_limit_per_family": field_limit,
                "relation_limit": relation_limit,
            },
        },
        "llm_guidance": {
            "purpose": "Infer an unknown industrial protocol structure from compact statistical evidence. Do not assume a known protocol unless evidence supports it.",
            "recommended_tasks": [
                "identify_message_families",
                "name_fields",
                "infer_opcodes",
                "infer_lengths",
                "explain_request_response_relations",
                "flag_low_confidence_hypotheses",
            ],
            "raw_payloads_included": False,
        },
        "evaluation": _compact_evaluation(evaluation),
        "relations": relations,
        "global_hypotheses": candidates,
        "families": [_compact_family(family, field_limit=field_limit) for family in families],
        "open_questions": [
            "Which fields are likely operation selectors, transaction identifiers, lengths, status codes, or payload values?",
            "Which boundaries should be merged or split based on cross-family evidence?",
            "Which request/response relations are semantically meaningful versus timing artifacts?",
        ],
    }
    bundle["coverage"] = _coverage(bundle)
    return bundle
