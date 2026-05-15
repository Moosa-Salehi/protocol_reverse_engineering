from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any, Dict, Iterable, List, Sequence

from protocol_re.model.schema import MessageRecord


def _quantiles(values: Sequence[float]) -> Dict[str, float]:
    if not values:
        return {"min": 0.0, "p25": 0.0, "median": 0.0, "p75": 0.0, "max": 0.0, "mean": 0.0}
    ordered = sorted(float(value) for value in values)

    def pick(fraction: float) -> float:
        index = int(round((len(ordered) - 1) * fraction))
        return round(ordered[index], 6)

    return {
        "min": round(ordered[0], 6),
        "p25": pick(0.25),
        "median": pick(0.5),
        "p75": pick(0.75),
        "max": round(ordered[-1], 6),
        "mean": round(mean(ordered), 6),
    }


def _top_counter(counter: Counter[Any], limit: int = 20) -> List[Dict[str, Any]]:
    return [{"value": value, "count": count} for value, count in counter.most_common(limit)]


def corpus_summary(records: Sequence[MessageRecord]) -> Dict[str, Any]:
    lengths = [record.payload_len for record in records]
    directions = Counter(record.direction for record in records)
    sessions = Counter(record.session_id for record in records)
    source_files = Counter(record.source_file for record in records)
    return {
        "message_count": len(records),
        "session_count": len(sessions),
        "source_file_count": len(source_files),
        "payload_length": _quantiles(lengths),
        "direction_counts": dict(sorted(directions.items())),
        "top_sessions_by_messages": _top_counter(sessions, 10),
        "top_source_files_by_messages": _top_counter(source_files, 10),
    }


def clustering_summary(total_messages: int, assignments_payload: Dict[str, Any]) -> Dict[str, Any]:
    assignments = assignments_payload.get("assignments", []) or []
    family_counts = Counter(item.get("family_id", "unassigned") for item in assignments)
    assigned_count = len(assignments)
    noise_count = family_counts.get("noise", 0)
    cluster_sizes = [count for family_id, count in family_counts.items() if family_id != "noise"]
    sample_size = assignments_payload.get("sample_size")
    corpus_assignment_coverage_ratio = round(assigned_count / total_messages, 6) if total_messages else 0.0
    clustering_sample_ratio = round(sample_size / total_messages, 6) if total_messages and sample_size is not None else None
    return {
        "assigned_message_count": assigned_count,
        "total_message_count": total_messages,
        "assignment_coverage_ratio": corpus_assignment_coverage_ratio,
        "corpus_assignment_coverage_ratio": corpus_assignment_coverage_ratio,
        "clustering_sample_ratio": clustering_sample_ratio,
        "unassigned_message_count": max(0, total_messages - assigned_count),
        "family_count": len(family_counts),
        "noise_count": noise_count,
        "noise_ratio_of_assigned": round(noise_count / assigned_count, 6) if assigned_count else 0.0,
        "sample_size": sample_size,
        "assignment_strategy": assignments_payload.get("assignment_strategy"),
        "feature_shape": assignments_payload.get("feature_shape"),
        "cluster_size_distribution": _quantiles(cluster_sizes),
        "largest_families": _top_counter(family_counts, 20),
    }


def boundary_summary(families_payload: Dict[str, Any]) -> Dict[str, Any]:
    family_count = len(families_payload)
    segment_counts: List[int] = []
    segment_confidences: List[float] = []
    field_counts: List[int] = []
    field_confidences: List[float] = []
    template_lengths: List[int] = []
    parseable_count = 0
    boundary_feature_evidence_count = 0

    for details in families_payload.values():
        segments = details.get("segments", []) or []
        fields = details.get("field_hypotheses", []) or []
        segment_counts.append(len(segments))
        field_counts.append(len(fields))
        template = details.get("template", "") or ""
        template_lengths.append(len(template.split()) if template else 0)
        if segments and fields:
            parseable_count += 1
        for segment in segments:
            segment_confidences.append(float(segment.get("confidence", 0.0) or 0.0))
            if (segment.get("evidence", {}) or {}).get("feature_source"):
                boundary_feature_evidence_count += 1
        for field in fields:
            field_confidences.append(float(field.get("confidence", 0.0) or 0.0))

    return {
        "family_count": family_count,
        "parseable_family_count": parseable_count,
        "parseable_family_ratio": round(parseable_count / family_count, 6) if family_count else 0.0,
        "segment_count_distribution": _quantiles(segment_counts),
        "segment_confidence_distribution": _quantiles(segment_confidences),
        "field_count_distribution": _quantiles(field_counts),
        "field_confidence_distribution": _quantiles(field_confidences),
        "template_length_distribution": _quantiles(template_lengths),
        "segments_with_feature_evidence": boundary_feature_evidence_count,
    }


