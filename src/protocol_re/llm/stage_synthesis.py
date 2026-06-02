"""
Stage 5: Protocol Structure Synthesis

LLM-assisted protocol specification synthesis from refined model.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from protocol_re.llm.multi_stage import StageConfig, StageResult, LLMStage, load_prompt_template
from protocol_re.llm.analyze import LLMRequestConfig, call_openai_compatible_chat, extract_message_json
from protocol_re.llm.evidence_builders import summarize_stage_artifact


def estimate_tokens(text: str) -> int:
    """
    Rough token estimation (1 token ≈ 4 characters for English text).
    This is a conservative estimate.
    """
    return len(text) // 4


def prepare_synthesis_evidence(
    protocol_model: Dict[str, Any],
    boundary_summary: Optional[Dict[str, Any]] = None,
    semantic_summary: Optional[Dict[str, Any]] = None,
    relation_summary: Optional[Dict[str, Any]] = None,
    evaluation_metrics: Optional[Dict[str, Any]] = None,
    max_families: int = 10,
    max_relations: int = 10,
) -> Dict[str, Any]:
    """
    Prepare compact evidence bundle for protocol synthesis.

    Keeps evidence under ~3K tokens to leave room for prompt template (~2K tokens).

    Args:
        protocol_model: Full protocol model
        boundary_summary: Summary from stage 07b
        semantic_summary: Summary from stage 11b
        relation_summary: Summary from stage 10b
        evaluation_metrics: Pipeline quality metrics
        max_families: Maximum families to include (top N by message count)
        max_relations: Maximum relations to include

    Returns:
        Compact evidence bundle
    """
    # Extract compact family summaries (top N by message count)
    families = protocol_model.get("families", [])
    families_sorted = sorted(families, key=lambda f: f.get("message_count", 0), reverse=True)

    compact_families = []
    for family in families_sorted[:max_families]:
        fields = family.get("fields") or family.get("field_hypotheses", [])
        compact_fields = []

        for field in fields[:8]:
            evidence = field.get("evidence", {}) or {}
            attributes = field.get("attributes", {}) or {}
            compact_field = {
                "offset": field.get("start", field.get("start_offset", field.get("offset", 0))),
                "width": field.get("length", field.get("width", 1)),
                "field_type": field.get("field_type", "unknown"),
                "semantic_role": field.get("semantic_role", attributes.get("semantic_role", "unknown")),
                "confidence": field.get("confidence"),
            }
            if "semantic_confidence" in field:
                compact_field["semantic_confidence"] = field["semantic_confidence"]
            if field.get("endian"):
                compact_field["endian"] = field.get("endian")
            if evidence:
                selected_evidence = {
                    key: evidence[key]
                    for key in ("unique_values", "length_match_score", "cardinality_ratio")
                    if key in evidence
                }
                if selected_evidence:
                    compact_field["evidence"] = selected_evidence
            if attributes.get("value_hex"):
                compact_field["constant_value_hex"] = attributes["value_hex"]
            compact_fields.append(compact_field)

        compact_families.append({
            "family_id": family.get("family_id"),
            "role": family.get("role", "unknown"),
            "message_count": family.get("message_count", 0),
            "avg_length": (
                family.get("statistics", {}).get("avg_length")
                or family.get("feature_summary", {}).get("length_stats", {}).get("mean")
                or 0
            ),
            "template": family.get("template", ""),
            "fields": compact_fields,
        })

    # Extract compact relation summaries (top N by pair count). The protocol model
    # stores relations as a list of family edges, but older artifacts nested them
    # under {"family_edges": [...]} — accept both shapes.
    relations_obj = protocol_model.get("relations", [])
    if isinstance(relations_obj, dict):
        relations = relations_obj.get("family_edges", []) or []
    else:
        relations = relations_obj or []
    relations_sorted = sorted(relations, key=lambda r: r.get("pair_count", 0), reverse=True)

    compact_relations = []
    for relation in relations_sorted[:max_relations]:
        compact_relation = {
            "request_family": relation.get("request_family_id"),
            "response_family": relation.get("response_family_id"),
            "pair_count": relation.get("pair_count", 0),
            "validated": relation.get("llm_validated", False),
        }

        # Add echo fields if present
        echo_fields = relation.get("echo_fields", [])
        if echo_fields:
            compact_relation["echo_fields"] = [
                {"offset": e.get("request_offset"), "width": e.get("width")}
                for e in echo_fields[:2]  # Top 2 echo fields only
            ]

        compact_relations.append(compact_relation)

    # Build compact evidence
    evidence = {
        "protocol_model": {
            "total_families": len(families),
            "total_messages": protocol_model.get("metadata", {}).get("total_messages")
            or sum(int(family.get("message_count", 0) or 0) for family in families),
            "families": compact_families,
            "relations": compact_relations,
        }
    }

    # Add multi-stage summaries if available
    if boundary_summary:
        evidence["boundary_refinement_summary"] = summarize_stage_artifact(boundary_summary, "boundary") or {
            "total_families": boundary_summary.get("total_families", 0),
            "total_applied": boundary_summary.get("total_applied", 0),
            "total_rejected": boundary_summary.get("total_rejected", 0),
        }

    if semantic_summary:
        evidence["semantic_labeling_summary"] = summarize_stage_artifact(semantic_summary, "semantic") or {
            "total_families": semantic_summary.get("total_families", 0),
            "total_labels_applied": semantic_summary.get("total_labels_applied", 0),
            "total_labels_rejected": semantic_summary.get("total_labels_rejected", 0),
        }

    if relation_summary:
        evidence["relation_validation_summary"] = summarize_stage_artifact(relation_summary, "relation") or {
            "original_count": relation_summary.get("original_count", 0),
            "kept_count": relation_summary.get("kept_count", 0),
            "discarded_count": relation_summary.get("discarded_count", 0),
        }

    if evaluation_metrics:
        evidence["evaluation_metrics"] = {
            "message_type_recall": evaluation_metrics.get("message_type_matching", {}).get("recall", 0),
            "boundary_precision": evaluation_metrics.get("field_boundaries", {}).get("precision", 0),
            "boundary_recall": evaluation_metrics.get("field_boundaries", {}).get("recall", 0),
            "relation_precision": evaluation_metrics.get("relations", {}).get("precision", 0),
            "relation_recall": evaluation_metrics.get("relations", {}).get("recall", 0),
        }

    return evidence


def render_synthesis_prompt(evidence: Dict[str, Any], template_path: Optional[str] = None) -> str:
    """
    Render protocol synthesis prompt with evidence.

    Args:
        evidence: Compact evidence bundle
        template_path: Path to prompt template (uses default if None)

    Returns:
        Rendered prompt string
    """
    if template_path:
        template = load_prompt_template(template_path)
    else:
        template = load_prompt_template("assets/prompts/protocol_synthesis.md")

    evidence_json = json.dumps(evidence, indent=2, ensure_ascii=False)
    prompt = template + "\n\n## Evidence Bundle\n\n```json\n" + evidence_json + "\n```\n"

    # Check token estimate
    estimated_tokens = estimate_tokens(prompt)
    if estimated_tokens > 5000:
        print(f"[!] Warning: Prompt estimated at {estimated_tokens} tokens (target: <5000)")

    return prompt


def split_families_for_synthesis(
    families: List[Dict[str, Any]],
    max_families_per_chunk: int = 5,
) -> List[List[Dict[str, Any]]]:
    """
    Split families into chunks for multi-prompt synthesis if needed.

    Args:
        families: List of family summaries
        max_families_per_chunk: Maximum families per chunk

    Returns:
        List of family chunks
    """
    chunks = []
    for i in range(0, len(families), max_families_per_chunk):
        chunks.append(families[i:i + max_families_per_chunk])
    return chunks


def run_protocol_synthesis_stage(
    protocol_model: Dict[str, Any],
    config: StageConfig,
    llm_config: LLMRequestConfig,
    boundary_summary: Optional[Dict[str, Any]] = None,
    semantic_summary: Optional[Dict[str, Any]] = None,
    relation_summary: Optional[Dict[str, Any]] = None,
    evaluation_metrics: Optional[Dict[str, Any]] = None,
) -> StageResult:
    """
    Run protocol synthesis stage.

    Args:
        protocol_model: Refined protocol model
        config: Stage configuration
        llm_config: LLM API configuration
        boundary_summary: Summary from stage 07b
        semantic_summary: Summary from stage 11b
        relation_summary: Summary from stage 10b
        evaluation_metrics: Pipeline quality metrics

    Returns:
        StageResult with synthesis output
    """
    try:
        # Prepare compact evidence
        evidence = prepare_synthesis_evidence(
            protocol_model,
            boundary_summary,
            semantic_summary,
            relation_summary,
            evaluation_metrics,
            max_families=8,
            max_relations=8,
        )

        # Render prompt
        prompt = render_synthesis_prompt(evidence, config.prompt_template_path)

        # Check if we need to split into multiple prompts
        estimated_tokens = estimate_tokens(prompt)

        if estimated_tokens > 5000:
            print(f"[*] Prompt too large ({estimated_tokens} tokens), splitting into multiple calls...")

            # Split families into chunks
            families = evidence["protocol_model"]["families"]
            family_chunks = split_families_for_synthesis(families, max_families_per_chunk=5)

            # Call LLM for each chunk
            chunk_results = []
            for i, chunk in enumerate(family_chunks):
                print(f"[*] Processing chunk {i+1}/{len(family_chunks)} ({len(chunk)} families)...")

                chunk_evidence = evidence.copy()
                chunk_evidence["protocol_model"]["families"] = chunk
                chunk_prompt = render_synthesis_prompt(chunk_evidence, config.prompt_template_path)

                if config.render_only:
                    continue

                response = call_openai_compatible_chat(chunk_prompt, llm_config)
                response_json = extract_message_json(response)
                chunk_results.append(response_json)

            # Merge chunk results
            if config.render_only:
                return StageResult(
                    stage=LLMStage.PROTOCOL_SYNTHESIS,
                    success=True,
                    suggestions=[],
                    applied_count=0,
                    rejected_count=0,
                    validation_log=[],
                    prompt=prompt,
                    response=None,
                )

            # Combine markdown summaries from all chunks
            combined_markdown = "# Protocol Specification\n\n"
            for i, result in enumerate(chunk_results):
                combined_markdown += f"\n## Part {i+1}\n\n"
                combined_markdown += result.get("markdown_summary", "")

            synthesis_output = {
                "markdown_summary": combined_markdown,
                "chunks": chunk_results,
            }

            return StageResult(
                stage=LLMStage.PROTOCOL_SYNTHESIS,
                success=True,
                suggestions=[synthesis_output],
                applied_count=1,
                rejected_count=0,
                validation_log=[],
                prompt=prompt,
                response=json.dumps(synthesis_output),
            )

        # Single prompt case
        if config.render_only:
            return StageResult(
                stage=LLMStage.PROTOCOL_SYNTHESIS,
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

        return StageResult(
            stage=LLMStage.PROTOCOL_SYNTHESIS,
            success=True,
            suggestions=[response_json],
            applied_count=1,
            rejected_count=0,
            validation_log=[],
            prompt=prompt,
            response=json.dumps(response_json),
        )

    except Exception as e:
        return StageResult(
            stage=LLMStage.PROTOCOL_SYNTHESIS,
            success=False,
            suggestions=[],
            applied_count=0,
            rejected_count=0,
            validation_log=[],
            prompt="",
            response=None,
            error=str(e),
        )
