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
            "family_count": boundaries.get("family_count"),
            "field_confidence_distribution": boundaries.get("field_confidence_distribution", {}),
            "segment_confidence_distribution": boundaries.get("segment_confidence_distribution", {}),
            "segments_with_feature_evidence": boundaries.get("segments_with_feature_evidence"),
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
            "top_edges": (relations.get("top_edges", []) or [])[:10],
        },
        "semantics": {
            "semantic_coverage_ratio": semantics.get("semantic_coverage_ratio"),
            "semantic_family_count": semantics.get("semantic_family_count"),
            "role_counts": semantics.get("role_counts", {}),
            "role_confidence_distribution": semantics.get("role_confidence_distribution", {}),
            "field_label_confidence_distribution": semantics.get("field_label_confidence_distribution", {}),
            "top_field_labels": (semantics.get("top_field_labels", []) or [])[:10],
        },
    }


def _compact_family(model: Dict[str, Any], family: Dict[str, Any], vector_limit: int, relation_limit: int) -> Dict[str, Any]:
    semantic_summary = family.get("semantic_summary") or {}
    feature_summary = family.get("feature_summary") or {}
    keyword_summary = family.get("keyword_summary") or {}
    subcluster_summary = family.get("subcluster_summary") or {}
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
        "format_evidence": {
            "keyword": keyword_summary.get("keyword") if isinstance(keyword_summary, dict) else None,
            "keyword_subformats": dict(list((keyword_summary.get("subclusters", {}) or {}).items())[:10])
            if isinstance(keyword_summary, dict)
            else {},
            "best_subcluster_strategy": subcluster_summary.get("best_strategy") if isinstance(subcluster_summary, dict) else None,
            "subcluster_scores": subcluster_summary.get("scores", {}) if isinstance(subcluster_summary, dict) else {},
            "subcluster_formats": dict(list((subcluster_summary.get("formats", {}) or {}).items())[:10])
            if isinstance(subcluster_summary, dict)
            else {},
        },
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
    evaluation: Optional[Dict[str, Any]] = None,
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
            "has_evaluation": evaluation is not None,
            "notes": "Compact evidence for downstream LLM analysis; raw payloads are intentionally omitted.",
        },
        "evaluation": _compact_evaluation(evaluation),
        "families": [
            _compact_family(model, family, vector_limit=vector_limit, relation_limit=relation_limit)
            for family in families
        ],
    }
