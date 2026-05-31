"""
Boundary quality metrics for evaluating boundary detection performance.

This module provides:
1. Over-segmentation ratio calculation
2. Boundary confidence distribution tracking
3. Average fields per family reporting
4. Precision/recall tracking (when ground truth available)
"""
from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median, stdev
from typing import Any, Dict, List, Optional, Sequence

from protocol_re.model.schema import FieldHypothesis, Segment


@dataclass
class BoundaryQualityMetrics:
    """Quality metrics for boundary detection."""

    # Basic statistics
    total_families: int
    total_segments: int
    avg_segments_per_family: float
    median_segments_per_family: float

    # Confidence statistics
    avg_confidence: float
    median_confidence: float
    confidence_stdev: float
    low_confidence_count: int  # confidence < 0.5
    high_confidence_count: int  # confidence >= 0.8

    # Over-segmentation indicators
    single_byte_segment_count: int
    single_byte_ratio: float
    over_segmentation_ratio: float  # ratio of families with >15 fields

    # Confidence distribution (buckets: 0-0.2, 0.2-0.4, 0.4-0.6, 0.6-0.8, 0.8-1.0)
    confidence_distribution: Dict[str, int]

    # Per-family statistics
    family_segment_counts: Dict[str, int]
    family_avg_confidences: Dict[str, float]

    # Ground truth comparison (if available)
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    false_positive_count: Optional[int] = None
    false_negative_count: Optional[int] = None
    true_positive_count: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "total_families": self.total_families,
            "total_segments": self.total_segments,
            "avg_segments_per_family": round(self.avg_segments_per_family, 2),
            "median_segments_per_family": self.median_segments_per_family,
            "avg_confidence": round(self.avg_confidence, 4),
            "median_confidence": round(self.median_confidence, 4),
            "confidence_stdev": round(self.confidence_stdev, 4),
            "low_confidence_count": self.low_confidence_count,
            "high_confidence_count": self.high_confidence_count,
            "single_byte_segment_count": self.single_byte_segment_count,
            "single_byte_ratio": round(self.single_byte_ratio, 4),
            "over_segmentation_ratio": round(self.over_segmentation_ratio, 4),
            "confidence_distribution": self.confidence_distribution,
            "family_segment_counts": self.family_segment_counts,
            "family_avg_confidences": {
                k: round(v, 4) for k, v in self.family_avg_confidences.items()
            },
            "precision": round(self.precision, 4) if self.precision is not None else None,
            "recall": round(self.recall, 4) if self.recall is not None else None,
            "f1_score": round(self.f1_score, 4) if self.f1_score is not None else None,
            "false_positive_count": self.false_positive_count,
            "false_negative_count": self.false_negative_count,
            "true_positive_count": self.true_positive_count,
        }

    def summary_text(self) -> str:
        """Generate human-readable summary."""
        lines = [
            "=== Boundary Quality Metrics ===",
            f"Total families: {self.total_families}",
            f"Total segments: {self.total_segments}",
            f"Avg segments per family: {self.avg_segments_per_family:.2f}",
            f"Median segments per family: {self.median_segments_per_family}",
            "",
            "Confidence Statistics:",
            f"  Average: {self.avg_confidence:.4f}",
            f"  Median: {self.median_confidence:.4f}",
            f"  Std Dev: {self.confidence_stdev:.4f}",
            f"  Low confidence (<0.5): {self.low_confidence_count}",
            f"  High confidence (>=0.8): {self.high_confidence_count}",
            "",
            "Over-Segmentation Indicators:",
            f"  Single-byte segments: {self.single_byte_segment_count} ({self.single_byte_ratio:.2%})",
            f"  Families with >15 fields: {self.over_segmentation_ratio:.2%}",
            "",
            "Confidence Distribution:",
        ]

        for bucket, count in sorted(self.confidence_distribution.items()):
            lines.append(f"  {bucket}: {count}")

        if self.precision is not None:
            lines.extend([
                "",
                "Ground Truth Comparison:",
                f"  Precision: {self.precision:.4f}",
                f"  Recall: {self.recall:.4f}",
                f"  F1 Score: {self.f1_score:.4f}",
                f"  True Positives: {self.true_positive_count}",
                f"  False Positives: {self.false_positive_count}",
                f"  False Negatives: {self.false_negative_count}",
            ])

        return "\n".join(lines)