def pair_summary(pairs_payload: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    scores = [float(pair.get("score", 0.0) or 0.0) for pair in pairs_payload]
    latencies = [float(pair["latency_ms"]) for pair in pairs_payload if pair.get("latency_ms") is not None]
    modes = Counter((pair.get("evidence", {}) or {}).get("pairing_mode", "scored_window") for pair in pairs_payload)
    direction_known = 0
    direction_unknown = 0
    for pair in pairs_payload:
        evidence = pair.get("evidence", {}) or {}
        if evidence.get("direction_unknown"):
            direction_unknown += 1
        else:
            direction_known += 1
    return {
        "pair_count": len(pairs_payload),
        "score_distribution": _quantiles(scores),
        "latency_ms_distribution": _quantiles(latencies),
        "pairing_modes": dict(sorted(modes.items())),
        "direction_known_pair_count": direction_known,
        "direction_unknown_pair_count": direction_unknown,
        "direction_unknown_pair_ratio": round(direction_unknown / len(pairs_payload), 6) if pairs_payload else 0.0,
    }


def relation_summary(relations_payload: Dict[str, Any]) -> Dict[str, Any]:
    edges = relations_payload.get("family_edges", []) or []
    pair_counts = [int(edge.get("pair_count", 0) or 0) for edge in edges]
    scores = [float(edge.get("avg_pair_score", 0.0) or 0.0) for edge in edges]
    echo_edge_count = sum(1 for edge in edges if edge.get("echo_fields"))
    length_edge_count = sum(1 for edge in edges if edge.get("length_relations"))
    echo_supports = [
        float(echo.get("support", 0.0) or 0.0)
        for edge in edges
        for echo in (edge.get("echo_fields", []) or [])
    ]
    length_supports = [
        float(item.get("support", 0.0) or 0.0)
        for edge in edges
        for item in (edge.get("length_relations", []) or [])
    ]
    role_hints = Counter((item or {}).get("role_hint", "unknown") for item in (relations_payload.get("role_hints", {}) or {}).values())
    top_edges = sorted(
        edges,
        key=lambda item: (
            -int(item.get("pair_count", 0) or 0),
            -float(item.get("support_ratio", 0.0) or 0.0),
            -float(item.get("edge_lift", 0.0) or 0.0),
            -float(item.get("avg_pair_score", 0.0) or 0.0),
        ),
    )[:20]
    return {
        "edge_count": len(edges),
        "pair_count_distribution": _quantiles(pair_counts),
        "avg_pair_score_distribution": _quantiles(scores),
        "edges_with_echo_fields": echo_edge_count,
        "edges_with_length_relations": length_edge_count,
        "echo_support_distribution": _quantiles(echo_supports),
        "length_relation_support_distribution": _quantiles(length_supports),
        "role_hint_counts": dict(sorted(role_hints.items())),
        "top_edges": [
            {
                "request_family_id": edge.get("request_family_id"),
                "response_family_id": edge.get("response_family_id"),
                "pair_count": edge.get("pair_count"),
                "avg_pair_score": edge.get("avg_pair_score"),
                "support_ratio": edge.get("support_ratio"),
                "edge_lift": edge.get("edge_lift"),
                "direction_consistency": edge.get("direction_consistency"),
                "dominant_direction": edge.get("dominant_direction"),
                "temporal_order_consistency": edge.get("temporal_order_consistency"),
                "order_usable_pairs": edge.get("order_usable_pairs"),
                "echo_field_count": len(edge.get("echo_fields", []) or []),
                "length_relation_count": len(edge.get("length_relations", []) or []),
            }
            for edge in top_edges
        ],
    }


def semantics_summary(semantics_payload: Dict[str, Any], family_count: int) -> Dict[str, Any]:
    semantic_items = list((semantics_payload or {}).values())
    confidences: List[float] = []
    field_label_counts: List[int] = []
    label_confidences: List[float] = []
    note_counts: List[int] = []
    role_counts: Counter[Any] = Counter()
    label_counts: Counter[Any] = Counter()

    for item in semantic_items:
        role_counts[item.get("role", "unknown")] += 1
        confidences.append(float(item.get("confidence", 0.0) or 0.0))
        labels = item.get("field_labels", []) or []
        notes = item.get("notes", []) or []
        field_label_counts.append(len(labels))
        note_counts.append(len(notes))
        for label in labels:
            label_counts[label.get("label", "unknown")] += 1
            label_confidences.append(float(label.get("confidence", 0.0) or 0.0))

    return {
        "semantic_family_count": len(semantic_items),
        "family_count": family_count,
        "semantic_coverage_ratio": round(len(semantic_items) / family_count, 6) if family_count else 0.0,
        "role_counts": dict(sorted(role_counts.items())),
        "role_confidence_distribution": _quantiles(confidences),
        "field_label_count_distribution": _quantiles(field_label_counts),
        "field_label_confidence_distribution": _quantiles(label_confidences),
        "note_count_distribution": _quantiles(note_counts),
        "top_field_labels": _top_counter(label_counts, 20),
    }


def framing_summary(framing_payload: Dict[str, Any], family_count: int) -> Dict[str, Any]:
    family_items = (framing_payload or {}).get("families", {}) or {}
    best_confidences: List[float] = []
    header_ends: Counter[Any] = Counter()
    field_types: Counter[Any] = Counter()
    usable_family_count = 0

    for item in family_items.values():
        layouts = item.get("layout_hypotheses", []) or []
        if not layouts:
            continue
        best = layouts[0]
        confidence = float(best.get("confidence", 0.0) or 0.0)
        best_confidences.append(confidence)
        if confidence > 0.0:
            usable_family_count += 1
        header_ends[int(best.get("header_end", 0) or 0)] += 1
        for field in best.get("field_regions", []) or []:
            field_types[field.get("field_type", "unknown")] += 1

    return {
        "family_count": family_count,
        "framing_family_count": len(family_items),
        "usable_family_count": usable_family_count,
        "usable_family_ratio": round(usable_family_count / family_count, 6) if family_count else 0.0,
        "best_confidence_distribution": _quantiles(best_confidences),
        "top_header_ends": _top_counter(header_ends, 10),
        "field_type_counts": dict(sorted(field_types.items())),
        "global": (framing_payload or {}).get("global", {}),
    }


def build_evaluation_report(
    records: Sequence[MessageRecord],
    assignments_payload: Dict[str, Any],
    families_payload: Dict[str, Any],
    pairs_payload: Sequence[Dict[str, Any]],
    relations_payload: Dict[str, Any],
    semantics_payload: Dict[str, Any] | None = None,
    framing_payload: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    total_messages = len(records)
    family_count = len(families_payload)
    return {
        "artifact_type": "protocol_re_evaluation_report",
        "corpus": corpus_summary(records),
        "clustering": clustering_summary(total_messages, assignments_payload),
        "boundaries": boundary_summary(families_payload),
        "pairs": pair_summary(pairs_payload),
        "relations": relation_summary(relations_payload),
        "semantics": semantics_summary(semantics_payload or {}, family_count),
        "framing": framing_summary(framing_payload or {}, family_count),
        "notes": [
            "Metrics are heuristic quality indicators for reverse-engineering workflow triage.",
            "Low assignment coverage usually means clustering sampled fewer messages than the full corpus.",
            "Direction-unknown pair ratios are expected to be high when no service port is configured.",
        ],
    }
