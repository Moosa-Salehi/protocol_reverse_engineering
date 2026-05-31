"""
LLM-assisted boundary refinement for reducing over-segmentation.

This module provides:
1. Export boundary candidates with scores for LLM review
2. Generate prompts for LLM to identify over-segmentation
3. Parse and validate LLM suggestions
4. Apply validated merge suggestions
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

from protocol_re.model.schema import Segment
from protocol_re.utils.bytes import hex_to_bytes


@dataclass
class MergeSuggestion:
    """A suggestion to merge adjacent segments."""

    family_id: str
    segment_indices: List[int]  # Indices of segments to merge
    reason: str
    confidence: float
    statistical_support: Optional[Dict[str, Any]] = None


@dataclass
class RefinementResult:
    """Result of LLM-assisted boundary refinement."""

    original_segment_count: int
    refined_segment_count: int
    merge_suggestions: List[MergeSuggestion]
    applied_merges: List[MergeSuggestion]
    rejected_merges: List[Tuple[MergeSuggestion, str]]  # (suggestion, rejection_reason)
    refined_segments: List[Segment]


def export_boundaries_for_llm(
    family_id: str,
    segments: List[Segment],
    messages_hex: Sequence[str],
    max_sample_messages: int = 5,
) -> Dict[str, Any]:
    """
    Export boundary information in a format suitable for LLM review.

    Args:
        family_id: Family identifier
        segments: Detected segments
        messages_hex: Sample messages from the family
        max_sample_messages: Maximum number of sample messages to include

    Returns:
        Dictionary with boundary information for LLM
    """
    # Sample messages
    sample_messages = list(messages_hex[:max_sample_messages])
    messages = [hex_to_bytes(msg) for msg in sample_messages]

    # Build segment information
    segment_info = []
    for idx, seg in enumerate(segments):
        # Extract values from sample messages
        values = [msg[seg.start:seg.end].hex() for msg in messages if len(msg) >= seg.end]
        unique_values = list(set(values))

        segment_info.append({
            "index": idx,
            "start": seg.start,
            "end": seg.end,
            "width": seg.end - seg.start,
            "kind": seg.kind,
            "confidence": seg.confidence,
            "sample_values": values[:5],  # First 5 values
            "unique_value_count": len(unique_values),
            "evidence": seg.evidence,
        })

    # Build message visualization
    message_viz = []
    for msg_hex in sample_messages:
        msg = hex_to_bytes(msg_hex)
        # Create field-by-field breakdown
        fields = []
        for idx, seg in enumerate(segments):
            if len(msg) >= seg.end:
                value = msg[seg.start:seg.end].hex()
                fields.append({
                    "field_index": idx,
                    "value": value,
                    "width": seg.end - seg.start,
                })
        message_viz.append({
            "hex": msg_hex,
            "fields": fields,
        })

    return {
        "family_id": family_id,
        "segment_count": len(segments),
        "segments": segment_info,
        "sample_messages": message_viz,
        "statistics": {
            "total_segments": len(segments),
            "single_byte_segments": sum(1 for s in segments if (s.end - s.start) == 1),
            "constant_segments": sum(1 for s in segments if s.kind == "constant"),
            "variable_segments": sum(1 for s in segments if s.kind == "variable"),
            "avg_confidence": sum(s.confidence for s in segments) / len(segments) if segments else 0.0,
        }
    }


def generate_refinement_prompt(boundary_export: Dict[str, Any]) -> str:
    """
    Generate a prompt for LLM to review boundaries and suggest merges.

    Args:
        boundary_export: Boundary information from export_boundaries_for_llm

    Returns:
        Prompt string for LLM
    """
    family_id = boundary_export["family_id"]
    segment_count = boundary_export["segment_count"]
    stats = boundary_export["statistics"]

    prompt = f"""Review the following field boundary detection for protocol family '{family_id}'.

**Statistics:**
- Total segments: {stats['total_segments']}
- Single-byte segments: {stats['single_byte_segments']}
- Constant segments: {stats['constant_segments']}
- Variable segments: {stats['variable_segments']}
- Average confidence: {stats['avg_confidence']:.4f}

**Detected Segments:**
"""

    # Add segment details
    for seg in boundary_export["segments"]:
        prompt += f"\nSegment {seg['index']}: bytes {seg['start']}-{seg['end']} (width={seg['width']})\n"
        prompt += f"  Kind: {seg['kind']}, Confidence: {seg['confidence']:.4f}\n"
        prompt += f"  Unique values: {seg['unique_value_count']}\n"
        prompt += f"  Sample values: {', '.join(seg['sample_values'][:3])}\n"

    prompt += "\n**Sample Messages (field-by-field):**\n"

    # Add message visualization
    for idx, msg in enumerate(boundary_export["sample_messages"][:3]):
        prompt += f"\nMessage {idx + 1}:\n"
        field_strs = []
        for field in msg["fields"]:
            field_strs.append(f"[{field['field_index']}:{field['value']}]")
        prompt += "  " + " ".join(field_strs) + "\n"

    prompt += """
