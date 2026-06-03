#!/usr/bin/env python3
"""
Stage 07b: LLM-Assisted Boundary Refinement

Refine field boundaries using LLM to reduce over-segmentation.
"""
from __future__ import annotations

import argparse
import json
import os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.utils.logging import setup_stage_logging

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.model.schema import FamilyAssignment
from protocol_re.llm.multi_stage import StageConfig, LLMStage, load_cached_response
from protocol_re.llm.stage_boundaries import run_boundary_refinement_stage
from protocol_re.llm.analyze import LLMRequestConfig
from protocol_re.llm.stage_errors import warn_or_fail_stage_failures
from protocol_re.llm.user_responses import (
    ensure_user_response_placeholder,
    load_user_provided_response,
    make_user_response_path,
)


def load_llm_config(config_path: str) -> dict:
    """Load LLM configuration from JSON file."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_llm_request_config(config_dict: dict, api_key: str, logger: object) -> LLMRequestConfig:
    """Build request config, including retry and sequential pacing options."""
    return LLMRequestConfig(
        model=config_dict.get("model", "gpt-4o-mini"),
        base_url=config_dict.get("openai_base_url", "https://api.openai.com/v1"),
        api_key=api_key,
        temperature=config_dict.get("temperature", 0.1),
        max_tokens=config_dict.get("max_tokens", 3000),
        timeout=config_dict.get("timeout", 180),
        max_retries=int(config_dict.get("max_retries", 3)),
        retry_delay_seconds=float(config_dict.get("retry_delay_seconds", 1.0)),
        max_retry_delay_seconds=float(config_dict.get("max_retry_delay_seconds", 10.0)),
        request_interval_seconds=float(config_dict.get("request_interval_seconds", 1.0)),
        logger=logger,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refine field boundaries using LLM to reduce over-segmentation."
    )
    parser.add_argument("messages_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("families_json", help="Input families JSON from stage 07")
    parser.add_argument("output_json", help="Output refined families JSON")
    parser.add_argument("--assignments-json", help="Family assignments from stage 04")
    parser.add_argument("--features-json", help="Family features JSON from stage 06")
    parser.add_argument("--llm-config", default="config/llm_config.json", help="LLM configuration JSON")
    parser.add_argument("--render-only", action="store_true", help="Only render prompts, don't call LLM")
    parser.add_argument("--min-confidence", type=float, default=0.6, help="Minimum confidence for merge suggestions")
    parser.add_argument("--max-samples", type=int, default=10, help="Maximum sample messages per family")
    parser.add_argument("--prompt-template", help="Custom prompt template path")
    parser.add_argument("--results-dir", default="data/llm_stage_results", help="Directory for stage results")
    parser.add_argument("--reuse-llm-responses", action="store_true", help="Reuse existing stage result responses instead of calling the LLM API")
    parser.add_argument("--use-user-provided-response", action="store_true", help="Load filled LLM responses from data/user_provided_LLM_responses before calling the API")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("07b_refine_boundaries_llm", Path(args.log_dir))

    logger.info("Starting LLM-assisted boundary refinement")
    logger.decision(
        decision="LLM boundary refinement mode",
        reason="User configuration",
        render_only=args.render_only,
        min_confidence=args.min_confidence,
        max_samples=args.max_samples,
    )

    with logger.stage("load_data"):
        logger.info(f"Loading messages from {args.messages_jsonl}")
        messages = load_corpus_jsonl(args.messages_jsonl)
        messages_by_id = {msg.msg_id: msg for msg in messages}
        logger.metric("messages_loaded", len(messages), "messages")

        logger.info(f"Loading families from {args.families_json}")
        with open(args.families_json, "r", encoding="utf-8") as f:
            families_data = json.load(f)
        logger.metric("families_loaded", len(families_data), "families")  # dict keyed by family_id

    # Load assignments if provided
    with logger.stage("load_assignments"):
        family_assignments = {}
        if args.assignments_json:
            logger.info(f"Loading assignments from {args.assignments_json}")
            with open(args.assignments_json, "r", encoding="utf-8") as f:
                assignments_payload = json.load(f)
            for assignment in assignments_payload.get("assignments", []):
                msg_id = assignment["msg_id"]
                family_id = assignment["family_id"]
                if family_id not in family_assignments:
                    family_assignments[family_id] = []
                family_assignments[family_id].append(msg_id)
            logger.metric("assignments_loaded", len(assignments_payload.get("assignments", [])), "assignments")

    with logger.stage("load_features"):
        features_by_family = {}
        if args.features_json:
            logger.info(f"Loading features from {args.features_json}")
            with open(args.features_json, "r", encoding="utf-8") as f:
                features_payload = json.load(f)
            if "families" in features_payload and isinstance(features_payload.get("families"), list):
                features_by_family = {
                    item.get("family_id"): item
                    for item in features_payload.get("families", [])
                    if item.get("family_id")
                }
            else:
                features_by_family = features_payload
            logger.metric("families_with_features", len(features_by_family), "families")

    # Load LLM config
    with logger.stage("setup_llm"):
        if not args.render_only and (not args.use_user_provided_response or Path(args.llm_config).is_file()):
            logger.info(f"Loading LLM config from {args.llm_config}")
            llm_config_dict = load_llm_config(args.llm_config)
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set in environment")
                api_key = llm_config_dict.get("api_key", "")

            llm_config = build_llm_request_config(llm_config_dict, api_key, logger)
            logger.info(f"LLM configured: model={llm_config.model}")
        else:
            llm_config_dict = {}
            llm_config = None
            if args.render_only:
                logger.info("Render-only mode: LLM will not be called")
            else:
                logger.warning("LLM config not loaded; API fallback is unavailable unless cached or user-provided responses are filled")

    # Create stage config
    stage_config = StageConfig(
        stage=LLMStage.BOUNDARY_REFINEMENT,
        prompt_template_path=args.prompt_template or "assets/prompts/boundary_refinement.md",
        min_confidence=args.min_confidence,
        render_only=args.render_only,
        max_tokens=3000,
        temperature=0.1,
    )

    # Create results directory
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Process each family. Stage 07 emits a dict keyed by family_id; we refine in
    # place and re-emit the same dict schema so downstream stages (11, 12) consume it.
    refined_families = {}
    total_applied = 0
    total_rejected = 0
    stage_results: list[tuple[str, object]] = []

    for family_id, details in families_data.items():
        refined_details = dict(details)
        fields = details.get("field_hypotheses", [])

        if not fields:
            print(f"[*] Skipping {family_id}: no fields")
            refined_families[family_id] = refined_details
            continue

        print(f"\n[*] Processing {family_id} ({len(fields)} fields)")

        # Get sample messages for this family
        sample_messages = []
        if family_id in family_assignments:
            msg_ids = family_assignments[family_id][:args.max_samples]
            sample_messages = [messages_by_id[mid] for mid in msg_ids if mid in messages_by_id]

        if not sample_messages:
            print(f"[*] No sample messages for {family_id}, skipping LLM refinement")
            refined_families[family_id] = refined_details
            continue

        result_path = results_dir / f"boundary_refinement_{family_id}.json"
        user_response_path = make_user_response_path("boundary_refinement", family_id)
        prompt_path = results_dir / f"boundary_refinement_{family_id}_prompt.md"
        ensure_user_response_placeholder(
            user_response_path,
            stage="boundary_refinement",
            prompt_path=prompt_path,
            model=llm_config_dict.get("model", ""),
            request_label=f"stage 07b boundary refinement for {family_id}",
            metadata={"family_id": family_id, "result_path": str(result_path)},
        )

        cached_response = None
        if args.use_user_provided_response:
            cached_response = load_user_provided_response(user_response_path)
            if cached_response is not None:
                print(f"[*] Using user-provided LLM response from {user_response_path}")
        if cached_response is None and args.reuse_llm_responses:
            cached_response = load_cached_response(result_path)
            if cached_response is not None:
                print(f"[*] Reusing cached LLM response from {result_path}")

        # Run boundary refinement stage
        result = run_boundary_refinement_stage(
            family_id=family_id,
            fields=fields,
            messages=sample_messages,
            config=stage_config,
            llm_config=llm_config,
            cached_response=cached_response,
            boundary_scores=details.get("boundary_scores"),
            family_stats=details.get("statistics"),
            family_details=details,
            family_features=features_by_family.get(family_id),
        )

        stage_results.append((family_id, result))

        # Save stage result
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump({
                "family_id": family_id,
                "success": result.success,
                "applied_count": result.applied_count,
                "rejected_count": result.rejected_count,
                "validation_log": result.validation_log,
                "response": result.response,
                "error": result.error,
                "error_category": result.error_category,
            }, f, indent=2)

        if args.render_only:
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(result.prompt)
            print(f"[+] Saved prompt to {prompt_path}")
            refined_families[family_id] = refined_details
            continue

        if not result.success:
            print(f"[!] Warning: leaving {family_id} unchanged: {result.error}")
            refined_families[family_id] = refined_details
            continue

        print(f"[+] Applied: {result.applied_count}, Rejected: {result.rejected_count}")
        total_applied += result.applied_count
        total_rejected += result.rejected_count

        # Apply refinements to family
        if result.applied_count > 0:
            # Note: The actual field updates are in the validation_log
            refined_details["llm_boundary_refinement"] = {
                "applied": result.applied_count,
                "rejected": result.rejected_count,
                "stage": "boundary_refinement",
            }

        refined_families[family_id] = refined_details

    # Save refined families, preserving the stage-07 dict schema
    output_data = refined_families

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[+] Wrote refined families to {args.output_json}")
    print(f"[+] Total merges applied: {total_applied}")
    print(f"[+] Total merges rejected: {total_rejected}")
    print(f"[+] Stage results saved to {args.results_dir}")

    # API failures warn and keep fallback artifacts; other failures remain fatal.
    warn_or_fail_stage_failures(stage_results, render_only=args.render_only, stage_name="07b_refine_boundaries_llm", logger=logger)


if __name__ == "__main__":
    main()