def compute_boundary_quality_metrics(
    family_segments: Dict[str, List[Segment]],
    ground_truth: Optional[Dict[str, Any]] = None,
) -> BoundaryQualityMetrics:
    """
    Compute boundary quality metrics from detected segments.

    Args:
        family_segments: Dictionary mapping family_id to list of segments
        ground_truth: Optional ground truth data for precision/recall calculation

    Returns:
        BoundaryQualityMetrics object
    """
    if not family_segments:
        return _empty_metrics()

    # Collect all segments and confidences
    all_segments: List[Segment] = []
    all_confidences: List[float] = []
    family_segment_counts: Dict[str, int] = {}
    family_avg_confidences: Dict[str, float] = {}

    for family_id, segments in family_segments.items():
        all_segments.extend(segments)
        family_segment_counts[family_id] = len(segments)

        confidences = [seg.confidence for seg in segments]
        all_confidences.extend(confidences)
        family_avg_confidences[family_id] = mean(confidences) if confidences else 0.0

    # Basic statistics
    total_families = len(family_segments)
    total_segments = len(all_segments)
    segment_counts = list(family_segment_counts.values())
    avg_segments_per_family = mean(segment_counts) if segment_counts else 0.0
    median_segments_per_family = int(median(segment_counts)) if segment_counts else 0

    # Confidence statistics
    avg_confidence = mean(all_confidences) if all_confidences else 0.0
    median_confidence = median(all_confidences) if all_confidences else 0.0
    confidence_stdev = stdev(all_confidences) if len(all_confidences) > 1 else 0.0
    low_confidence_count = sum(1 for c in all_confidences if c < 0.5)
    high_confidence_count = sum(1 for c in all_confidences if c >= 0.8)

    # Over-segmentation indicators
    single_byte_segment_count = sum(1 for seg in all_segments if (seg.end - seg.start) == 1)
    single_byte_ratio = single_byte_segment_count / total_segments if total_segments > 0 else 0.0
    over_segmented_families = sum(1 for count in segment_counts if count > 15)
    over_segmentation_ratio = over_segmented_families / total_families if total_families > 0 else 0.0

    # Confidence distribution
    confidence_distribution = {
        "0.0-0.2": sum(1 for c in all_confidences if 0.0 <= c < 0.2),
        "0.2-0.4": sum(1 for c in all_confidences if 0.2 <= c < 0.4),
        "0.4-0.6": sum(1 for c in all_confidences if 0.4 <= c < 0.6),
        "0.6-0.8": sum(1 for c in all_confidences if 0.6 <= c < 0.8),
        "0.8-1.0": sum(1 for c in all_confidences if 0.8 <= c <= 1.0),
    }

    # Ground truth comparison (if available)
    precision = None
    recall = None
    f1_score = None
    false_positive_count = None
    false_negative_count = None
    true_positive_count = None

    if ground_truth is not None:
        gt_metrics = _compare_with_ground_truth(family_segments, ground_truth)
        precision = gt_metrics.get("precision")
        recall = gt_metrics.get("recall")
        f1_score = gt_metrics.get("f1_score")
        false_positive_count = gt_metrics.get("false_positive_count")
        false_negative_count = gt_metrics.get("false_negative_count")
        true_positive_count = gt_metrics.get("true_positive_count")

    return BoundaryQualityMetrics(
        total_families=total_families,
        total_segments=total_segments,
        avg_segments_per_family=avg_segments_per_family,
        median_segments_per_family=median_segments_per_family,
        avg_confidence=avg_confidence,
        median_confidence=median_confidence,
        confidence_stdev=confidence_stdev,
        low_confidence_count=low_confidence_count,
        high_confidence_count=high_confidence_count,
        single_byte_segment_count=single_byte_segment_count,
        single_byte_ratio=single_byte_ratio,
        over_segmentation_ratio=over_segmentation_ratio,
        confidence_distribution=confidence_distribution,
        family_segment_counts=family_segment_counts,
        family_avg_confidences=family_avg_confidences,
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        false_positive_count=false_positive_count,
        false_negative_count=false_negative_count,
        true_positive_count=true_positive_count,
    )


