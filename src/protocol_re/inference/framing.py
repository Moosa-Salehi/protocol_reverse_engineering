from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from math import log2
from statistics import mean
from typing import Any, Dict, List, Optional, Sequence, Tuple

from protocol_re.utils.bytes import best_numeric_endian, hex_to_bytes, safe_int_from_bytes


@dataclass
class FramingFieldRegion:
    start: int
    end: int
    field_type: str
    confidence: float
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "length": max(0, self.end - self.start),
            "field_type": self.field_type,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class FramingLayoutHypothesis:
    family_id: str
    header_start: int
    header_end: int
    body_start: int
    body_end: Optional[int]
    confidence: float
    field_regions: List[FramingFieldRegion] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "family_id": self.family_id,
            "header_start": self.header_start,
            "header_end": self.header_end,
            "body_start": self.body_start,
            "body_end": self.body_end,
            "confidence": self.confidence,
            "field_regions": [region.to_dict() for region in self.field_regions],
            "evidence": self.evidence,
        }


def infer_framing_hypotheses(
    family_messages: Dict[str, Sequence[str]],
    max_header_bytes: int = 32,
    max_hypotheses_per_family: int = 3,
    min_messages: int = 3,
    detect_layers: bool = False,
    layer_min_confidence: float = 0.6,
) -> Dict[str, Any]:
    """Infer protocol-agnostic frame/header layouts per family and globally.

    Args:
        family_messages: Dictionary mapping family_id to list of message hex strings
        max_header_bytes: Maximum prefix bytes to scan for framing fields
        max_hypotheses_per_family: Layout hypotheses retained per family
        min_messages: Minimum messages needed for non-fallback family inference
        detect_layers: Enable multi-layer protocol detection (A6)
        layer_min_confidence: Minimum confidence for layer boundary detection

    Returns:
        Dictionary with framing hypotheses and optional layer information
    """
    family_results: Dict[str, Any] = {}
    global_header_votes: Counter[int] = Counter()
    global_field_votes: Counter[str] = Counter()
    best_confidences: List[float] = []

    for family_id, messages_hex in sorted(family_messages.items()):
        messages = [hex_to_bytes(item) for item in messages_hex if item]
        result = infer_family_framing(
            family_id,
            messages,
            max_header_bytes=max_header_bytes,
            max_hypotheses=max_hypotheses_per_family,
            min_messages=min_messages,
        )

        # A6: Add layer boundary detection if enabled
        if detect_layers:
            from protocol_re.inference.layer_detection import detect_layer_boundary_from_framing
            layer_boundary = detect_layer_boundary_from_framing(result, layer_min_confidence)
            result["layer_boundary"] = {
                "detected": layer_boundary is not None,
                "boundary_offset": layer_boundary.offset if layer_boundary else 0,
                "confidence": layer_boundary.confidence if layer_boundary else 0.0,
                "evidence": layer_boundary.evidence if layer_boundary else {},
            }

        family_results[family_id] = result
        best = (result.get("layout_hypotheses") or [{}])[0]
        if best:
            global_header_votes[int(best.get("header_end", 0) or 0)] += 1
            best_confidences.append(float(best.get("confidence", 0.0) or 0.0))
            for region in best.get("field_regions", []) or []:
                global_field_votes[str(region.get("field_type", "unknown"))] += 1

    family_count = len(family_results)
    common_header_ends = [
        {"header_end": header_end, "family_count": count, "family_ratio": round(count / max(family_count, 1), 4)}
        for header_end, count in global_header_votes.most_common(10)
    ]

    metadata = {
        "algorithm": "protocol_agnostic_framing_v1",
        "family_count": family_count,
        "max_header_bytes": max_header_bytes,
        "max_hypotheses_per_family": max_hypotheses_per_family,
        "min_messages": min_messages,
    }

    # A6: Add layer detection metadata
    if detect_layers:
        metadata["layer_detection_enabled"] = True
        metadata["layer_min_confidence"] = layer_min_confidence
        layered_count = sum(
            1 for result in family_results.values()
            if result.get("layer_boundary", {}).get("detected", False)
        )
        metadata["families_with_layers"] = layered_count

    return {
        "metadata": metadata,
        "global": {
            "common_header_ends": common_header_ends,
            "field_type_counts": dict(global_field_votes.most_common()),
            "mean_best_confidence": round(mean(best_confidences), 4) if best_confidences else 0.0,
            "families_with_header_candidate": sum(1 for value in best_confidences if value >= 0.45),
        },
        "families": family_results,
    }


