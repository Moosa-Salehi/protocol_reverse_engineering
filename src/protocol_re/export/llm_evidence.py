from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


def _top_items(items: Iterable[Dict[str, Any]], limit: int, score_key: str = "confidence") -> List[Dict[str, Any]]:
    return sorted(
        list(items),
        key=lambda item: (-float(item.get(score_key, 0.0) or 0.0), int(item.get("start", 0) or 0)),
    )[:limit]


def _vector_digest(values: List[float], limit: int) -> Dict[str, Any]:
    if not values:
        return {"length": 0, "head": [], "top_offsets": []}
    top_offsets = sorted(
        enumerate(values),
        key=lambda item: (-float(item[1]), item[0]),
    )[:limit]
    return {
        "length": len(values),
        "head": [round(float(value), 6) for value in values[:limit]],
        "top_offsets": [
            {"offset": offset, "value": round(float(value), 6)}
            for offset, value in top_offsets
        ],
    }


def _compact_feature_summary(feature_summary: Optional[Dict[str, Any]], vector_limit: int) -> Dict[str, Any]:
    if not feature_summary:
        return {}

    position_stats = feature_summary.get("position_stats", {}) or {}
    motif_stats = feature_summary.get("motif_stats", {}) or {}
    structure_stats = feature_summary.get("structure_stats", {}) or {}
    length_stats = feature_summary.get("length_stats", {}) or {}

    return {
        "example_msg_ids": feature_summary.get("example_msg_ids", [])[:10],
        "length_stats": {
            "min": length_stats.get("min"),
            "max": length_stats.get("max"),
            "mean": length_stats.get("mean"),
            "std_dev": length_stats.get("std_dev"),
            "distinct_lengths": length_stats.get("distinct_lengths"),
            "length_histogram": dict(list((length_stats.get("length_histogram", {}) or {}).items())[:20]),
        },
        "entropy_summary": feature_summary.get("entropy_summary", {}),
        "unique_ratio_summary": feature_summary.get("unique_ratio_summary", {}),
        "run_length_summary": feature_summary.get("run_length_summary", {}),
        "position_vectors": {
            "entropy": _vector_digest(position_stats.get("entropy_vector", []) or [], vector_limit),
            "unique_ratio": _vector_digest(position_stats.get("uniqueness_ratio_vector", []) or [], vector_limit),
            "coverage": _vector_digest(position_stats.get("coverage_vector", []) or [], vector_limit),
        },
        "motifs": {
            "messages_with_repetition_ratio": motif_stats.get("messages_with_repetition_ratio"),
            "repeated_ngram_instances": motif_stats.get("repeated_ngram_instances"),
            "top_motifs": (motif_stats.get("top_motifs", []) or [])[:10],
            "wide_repeated_motifs": (motif_stats.get("wide_repeated_motifs", []) or [])[:10],
            "ngram_frequencies": {
                str(width): rows[:8]
                for width, rows in (motif_stats.get("ngram_frequencies", {}) or {}).items()
            },
        },
        "structure": {
            "length_profile": structure_stats.get("length_profile", {}),
            "trailing_block_stats": structure_stats.get("trailing_block_stats", {}),
            "recurring_field_groups": (structure_stats.get("recurring_field_groups", []) or [])[:10],
        },
    }


def _relations_for_family(model: Dict[str, Any], family_id: str, limit: int) -> List[Dict[str, Any]]:
    relations = []
    for relation in model.get("relations", []) or []:
        if relation.get("request_family_id") != family_id and relation.get("response_family_id") != family_id:
            continue
        relations.append(
            {
                "request_family_id": relation.get("request_family_id"),
                "response_family_id": relation.get("response_family_id"),
                "pair_count": relation.get("pair_count"),
                "avg_pair_score": relation.get("avg_pair_score"),
                "avg_latency_ms": relation.get("avg_latency_ms"),
                "echo_fields": (relation.get("echo_fields", []) or [])[:8],
                "length_relations": (relation.get("length_relations", []) or [])[:8],
            }
        )
    return sorted(
        relations,
        key=lambda item: (-int(item.get("pair_count", 0) or 0), -float(item.get("avg_pair_score", 0.0) or 0.0)),
    )[:limit]


def _compact_family(model: Dict[str, Any], family: Dict[str, Any], vector_limit: int, relation_limit: int) -> Dict[str, Any]:
    semantic_summary = family.get("semantic_summary") or {}
    feature_summary = family.get("feature_summary") or {}
    segments = family.get("segments", []) or []
    fields = family.get("field_hypotheses", []) or []
    semantic_labels = semantic_summary.get("field_labels", []) or []

    return {
        "family_id": family.get("family_id"),
        "role": family.get("role", "unknown"),
        "message_count": family.get("message_count", 0),
        "template": family.get("template", ""),
        "related_families": family.get("related_families", [])[:20],
        "examples": family.get("examples", []) or feature_summary.get("example_msg_ids", [])[:10],
        "segments": sorted(segments, key=lambda item: (int(item.get("start", 0)), int(item.get("end", 0))))[:30],
        "field_hypotheses": _top_items(fields, 20),
        "semantic_summary": {
            "role": semantic_summary.get("role", family.get("role", "unknown")),
            "confidence": semantic_summary.get("confidence", 0.0),
            "field_labels": _top_items(semantic_labels, 20),
            "notes": (semantic_summary.get("notes", []) or [])[:10],
        },
        "feature_evidence": _compact_feature_summary(feature_summary, vector_limit),
        "relations": _relations_for_family(model, str(family.get("family_id")), relation_limit),
        "confidence_notes": _family_confidence_notes(family),
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
        high_conf = sum(1 for field in fields if float(field.get("confidence", 0.0) or 0.0) >= 0.8)
        notes.append(f"{high_conf}/{len(fields)} field hypotheses have confidence >= 0.8.")
    if family.get("related_families"):
        notes.append(f"Has {len(family.get('related_families', []))} related family links.")
    return notes


def build_llm_evidence_bundle(
    model: Dict[str, Any],
    family_limit: Optional[int] = None,
    vector_limit: int = 16,
    relation_limit: int = 10,
) -> Dict[str, Any]:
    families = sorted(
        model.get("families", []) or [],
        key=lambda item: (-int(item.get("message_count", 0) or 0), str(item.get("family_id", ""))),
    )
    if family_limit is not None:
        families = families[:family_limit]

    return {
        "artifact_type": "llm_protocol_evidence_bundle",
        "protocol_name": model.get("protocol_name", "unknown-industrial-protocol"),
        "version": model.get("version", "0.1"),
        "metadata": {
            "source_metadata": model.get("metadata", {}),
            "total_families_in_model": len(model.get("families", []) or []),
            "families_in_bundle": len(families),
            "total_relations_in_model": len(model.get("relations", []) or []),
            "vector_digest_limit": vector_limit,
            "relation_limit_per_family": relation_limit,
            "notes": "Compact evidence for downstream LLM analysis; raw payloads are intentionally omitted.",
        },
        "families": [
            _compact_family(model, family, vector_limit=vector_limit, relation_limit=relation_limit)
            for family in families
        ],
    }
