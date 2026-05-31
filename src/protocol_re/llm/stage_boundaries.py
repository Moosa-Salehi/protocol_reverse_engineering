"""
Stage 2: Boundary Refinement

LLM-assisted boundary refinement to reduce over-segmentation.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from protocol_re.llm.multi_stage import StageConfig, StageResult, LLMStage, load_prompt_template
from protocol_re.llm.analyze import LLMRequestConfig, call_openai_compatible_chat, extract_message_json
from protocol_re.model.schema import MessageRecord


def prepare_boundary_evidence(
    family_id: str,
    fields: List[Dict[str, Any]],
    messages: Sequence[MessageRecord],
    boundary_scores: Optional[List[Dict[str, Any]]] = None,
    family_stats: Optional[Dict[str, Any]] = None,
    max_samples: int = 10,
) -> Dict[str, Any]:
    """
    Prepare focused evidence bundle for boundary refinement of a single family.

    Args:
        family_id: Family identifier
        fields: Current field boundary hypotheses
        messages: Sample messages from this family
        boundary_scores: Statistical scores for each boundary
        family_stats: Family statistics (length distribution, etc.)
        max_samples: Maximum number of sample messages to include

    Returns:
        Evidence bundle for LLM analysis
    """
    # Sample messages (limit to avoid overwhelming LLM)
    sample_messages = []
    for msg in messages[:max_samples]:
        sample_messages.append({
            "msg_id": msg.msg_id,
            "payload_hex": msg.payload_hex,
            "length": msg.length,
        })

    evidence = {
        "family_id": family_id,
        "field_boundaries": fields,
        "sample_messages": sample_messages,
        "boundary_scores": boundary_scores or [],
        "family_statistics": family_stats or {},
    }

    return evidence


def render_boundary_prompt(evidence: Dict[str, Any], template_path: Optional[str] = None) -> str:
    """
    Render boundary refinement prompt with evidence.

    Args:
        evidence: Evidence bundle
        template_path: Path to prompt template (uses default if None)

    Returns:
        Rendered prompt string
    """
    if template_path:
        template = load_prompt_template(template_path)
    else:
        template = load_prompt_template("prompts/boundary_refinement.md")

    evidence_json = json.dumps(evidence, indent=2, ensure_ascii=False)
    return template + "\n\n## Evidence Bundle\n\n```json\n" + evidence_json + "\n```\n"


def validate_merge_suggestion(
    suggestion: Dict[str, Any],
    fields: List[Dict[str, Any]],
    boundary_scores: Optional[List[Dict[str, Any]]],
    min_confidence: float = 0.6,
) -> tuple[bool, str]:
    """
    Validate a field merge suggestion against statistical evidence.

    Args:
        suggestion: LLM merge suggestion
        fields: Current field definitions
        boundary_scores: Statistical boundary scores
        min_confidence: Minimum confidence threshold

    Returns:
        (is_valid, reason) tuple
    """
    # Check confidence threshold
    confidence = suggestion.get("confidence", 0.0)
    if confidence < min_confidence:
        return False, f"Confidence {confidence} below threshold {min_confidence}"

    # Check fields_to_merge are valid indices
    fields_to_merge = suggestion.get("fields_to_merge", [])
    if not fields_to_merge or len(fields_to_merge) < 2:
        return False, "Must merge at least 2 fields"

    for idx in fields_to_merge:
        if idx < 0 or idx >= len(fields):
            return False, f"Invalid field index {idx}"

    # Check fields are consecutive
    sorted_indices = sorted(fields_to_merge)
    for i in range(len(sorted_indices) - 1):
        if sorted_indices[i + 1] != sorted_indices[i] + 1:
            return False, "Fields to merge must be consecutive"

    # Check merged field definition is valid
    merged_field = suggestion.get("merged_field", {})
    if not merged_field:
        return False, "Missing merged_field definition"

    start = merged_field.get("start_offset")
    end = merged_field.get("end_offset")
    width = merged_field.get("width")

    if start is None or end is None or width is None:
        return False, "Merged field missing start_offset, end_offset, or width"

    if end <= start or width != (end - start):
        return False, f"Invalid merged field dimensions: start={start}, end={end}, width={width}"

    # Validate against boundary scores if available
    if boundary_scores:
        # Check that boundaries being removed have low scores
        evidence = suggestion.get("evidence", {})
        boundary_score_values = evidence.get("boundary_scores", [])
        if boundary_score_values:
            avg_score = sum(boundary_score_values) / len(boundary_score_values)
            if avg_score > 0.7:  # High boundary scores suggest strong boundaries
                return False, f"Boundary scores too high ({avg_score:.2f}) to merge"

    return True, "Valid merge suggestion"


def apply_merge_suggestions(
    fields: List[Dict[str, Any]],
    suggestions: List[Dict[str, Any]],
    min_confidence: float = 0.6,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Apply validated merge suggestions to field boundaries.

    Args:
        fields: Current field definitions
        suggestions: LLM merge suggestions
        min_confidence: Minimum confidence threshold

    Returns:
        (updated_fields, validation_log) tuple
    """
    validation_log = []
    applied_merges = []

    # Sort suggestions by confidence (highest first)
    sorted_suggestions = sorted(suggestions, key=lambda s: s.get("confidence", 0.0), reverse=True)

    for suggestion in sorted_suggestions:
        is_valid, reason = validate_merge_suggestion(suggestion, fields, None, min_confidence)

        log_entry = {
            "suggestion": suggestion,
            "valid": is_valid,
            "reason": reason,
        }

        if is_valid:
            applied_merges.append(suggestion)
            log_entry["applied"] = True
        else:
            log_entry["applied"] = False

        validation_log.append(log_entry)

    # Apply merges (process in reverse order to maintain indices)
    updated_fields = fields.copy()
    for suggestion in reversed(applied_merges):
        fields_to_merge = suggestion["fields_to_merge"]
        merged_field = suggestion["merged_field"]

        # Remove old fields
        for idx in sorted(fields_to_merge, reverse=True):
            if idx < len(updated_fields):
                updated_fields.pop(idx)

        # Insert merged field at the position of the first removed field
        insert_pos = min(fields_to_merge)
        updated_fields.insert(insert_pos, merged_field)

    return updated_fields, validation_log


