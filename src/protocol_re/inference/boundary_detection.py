"""
Enhanced boundary detection with anti-fragmentation penalties.

This module addresses over-segmentation by:
1. Penalizing excessive 1-byte fields
2. Requiring minimum segment widths
3. Merging adjacent similar fields
4. Adding maximum field count limits
5. Reducing entropy weight in scoring
"""
from __future__ import annotations

from collections import Counter
from math import log2
from statistics import mean
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from protocol_re.model.schema import FieldHypothesis, Segment
from protocol_re.utils.bytes import best_numeric_endian, hex_to_bytes, safe_int_from_bytes

from protocol_re.config.thresholds import BoundaryDetection as _BD

# Re-export for backward compatibility
MAX_BOUNDARY_DETECTION_LENGTH = _BD.MAX_BOUNDARY_DETECTION_LENGTH
MAX_FIELDS_PER_FAMILY = _BD.MAX_FIELDS_PER_FAMILY
MIN_FIELD_WIDTH_DEFAULT = _BD.MIN_FIELD_WIDTH_DEFAULT
SINGLE_BYTE_PENALTY = _BD.SINGLE_BYTE_PENALTY
ENTROPY_WEIGHT_REDUCED = _BD.ENTROPY_WEIGHT_REDUCED
MERGE_WIDTH_TARGETS_DEFAULT = _BD.MERGE_WIDTH_TARGETS_DEFAULT
LENGTH_FIELD_WIDTHS_DEFAULT = _BD.LENGTH_FIELD_WIDTHS_DEFAULT
LENGTH_MATCH_THRESHOLD_DEFAULT = _BD.LENGTH_MATCH_THRESHOLD_DEFAULT
BOUNDARY_CONFIDENCE_WEIGHT_DEFAULT = _BD.BOUNDARY_CONFIDENCE_WEIGHT_DEFAULT
ISOLATE_BODY_OPCODE_DEFAULT = _BD.ISOLATE_BODY_OPCODE
OPCODE_MAX_CARDINALITY_RATIO = _BD.OPCODE_MAX_CARDINALITY_RATIO


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


def score_boundaries(
    messages_hex: Sequence[str],
    reduce_entropy_weight: bool = True,
    entropy_weight: Optional[float] = None,
) -> List[Dict[str, float]]:
    """
    Score potential field boundaries.

    Args:
        messages_hex: Messages to analyze
        reduce_entropy_weight: If True, reduce entropy weight to avoid over-segmentation
        entropy_weight: Optional explicit entropy-jump weight
    """
    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = max((len(msg) for msg in messages), default=0)
    analysis_len = min(max_len, MAX_BOUNDARY_DETECTION_LENGTH)
    stats = position_statistics(messages_hex)
    scores: List[Dict[str, float]] = []

    # Adjust weights to reduce over-segmentation
    entropy_weight = entropy_weight if entropy_weight is not None else (ENTROPY_WEIGHT_REDUCED if reduce_entropy_weight else 1.2)
    uniqueness_weight = 0.8
    dependency_weight = 1.0  # Increased from 0.6 (more important)
    coverage_weight = 0.4

    for offset in range(min(len(stats) - 1, analysis_len - 1)):
        left_values = [msg[offset] for msg in messages if offset < len(msg) and offset + 1 < len(msg)]
        right_values = [msg[offset + 1] for msg in messages if offset < len(msg) and offset + 1 < len(msg)]

        entropy_jump = abs(stats[offset + 1]["entropy"] - stats[offset]["entropy"])
        uniqueness_jump = abs(stats[offset + 1]["unique_ratio"] - stats[offset]["unique_ratio"])
        dependency_drop = max(0.0, stats[offset]["entropy"] + stats[offset + 1]["entropy"] - _mutual_information(left_values, right_values))
        coverage_drop = abs(stats[offset + 1]["coverage"] - stats[offset]["coverage"])

        score = (
            entropy_weight * entropy_jump +
            uniqueness_weight * uniqueness_jump +
            dependency_weight * dependency_drop +
            coverage_weight * coverage_drop
        )

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


