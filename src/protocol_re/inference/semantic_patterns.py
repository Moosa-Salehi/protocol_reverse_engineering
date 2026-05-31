"""
Protocol-agnostic semantic pattern detection utilities.

This module provides utilities for detecting common protocol patterns,
propagating semantic labels across families, and resolving conflicting
semantic hypotheses.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

from protocol_re.inference.field_semantics import SemanticHypothesis


def detect_header_payload_structure(
    field_hypotheses: List[Dict[str, Any]],
    framing_summary: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Detect common header + payload pattern.

    Returns:
        Dictionary with:
        - header_end: offset where header ends
        - payload_start: offset where payload begins
        - header_fields: list of field indices in header
        - payload_fields: list of field indices in payload
    """
    result = {
        "header_end": None,
        "payload_start": None,
        "header_fields": [],
        "payload_fields": [],
    }

    # Use framing body_start as the boundary
    if framing_summary:
        for layout in framing_summary.get("layout_hypotheses", []):
            body_start = layout.get("body_start")
            if body_start is not None:
                result["header_end"] = body_start
                result["payload_start"] = body_start
                break

    # Classify fields as header or payload
    if result["header_end"] is not None:
        for idx, field in enumerate(field_hypotheses):
            start = field.get("start", 0)
            if start < result["header_end"]:
                result["header_fields"].append(idx)
            else:
                result["payload_fields"].append(idx)

    return result


def propagate_semantic_labels_across_families(
    all_family_semantics: Dict[str, List[SemanticHypothesis]],
    min_family_count: int = 3,
    confidence_boost: float = 0.1,
) -> Dict[str, List[SemanticHypothesis]]:
    """
    Propagate high-confidence semantic labels across families.

    If multiple families have the same field at the same offset with the same
    semantic role, boost confidence for weaker hypotheses.

    Args:
        all_family_semantics: Map of family_id -> list of semantic hypotheses
        min_family_count: Minimum families needed to propagate
        confidence_boost: Amount to boost confidence (default: 0.1)

    Returns:
        Updated family semantics with boosted confidence
    """
    # Collect semantic labels by (offset, length, role)
    label_votes: Dict[Tuple[int, int, str], List[Tuple[str, float]]] = defaultdict(list)

    for family_id, hypotheses in all_family_semantics.items():
        for hyp in hypotheses:
            key = (hyp.field_start, hyp.field_length, hyp.semantic_role)
            label_votes[key].append((family_id, hyp.confidence))

    # Find common labels across families
    common_labels = {}
    for key, votes in label_votes.items():
        if len(votes) >= min_family_count:
            avg_confidence = sum(conf for _, conf in votes) / len(votes)
            common_labels[key] = {
                "family_count": len(votes),
                "avg_confidence": avg_confidence,
                "families": [fid for fid, _ in votes],
            }

    # Boost confidence for fields matching common patterns
    updated_semantics = {}
    for family_id, hypotheses in all_family_semantics.items():
        updated_hyps = []
        for hyp in hypotheses:
            key = (hyp.field_start, hyp.field_length, hyp.semantic_role)
            if key in common_labels:
                common_info = common_labels[key]
                # Boost confidence if this family has lower confidence than average
                if hyp.confidence < common_info["avg_confidence"]:
                    new_confidence = min(0.95, hyp.confidence + confidence_boost)
                    hyp.confidence = new_confidence
                    hyp.evidence["cross_family_support"] = {
                        "family_count": common_info["family_count"],
                        "avg_confidence": round(common_info["avg_confidence"], 4),
                    }
            updated_hyps.append(hyp)
        updated_semantics[family_id] = updated_hyps

    return updated_semantics


def resolve_conflicting_hypotheses(
    hypotheses: List[SemanticHypothesis],
    max_hypotheses_per_field: int = 3,
    min_confidence: float = 0.5,
) -> List[SemanticHypothesis]:
    """
    Handle overlapping or conflicting semantic hypotheses.

    Strategy:
    1. Group hypotheses by field range (start, length)
    2. For each field, keep top N by confidence
    3. Remove redundant hypotheses (same role, overlapping range)
    4. Filter by minimum confidence threshold

    Args:
        hypotheses: List of semantic hypotheses
        max_hypotheses_per_field: Maximum hypotheses to keep per field
        min_confidence: Minimum confidence threshold

    Returns:
        Filtered and deduplicated list of hypotheses
    """
    if not hypotheses:
        return []

    # Filter by minimum confidence first
    hypotheses = [h for h in hypotheses if h.confidence >= min_confidence]

    # Group by field range
    field_groups: Dict[Tuple[int, int], List[SemanticHypothesis]] = defaultdict(list)
    for hyp in hypotheses:
        key = (hyp.field_start, hyp.field_length)
        field_groups[key].append(hyp)

    # Process each field group
    result = []
    for field_key, field_hyps in field_groups.items():
        # Sort by confidence (descending)
        field_hyps.sort(key=lambda h: h.confidence, reverse=True)

        # Deduplicate by semantic role (keep highest confidence)
        seen_roles = set()
        deduped = []
        for hyp in field_hyps:
            if hyp.semantic_role not in seen_roles:
                deduped.append(hyp)
                seen_roles.add(hyp.semantic_role)

        # Keep top N
        result.extend(deduped[:max_hypotheses_per_field])

    # Sort by field position, then confidence
    result.sort(key=lambda h: (h.field_start, -h.confidence))

    return result