def run_boundary_refinement_stage(
    family_id: str,
    fields: List[Dict[str, Any]],
    messages: Sequence[MessageRecord],
    config: StageConfig,
    llm_config: LLMRequestConfig,
    boundary_scores: Optional[List[Dict[str, Any]]] = None,
    family_stats: Optional[Dict[str, Any]] = None,
) -> StageResult:
    """
    Run boundary refinement stage for a single family.

    Args:
        family_id: Family identifier
        fields: Current field boundaries
        messages: Sample messages from family
        config: Stage configuration
        llm_config: LLM API configuration
        boundary_scores: Statistical boundary scores
        family_stats: Family statistics

    Returns:
        StageResult with suggestions and validation log
    """
    try:
        # Prepare evidence
        evidence = prepare_boundary_evidence(
            family_id, fields, messages, boundary_scores, family_stats
        )

        # Render prompt
        prompt = render_boundary_prompt(evidence, config.prompt_template_path)

        # Call LLM (or skip if render_only)
        if config.render_only:
            return StageResult(
                stage=LLMStage.BOUNDARY_REFINEMENT,
                success=True,
                suggestions=[],
                applied_count=0,
                rejected_count=0,
                validation_log=[],
                prompt=prompt,
                response=None,
            )

        response = call_openai_compatible_chat(prompt, llm_config)
        response_json = extract_message_json(response)

        # Extract suggestions
        suggestions = response_json.get("merge_suggestions", [])

        # Validate and apply suggestions
        updated_fields, validation_log = apply_merge_suggestions(
            fields, suggestions, config.min_confidence
        )

        applied_count = sum(1 for log in validation_log if log.get("applied", False))
        rejected_count = len(validation_log) - applied_count

        return StageResult(
            stage=LLMStage.BOUNDARY_REFINEMENT,
            success=True,
            suggestions=suggestions,
            applied_count=applied_count,
            rejected_count=rejected_count,
            validation_log=validation_log,
            prompt=prompt,
            response=json.dumps(response_json),
        )

    except Exception as e:
        return StageResult(
            stage=LLMStage.BOUNDARY_REFINEMENT,
            success=False,
            suggestions=[],
            applied_count=0,
            rejected_count=0,
            validation_log=[],
            prompt="",
            response=None,
            error=str(e),
        )
