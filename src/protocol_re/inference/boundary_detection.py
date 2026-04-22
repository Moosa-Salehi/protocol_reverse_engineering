from __future__ import annotations

from collections import Counter, defaultdict
from math import log2
from statistics import mean
from typing import Dict, Iterable, List, Sequence, Tuple

from protocol_re.model.schema import FieldHypothesis, Segment
from protocol_re.utils.bytes import hex_to_bytes, safe_int_from_bytes


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
    stats: List[Dict[str, float]] = []

    for offset in range(max_len):
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
    stats = position_statistics(messages_hex)
    scores: List[Dict[str, float]] = []

    for offset in range(max_len - 1):
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
) -> List[Segment]:
    if not messages_hex:
        return []

    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = max(len(msg) for msg in messages)
    boundary_scores = score_boundaries(messages_hex)

    raw_boundaries = [0]
    for item in boundary_scores:
        boundary = int(item["boundary_after"]) + 1
        if item["score"] >= score_threshold and boundary - raw_boundaries[-1] >= min_segment_width:
            raw_boundaries.append(boundary)
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
        segments.append(
            Segment(
                start=start,
                end=end,
                kind=kind,
                confidence=round(confidence, 4),
                evidence={
                    "value_count": value_count,
                    "mean_byte_entropy": round(entropy_proxy, 4),
                },
            )
        )

    return segments


def infer_template(messages_hex: Sequence[str], stability_threshold: float = 0.95) -> str:
    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = max((len(msg) for msg in messages), default=0)
    template: List[str] = []

    for offset in range(max_len):
        values = [msg[offset] for msg in messages if offset < len(msg)]
        if not values:
            continue
        counts = Counter(values)
        value, count = counts.most_common(1)[0]
        if count / len(values) >= stability_threshold:
            template.append(f"{value:02x}")
        else:
            template.append("??")

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
