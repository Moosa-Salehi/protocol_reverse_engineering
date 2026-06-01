#!/usr/bin/env python3
"""
Stage 10b: LLM-Assisted Relation Validation

Validate request/response relations using LLM to filter false positives.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.llm.multi_stage import StageConfig, LLMStage
from protocol_re.llm.stage_relations import run_relation_validation_stage
from protocol_re.llm.analyze import LLMRequestConfig
from protocol_re.utils.logging import setup_stage_logging


def load_llm_config(config_path: str) -> dict:
    """Load LLM configuration from JSON file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate request/response relations using LLM to filter false positives."
    )
    parser.add_argument("relations_json", help="Input relations JSON from stage 10")
    parser.add_argument("output_json", help="Output validated relations JSON")
    parser.add_argument("--families-json", help="Families JSON for family summaries")
    parser.add_argument("--llm-config", default="config/llm_config.json", help="LLM configuration JSON")
    parser.add_argument("--render-only", action="store_true", help="Only render prompts, don't call LLM")
    parser.add_argument("--min-confidence", type=float, default=0.7, help="Minimum confidence for keeping relations")
    parser.add_argument("--prompt-template", help="Custom prompt template path")
    parser.add_argument("--results-dir", default="data/llm_stage_results", help="Directory for stage results")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("10b_validate_relations_llm", Path(args.log_dir))

    logger.info("Starting LLM-assisted relation validation")
    logger.decision(
        decision="LLM relation validation mode",
        reason="User configuration",
        render_only=args.render_only,
        min_confidence=args.min_confidence,
    )

    with logger.stage("load_relations"):
        logger.info(f"Loading relations from {args.relations_json}")
        with open(args.relations_json, "r", encoding="utf-8") as f:
            relations_data = json.load(f)

        relations = relations_data.get("family_edges", [])
        role_hints = relations_data.get("role_hints", {})
        logger.metric("relations_loaded", len(relations), "relations")
        logger.metric("families_with_roles", len(role_hints), "families")

    with logger.stage("load_families"):
        # Load family summaries if provided
        family_summaries = {}
        if args.families_json:
            logger.info(f"Loading families from {args.families_json}")
            with open(args.families_json, "r", encoding="utf-8") as f:
                families_data = json.load(f)

            # Stage 07 emits a dict keyed by family_id
            for family_id, details in families_data.items():
                family_summaries[family_id] = {
                    "family_id": family_id,
                    "message_count": details.get("message_count", 0),
                    "field_count": len(details.get("field_hypotheses", [])),
                    "avg_length": details.get("statistics", {}).get("avg_length", 0),
                }
            logger.metric("family_summaries_loaded", len(family_summaries), "families")

    with logger.stage("setup_llm"):
        # Load LLM config
        if not args.render_only:
            logger.info(f"Loading LLM config from {args.llm_config}")
            llm_config_dict = load_llm_config(args.llm_config)
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set in environment")
                api_key = llm_config_dict.get("api_key", "")

            llm_config = LLMRequestConfig(
                model=llm_config_dict.get("model", "gpt-4o-mini"),
                base_url=llm_config_dict.get("openai_base_url", "https://api.openai.com/v1"),
                api_key=api_key,
                temperature=llm_config_dict.get("temperature", 0.1),
                max_tokens=llm_config_dict.get("max_tokens", 3000),
                timeout=llm_config_dict.get("timeout", 180),
            )
            logger.info(f"LLM configured: model={llm_config.model}")
        else:
            llm_config = None
            logger.info("Render-only mode: LLM will not be called")

    # Create stage config
    stage_config = StageConfig(
        stage=LLMStage.RELATION_VALIDATION,
        prompt_template_path=args.prompt_template or "assets/prompts/relation_validation.md",
        min_confidence=args.min_confidence,
        render_only=args.render_only,
        max_tokens=3000,
        temperature=0.1,
    )

    # Create results directory
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[*] Validating {len(relations)} relations")

    # Run relation validation stage
    result = run_relation_validation_stage(
        relations=relations,
        config=stage_config,
        llm_config=llm_config,
        family_summaries=family_summaries,
    )

    # Save stage result
    result_path = results_dir / "relation_validation.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({
            "success": result.success,
            "kept_count": result.applied_count,
            "discarded_count": result.rejected_count,
            "validation_log": result.validation_log,
            "error": result.error,
        }, f, indent=2)

    if args.render_only:
        prompt_path = results_dir / "relation_validation_prompt.md"
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(result.prompt)
        print(f"[+] Saved prompt to {prompt_path}")

        # Save original relations (no changes in render-only mode)
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(relations_data, f, indent=2)
        return

    if not result.success:
        print(f"[!] Error validating relations: {result.error}")
        # Save original relations on error
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(relations_data, f, indent=2)
        return

    print(f"[+] Kept: {result.applied_count}, Discarded: {result.rejected_count}")

    # Extract validated relations from result
    # The validation log contains decisions for each relation
    validated_relations = []
    discarded_relations = []

    # Build decision map from suggestions
    decision_map = {}
    for suggestion in result.suggestions:
        key = (suggestion.get("request_family_id"), suggestion.get("response_family_id"))
        decision_map[key] = suggestion

    # Filter relations based on decisions
    for relation in relations:
        req_family = relation.get("request_family_id")
        resp_family = relation.get("response_family_id")
        key = (req_family, resp_family)

        if key in decision_map:
            decision = decision_map[key]
            if decision.get("decision") == "keep":
                # Add validation metadata
                relation_copy = relation.copy()
                relation_copy["llm_validated"] = True
                relation_copy["llm_confidence"] = decision.get("confidence", 0.0)
                relation_copy["llm_rationale"] = decision.get("rationale", "")
                validated_relations.append(relation_copy)
            else:
                # Track discarded relations
                discarded_relations.append({
                    "relation": relation,
                    "reason": decision.get("rationale", ""),
                    "confidence": decision.get("confidence", 0.0),
                })
        else:
            # No LLM decision - keep by default (conservative)
            validated_relations.append(relation)

    # Save validated relations
    output_data = {
        "family_edges": validated_relations,
        "role_hints": role_hints,
        "llm_validation_summary": {
            "stage": "relation_validation",
            "original_count": len(relations),
            "kept_count": len(validated_relations),
            "discarded_count": len(discarded_relations),
            "precision_improvement": f"{len(relations)} → {len(validated_relations)} relations",
        },
        "discarded_relations": discarded_relations,
    }

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[+] Wrote validated relations to {args.output_json}")
    print(f"[+] Original relations: {len(relations)}")
    print(f"[+] Kept relations: {len(validated_relations)}")
    print(f"[+] Discarded relations: {len(discarded_relations)}")
    print(f"[+] Precision improvement: {len(relations)} → {len(validated_relations)}")
    print(f"[+] Stage results saved to {result_path}")


if __name__ == "__main__":
    main()
