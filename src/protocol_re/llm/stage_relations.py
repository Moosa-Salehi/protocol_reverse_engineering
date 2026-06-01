"""
Stage 4: Relation Validation

LLM-assisted validation of request/response relations to filter false positives.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from protocol_re.llm.multi_stage import StageConfig, StageResult, LLMStage, load_prompt_template
from protocol_re.llm.analyze import LLMRequestConfig, call_openai_compatible_chat, extract_message_json


def prepare_relation_evidence(
    relations: List[Dict[str, Any]],
    family_summaries: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Prepare focused evidence bundle for relation validation.

    Args:
        relations: List of inferred relations with echo fields, length relations, edge features
        family_summaries: Brief statistics for each family involved

    Returns:
        Evidence bundle for LLM analysis
    """
    evidence = {
        "relations": relations,
        "family_summaries": family_summaries or {},
    }

    return evidence


def render_relation_prompt(evidence: Dict[str, Any], template_path: Optional[str] = None) -> str:
    """
    Render relation validation prompt with evidence.

    Args:
        evidence: Evidence bundle
        template_path: Path to prompt template (uses default if None)

    Returns:
        Rendered prompt string
    """
    if template_path:
        template = load_prompt_template(template_path)
    else:
        template = load_prompt_template("assets/prompts/relation_validation.md")

    evidence_json = json.dumps(evidence, indent=2, ensure_ascii=False)
    return template + "\n\n## Evidence Bundle\n\n```json\n" + evidence_json + "\n```\n"


def validate_relation_decision(
    decision: Dict[str, Any],
    relations: List[Dict[str, Any]],
    min_confidence: float = 0.7,
) -> tuple[bool, str]:
    """
    Validate a relation keep/discard decision against evidence.

    Args:
        decision: LLM relation validation decision
        relations: Original relations
        min_confidence: Minimum confidence threshold for keeping relations

    Returns:
        (is_valid, reason) tuple
    """
    # Check required fields
    request_family = decision.get("request_family_id")
    response_family = decision.get("response_family_id")
    action = decision.get("decision")
    confidence = decision.get("confidence", 0.0)

    if not request_family or not response_family:
        return False, "Missing request_family_id or response_family_id"

    if action not in ("keep", "discard"):
        return False, f"Invalid decision: {action} (must be 'keep' or 'discard')"

    # Check rationale is provided
    rationale = decision.get("rationale", "")
    if not rationale:
        return False, "Missing rationale"

    # Validate confidence threshold for "keep" decisions
    if action == "keep" and confidence < min_confidence:
        return False, f"Keep decision requires confidence >= {min_confidence}, got {confidence}"

    # Check that relation exists in original data
    relation_found = False
    for rel in relations:
        if (rel.get("request_family_id") == request_family and
            rel.get("response_family_id") == response_family):
            relation_found = True
            break

    if not relation_found:
        return False, f"Relation {request_family}->{response_family} not found in original data"

    return True, "Valid relation decision"


def apply_relation_validation(
    relations: List[Dict[str, Any]],
    decisions: List[Dict[str, Any]],
    min_confidence: float = 0.7,
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Apply validated relation decisions to filter relations.

    Args:
        relations: Original relations
        decisions: LLM validation decisions
        min_confidence: Minimum confidence threshold

    Returns:
        (filtered_relations, validation_log) tuple
    """
    validation_log = []
    kept_relations = []

    # Create decision map
    decision_map = {}
    for decision in decisions:
        is_valid, reason = validate_relation_decision(decision, relations, min_confidence)

        log_entry = {
            "decision": decision,
            "valid": is_valid,
            "reason": reason,
        }

        if is_valid:
            key = (decision["request_family_id"], decision["response_family_id"])
            decision_map[key] = decision
            log_entry["applied"] = True
        else:
            log_entry["applied"] = False

        validation_log.append(log_entry)

    # Filter relations based on decisions
    for relation in relations:
        req_family = relation.get("request_family_id")
        resp_family = relation.get("response_family_id")
        key = (req_family, resp_family)

        if key in decision_map:
            decision = decision_map[key]
            if decision["decision"] == "keep":
                # Add validation metadata to relation
                relation_copy = relation.copy()
                relation_copy["llm_validated"] = True
                relation_copy["llm_confidence"] = decision["confidence"]
                relation_copy["llm_rationale"] = decision["rationale"]
                kept_relations.append(relation_copy)
        else:
            # No LLM decision - keep by default (conservative)
            kept_relations.append(relation)

    return kept_relations, validation_log


def run_relation_validation_stage(
    relations: List[Dict[str, Any]],
    config: StageConfig,
    llm_config: LLMRequestConfig,
    family_summaries: Optional[Dict[str, Dict[str, Any]]] = None,
) -> StageResult:
    """
    Run relation validation stage.

    Args:
        relations: Inferred relations to validate
        config: Stage configuration
        llm_config: LLM API configuration
        family_summaries: Brief statistics for families

    Returns:
        StageResult with validation decisions and log
    """
    try:
        # Prepare evidence
        evidence = prepare_relation_evidence(relations, family_summaries)

        # Render prompt
        prompt = render_relation_prompt(evidence, config.prompt_template_path)

        # Call LLM (or skip if render_only)
        if config.render_only:
            return StageResult(
                stage=LLMStage.RELATION_VALIDATION,
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

        # Extract decisions
        decisions = response_json.get("validated_relations", [])

        # Apply validation
        filtered_relations, validation_log = apply_relation_validation(
            relations, decisions, config.min_confidence
        )

        applied_count = sum(1 for log in validation_log if log.get("applied", False))
        rejected_count = len(validation_log) - applied_count

        # Count kept vs discarded
        kept_count = sum(1 for d in decisions if d.get("decision") == "keep")
        discarded_count = sum(1 for d in decisions if d.get("decision") == "discard")

        return StageResult(
            stage=LLMStage.RELATION_VALIDATION,
            success=True,
            suggestions=decisions,
            applied_count=kept_count,
            rejected_count=discarded_count,
            validation_log=validation_log,
            prompt=prompt,
            response=json.dumps(response_json),
        )

    except Exception as e:
        return StageResult(
            stage=LLMStage.RELATION_VALIDATION,
            success=False,
            suggestions=[],
            applied_count=0,
            rejected_count=0,
            validation_log=[],
            prompt="",
            response=None,
            error=str(e),
        )