def detect_length_field_candidates(
    messages_hex: Sequence[str],
    widths: Sequence[int] = LENGTH_FIELD_WIDTHS_DEFAULT,
    match_threshold: float = LENGTH_MATCH_THRESHOLD_DEFAULT,
    min_samples: int = 3,
    require_variable_lengths: bool = True,
) -> List[Dict[str, Any]]:
    """Find fields whose numeric value equals bytes remaining after the field."""
    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = min(max((len(msg) for msg in messages), default=0), MAX_BOUNDARY_DETECTION_LENGTH)
    candidates: List[Dict[str, Any]] = []

    for width in sorted({int(item) for item in widths if int(item) > 0}):
        if width not in (2, 4):
            continue
        for start in range(0, max(0, max_len - width + 1)):
            end = start + width
            best: Optional[Dict[str, Any]] = None
            for candidate_endian in ("big", "little"):
                usable = 0
                matches = 0
                values = set()
                expected_lengths = set()
                for message in messages:
                    if len(message) < end:
                        continue
                    usable += 1
                    value = safe_int_from_bytes(message[start:end], endian=candidate_endian)
                    expected = len(message) - end
                    values.add(value)
                    expected_lengths.add(expected)
                    if value == expected:
                        matches += 1
                if usable < min_samples:
                    continue
                ratio = matches / usable
                if ratio < match_threshold:
                    continue
                if require_variable_lengths and len(values) <= 1 and len(expected_lengths) <= 1:
                    continue
                candidate = {
                    "start": start,
                    "end": end,
                    "width": width,
                    "endian": candidate_endian,
                    "match_ratio": ratio,
                    "usable_messages": usable,
                    "matched_messages": matches,
                    "distinct_values": len(values),
                    "distinct_expected_lengths": len(expected_lengths),
                }
                if best is None or ratio > float(best["match_ratio"]):
                    best = candidate
            if best is not None:
                candidates.append(best)

    candidates.sort(key=lambda item: (-float(item["match_ratio"]), int(item["width"]), int(item["start"])))
    selected: List[Dict[str, Any]] = []
    occupied: Set[int] = set()
    for candidate in candidates:
        offsets = set(range(int(candidate["start"]), int(candidate["end"])))
        if occupied.intersection(offsets):
            continue
        selected.append(candidate)
        occupied.update(offsets)
    selected.sort(key=lambda item: (int(item["start"]), int(item["width"])))
    return selected


def _length_evidence_by_span(length_candidates: Sequence[Dict[str, Any]]) -> Dict[Tuple[int, int], Dict[str, Any]]:
    evidence_by_span: Dict[Tuple[int, int], Dict[str, Any]] = {}
    for candidate in length_candidates:
        span = (int(candidate["start"]), int(candidate["end"]))
        current = evidence_by_span.get(span)
        if current is None or float(candidate["match_ratio"]) > float(current.get("match_ratio", 0.0)):
            evidence_by_span[span] = {
                "semantic_hint": "length",
                "length_match_ratio": round(float(candidate["match_ratio"]), 4),
                "length_endian": candidate["endian"],
                "length_usable_messages": int(candidate["usable_messages"]),
                "length_matched_messages": int(candidate["matched_messages"]),
                "length_distinct_values": int(candidate["distinct_values"]),
                "length_distinct_expected_lengths": int(candidate["distinct_expected_lengths"]),
            }
    return evidence_by_span


def _protected_length_boundaries(length_candidates: Sequence[Dict[str, Any]]) -> Set[int]:
    protected: Set[int] = set()
    for candidate in length_candidates:
        protected.add(int(candidate["start"]))
        protected.add(int(candidate["end"]))
    return protected


def _inside_length_candidate(boundary: int, length_candidates: Sequence[Dict[str, Any]]) -> bool:
    return any(int(candidate["start"]) < boundary < int(candidate["end"]) for candidate in length_candidates)