def merge_overlapping_hypotheses(
    hypotheses: List[SemanticHypothesis],
) -> List[SemanticHypothesis]:
    """
    Merge overlapping hypotheses with the same semantic role.

    If two hypotheses have the same semantic role and overlapping ranges,
    merge them into a single hypothesis covering the union of both ranges.

    Args:
        hypotheses: List of semantic hypotheses

    Returns:
        List with overlapping hypotheses merged
    """
    if not hypotheses:
        return []

    # Group by semantic role
    role_groups: Dict[str, List[SemanticHypothesis]] = defaultdict(list)
    for hyp in hypotheses:
        role_groups[hyp.semantic_role].append(hyp)

    result = []
    for role, role_hyps in role_groups.items():
        # Sort by start position
        role_hyps.sort(key=lambda h: h.field_start)

        merged = []
        current = None

        for hyp in role_hyps:
            if current is None:
                current = hyp
            else:
                # Check if overlapping or adjacent
                current_end = current.field_start + current.field_length
                hyp_end = hyp.field_start + hyp.field_length

                if hyp.field_start <= current_end:
                    # Overlapping or adjacent - merge
                    new_start = min(current.field_start, hyp.field_start)
                    new_end = max(current_end, hyp_end)
                    new_length = new_end - new_start

                    # Use higher confidence
                    new_confidence = max(current.confidence, hyp.confidence)

                    # Merge evidence
                    merged_evidence = {**current.evidence, **hyp.evidence}
                    merged_evidence["merged"] = True

                    current = SemanticHypothesis(
                        field_start=new_start,
                        field_length=new_length,
                        semantic_role=role,
                        confidence=new_confidence,
                        evidence=merged_evidence,
                        encoding_type=current.encoding_type or hyp.encoding_type,
                    )
                else:
                    # Not overlapping - save current and start new
                    merged.append(current)
                    current = hyp

        if current is not None:
            merged.append(current)

        result.extend(merged)

    # Sort by field position
    result.sort(key=lambda h: h.field_start)

    return result


def detect_common_protocol_patterns(
    hypotheses: List[SemanticHypothesis],
) -> Dict[str, Any]:
    """
    Detect common protocol patterns in the semantic hypotheses.

    Patterns detected:
    - Request/response with transaction ID
    - Header with length field
    - Message type discriminator
    - Checksum/CRC at end

    Returns:
        Dictionary describing detected patterns
    """
    patterns = {
        "has_transaction_id": False,
        "has_length_field": False,
        "has_discriminator": False,
        "has_checksum": False,
        "has_payload": False,
        "pattern_confidence": 0.0,
    }

    role_counts = Counter(h.semantic_role for h in hypotheses)

    # Check for common patterns
    if "transaction_id" in role_counts:
        patterns["has_transaction_id"] = True

    if "length" in role_counts:
        patterns["has_length_field"] = True

    if "discriminator" in role_counts:
        patterns["has_discriminator"] = True

    if "checksum" in role_counts:
        patterns["has_checksum"] = True

    if "payload" in role_counts:
        patterns["has_payload"] = True

    # Calculate pattern confidence (how many common patterns detected)
    pattern_count = sum([
        patterns["has_transaction_id"],
        patterns["has_length_field"],
        patterns["has_discriminator"],
    ])
    patterns["pattern_confidence"] = round(pattern_count / 3.0, 4)

    return patterns


def validate_semantic_consistency(
    hypotheses: List[SemanticHypothesis],
) -> List[Dict[str, Any]]:
    """
    Validate semantic consistency and flag potential issues.

    Checks:
    - Multiple transaction IDs (unusual)
    - Multiple length fields (unusual)
    - Discriminator not in first few bytes (unusual)
    - Checksum not at end (unusual)

    Returns:
        List of validation warnings
    """
    warnings = []

    # Count semantic roles
    role_counts = Counter(h.semantic_role for h in hypotheses)

    # Check for multiple transaction IDs
    if role_counts.get("transaction_id", 0) > 1:
        warnings.append({
            "type": "multiple_transaction_ids",
            "message": f"Found {role_counts['transaction_id']} transaction ID fields (expected 0-1)",
            "severity": "warning",
        })

    # Check for multiple length fields
    if role_counts.get("length", 0) > 2:
        warnings.append({
            "type": "multiple_length_fields",
            "message": f"Found {role_counts['length']} length fields (expected 0-2)",
            "severity": "warning",
        })

    # Check discriminator position
    discriminators = [h for h in hypotheses if h.semantic_role == "discriminator"]
    for disc in discriminators:
        if disc.field_start > 8:
            warnings.append({
                "type": "late_discriminator",
                "message": f"Discriminator at offset {disc.field_start} (expected 0-8)",
                "severity": "info",
            })

    # Check checksum position
    checksums = [h for h in hypotheses if h.semantic_role == "checksum"]
    if checksums and hypotheses:
        last_offset = max(h.field_start + h.field_length for h in hypotheses)
        for cksum in checksums:
            cksum_end = cksum.field_start + cksum.field_length
            if cksum_end < last_offset - 4:
                warnings.append({
                    "type": "early_checksum",
                    "message": f"Checksum at offset {cksum.field_start} (expected near end)",
                    "severity": "info",
                })

    return warnings
