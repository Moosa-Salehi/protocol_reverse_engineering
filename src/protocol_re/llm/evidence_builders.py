"""Helpers for building compact, evidence-backed LLM prompt bundles."""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from protocol_re.model.schema import MessageRecord


MAX_PROMPT_HEX_CHARS = 100


def _field_start(field: Mapping[str, Any]) -> int:
    return int(field.get("start", field.get("offset", field.get("start_offset", 0))) or 0)


def _field_length(field: Mapping[str, Any]) -> int:
    if "length" in field:
        return int(field.get("length") or 0)
    if "width" in field:
        return int(field.get("width") or 0)
    start = _field_start(field)
    end = int(field.get("end", field.get("end_offset", start)) or start)
    return max(0, end - start)


def _slice_hex(payload_hex: str, start: int, length: int) -> str:
    return _truncate_hex(payload_hex[start * 2 : (start + length) * 2])


def _truncate_hex(value: Any, max_chars: int = MAX_PROMPT_HEX_CHARS) -> str:
    text = str(value or "")
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def build_sample_messages(messages: Sequence[MessageRecord], max_samples: int = 10) -> List[Dict[str, Any]]:
    samples: List[Dict[str, Any]] = []
    for msg in messages[:max_samples]:
        samples.append(
            {
                "msg_id": msg.msg_id,
                "payload_hex": _truncate_hex(msg.payload_hex),
                "payload_hex_truncated": len(msg.payload_hex) > MAX_PROMPT_HEX_CHARS,
                "length": msg.payload_len,
                "direction": msg.direction,
                "session_id": msg.session_id,
            }
        )
    return samples


def build_sample_values(
    fields: Sequence[Mapping[str, Any]],
    messages: Sequence[MessageRecord],
    max_samples: int = 5,
) -> List[Dict[str, Any]]:
    values: List[Dict[str, Any]] = []
    for index, field in enumerate(fields):
        start = _field_start(field)
        length = _field_length(field)
        samples = []
        for msg in messages[:max_samples]:
            samples.append(
                {
                    "msg_id": msg.msg_id,
                    "hex": _slice_hex(msg.payload_hex, start, length),
                    "message_length": msg.payload_len,
                }
            )
        values.append(
            {
                "field_index": index,
                "offset": start,
                "width": length,
                "values": samples,
            }
        )
    return values


def build_field_statistics(
    fields: Sequence[Mapping[str, Any]],
    messages: Sequence[MessageRecord] = (),
    family_features: Optional[Mapping[str, Any]] = None,
    segments: Sequence[Mapping[str, Any]] = (),
    max_values: int = 5,
) -> Dict[str, Dict[str, Any]]:
    position_stats = (family_features or {}).get("position_stats", {}) if family_features else {}
    entropy_vector = position_stats.get("entropy_vector", []) or []
    unique_ratio_vector = position_stats.get("uniqueness_ratio_vector", []) or []
    coverage_vector = position_stats.get("coverage_vector", []) or []
    segment_by_span = {(_field_start(seg), _field_length(seg)): seg for seg in segments}

    stats: Dict[str, Dict[str, Any]] = {}
    for index, field in enumerate(fields):
        start = _field_start(field)
        length = _field_length(field)
        observed = [_slice_hex(msg.payload_hex, start, length) for msg in messages if msg.payload_len >= start + length]
        counts = Counter(observed)
        offsets = range(start, start + length)
        entropies = [float(entropy_vector[i]) for i in offsets if i < len(entropy_vector)]
        unique_ratios = [float(unique_ratio_vector[i]) for i in offsets if i < len(unique_ratio_vector)]
        coverages = [float(coverage_vector[i]) for i in offsets if i < len(coverage_vector)]
        segment = segment_by_span.get((start, length), {})
        segment_evidence = segment.get("evidence", {}) if isinstance(segment, Mapping) else {}
        field_evidence = dict(field.get("evidence", {}) or {})

        stats[f"field_{index}"] = {
            "offset": start,
            "width": length,
            "field_type": field.get("field_type", field.get("semantic_role", "unknown")),
            "confidence": field.get("confidence"),
            "endian": field.get("endian"),
            "cardinality": field_evidence.get("unique_values", len(counts)),
            "sample_cardinality": len(counts),
            "dominant_values": [
                {"hex": value, "count": count, "ratio": round(count / len(observed), 6) if observed else 0.0}
                for value, count in counts.most_common(max_values)
            ],
            "entropy_mean": round(sum(entropies) / len(entropies), 6) if entropies else segment_evidence.get("mean_byte_entropy"),
            "unique_ratio_mean": round(sum(unique_ratios) / len(unique_ratios), 6) if unique_ratios else field_evidence.get("cardinality_ratio"),
            "coverage_mean": round(sum(coverages) / len(coverages), 6) if coverages else segment_evidence.get("feature_avg_coverage"),
            "stability_score": segment_evidence.get("feature_stability_score"),
            "length_match_score": field_evidence.get("length_match_score"),
            "raw_evidence": {
                key: field_evidence[key]
                for key in ("unique_values", "length_match_score", "cardinality_ratio")
                if key in field_evidence
            },
            "segment_evidence": {
                key: segment_evidence[key]
                for key in (
                    "value_count",
                    "mean_byte_entropy",
                    "boundary_support",
                    "feature_stability_score",
                    "feature_avg_unique_ratio",
                    "feature_avg_coverage",
                    "merge_reason",
                    "original_segments",
                )
                if key in segment_evidence
            },
        }
    return stats