def infer_family_framing(
    family_id: str,
    messages: Sequence[bytes],
    max_header_bytes: int = 32,
    max_hypotheses: int = 3,
    min_messages: int = 3,
) -> Dict[str, Any]:
    messages = [bytes(message) for message in messages if message]
    lengths = [len(message) for message in messages]
    if len(messages) < min_messages or not lengths:
        return _fallback_result(family_id, messages, "insufficient_messages")

    max_observed_len = max(lengths)
    scan_limit = min(max_header_bytes, max_observed_len)
    position_stats = _position_stats(messages, scan_limit)
    field_regions = _candidate_fields(messages, position_stats, scan_limit)
    tail_variability = _tail_variability_scores(position_stats, scan_limit)
    boundary_scores = _header_boundary_scores(messages, position_stats, field_regions, tail_variability, scan_limit)

    layouts: List[FramingLayoutHypothesis] = []
    for header_end, score_info in sorted(boundary_scores.items(), key=lambda item: item[1]["score"], reverse=True)[: max_hypotheses * 3]:
        regions = [region for region in field_regions if region.end <= header_end]
        if not regions and header_end > 0:
            continue
        score = float(score_info["score"])
        confidence = max(0.0, min(1.0, score / 6.0))
        layouts.append(
            FramingLayoutHypothesis(
                family_id=family_id,
                header_start=0,
                header_end=header_end,
                body_start=header_end,
                body_end=None,
                confidence=round(confidence, 4),
                field_regions=sorted(regions, key=lambda item: (item.start, item.end, -item.confidence)),
                evidence={
                    **score_info,
                    "message_count": len(messages),
                    "length_min": min(lengths),
                    "length_max": max(lengths),
                    "length_distinct": len(set(lengths)),
                },
            )
        )

    layouts = _dedupe_layouts(layouts)[:max_hypotheses]
    if not layouts:
        layouts = [
            FramingLayoutHypothesis(
                family_id=family_id,
                header_start=0,
                header_end=0,
                body_start=0,
                body_end=None,
                confidence=0.0,
                evidence={"fallback_reason": "no_supported_header_boundary", "message_count": len(messages)},
            )
        ]

    return {
        "message_count": len(messages),
        "length_stats": {"min": min(lengths), "max": max(lengths), "distinct": len(set(lengths))},
        "layout_hypotheses": [layout.to_dict() for layout in layouts],
        "position_evidence": _compact_position_evidence(position_stats),
    }


def _fallback_result(family_id: str, messages: Sequence[bytes], reason: str) -> Dict[str, Any]:
    lengths = [len(message) for message in messages]
    return {
        "message_count": len(messages),
        "length_stats": {"min": min(lengths) if lengths else 0, "max": max(lengths) if lengths else 0, "distinct": len(set(lengths))},
        "layout_hypotheses": [
            FramingLayoutHypothesis(
                family_id=family_id,
                header_start=0,
                header_end=0,
                body_start=0,
                body_end=None,
                confidence=0.0,
                evidence={"fallback_reason": reason, "message_count": len(messages)},
            ).to_dict()
        ],
        "position_evidence": [],
    }