def boundary_change_support(messages: Sequence[bytes], boundary: int) -> float:
    """Return the fraction of messages with a local byte transition at boundary."""
    if boundary <= 0:
        return 1.0
    usable = 0
    changes = 0
    for message in messages:
        if boundary >= len(message):
            continue
        usable += 1
        if message[boundary - 1] != message[boundary]:
            changes += 1
    return changes / usable if usable else 0.0


def _normalise_score(score: float, score_threshold: float) -> float:
    if score_threshold <= 0:
        return min(1.0, max(0.0, score))
    return min(1.0, max(0.0, score / score_threshold))


def should_merge_segments(
    seg1: Segment,
    seg2: Segment,
    messages_hex: Sequence[str]
) -> bool:
    """
    Determine if two adjacent segments should be merged.

    Merge if:
    - Both are 1-byte fields
    - Both are constants
    - Both have same field type and low confidence
    """
    # Both are 1-byte
    if (seg2.start - seg1.start) == 1 and (seg2.end - seg2.start) == 1:
        # Merge adjacent 1-byte fields unless they're clearly different types
        if seg1.kind == seg2.kind == "constant":
            return True
        if seg1.kind == seg2.kind == "variable" and seg1.confidence < 0.7 and seg2.confidence < 0.7:
            return True

    return False


def merge_segments(
    segments: List[Segment],
    messages_hex: Sequence[str],
    protected_boundaries: Optional[Set[int]] = None,
    merge_width_targets: Sequence[int] = MERGE_WIDTH_TARGETS_DEFAULT,
) -> List[Segment]:
    """
    Merge adjacent segments that should be combined.

    More aggressive merging to reduce over-segmentation:
    - Merge consecutive 1-byte variable fields
    - Merge adjacent constants
    - Merge low-confidence adjacent fields
    - Multi-pass merging for better results
    """
    if len(segments) <= 1:
        return segments

    protected_boundaries = protected_boundaries or set()
    merge_width_targets = tuple(sorted({int(width) for width in merge_width_targets if int(width) > 0}))
    max_merge_width = max(merge_width_targets, default=0)

    # Multi-pass merging: keep merging until no more merges happen
    max_passes = 3
    for pass_num in range(max_passes):
        merged: List[Segment] = []
        current = segments[0]
        merge_count = 0

        for next_seg in segments[1:]:
            # Check if segments are adjacent
            if current.end != next_seg.start:
                merged.append(current)
                current = next_seg
                continue
            if current.end in protected_boundaries:
                merged.append(current)
                current = next_seg
                continue

            should_merge = False
            merge_reason = ""

            # Rule 1: Merge adjacent constants (always)
            if current.kind == next_seg.kind == "constant":
                should_merge = True
                merge_reason = "adjacent_constants"

            # Rule 2: Merge consecutive 1-byte variable fields (aggressive)
            elif (current.end - current.start) == 1 and (next_seg.end - next_seg.start) == 1:
                if current.kind == next_seg.kind == "variable":
                    should_merge = True
                    merge_reason = "consecutive_single_byte_variables"
                # Also merge 1-byte constant + 1-byte variable if both low confidence
                elif current.confidence < 0.7 and next_seg.confidence < 0.7:
                    should_merge = True
                    merge_reason = "adjacent_single_byte_low_confidence"

            # Rule 3: Merge low-confidence adjacent fields of same kind
            elif (current.kind == next_seg.kind and
                  current.confidence < 0.7 and next_seg.confidence < 0.7):
                should_merge = True
                merge_reason = "low_confidence_same_kind"

            # Rule 4: Merge if combined width is reasonable (2 or 4 bytes)
            elif (current.kind == next_seg.kind and
                  (next_seg.end - current.start) in merge_width_targets):
                if current.confidence < 0.8 or next_seg.confidence < 0.8:
                    should_merge = True
                    merge_reason = "standard_width_alignment"

            # Rule 5: Merge multiple 1-byte segments into standard widths (2, 4 bytes)
            elif (current.end - current.start) <= 2 and (next_seg.end - next_seg.start) <= 2:
                combined_width = next_seg.end - current.start
                if combined_width in merge_width_targets and current.kind == next_seg.kind:
                    # Merge if at least one has low confidence
                    if current.confidence < 0.75 or next_seg.confidence < 0.75:
                        should_merge = True
                        merge_reason = "small_segments_to_standard_width"

            # Rule 6: Aggressive merging for very small segments (pass 2+)
            elif pass_num > 0:
                # In later passes, be more aggressive with small segments
                if (current.end - current.start) == 1 or (next_seg.end - next_seg.start) == 1:
                    combined_width = next_seg.end - current.start
                    if combined_width <= max_merge_width:
                        should_merge = True
                        merge_reason = "aggressive_small_segment_merge"

            if should_merge:
                merge_count += 1
                # Merge: extend current segment
                # Use the more specific kind if one is constant and one is variable
                merged_kind = current.kind
                if current.kind != next_seg.kind:
                    # Prefer variable over constant when merging different kinds
                    merged_kind = "variable" if "variable" in (current.kind, next_seg.kind) else current.kind

                current = Segment(
                    start=current.start,
                    end=next_seg.end,
                    kind=merged_kind,
                    confidence=min(current.confidence, next_seg.confidence) * 0.95,  # Slight penalty for merging
                    evidence={
                        **current.evidence,
                        "merged": True,
                        "merge_reason": merge_reason,
                        "merge_pass": pass_num + 1,
                        "original_segments": current.evidence.get("original_segments", 1) + 1
                    }
                )
            else:
                # Don't merge - add current and move to next
                merged.append(current)
                current = next_seg

        # Add the last segment
        merged.append(current)

        # If no merges happened, we're done
        if merge_count == 0:
            break

        # Prepare for next pass
        segments = merged

    return merged


