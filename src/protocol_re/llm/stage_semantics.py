"""
Stage 3: Semantic Labeling

LLM-assisted semantic field labeling based on statistical evidence.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence

from protocol_re.llm.multi_stage import StageConfig, StageResult, LLMStage, load_prompt_template
from protocol_re.llm.analyze import LLMAPIError, LLMRequestConfig, call_openai_compatible_chat_with_raw, extract_message_json
from protocol_re.llm.stage_errors import LLM_API_ERROR_CATEGORY
from protocol_re.llm.evidence_builders import build_field_statistics, build_sample_values
from protocol_re.model.schema import MessageRecord


def prepare_semantic_evidence(
    family_id: str,
    fields: List[Dict[str, Any]],
    field_statistics: Optional[Dict[str, Any]] = None,
    relations: Optional[List[Dict[str, Any]]] = None,
    family_role: Optional[str] = None,
    sample_values: Optional[List[List[Any]]] = None,
    messages: Sequence[MessageRecord] = (),
    family_features: Optional[Dict[str, Any]] = None,
    segments: Sequence[Dict[str, Any]] = (),
) -> Dict[str, Any]:
    """
    Prepare focused evidence bundle for semantic labeling of a single family.

    Args:
        family_id: Family identifier
        fields: Field definitions with offsets and widths
        field_statistics: Per-field cardinality, entropy, stability, etc.
        relations: Request/response relations involving this family
        family_role: "request", "response", or "unknown"
        sample_values: Sample field values from representative messages

    Returns:
        Evidence bundle for LLM analysis
    """
    derived_statistics = field_statistics or build_field_statistics(fields, messages, family_features, segments)
    derived_samples = sample_values or build_sample_values(fields, messages)
    evidence = {
        "family_id": family_id,
        "fields": fields,
        "field_statistics": derived_statistics,
        "relations": relations or [],
        "family_role": family_role or "unknown",
        "sample_values": derived_samples,
    }

    return evidence


def render_semantic_prompt(evidence: Dict[str, Any], template_path: Optional[str] = None) -> str:
    """
    Render semantic labeling prompt with evidence.

    Args:
        evidence: Evidence bundle
        template_path: Path to prompt template (uses default if None)

    Returns:
        Rendered prompt string
    """
    if template_path:
        template = load_prompt_template(template_path)
    else:
        template = load_prompt_template("assets/prompts/semantic_labeling.md")

    evidence_json = json.dumps(evidence, indent=2, ensure_ascii=False)
    return template + "\n\n## Evidence Bundle\n\n```json\n" + evidence_json + "\n```\n"


def validate_semantic_label(
    label: Dict[str, Any],
    fields: List[Dict[str, Any]],
    field_statistics: Optional[Dict[str, Any]],
    min_confidence: float = 0.5,
) -> tuple[bool, str]:
    """
    Validate a semantic label suggestion against statistical evidence.

    Args:
        label: LLM semantic label suggestion
        fields: Field definitions
        field_statistics: Statistical evidence for fields
        min_confidence: Minimum confidence threshold

    Returns:
        (is_valid, reason) tuple
    """
    # Check confidence threshold
    confidence = label.get("confidence", 0.0)
    if confidence < min_confidence:
        return False, f"Confidence {confidence} below threshold {min_confidence}"

    # Check field_index is valid
    field_index = label.get("field_index")
    if field_index is None or field_index < 0 or field_index >= len(fields):
        return False, f"Invalid field_index {field_index}"

    # Check semantic_role is provided
    semantic_role = label.get("semantic_role")
    if not semantic_role:
        return False, "Missing semantic_role"

    # Check evidence is provided
    evidence = label.get("evidence", [])
    if not evidence or len(evidence) < 1:
        return False, "Insufficient evidence (need at least 1 evidence item)"

    # Validate semantic role is from known taxonomy
    valid_roles = {
        "discriminator", "opcode", "function_code",
        "length", "byte_count",
        "transaction_id", "correlation_id",
        "sequence_number", "counter",
        "address", "unit_id", "device_id",
        "quantity", "count",
        "status", "error_code",
        "flags", "bitfield",
        "payload", "data", "value",
        "checksum", "crc",
        "constant", "reserved", "padding",
        "timestamp",
    }

    if semantic_role not in valid_roles:
        return False, f"Unknown semantic role: {semantic_role}"

    # Validate against field statistics if available
    if field_statistics:
        field_key = f"field_{field_index}"
        field_stats = field_statistics.get(field_key, {})

        # Basic sanity checks based on role
        cardinality = field_stats.get("cardinality", 0)
        offset = label.get("offset", 0)
        width = label.get("width", 0)

        # Discriminator/opcode should have low cardinality
        if semantic_role in ("discriminator", "opcode", "function_code"):
            if cardinality > 256:
                return False, f"Discriminator has too high cardinality ({cardinality})"

        # Transaction ID should have high cardinality
        if semantic_role in ("transaction_id", "correlation_id"):
            if cardinality < 10:
                return False, f"Transaction ID has too low cardinality ({cardinality})"

        # Constant should have cardinality = 1
        if semantic_role in ("constant", "reserved", "padding"):
            if cardinality > 3:
                return False, f"Constant field has too high cardinality ({cardinality})"

    return True, "Valid semantic label"


def apply_semantic_labels(
    fields: List[Dict[str, Any]],
    labels: List[Dict[str, Any]],
    min_confidence: float = 0.5,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Apply validated semantic labels to fields.

    Args:
        fields: Current field definitions
        labels: LLM semantic label suggestions
        min_confidence: Minimum confidence threshold

    Returns:
        (updated_fields, validation_log) tuple
    """
    validation_log = []
    applied_labels = []

    # Sort labels by confidence (highest first)
    sorted_labels = sorted(labels, key=lambda l: l.get("confidence", 0.0), reverse=True)

    for label in sorted_labels:
        is_valid, reason = validate_semantic_label(label, fields, None, min_confidence)

        log_entry = {
            "label": label,
            "valid": is_valid,
            "reason": reason,
        }

        if is_valid:
            applied_labels.append(label)
            log_entry["applied"] = True
        else:
            log_entry["applied"] = False

        validation_log.append(log_entry)

    # Apply labels to fields
    updated_fields = [field.copy() for field in fields]
    for label in applied_labels:
        field_index = label["field_index"]
        if field_index < len(updated_fields):
            updated_fields[field_index]["semantic_role"] = label["semantic_role"]
            updated_fields[field_index]["semantic_confidence"] = label["confidence"]
            updated_fields[field_index]["semantic_evidence"] = label.get("evidence", [])

    return updated_fields, validation_log


