"""
Multi-stage LLM integration for protocol reverse engineering.

This module provides a framework for breaking down the monolithic LLM analysis
into focused, stage-specific interactions with evidence-gated validation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class LLMStage(Enum):
    """Available LLM analysis stages."""
    BOUNDARY_REFINEMENT = "boundary_refinement"
    SEMANTIC_LABELING = "semantic_labeling"
    RELATION_VALIDATION = "relation_validation"
    PROTOCOL_SYNTHESIS = "protocol_synthesis"


@dataclass
class StageConfig:
    """Configuration for a single LLM stage."""
    stage: LLMStage
    enabled: bool = True
    prompt_template_path: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.1
    min_confidence: float = 0.6
    render_only: bool = False


@dataclass
class StageResult:
    """Result from a single LLM stage."""
    stage: LLMStage
    success: bool
    suggestions: List[Dict[str, Any]]
    applied_count: int
    rejected_count: int
    validation_log: List[Dict[str, Any]]
    prompt: str
    # Raw LLM API response body, preserved for auditability.
    response: Optional[str]
    error: Optional[str] = None
    error_category: Optional[str] = None


@dataclass
class MultiStagePipeline:
    """Configuration for multi-stage LLM pipeline."""
    stages: List[StageConfig]
    llm_config: Dict[str, Any]
    evidence_gating: bool = True
    cache_responses: bool = True
    cache_dir: str = "data/llm_cache"


def create_default_pipeline(
    llm_config: Dict[str, Any],
    render_only: bool = False,
    enable_boundary_refinement: bool = True,
    enable_semantic_labeling: bool = True,
    enable_relation_validation: bool = True,
    enable_protocol_synthesis: bool = True,
) -> MultiStagePipeline:
    """
    Create a default multi-stage LLM pipeline with standard configuration.

    Args:
        llm_config: LLM API configuration (model, base_url, api_key, etc.)
        render_only: If True, only render prompts without calling LLM API
        enable_*: Enable/disable specific stages

    Returns:
        Configured MultiStagePipeline
    """
    stages = []

    if enable_boundary_refinement:
        stages.append(StageConfig(
            stage=LLMStage.BOUNDARY_REFINEMENT,
            prompt_template_path="assets/prompts/boundary_refinement.md",
            max_tokens=3000,
            temperature=0.1,
            min_confidence=0.6,
            render_only=render_only,
        ))

    if enable_semantic_labeling:
        stages.append(StageConfig(
            stage=LLMStage.SEMANTIC_LABELING,
            prompt_template_path="assets/prompts/semantic_labeling.md",
            max_tokens=4000,
            temperature=0.1,
            min_confidence=0.5,
            render_only=render_only,
        ))

    if enable_relation_validation:
        stages.append(StageConfig(
            stage=LLMStage.RELATION_VALIDATION,
            prompt_template_path="assets/prompts/relation_validation.md",
            max_tokens=3000,
            temperature=0.1,
            min_confidence=0.7,
            render_only=render_only,
        ))

    if enable_protocol_synthesis:
        stages.append(StageConfig(
            stage=LLMStage.PROTOCOL_SYNTHESIS,
            prompt_template_path=None,  # Uses default template
            max_tokens=4000,
            temperature=0.2,
            min_confidence=0.0,  # No confidence filtering for synthesis
            render_only=render_only,
        ))

    return MultiStagePipeline(
        stages=stages,
        llm_config=llm_config,
        evidence_gating=True,
        cache_responses=True,
        cache_dir="data/llm_cache",
    )


def load_prompt_template(template_path: str) -> str:
    """Load a prompt template from file."""
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def save_stage_result(result: StageResult, output_path: str) -> None:
    """Save stage result to JSON file."""
    data = {
        "stage": result.stage.value,
        "success": result.success,
        "suggestions": result.suggestions,
        "applied_count": result.applied_count,
        "rejected_count": result.rejected_count,
        "validation_log": result.validation_log,
        "response": result.response,
        "error": result.error,
        "error_category": result.error_category,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_stage_result(input_path: str) -> StageResult:
    """Load stage result from JSON file."""
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return StageResult(
        stage=LLMStage(data["stage"]),
        success=data["success"],
        suggestions=data["suggestions"],
        applied_count=data["applied_count"],
        rejected_count=data["rejected_count"],
        validation_log=data["validation_log"],
        prompt="",  # Not saved
        response=data.get("response"),
        error=data.get("error"),
        error_category=data.get("error_category"),
    )