def derive_boundary_scores(
    fields: Sequence[Mapping[str, Any]],
    segments: Sequence[Mapping[str, Any]] = (),
) -> List[Dict[str, Any]]:
    segment_by_end = {int(seg.get("end", 0)): seg for seg in segments}
    scores: List[Dict[str, Any]] = []
    for left_index, field in enumerate(fields[:-1]):
        boundary_after = _field_start(field) + _field_length(field)
        left = segment_by_end.get(boundary_after, {})
        left_evidence = left.get("evidence", {}) if isinstance(left, Mapping) else {}
        next_field = fields[left_index + 1]
        scores.append(
            {
                "boundary_after": boundary_after,
                "left_field_index": left_index,
                "right_field_index": left_index + 1,
                "left_width": _field_length(field),
                "right_width": _field_length(next_field),
                "field_confidence_left": field.get("confidence"),
                "field_confidence_right": next_field.get("confidence"),
                "boundary_support": left_evidence.get("boundary_support"),
                "entropy_left_mean": left_evidence.get("mean_byte_entropy"),
                "stability_left": left_evidence.get("feature_stability_score"),
                "evidence_source": "segments" if left_evidence else "field_adjacency",
            }
        )
    return scores


def build_family_statistics(
    details: Optional[Mapping[str, Any]] = None,
    family_features: Optional[Mapping[str, Any]] = None,
    messages: Sequence[MessageRecord] = (),
) -> Dict[str, Any]:
    details = details or {}
    family_features = family_features or {}
    lengths = [msg.payload_len for msg in messages]
    length_hist = Counter(lengths)
    length_stats = family_features.get("length_stats") or details.get("statistics") or {}
    if not length_stats and lengths:
        length_stats = {
            "min": min(lengths),
            "max": max(lengths),
            "mean": round(sum(lengths) / len(lengths), 6),
            "distinct_lengths": len(length_hist),
            "length_histogram": dict(sorted(length_hist.items())),
        }
    fields = details.get("field_hypotheses", []) or []
    one_byte_fields = sum(1 for field in fields if _field_length(field) == 1)
    return {
        "message_count": details.get("message_count", family_features.get("message_count", len(messages))),
        "template": details.get("template"),
        "field_count": len(fields),
        "one_byte_field_count": one_byte_fields,
        "length_stats": length_stats,
        "entropy_summary": family_features.get("entropy_summary", {}),
        "unique_ratio_summary": family_features.get("unique_ratio_summary", {}),
        "structure_stats": family_features.get("structure_stats", {}),
    }


def summarize_stage_artifact(payload: Optional[Mapping[str, Any]], stage: str) -> Dict[str, Any]:
    if not payload:
        return {}
    if stage == "boundary":
        families = payload if all(isinstance(v, Mapping) for v in payload.values()) else {}
        applied = sum(int((details.get("llm_boundary_refinement") or {}).get("applied", 0)) for details in families.values())
        rejected = sum(int((details.get("llm_boundary_refinement") or {}).get("rejected", 0)) for details in families.values())
        return {"total_families": len(families), "total_applied": applied, "total_rejected": rejected}
    if stage == "semantic":
        families = payload if all(isinstance(v, Mapping) for v in payload.values()) else {}
        applied = sum(int((details.get("llm_semantic_labeling") or {}).get("applied", 0)) for details in families.values())
        rejected = sum(int((details.get("llm_semantic_labeling") or {}).get("rejected", 0)) for details in families.values())
        labeled = sum(1 for details in families.values() for field in details.get("field_hypotheses", []) if field.get("semantic_role"))
        return {"total_families": len(families), "total_labels_applied": applied or labeled, "total_labels_rejected": rejected}
    if stage == "relation":
        summary = payload.get("llm_validation_summary") or {}
        if summary:
            return {
                "original_count": summary.get("original_count", 0),
                "kept_count": summary.get("kept_count", 0),
                "discarded_count": summary.get("discarded_count", 0),
            }
        relations = payload.get("family_edges", []) or []
        return {"original_count": len(relations), "kept_count": len(relations), "discarded_count": 0}
    return {}


def index_messages_by_family(
    messages_by_id: Mapping[int, MessageRecord],
    assignments_payload: Mapping[str, Any],
    max_samples: int,
) -> Dict[str, List[MessageRecord]]:
    grouped: Dict[str, List[MessageRecord]] = {}
    for assignment in assignments_payload.get("assignments", []) or []:
        family_id = assignment.get("family_id")
        msg = messages_by_id.get(int(assignment.get("msg_id")))
        if family_id and msg and len(grouped.setdefault(family_id, [])) < max_samples:
            grouped[family_id].append(msg)
    return grouped