**Task:**
Identify segments that should be merged to reduce over-segmentation. Look for:
1. Adjacent single-byte fields that likely belong together
2. Adjacent constant fields
3. Adjacent fields with similar characteristics (both variable, low confidence)
4. Fields that would make more sense as standard widths (2, 4 bytes)

**Output Format (JSON):**
```json
{
  "merge_suggestions": [
    {
      "segment_indices": [0, 1, 2],
      "reason": "Three consecutive single-byte fields with low confidence should be merged into one 3-byte field",
      "confidence": 0.8
    }
  ]
}
```

Provide your analysis as valid JSON only. If no merges are needed, return an empty merge_suggestions array.
"""

    return prompt


def parse_llm_response(response: str) -> List[Dict[str, Any]]:
    """
    Parse LLM response to extract merge suggestions.

    Args:
        response: LLM response text

    Returns:
        List of merge suggestion dictionaries
    """
    # Try to extract JSON from response
    try:
        # Look for JSON code block
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
        else:
            # Try to parse entire response as JSON
            json_str = response.strip()

        data = json.loads(json_str)
        return data.get("merge_suggestions", [])

    except (json.JSONDecodeError, ValueError) as e:
        # Failed to parse - return empty list
        return []


def validate_merge_suggestion(
    suggestion: Dict[str, Any],
    segments: List[Segment],
    messages_hex: Sequence[str],
    min_confidence: float = 0.6,
) -> Tuple[bool, Optional[str]]:
    """
    Validate a merge suggestion against statistical evidence.

    Args:
        suggestion: Merge suggestion from LLM
        segments: Current segments
        messages_hex: Messages for validation
        min_confidence: Minimum confidence threshold for suggestion

    Returns:
        (is_valid, rejection_reason) tuple
    """
    indices = suggestion.get("segment_indices", [])
    confidence = suggestion.get("confidence", 0.0)

    # Basic validation
    if not indices or len(indices) < 2:
        return False, "Must merge at least 2 segments"

    if confidence < min_confidence:
        return False, f"Confidence {confidence:.2f} below threshold {min_confidence}"

    # Check indices are valid
    if any(idx < 0 or idx >= len(segments) for idx in indices):
        return False, "Invalid segment indices"

    # Check segments are adjacent
    sorted_indices = sorted(indices)
    for i in range(len(sorted_indices) - 1):
        if sorted_indices[i + 1] != sorted_indices[i] + 1:
            return False, "Segments must be adjacent"

    # Check segments are actually adjacent in byte positions
    for i in range(len(sorted_indices) - 1):
        seg1 = segments[sorted_indices[i]]
        seg2 = segments[sorted_indices[i + 1]]
        if seg1.end != seg2.start:
            return False, "Segments are not contiguous in byte positions"

    # Statistical validation: check if merge makes sense
    merged_segments = [segments[idx] for idx in sorted_indices]
    messages = [hex_to_bytes(msg) for msg in messages_hex]

    # Check if all segments have similar characteristics
    kinds = [seg.kind for seg in merged_segments]
    confidences = [seg.confidence for seg in merged_segments]

    # Allow merge if:
    # 1. All are constants
    # 2. All are single-byte
    # 3. All have low confidence (<0.7)
    # 4. Combined width is standard (2, 4 bytes)

    all_constants = all(k == "constant" for k in kinds)
    all_single_byte = all((seg.end - seg.start) == 1 for seg in merged_segments)
    all_low_confidence = all(c < 0.7 for c in confidences)

    start = merged_segments[0].start
    end = merged_segments[-1].end
    combined_width = end - start
    standard_width = combined_width in (2, 4, 8)

    if all_constants:
        return True, None  # Always allow merging constants

    if all_single_byte and (all_low_confidence or standard_width):
        return True, None  # Allow merging single-byte fields with low confidence or to standard width

    if all_low_confidence and standard_width:
        return True, None  # Allow merging low-confidence fields to standard width

    # Otherwise, require strong justification
    if confidence >= 0.85:
        return True, None  # High confidence from LLM overrides

    return False, "Insufficient statistical support for merge"


def apply_merge_suggestions(
    segments: List[Segment],
    suggestions: List[MergeSuggestion],
) -> List[Segment]:
    """
    Apply validated merge suggestions to segments.

    Args:
        segments: Original segments
        suggestions: Validated merge suggestions to apply

    Returns:
        New list of segments with merges applied
    """
    if not suggestions:
        return segments

    # Build a map of which segments to merge
    merge_groups: Dict[int, List[int]] = {}  # leader_index -> [all indices in group]

    for suggestion in suggestions:
        indices = sorted(suggestion.segment_indices)
        leader = indices[0]
        merge_groups[leader] = indices

    # Build new segment list
    new_segments: List[Segment] = []
    skip_indices = set()

    for idx, seg in enumerate(segments):
        if idx in skip_indices:
            continue

        if idx in merge_groups:
            # This is a merge leader - merge all segments in the group
            group_indices = merge_groups[idx]
            merged_seg = _merge_segment_group(
                [segments[i] for i in group_indices],
                segments,
                group_indices,
            )
            new_segments.append(merged_seg)

            # Mark other segments in group as processed
            skip_indices.update(group_indices[1:])
        else:
            # Not part of any merge - keep as is
            new_segments.append(seg)

    return new_segments


def _merge_segment_group(
    group_segments: List[Segment],
    all_segments: List[Segment],
    group_indices: List[int],
) -> Segment:
    """Merge a group of segments into one."""
    start = group_segments[0].start
    end = group_segments[-1].end

    # Determine merged kind
    kinds = [seg.kind for seg in group_segments]
    if all(k == "constant" for k in kinds):
        merged_kind = "constant"
    elif all(k == "variable" for k in kinds):
        merged_kind = "variable"
    else:
        # Mixed - prefer variable
        merged_kind = "variable"

    # Merged confidence is minimum of all confidences, with slight penalty
    merged_confidence = min(seg.confidence for seg in group_segments) * 0.95

    # Merge evidence
    merged_evidence = {
        "merged_by_llm": True,
        "original_segment_count": len(group_segments),
        "original_indices": group_indices,
        "merge_reason": "llm_suggestion",
    }

    # Include evidence from original segments
    for idx, seg in enumerate(group_segments):
        merged_evidence[f"original_{idx}_evidence"] = seg.evidence

    return Segment(
        start=start,
        end=end,
        kind=merged_kind,
        confidence=round(merged_confidence, 4),
        evidence=merged_evidence,
    )


def refine_boundaries_with_llm(
    family_id: str,
    segments: List[Segment],
    messages_hex: Sequence[str],
    llm_response: str,
    min_suggestion_confidence: float = 0.6,
) -> RefinementResult:
    """
    Refine boundaries using LLM suggestions.

    Args:
        family_id: Family identifier
        segments: Original segments
        messages_hex: Messages for validation
        llm_response: Response from LLM
        min_suggestion_confidence: Minimum confidence for suggestions

    Returns:
        RefinementResult with applied and rejected suggestions
    """
    original_count = len(segments)

    # Parse LLM response
    raw_suggestions = parse_llm_response(llm_response)

    # Convert to MergeSuggestion objects and validate
    merge_suggestions: List[MergeSuggestion] = []
    applied_merges: List[MergeSuggestion] = []
    rejected_merges: List[Tuple[MergeSuggestion, str]] = []

    for raw_sug in raw_suggestions:
        suggestion = MergeSuggestion(
            family_id=family_id,
            segment_indices=raw_sug.get("segment_indices", []),
            reason=raw_sug.get("reason", ""),
            confidence=raw_sug.get("confidence", 0.0),
        )

        # Validate suggestion
        is_valid, rejection_reason = validate_merge_suggestion(
            raw_sug,
            segments,
            messages_hex,
            min_confidence=min_suggestion_confidence,
        )

        merge_suggestions.append(suggestion)

        if is_valid:
            applied_merges.append(suggestion)
        else:
            rejected_merges.append((suggestion, rejection_reason or "Unknown reason"))

    # Apply validated merges
    refined_segments = apply_merge_suggestions(segments, applied_merges)

    return RefinementResult(
        original_segment_count=original_count,
        refined_segment_count=len(refined_segments),
        merge_suggestions=merge_suggestions,
        applied_merges=applied_merges,
        rejected_merges=rejected_merges,
        refined_segments=refined_segments,
    )


def format_refinement_summary(result: RefinementResult) -> str:
    """
    Format refinement result as human-readable summary.

    Args:
        result: Refinement result

    Returns:
        Summary string
    """
    lines = [
        "=== LLM Boundary Refinement Summary ===",
        f"Original segments: {result.original_segment_count}",
        f"Refined segments: {result.refined_segment_count}",
        f"Reduction: {result.original_segment_count - result.refined_segment_count} segments",
        "",
        f"Total suggestions: {len(result.merge_suggestions)}",
        f"Applied: {len(result.applied_merges)}",
        f"Rejected: {len(result.rejected_merges)}",
    ]

    if result.applied_merges:
        lines.append("\nApplied Merges:")
        for merge in result.applied_merges:
            lines.append(f"  - Segments {merge.segment_indices}: {merge.reason}")
            lines.append(f"    Confidence: {merge.confidence:.2f}")

    if result.rejected_merges:
        lines.append("\nRejected Merges:")
        for merge, reason in result.rejected_merges:
            lines.append(f"  - Segments {merge.segment_indices}: {merge.reason}")
            lines.append(f"    Rejection: {reason}")

    return "\n".join(lines)