def run_semantic_labeling_stage(
    family_id: str,
    fields: List[Dict[str, Any]],
    config: StageConfig,
    llm_config: LLMRequestConfig,
    cached_response: Optional[str] = None,
    field_statistics: Optional[Dict[str, Any]] = None,
    relations: Optional[List[Dict[str, Any]]] = None,
    family_role: Optional[str] = None,
    messages: Sequence[MessageRecord] = (),
    sample_values: Optional[List[List[Any]]] = None,
    family_features: Optional[Dict[str, Any]] = None,
    segments: Sequence[Dict[str, Any]] = (),
) -> StageResult:
    """
    Run semantic labeling stage for a single family.

    Args:
        family_id: Family identifier
        fields: Field definitions
        config: Stage configuration
        llm_config: LLM API configuration
        field_statistics: Statistical evidence for fields
        relations: Request/response relations
        family_role: "request", "response", or "unknown"

    Returns:
        StageResult with suggestions and validation log
    """
    prompt = ""
    try:
        # Prepare evidence
        evidence = prepare_semantic_evidence(
            family_id,
            fields,
            field_statistics,
            relations,
            family_role,
            sample_values,
            messages,
            family_features,
            segments,
        )

        # Render prompt
        prompt = render_semantic_prompt(evidence, config.prompt_template_path)

        # Call LLM (or skip if render_only)
        if config.render_only:
            return StageResult(
                stage=LLMStage.SEMANTIC_LABELING,
                success=True,
                suggestions=[],
                applied_count=0,
                rejected_count=0,
                validation_log=[],
                prompt=prompt,
                response=None,
            )

        if cached_response is not None:
            raw_response = cached_response
            response = json.loads(cached_response)
        else:
            response, raw_response = call_openai_compatible_chat_with_raw(
                prompt,
                llm_config,
                request_label=f"stage 11b semantic labeling for {family_id}",
            )
        response_json = extract_message_json(response)

        # Extract suggestions
        labels = response_json.get("semantic_labels", [])

        # Validate and apply labels
        updated_fields, validation_log = apply_semantic_labels(
            fields, labels, config.min_confidence
        )

        applied_count = sum(1 for log in validation_log if log.get("applied", False))
        rejected_count = len(validation_log) - applied_count

        return StageResult(
            stage=LLMStage.SEMANTIC_LABELING,
            success=True,
            suggestions=labels,
            applied_count=applied_count,
            rejected_count=rejected_count,
            validation_log=validation_log,
            prompt=prompt,
            response=raw_response,
        )

    except LLMAPIError as e:
        return StageResult(
            stage=LLMStage.SEMANTIC_LABELING,
            success=False,
            suggestions=[],
            applied_count=0,
            rejected_count=0,
            validation_log=[],
            prompt=prompt,
            response=None,
            error=f"{e.category}: {e}",
            error_category=LLM_API_ERROR_CATEGORY,
        )

    except Exception as e:
        return StageResult(
            stage=LLMStage.SEMANTIC_LABELING,
            success=False,
            suggestions=[],
            applied_count=0,
            rejected_count=0,
            validation_log=[],
            prompt="",
            response=None,
            error=str(e),
        )