def _empty_metrics() -> BoundaryQualityMetrics:
    """Return empty metrics for edge cases."""
    return BoundaryQualityMetrics(
        total_families=0,
        total_segments=0,
        avg_segments_per_family=0.0,
        median_segments_per_family=0,
        avg_confidence=0.0,
        median_confidence=0.0,
        confidence_stdev=0.0,
        low_confidence_count=0,
        high_confidence_count=0,
        single_byte_segment_count=0,
        single_byte_ratio=0.0,
        over_segmentation_ratio=0.0,
        confidence_distribution={
            "0.0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0,
        },
        family_segment_counts={},
        family_avg_confidences={},
    )


def _compare_with_ground_truth(
    family_segments: Dict[str, List[Segment]],
    ground_truth: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compare detected boundaries with ground truth.

    Args:
        family_segments: Detected segments per family
        ground_truth: Ground truth data (format depends on evaluation schema)

    Returns:
        Dictionary with precision, recall, F1, and counts
    """
    # Extract ground truth boundaries
    gt_boundaries = _extract_ground_truth_boundaries(ground_truth)

    # Extract detected boundaries
    detected_boundaries = _extract_detected_boundaries(family_segments)

    # Compare boundaries (with tolerance of ±1 byte)
    true_positives = 0
    false_positives = 0
    false_negatives = 0

    matched_gt = set()

    for family_id, det_bounds in detected_boundaries.items():
        gt_bounds = gt_boundaries.get(family_id, set())

        for det_bound in det_bounds:
            # Check if this boundary matches any ground truth boundary (±1 byte tolerance)
            matched = False
            for gt_bound in gt_bounds:
                if abs(det_bound - gt_bound) <= 1:
                    matched = True
                    matched_gt.add((family_id, gt_bound))
                    break

            if matched:
                true_positives += 1
            else:
                false_positives += 1

    # Count false negatives (ground truth boundaries not detected)
    for family_id, gt_bounds in gt_boundaries.items():
        for gt_bound in gt_bounds:
            if (family_id, gt_bound) not in matched_gt:
                false_negatives += 1

    # Calculate metrics
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positive_count": true_positives,
        "false_positive_count": false_positives,
        "false_negative_count": false_negatives,
    }


def _extract_ground_truth_boundaries(ground_truth: Dict[str, Any]) -> Dict[str, set[int]]:
    """Extract boundary positions from ground truth data."""
    boundaries: Dict[str, set[int]] = {}

    # Try to extract from common ground truth formats
    if "families" in ground_truth:
        for family in ground_truth["families"]:
            family_id = family.get("family_id", "")
            fields = family.get("fields", [])

            family_boundaries = set()
            for field in fields:
                start = field.get("start", field.get("offset", 0))
                length = field.get("length", 0)
                end = start + length

                family_boundaries.add(start)
                family_boundaries.add(end)

            if family_boundaries:
                boundaries[family_id] = family_boundaries

    return boundaries


def _extract_detected_boundaries(family_segments: Dict[str, List[Segment]]) -> Dict[str, set[int]]:
    """Extract boundary positions from detected segments."""
    boundaries: Dict[str, set[int]] = {}

    for family_id, segments in family_segments.items():
        family_boundaries = set()
        for segment in segments:
            family_boundaries.add(segment.start)
            family_boundaries.add(segment.end)

        boundaries[family_id] = family_boundaries

    return boundaries


def identify_problematic_families(
    metrics: BoundaryQualityMetrics,
    max_fields_threshold: int = 15,
    low_confidence_threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Identify families with potential boundary detection issues.

    Args:
        metrics: Computed boundary quality metrics
        max_fields_threshold: Maximum reasonable field count
        low_confidence_threshold: Threshold for low confidence

    Returns:
        List of problematic families with issue descriptions
    """
    problematic = []

    for family_id, segment_count in metrics.family_segment_counts.items():
        issues = []

        # Check for over-segmentation
        if segment_count > max_fields_threshold:
            issues.append(f"over_segmented ({segment_count} fields)")

        # Check for low average confidence
        avg_conf = metrics.family_avg_confidences.get(family_id, 1.0)
        if avg_conf < low_confidence_threshold:
            issues.append(f"low_confidence ({avg_conf:.2f})")

        if issues:
            problematic.append({
                "family_id": family_id,
                "segment_count": segment_count,
                "avg_confidence": round(avg_conf, 4),
                "issues": issues,
            })

    # Sort by severity (most segments first)
    problematic.sort(key=lambda x: x["segment_count"], reverse=True)

    return problematic
