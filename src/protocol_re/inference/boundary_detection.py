from __future__ import annotations

from collections import Counter, defaultdict
from math import log2
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FieldHypothesis, Segment
from protocol_re.utils.bytes import hex_to_bytes, safe_int_from_bytes

# Performance limits for large payloads
MAX_BOUNDARY_DETECTION_LENGTH = 512  # Limit boundary detection to first 512 bytes


def _entropy(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = float(sum(counts.values()))
    return -sum((count / total) * log2(count / total) for count in counts.values())


def _mutual_information(left: Sequence[int], right: Sequence[int]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    total = float(len(left))
    left_counts = Counter(left)
    right_counts = Counter(right)
    pair_counts = Counter(zip(left, right))
    mi = 0.0
    for (lval, rval), joint_count in pair_counts.items():
        pxy = joint_count / total
        px = left_counts[lval] / total
        py = right_counts[rval] / total
        mi += pxy * log2(pxy / (px * py))
    return mi


def position_statistics(messages_hex: Sequence[str]) -> List[Dict[str, float]]:
    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = max((len(msg) for msg in messages), default=0)
    # Limit analysis length to avoid performance issues with large payloads
    analysis_len = min(max_len, MAX_BOUNDARY_DETECTION_LENGTH)
    stats: List[Dict[str, float]] = []

    for offset in range(analysis_len):
        values = [msg[offset] for msg in messages if offset < len(msg)]
        coverage = len(values) / len(messages) if messages else 0.0
        stats.append(
            {
                "offset": float(offset),
                "coverage": coverage,
                "entropy": _entropy(values),
                "unique_ratio": len(set(values)) / len(values) if values else 0.0,
            }
        )

    return stats


def score_boundaries(messages_hex: Sequence[str]) -> List[Dict[str, float]]:
    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = max((len(msg) for msg in messages), default=0)
    # Limit analysis length to avoid performance issues with large payloads
    analysis_len = min(max_len, MAX_BOUNDARY_DETECTION_LENGTH)
    stats = position_statistics(messages_hex)
    scores: List[Dict[str, float]] = []

    for offset in range(min(len(stats) - 1, analysis_len - 1)):
        left_values = [msg[offset] for msg in messages if offset < len(msg) and offset + 1 < len(msg)]
        right_values = [msg[offset + 1] for msg in messages if offset < len(msg) and offset + 1 < len(msg)]
        entropy_jump = abs(stats[offset + 1]["entropy"] - stats[offset]["entropy"])
        uniqueness_jump = abs(stats[offset + 1]["unique_ratio"] - stats[offset]["unique_ratio"])
        dependency_drop = max(0.0, stats[offset]["entropy"] + stats[offset + 1]["entropy"] - _mutual_information(left_values, right_values))
        coverage_drop = abs(stats[offset + 1]["coverage"] - stats[offset]["coverage"])
        score = (1.2 * entropy_jump) + (0.8 * uniqueness_jump) + (0.6 * dependency_drop) + (0.4 * coverage_drop)
        scores.append(
            {
                "boundary_after": float(offset),
                "score": score,
                "entropy_jump": entropy_jump,
                "uniqueness_jump": uniqueness_jump,
                "dependency_drop": dependency_drop,
                "coverage_drop": coverage_drop,
            }
        )

    return scores


def infer_segments(
    messages_hex: Sequence[str],
    score_threshold: float = 1.5,
    min_segment_width: int = 1,
    family_features: Optional[Dict[str, Any]] = None,
    framing_summary: Optional[Dict[str, Any]] = None,
) -> List[Segment]:
    if not messages_hex:
        return []

    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = max(len(msg) for msg in messages)
    boundary_scores = score_boundaries(messages_hex)
    boundary_score_by_offset = {int(item["boundary_after"]): item for item in boundary_scores}

    framing_boundary, framing_evidence = framing_body_boundary_hint(framing_summary, max_len)

    raw_boundaries = [0]
    for item in boundary_scores:
        boundary = int(item["boundary_after"]) + 1
        if item["score"] >= score_threshold and boundary - raw_boundaries[-1] >= min_segment_width:
            raw_boundaries.append(boundary)
    if framing_boundary is not None and framing_boundary not in raw_boundaries:
        raw_boundaries.append(framing_boundary)
    raw_boundaries = sorted(set(raw_boundaries))
    if raw_boundaries[-1] != max_len:
        raw_boundaries.append(max_len)

    segments: List[Segment] = []
    for start, end in zip(raw_boundaries, raw_boundaries[1:]):
        if end <= start:
            continue
        segment_values = [msg[start:end] for msg in messages if len(msg) >= end]
        value_count = len(set(segment_values)) if segment_values else 0
        entropy_proxy = mean([_entropy(list(value)) for value in segment_values]) if segment_values else 0.0
        kind = "constant" if value_count <= 1 else "variable"
        confidence = 1.0 / (1.0 + entropy_proxy)
        evidence: Dict[str, Any] = {
            "value_count": value_count,
            "mean_byte_entropy": round(entropy_proxy, 4),
        }

        left_boundary = boundary_score_by_offset.get(start - 1) if start > 0 else None
        right_boundary = boundary_score_by_offset.get(end - 1) if end < max_len else None
        boundary_supports = [
            float(item["score"])
            for item in (left_boundary, right_boundary)
            if item is not None
        ]
        if boundary_supports:
            evidence["boundary_support"] = round(max(boundary_supports), 4)

        feature_evidence = segment_feature_summary(family_features, start, end)
        if feature_evidence:
            evidence.update(feature_evidence)
            confidence = feature_adjusted_segment_confidence(kind, confidence, feature_evidence)

        if framing_boundary is not None and (start == framing_boundary or end == framing_boundary):
            evidence["framing_boundary_support"] = framing_evidence
            confidence = max(confidence, float(framing_evidence.get("confidence", 0.0)) * 0.85)

        segments.append(
            Segment(
                start=start,
                end=end,
                kind=kind,
                confidence=round(confidence, 4),
                evidence=evidence,
            )
        )

    return segments


def framing_body_boundary_hint(
    framing_summary: Optional[Dict[str, Any]],
    max_len: int,
    min_confidence: float = 0.65,
) -> Tuple[Optional[int], Dict[str, Any]]:
    if not framing_summary:
        return None, {}
    layouts = framing_summary.get("layout_hypotheses", []) or []
    if not layouts:
        return None, {}
    best = layouts[0]
    confidence = float(best.get("confidence", 0.0) or 0.0)
    body_start = int(best.get("body_start", best.get("header_end", 0)) or 0)
    if confidence < min_confidence or body_start <= 0 or body_start >= max_len:
        return None, {}
    return body_start, {
        "source": "framing",
        "confidence": round(confidence, 4),
        "header_start": int(best.get("header_start", 0) or 0),
        "header_end": int(best.get("header_end", body_start) or body_start),
        "body_start": body_start,
        "field_support_types": (best.get("evidence") or {}).get("field_support_types", []),
    }


def _average_window(values: Sequence[float], start: int, end: int) -> Optional[float]:
    window = [float(value) for value in values[start:end]]
    if not window:
        return None
    return mean(window)


def segment_feature_summary(
    family_features: Optional[Dict[str, Any]],
    start: int,
    end: int,
) -> Dict[str, Any]:
    if not family_features:
        return {}

    position_stats_payload = family_features.get("position_stats", {}) or {}
    entropy_vector = position_stats_payload.get("entropy_vector", []) or []
    unique_ratio_vector = position_stats_payload.get("uniqueness_ratio_vector", []) or []
    coverage_vector = position_stats_payload.get("coverage_vector", []) or []

    avg_entropy = _average_window(entropy_vector, start, end)
    avg_unique_ratio = _average_window(unique_ratio_vector, start, end)
    avg_coverage = _average_window(coverage_vector, start, end)
    if avg_entropy is None and avg_unique_ratio is None and avg_coverage is None:
        return {}

    evidence: Dict[str, Any] = {"feature_source": "family_features"}
    if avg_entropy is not None:
        evidence["feature_avg_offset_entropy"] = round(avg_entropy, 6)
        evidence["feature_stability_score"] = round(max(0.0, 1.0 - min(avg_entropy / 8.0, 1.0)), 6)
    if avg_unique_ratio is not None:
        evidence["feature_avg_unique_ratio"] = round(avg_unique_ratio, 6)
    if avg_coverage is not None:
        evidence["feature_avg_coverage"] = round(avg_coverage, 6)
    return evidence


def feature_adjusted_segment_confidence(
    kind: str,
    base_confidence: float,
    feature_evidence: Dict[str, Any],
) -> float:
    coverage = float(feature_evidence.get("feature_avg_coverage", 1.0))
    stability = float(feature_evidence.get("feature_stability_score", base_confidence))
    unique_ratio = float(feature_evidence.get("feature_avg_unique_ratio", 0.0))

    if kind == "constant":
        feature_confidence = (0.7 * stability) + (0.3 * coverage)
    else:
        variability_support = min(1.0, unique_ratio * 2.0)
        feature_confidence = (0.4 * stability) + (0.4 * variability_support) + (0.2 * coverage)

    return max(0.0, min(1.0, (0.55 * base_confidence) + (0.45 * feature_confidence)))


def infer_template(messages_hex: Sequence[str], stability_threshold: float = 0.95) -> str:
    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = max((len(msg) for msg in messages), default=0)
    # Limit template generation to avoid performance issues with large payloads
    analysis_len = min(max_len, MAX_BOUNDARY_DETECTION_LENGTH)
    template: List[str] = []

    for offset in range(analysis_len):
        values = [msg[offset] for msg in messages if offset < len(msg)]
        if not values:
            continue
        counts = Counter(values)
        value, count = counts.most_common(1)[0]
        if count / len(values) >= stability_threshold:
            template.append(f"{value:02x}")
        else:
            template.append("??")

    # Indicate if template was truncated
    if max_len > analysis_len:
        template.append(f"... [{max_len - analysis_len} more bytes]")

    return " ".join(template)


def infer_field_hypotheses(
    family_id: str,
    messages_hex: Sequence[str],
    segments: Sequence[Segment],
) -> List[FieldHypothesis]:
    messages = [hex_to_bytes(msg) for msg in messages_hex]
    hypotheses: List[FieldHypothesis] = []
    total_messages = len(messages)

    for segment in segments:
        values = [msg[segment.start:segment.end] for msg in messages if len(msg) >= segment.end]
        if not values:
            continue
        unique_values = set(values)
        width = segment.end - segment.start
        confidence = 0.5
        field_type = "blob"
        evidence: Dict[str, float] = {"unique_values": float(len(unique_values))}
        attributes: Dict[str, str] = {}
        endian = None

        if len(unique_values) == 1:
            field_type = "constant"
            confidence = 0.99
            attributes["value_hex"] = next(iter(unique_values)).hex()
        elif width in (1, 2, 4):
            best_length_score = 0.0
            best_endian = None
            for candidate_endian in ("big", "little"):
                matches_total = 0
                matches_suffix = 0
                usable = 0
                for message in messages:
                    if len(message) < segment.end:
                        continue
                    usable += 1
                    value = safe_int_from_bytes(message[segment.start:segment.end], endian=candidate_endian)
                    if value == len(message):
                        matches_total += 1
                    if value == len(message) - segment.end:
                        matches_suffix += 1
                if usable:
                    score = max(matches_total / usable, matches_suffix / usable)
                    if score > best_length_score:
                        best_length_score = score
                        best_endian = candidate_endian
            evidence["length_match_score"] = round(best_length_score, 4)

            cardinality_ratio = len(unique_values) / max(total_messages, 1)
            evidence["cardinality_ratio"] = round(cardinality_ratio, 4)
            if best_length_score >= 0.8:
                field_type = "length"
                confidence = best_length_score
                endian = best_endian
            elif cardinality_ratio <= 0.2:
                field_type = "keyword"
                confidence = 1.0 - cardinality_ratio
            elif cardinality_ratio >= 0.8 and width in (2, 4):
                field_type = "counter_or_transaction_id"
                confidence = min(0.95, cardinality_ratio)
                endian = best_endian or "big"
            elif width == 1 and len(unique_values) <= 8:
                field_type = "flags_or_status"
                confidence = 0.7

        hypotheses.append(
            FieldHypothesis(
                family_id=family_id,
                start=segment.start,
                length=width,
                field_type=field_type,
                confidence=round(confidence, 4),
                endian=endian,
                evidence=evidence,
                attributes=attributes,
            )
        )

    return hypotheses