def _entropy(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = float(sum(counts.values()))
    return -sum((count / total) * log2(count / total) for count in counts.values())


def _position_stats(messages: Sequence[bytes], scan_limit: int) -> List[Dict[str, Any]]:
    stats: List[Dict[str, Any]] = []
    total = len(messages)
    for offset in range(scan_limit):
        values = [message[offset] for message in messages if offset < len(message)]
        counts = Counter(values)
        dominant_value, dominant_count = counts.most_common(1)[0] if counts else (None, 0)
        coverage = len(values) / max(total, 1)
        stable_ratio = dominant_count / max(len(values), 1)
        unique_ratio = len(counts) / max(len(values), 1)
        stats.append(
            {
                "offset": offset,
                "coverage": coverage,
                "entropy": _entropy(values),
                "unique_ratio": unique_ratio,
                "cardinality": len(counts),
                "stable_ratio": stable_ratio,
                "dominant_value_hex": f"{dominant_value:02x}" if dominant_value is not None else None,
            }
        )
    return stats


def _candidate_fields(messages: Sequence[bytes], stats: Sequence[Dict[str, Any]], scan_limit: int) -> List[FramingFieldRegion]:
    candidates: List[FramingFieldRegion] = []
    candidates.extend(_constant_runs(stats))
    candidates.extend(_length_fields(messages, scan_limit))
    candidates.extend(_counter_like_fields(messages, scan_limit))
    candidates.extend(_low_cardinality_fields(stats))
    return _dedupe_fields(candidates)


def _constant_runs(stats: Sequence[Dict[str, Any]]) -> List[FramingFieldRegion]:
    regions: List[FramingFieldRegion] = []
    start: Optional[int] = None
    values: List[str] = []
    ratios: List[float] = []
    for item in list(stats) + [{"stable_ratio": 0.0, "offset": len(stats)}]:
        stable = float(item.get("stable_ratio", 0.0) or 0.0) >= 0.95 and float(item.get("coverage", 0.0) or 0.0) >= 0.9
        if stable and start is None:
            start = int(item["offset"])
            values = []
            ratios = []
        if stable:
            values.append(str(item.get("dominant_value_hex")))
            ratios.append(float(item.get("stable_ratio", 0.0) or 0.0))
        elif start is not None:
            end = int(item["offset"])
            regions.append(
                FramingFieldRegion(
                    start=start,
                    end=end,
                    field_type="constant",
                    confidence=round(mean(ratios), 4),
                    evidence={"value_hex": "".join(values), "stable_ratio": round(mean(ratios), 4)},
                )
            )
            start = None
    return regions


def _length_fields(messages: Sequence[bytes], scan_limit: int) -> List[FramingFieldRegion]:
    regions: List[FramingFieldRegion] = []
    for width in (1, 2, 4):
        for start in range(0, max(0, scan_limit - width + 1)):
            end = start + width
            for endian in ("big", "little"):
                usable = total_matches = suffix_matches = remaining_matches = 0
                for message in messages:
                    if len(message) < end:
                        continue
                    usable += 1
                    value = safe_int_from_bytes(message[start:end], endian=endian)
                    if value == len(message):
                        total_matches += 1
                    if value == len(message) - end:
                        suffix_matches += 1
                    if value == len(message) - start:
                        remaining_matches += 1
                if not usable:
                    continue
                match_count = max(total_matches, suffix_matches, remaining_matches)
                score = match_count / usable
                if score >= 0.65:
                    if match_count == total_matches:
                        relation = "total_length"
                    elif match_count == suffix_matches:
                        relation = "body_after_field"
                    else:
                        relation = "remaining_from_field"
                    regions.append(
                        FramingFieldRegion(
                            start=start,
                            end=end,
                            field_type="length",
                            confidence=round(score, 4),
                            evidence={"match_score": round(score, 4), "relation": relation, "endian": endian, "usable_messages": usable},
                        )
                    )
    return regions


def _counter_like_fields(messages: Sequence[bytes], scan_limit: int) -> List[FramingFieldRegion]:
    regions: List[FramingFieldRegion] = []
    for width in (1, 2, 4):
        for start in range(0, max(0, scan_limit - width + 1)):
            end = start + width
            chunks = [message[start:end] for message in messages if len(message) >= end]
            if len(chunks) < 3:
                continue
            endian, endian_stats = best_numeric_endian(chunks)
            if endian is None:
                continue
            stats = endian_stats[endian]
            unique_ratio = float(stats.get("unique_ratio", 0.0) or 0.0)
            monotonic_ratio = float(stats.get("monotonic_ratio", 0.0) or 0.0)
            small_delta_ratio = float(stats.get("small_delta_ratio", 0.0) or 0.0)
            sequence_score = float(stats.get("sequence_score", 0.0) or 0.0)
            score = (0.35 * unique_ratio) + (0.45 * sequence_score) + (0.20 * monotonic_ratio)
            if unique_ratio >= 0.45 and score >= 0.62:
                regions.append(
                    FramingFieldRegion(
                        start=start,
                        end=end,
                        field_type="transaction_or_counter",
                        confidence=round(min(score, 0.95), 4),
                        evidence={
                            "unique_ratio": round(unique_ratio, 4),
                            "monotonic_ratio": round(monotonic_ratio, 4),
                            "small_delta_ratio": round(small_delta_ratio, 4),
                            "delta_consistency": round(float(stats.get("delta_consistency", 0.0) or 0.0), 4),
                            "low_magnitude_score": round(float(stats.get("low_magnitude_score", 0.0) or 0.0), 4),
                            "sequence_score": round(sequence_score, 4),
                            "endian": endian,
                        },
                    )
                )
    return regions


def _low_cardinality_fields(stats: Sequence[Dict[str, Any]]) -> List[FramingFieldRegion]:
    regions: List[FramingFieldRegion] = []
    for item in stats:
        cardinality = int(item.get("cardinality", 0) or 0)
        coverage = float(item.get("coverage", 0.0) or 0.0)
        stable_ratio = float(item.get("stable_ratio", 0.0) or 0.0)
        unique_ratio = float(item.get("unique_ratio", 1.0) or 1.0)
        if coverage >= 0.9 and 1 < cardinality <= 16 and stable_ratio < 0.95 and unique_ratio <= 0.35:
            confidence = (0.45 * coverage) + (0.35 * (1.0 - unique_ratio)) + (0.20 * min(cardinality / 16.0, 1.0))
            regions.append(
                FramingFieldRegion(
                    start=int(item["offset"]),
                    end=int(item["offset"]) + 1,
                    field_type="discriminator",
                    confidence=round(min(confidence, 0.9), 4),
                    evidence={"cardinality": cardinality, "unique_ratio": round(unique_ratio, 4), "coverage": round(coverage, 4)},
                )
            )
    return regions


def _tail_variability_scores(stats: Sequence[Dict[str, Any]], scan_limit: int) -> Dict[int, Dict[str, float]]:
    scores: Dict[int, Dict[str, float]] = {}
    for boundary in range(0, scan_limit + 1):
        head = stats[:boundary]
        tail = stats[boundary:min(len(stats), boundary + 8)]
        head_stability = mean([float(item.get("stable_ratio", 0.0) or 0.0) for item in head]) if head else 0.0
        head_entropy = mean([float(item.get("entropy", 0.0) or 0.0) for item in head]) if head else 0.0
        tail_entropy = mean([float(item.get("entropy", 0.0) or 0.0) for item in tail]) if tail else 0.0
        tail_unique = mean([float(item.get("unique_ratio", 0.0) or 0.0) for item in tail]) if tail else 0.0
        scores[boundary] = {
            "head_stability": head_stability,
            "head_entropy": head_entropy,
            "tail_entropy": tail_entropy,
            "tail_unique_ratio": tail_unique,
            "tail_variability_jump": max(0.0, tail_entropy - head_entropy),
        }
    return scores


def _header_boundary_scores(
    messages: Sequence[bytes],
    stats: Sequence[Dict[str, Any]],
    fields: Sequence[FramingFieldRegion],
    tail_scores: Dict[int, Dict[str, float]],
    scan_limit: int,
) -> Dict[int, Dict[str, Any]]:
    scores: Dict[int, Dict[str, Any]] = {}
    for boundary in range(0, scan_limit + 1):
        fields_in_header = [field for field in fields if field.end <= boundary]
        if boundary == 0:
            score = 0.15
        else:
            evidence = tail_scores.get(boundary, {})
            field_score = sum(_field_weight(field) * field.confidence for field in fields_in_header)
            coverage_score = mean([float(item.get("coverage", 0.0) or 0.0) for item in stats[:boundary]]) if stats[:boundary] else 0.0
            stability_score = float(evidence.get("head_stability", 0.0))
            tail_jump = min(float(evidence.get("tail_variability_jump", 0.0)) / 3.0, 1.0)
            size_penalty = max(0.0, (boundary - 16) / 32.0)
            score = field_score + (0.8 * coverage_score) + (0.7 * stability_score) + (0.9 * tail_jump) - size_penalty
        scores[boundary] = {
            "score": round(score, 4),
            "field_support_count": len(fields_in_header),
            "field_support_types": sorted({field.field_type for field in fields_in_header}),
            **{key: round(value, 4) for key, value in tail_scores.get(boundary, {}).items()},
        }
    return scores


def _field_weight(field: FramingFieldRegion) -> float:
    return {
        "length": 1.25,
        "transaction_or_counter": 0.95,
        "discriminator": 0.75,
        "constant": 0.55,
    }.get(field.field_type, 0.4)


def _dedupe_fields(fields: Sequence[FramingFieldRegion]) -> List[FramingFieldRegion]:
    best: Dict[Tuple[int, int, str], FramingFieldRegion] = {}
    for field in fields:
        key = (field.start, field.end, field.field_type)
        previous = best.get(key)
        if previous is None or field.confidence > previous.confidence:
            best[key] = field
    return sorted(best.values(), key=lambda item: (item.start, item.end, -item.confidence))


def _dedupe_layouts(layouts: Sequence[FramingLayoutHypothesis]) -> List[FramingLayoutHypothesis]:
    best: Dict[int, FramingLayoutHypothesis] = {}
    for layout in layouts:
        previous = best.get(layout.header_end)
        if previous is None or layout.confidence > previous.confidence:
            best[layout.header_end] = layout
    return sorted(best.values(), key=lambda item: (-item.confidence, item.header_end))


def _compact_position_evidence(stats: Sequence[Dict[str, Any]], limit: int = 16) -> List[Dict[str, Any]]:
    return [
        {
            "offset": item["offset"],
            "coverage": round(float(item.get("coverage", 0.0) or 0.0), 4),
            "entropy": round(float(item.get("entropy", 0.0) or 0.0), 4),
            "unique_ratio": round(float(item.get("unique_ratio", 0.0) or 0.0), 4),
            "cardinality": item.get("cardinality", 0),
            "stable_ratio": round(float(item.get("stable_ratio", 0.0) or 0.0), 4),
            "dominant_value_hex": item.get("dominant_value_hex"),
        }
        for item in stats[:limit]
    ]