def infer_segments(
    messages_hex: Sequence[str],
    score_threshold: float = 2.0,  # Increased from 1.5
    min_segment_width: int = 1,
    family_features: Optional[Dict[str, Any]] = None,
    framing_summary: Optional[Dict[str, Any]] = None,
    max_fields: int = MAX_FIELDS_PER_FAMILY,
    enable_merging: bool = True,
    entropy_weight: Optional[float] = None,
    merge_width_targets: Sequence[int] = MERGE_WIDTH_TARGETS_DEFAULT,
    length_match_threshold: float = LENGTH_MATCH_THRESHOLD_DEFAULT,
    enable_length_validator: bool = True,
    boundary_confidence_weight: float = BOUNDARY_CONFIDENCE_WEIGHT_DEFAULT,
    isolate_body_opcode: bool = ISOLATE_BODY_OPCODE_DEFAULT,
) -> List[Segment]:
    """
    Infer field segments with anti-fragmentation.

    Args:
        messages_hex: Messages to analyze
        score_threshold: Minimum score for boundary (increased to reduce fragmentation)
        min_segment_width: Minimum segment width
        family_features: Optional family features
        framing_summary: Optional framing hints
        max_fields: Maximum number of fields (anti-fragmentation)
        enable_merging: Enable segment merging
        entropy_weight: Optional entropy-jump weight for boundary scoring
        merge_width_targets: Combined widths allowed by standard-width merge rules
        length_match_threshold: Minimum corpus match ratio for length-field protection
        enable_length_validator: Enable statistical length-field boundary protection
        boundary_confidence_weight: Weight for boundary-support term in segment confidence
    """
    if not messages_hex:
        return []

    messages = [hex_to_bytes(msg) for msg in messages_hex]
    max_len = max(len(msg) for msg in messages)
    boundary_scores = score_boundaries(messages_hex, reduce_entropy_weight=True, entropy_weight=entropy_weight)
    boundary_score_by_offset = {int(item["boundary_after"]): item for item in boundary_scores}
    boundary_change_by_pos = {boundary: boundary_change_support(messages, boundary) for boundary in range(1, max_len)}

    length_candidates = (
        detect_length_field_candidates(messages_hex, match_threshold=length_match_threshold)
        if enable_length_validator
        else []
    )
    length_evidence_by_span = _length_evidence_by_span(length_candidates)
    length_protected_boundaries = _protected_length_boundaries(length_candidates)

    framing_boundary, framing_evidence = framing_body_boundary_hint(framing_summary, max_len)

    # Opcode/command isolation: the first body byte after a confident framing
    # boundary is, in most binary protocols, a message-type / function / command
    # code. When it is constant or near-constant within the family, force a
    # 1-byte boundary right after it so the discriminator stays its own field
    # instead of being merged into the following uint16/uint32 chunk.
    opcode_boundary = (
        body_opcode_boundary_hint(messages, framing_boundary, max_len)
        if isolate_body_opcode
        else None
    )

    # Collect boundaries with scores
    boundary_candidates = [(0, float('inf'))]  # Start boundary always included

    for item in boundary_scores:
        boundary = int(item["boundary_after"]) + 1
        score = item["score"]
        if score >= score_threshold:
            boundary_candidates.append((boundary, score))

    # Add framing boundary if present
    if framing_boundary is not None:
        boundary_candidates.append((framing_boundary, float('inf')))

    # Force the cut right after the leading body byte (opcode/command isolation)
    if opcode_boundary is not None:
        boundary_candidates.append((opcode_boundary, float('inf')))

    for boundary in length_protected_boundaries:
        if 0 < boundary < max_len:
            boundary_candidates.append((boundary, float('inf')))

    # Add end boundary
    boundary_candidates.append((max_len, float('inf')))

    # Sort by position
    boundary_candidates.sort(key=lambda x: x[0])

    # Remove duplicates, keeping highest score
    unique_boundaries = {}
    for pos, score in boundary_candidates:
        if pos not in unique_boundaries or score > unique_boundaries[pos]:
            unique_boundaries[pos] = score

    raw_boundaries = sorted(unique_boundaries.keys())
    if length_candidates:
        raw_boundaries = [
            boundary
            for boundary in raw_boundaries
            if not _inside_length_candidate(boundary, length_candidates)
        ]

    # If too many boundaries, keep only the strongest
    if len(raw_boundaries) > max_fields + 1:
        # Keep start, end, and framing boundary
        protected = {0, max_len, *length_protected_boundaries}
        if framing_boundary is not None:
            protected.add(framing_boundary)
        if opcode_boundary is not None:
            protected.add(opcode_boundary)

        # Score other boundaries
        scored_boundaries = [
            (pos, unique_boundaries[pos])
            for pos in raw_boundaries
            if pos not in protected
        ]
        scored_boundaries.sort(key=lambda x: -x[1])  # Highest score first

        # Keep top N boundaries
        keep_count = max(0, max_fields - len(protected) + 1)
        kept_boundaries = [pos for pos, _ in scored_boundaries[:keep_count]]

        raw_boundaries = sorted(list(protected) + kept_boundaries)

    # Enforce minimum segment width
    filtered_boundaries = [raw_boundaries[0]]
    for boundary in raw_boundaries[1:]:
        if boundary - filtered_boundaries[-1] >= min_segment_width:
            filtered_boundaries.append(boundary)
        elif boundary in length_protected_boundaries:
            filtered_boundaries.append(boundary)
        elif boundary == max_len:  # Always keep end boundary
            filtered_boundaries.append(boundary)

    raw_boundaries = filtered_boundaries

    # Create segments
    segments: List[Segment] = []
    for start, end in zip(raw_boundaries, raw_boundaries[1:]):
        if end <= start:
            continue

        segment_values = [msg[start:end] for msg in messages if len(msg) >= end]
        value_count = len(set(segment_values)) if segment_values else 0
        entropy_proxy = mean([_entropy(list(value)) for value in segment_values]) if segment_values else 0.0
        kind = "constant" if value_count <= 1 else "variable"
        consistency_confidence = 1.0 / (1.0 + entropy_proxy)
        confidence = consistency_confidence

        # Apply single-byte penalty
        width = end - start
        if width == 1 and kind == "variable":
            # Penalize 1-byte variable fields unless high confidence
            if confidence < 0.9:
                confidence *= SINGLE_BYTE_PENALTY

        evidence: Dict[str, Any] = {
            "value_count": value_count,
            "mean_byte_entropy": round(entropy_proxy, 4),
            "consistency_confidence": round(confidence, 4),
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

        support_terms = []
        if start > 0:
            score_support = _normalise_score(float(left_boundary["score"]), score_threshold) if left_boundary else 0.0
            support_terms.append(max(boundary_change_by_pos.get(start, 0.0), score_support))
        if end < max_len:
            score_support = _normalise_score(float(right_boundary["score"]), score_threshold) if right_boundary else 0.0
            support_terms.append(max(boundary_change_by_pos.get(end, 0.0), score_support))
        boundary_support_ratio = mean(support_terms) if support_terms else 1.0

        length_evidence = length_evidence_by_span.get((start, end))
        if length_evidence:
            evidence.update(length_evidence)
            boundary_support_ratio = max(boundary_support_ratio, float(length_evidence["length_match_ratio"]))
            kind = "variable"

        evidence["boundary_support_ratio"] = round(boundary_support_ratio, 4)
        boundary_weight = min(1.0, max(0.0, boundary_confidence_weight))
        confidence = ((1.0 - boundary_weight) * confidence) + (boundary_weight * boundary_support_ratio)

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

    # Merge adjacent similar segments
    if enable_merging and len(segments) > 1:
        protected_boundaries = set(length_protected_boundaries)
        if framing_boundary is not None:
            protected_boundaries.add(framing_boundary)
        if opcode_boundary is not None:
            # Protect the opcode's right edge so the 1-byte discriminator is
            # never merged into the following field.
            protected_boundaries.add(opcode_boundary)
        segments = merge_segments(
            segments,
            messages_hex,
            protected_boundaries=protected_boundaries,
            merge_width_targets=merge_width_targets,
        )

    return segments


def body_opcode_boundary_hint(
    messages: Sequence[bytes],
    framing_boundary: Optional[int],
    max_len: int,
    max_cardinality_ratio: float = OPCODE_MAX_CARDINALITY_RATIO,
) -> Optional[int]:
    """Return the boundary that isolates the leading body byte as an opcode.

    The first byte of the application body (immediately after a confident
    framing/transport boundary) is, in most binary protocols, a message-type /
    function / command code. When that byte is constant or near-constant within
    the family it is treated as a discriminator and split into its own 1-byte
    field. Returns ``framing_boundary + 1`` in that case, otherwise ``None``.
    """
    if framing_boundary is None:
        return None
    if framing_boundary <= 0 or framing_boundary >= max_len - 1:
        return None
    values = [message[framing_boundary] for message in messages if len(message) > framing_boundary]
    if not values:
        return None
    cardinality_ratio = len(set(values)) / len(values)
    if len(set(values)) > 1 and cardinality_ratio > max_cardinality_ratio:
        return None
    return framing_boundary + 1


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
                observed_chunks = [message[segment.start:segment.end] for message in messages if len(message) >= segment.end]
                numeric_endian, endian_stats = best_numeric_endian(observed_chunks)
                endian = numeric_endian or best_endian
                if endian_stats:
                    evidence["endian_inference"] = {
                        key: {
                            "sequence_score": round(float(stats.get("sequence_score", 0.0) or 0.0), 4),
                            "monotonic_ratio": round(float(stats.get("monotonic_ratio", 0.0) or 0.0), 4),
                            "small_delta_ratio": round(float(stats.get("small_delta_ratio", 0.0) or 0.0), 4),
                            "delta_consistency": round(float(stats.get("delta_consistency", 0.0) or 0.0), 4),
                            "low_magnitude_score": round(float(stats.get("low_magnitude_score", 0.0) or 0.0), 4),
                        }
                        for key, stats in endian_stats.items()
                    }
                    evidence["selected_endian"] = endian
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
