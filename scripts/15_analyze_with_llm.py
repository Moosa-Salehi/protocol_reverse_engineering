#!/usr/bin/env python3
"""
Stage 15: Protocol Structure Synthesis (Refactored)

Synthesize protocol specification using multi-stage LLM results.
This replaces the monolithic evidence bundle approach with focused synthesis.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.llm.multi_stage import StageConfig, LLMStage
from protocol_re.llm.stage_synthesis import run_protocol_synthesis_stage
from protocol_re.llm.analyze import LLMRequestConfig
from protocol_re.utils.logging import setup_stage_logging


def load_json(path: str) -> dict:
    """Load JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_llm_config(config_path: str) -> dict:
    """Load LLM configuration from JSON file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_stage_summary(path: str) -> dict | None:
    """Load stage summary if file exists."""
    if not Path(path).exists():
        return None
    try:
        return load_json(path)
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synthesize protocol specification using multi-stage LLM results (refactored from monolithic approach)."
    )
    parser.add_argument("protocol_model_json", help="Input protocol model JSON (refined if available)")
    parser.add_argument("output_json", help="Output LLM synthesis JSON")
    parser.add_argument("--config", default="config/llm_config.json", help="LLM config JSON")
    parser.add_argument("--prompt-out", help="Optional path to write the rendered prompt")
    parser.add_argument("--template", help="Optional custom prompt template")
    parser.add_argument("--render-only", action="store_true", help="Only render prompt, don't call LLM")
    parser.add_argument("--temperature", type=float, help="Override temperature")
    parser.add_argument("--max-tokens", type=int, help="Override max_tokens")
    parser.add_argument("--timeout", type=int, help="Override timeout")

    # Multi-stage result inputs
    parser.add_argument("--boundary-summary", help="Boundary refinement summary JSON from stage 07b")
    parser.add_argument("--semantic-summary", help="Semantic labeling summary JSON from stage 11b")
    parser.add_argument("--relation-summary", help="Relation validation summary JSON from stage 10b")
    parser.add_argument("--evaluation-json", help="Pipeline evaluation metrics JSON")

    # Legacy compatibility
    parser.add_argument("--llm-evidence-json", help="[DEPRECATED] Legacy evidence bundle (ignored)")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")

    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("15_analyze_with_llm", Path(args.log_dir))

    logger.info("Starting LLM protocol synthesis")
    logger.decision(
        decision="LLM synthesis mode",
        reason="User configuration",
        render_only=args.render_only,
        has_template=args.template is not None,
    )

    with logger.stage("load_protocol_model"):
        logger.info(f"Loading protocol model from {args.protocol_model_json}")
        protocol_model = load_json(args.protocol_model_json)
        logger.metric("families_in_model", len(protocol_model.get('families', [])), "families")

    # Load multi-stage summaries if available
    boundary_summary = None
    semantic_summary = None
    relation_summary = None
    evaluation_metrics = None

    if args.boundary_summary:
        print(f"[+] Loading boundary refinement summary from {args.boundary_summary}")
        boundary_summary = load_stage_summary(args.boundary_summary)

    if args.semantic_summary:
        print(f"[+] Loading semantic labeling summary from {args.semantic_summary}")
        semantic_summary = load_stage_summary(args.semantic_summary)

    if args.relation_summary:
        print(f"[+] Loading relation validation summary from {args.relation_summary}")
        relation_summary = load_stage_summary(args.relation_summary)

    if args.evaluation_json:
        print(f"[+] Loading evaluation metrics from {args.evaluation_json}")
        evaluation_metrics = load_stage_summary(args.evaluation_json)

    # Auto-detect summaries from standard locations if not provided
    data_dir = Path(args.protocol_model_json).parent

    if not boundary_summary:
        auto_path = data_dir / "05_families_refined.json"
        if auto_path.exists():
            print(f"[*] Auto-detected boundary refinement: {auto_path}")
            data = load_json(str(auto_path))
            boundary_summary = data.get("llm_refinement_summary")

    if not semantic_summary:
        auto_path = data_dir / "05_families_labeled.json"
        if auto_path.exists():
            print(f"[*] Auto-detected semantic labeling: {auto_path}")
            data = load_json(str(auto_path))
            semantic_summary = data.get("llm_labeling_summary")

    if not relation_summary:
        auto_path = data_dir / "08_relations_validated.json"
        if auto_path.exists():
            print(f"[*] Auto-detected relation validation: {auto_path}")
            data = load_json(str(auto_path))
            relation_summary = data.get("llm_validation_summary")

    if not evaluation_metrics:
        auto_path = data_dir / "11_evaluation.json"
        if auto_path.exists():
            print(f"[*] Auto-detected evaluation metrics: {auto_path}")
            evaluation_metrics = load_json(str(auto_path))

    # Load LLM config
    model = ""
    if not args.render_only:
        print(f"[+] Loading LLM config from {args.config}")
        config_dict = load_llm_config(args.config)
        model = config_dict.get("model", "gpt-4o-mini")
        base_url = config_dict.get("openai_base_url", "https://api.openai.com/v1")
        api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            print("[!] Warning: OPENAI_API_KEY not set in environment")
            api_key = config_dict.get("api_key", "")

        temperature = args.temperature if args.temperature is not None else float(config_dict.get("temperature", 0.2))
        max_tokens = args.max_tokens if args.max_tokens is not None else int(config_dict.get("max_tokens", 4000))
        timeout = args.timeout if args.timeout is not None else int(config_dict.get("timeout", 180))

        llm_config = LLMRequestConfig(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
    else:
        llm_config = None

    # Create stage config
    stage_config = StageConfig(
        stage=LLMStage.PROTOCOL_SYNTHESIS,
        prompt_template_path=args.template or "assets/prompts/protocol_synthesis.md",
        render_only=args.render_only,
        max_tokens=4000,
        temperature=0.2,
    )

    print(f"\n[*] Running protocol synthesis stage...")
    print(f"[*] Multi-stage summaries available:")
    print(f"    - Boundary refinement: {'Yes' if boundary_summary else 'No'}")
    print(f"    - Semantic labeling: {'Yes' if semantic_summary else 'No'}")
    print(f"    - Relation validation: {'Yes' if relation_summary else 'No'}")
    print(f"    - Evaluation metrics: {'Yes' if evaluation_metrics else 'No'}")

    # Run synthesis stage
    result = run_protocol_synthesis_stage(
        protocol_model=protocol_model,
        config=stage_config,
        llm_config=llm_config,
        boundary_summary=boundary_summary,
        semantic_summary=semantic_summary,
        relation_summary=relation_summary,
        evaluation_metrics=evaluation_metrics,
    )

    # Save prompt if requested
    if args.prompt_out:
        Path(args.prompt_out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.prompt_out, "w", encoding="utf-8") as f:
            f.write(result.prompt)
        print(f"[+] Saved prompt to {args.prompt_out}")

    # Prepare output
    output = {
        "artifact_type": "llm_protocol_synthesis",
        "source_model": args.protocol_model_json,
        "multi_stage_summaries": {
            "boundary_refinement": boundary_summary is not None,
            "semantic_labeling": semantic_summary is not None,
            "relation_validation": relation_summary is not None,
            "evaluation_metrics": evaluation_metrics is not None,
        },
        "model": model,
        "render_only": args.render_only,
        "success": result.success,
        "error": result.error,
        "synthesis": None,
        "markdown_summary": None,
    }

    if result.success and result.suggestions:
        synthesis_data = result.suggestions[0]
        output["synthesis"] = synthesis_data
        output["markdown_summary"] = synthesis_data.get("markdown_summary", "")

        # For backward compatibility, also include as analysis_markdown
        output["analysis_markdown"] = output["markdown_summary"]
        output["patches"] = []  # No patches in synthesis stage

    # Save output
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    status = "prompt rendered" if args.render_only else "synthesis completed"
    print(f"\n[+] Protocol {status}")
    print(f"[+] Wrote output to {args.output_json}")

    if result.success and not args.render_only:
        print(f"[+] Synthesis includes {len(protocol_model.get('families', []))} families")
        if output.get("markdown_summary"):
            print(f"[+] Generated {len(output['markdown_summary'])} characters of documentation")


if __name__ == "__main__":
    main()
