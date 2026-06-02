#!/usr/bin/env python3
"""
Stage 11b: LLM-Assisted Semantic Labeling

Assign semantic labels to fields using LLM based on statistical evidence.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.llm.multi_stage import StageConfig, LLMStage
from protocol_re.llm.stage_semantics import run_semantic_labeling_stage
from protocol_re.llm.analyze import LLMRequestConfig
from protocol_re.llm.stage_errors import collect_stage_failures, fail_loudly_if_any
from protocol_re.utils.logging import setup_stage_logging
from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.llm.evidence_builders import index_messages_by_family


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
        max_tokens=config_dict.get("max_tokens", 4000),
        timeout=config_dict.get("timeout", 180),
        max_retries=int(config_dict.get("max_retries", 3)),
        retry_delay_seconds=float(config_dict.get("retry_delay_seconds", 1.0)),
        max_retry_delay_seconds=float(config_dict.get("max_retry_delay_seconds", 10.0)),
        request_interval_seconds=float(config_dict.get("request_interval_seconds", 1.0)),
        logger=logger,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assign semantic labels to fields using LLM based on statistical evidence."
    )
    parser.add_argument("families_json", help="Input families JSON from stage 07")
    parser.add_argument("output_json", help="Output families JSON with semantic labels")
    parser.add_argument("--relations-json", help="Relations JSON for semantic inference")
    parser.add_argument("--features-json", help="Family features JSON for field statistics")
    parser.add_argument("--messages-jsonl", help="Canonical message corpus JSONL for sample field values")
    parser.add_argument("--assignments-json", help="Family assignments JSON for sample field values")
    parser.add_argument("--max-samples", type=int, default=10, help="Maximum sample messages per family")
    parser.add_argument("--llm-config", default="config/llm_config.json", help="LLM configuration JSON")
    parser.add_argument("--render-only", action="store_true", help="Only render prompts, don't call LLM")
    parser.add_argument("--min-confidence", type=float, default=0.5, help="Minimum confidence for semantic labels")
    parser.add_argument("--prompt-template", help="Custom prompt template path")
    parser.add_argument("--results-dir", default="data/llm_stage_results", help="Directory for stage results")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("11b_label_semantics_llm", Path(args.log_dir))

    logger.info("Starting LLM-assisted semantic labeling")
    logger.decision(
        decision="LLM semantic labeling mode",
        reason="User configuration",
        render_only=args.render_only,
        min_confidence=args.min_confidence,
    )

    with logger.stage("load_families"):
        logger.info(f"Loading families from {args.families_json}")
        with open(args.families_json, "r", encoding="utf-8") as f:
            families_data = json.load(f)
        logger.metric("families_loaded", len(families_data), "families")  # dict keyed by family_id

    with logger.stage("load_relations"):
        # Load relations if provided
        relations_by_family = {}
        role_hints = {}
        if args.relations_json:
            logger.info(f"Loading relations from {args.relations_json}")
            with open(args.relations_json, "r", encoding="utf-8") as f:
                relations_data = json.load(f)

            role_hints = relations_data.get("role_hints", {})

            # Group relations by family
            for edge in relations_data.get("family_edges", []):
                req_family = edge.get("request_family_id")
                resp_family = edge.get("response_family_id")

                if req_family not in relations_by_family:
                    relations_by_family[req_family] = []
                if resp_family not in relations_by_family:
                    relations_by_family[resp_family] = []

                relations_by_family[req_family].append(edge)
                relations_by_family[resp_family].append(edge)

            logger.metric("relations_loaded", len(relations_data.get("family_edges", [])), "relations")
            logger.metric("families_with_roles", len(role_hints), "families")

    with logger.stage("load_features"):
        # Load features if provided
        features_by_family = {}
        if args.features_json:
            logger.info(f"Loading features from {args.features_json}")
            with open(args.features_json, "r", encoding="utf-8") as f:
                features_data = json.load(f)

            if "families" in features_data and isinstance(features_data.get("families"), list):
                for family_feature in features_data.get("families", []):
                    family_id = family_feature.get("family_id")
                    features_by_family[family_id] = family_feature
            else:
                features_by_family = features_data

            logger.metric("families_with_features", len(features_by_family), "families")

    with logger.stage("load_sample_messages"):
        messages_by_family = {}
        if args.messages_jsonl and args.assignments_json:
            logger.info(f"Loading sample messages from {args.messages_jsonl}")
            messages = load_corpus_jsonl(args.messages_jsonl)
            messages_by_id = {msg.msg_id: msg for msg in messages}
            with open(args.assignments_json, "r", encoding="utf-8") as f:
                assignments_payload = json.load(f)
            messages_by_family = index_messages_by_family(messages_by_id, assignments_payload, args.max_samples)
            logger.metric("families_with_sample_messages", len(messages_by_family), "families")

    with logger.stage("setup_llm"):
        # Load LLM config
        if not args.render_only:
            logger.info(f"Loading LLM config from {args.llm_config}")
            llm_config_dict = load_llm_config(args.llm_config)
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning("OPENAI_API_KEY not set in environment")
                api_key = llm_config_dict.get("api_key", "")

            llm_config = build_llm_request_config(llm_config_dict, api_key, logger)
            logger.info(f"LLM configured: model={llm_config.model}")
        else:
            llm_config = None
            logger.info("Render-only mode: LLM will not be called")

    # Create stage config
    stage_config = StageConfig(
        stage=LLMStage.SEMANTIC_LABELING,
        prompt_template_path=args.prompt_template or "assets/prompts/semantic_labeling.md",
        min_confidence=args.min_confidence,
        render_only=args.render_only,
        max_tokens=4000,
        temperature=0.1,
    )

    # Create results directory
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Process each family. Stage 07 emits a dict keyed by family_id; we label fields
    # in place and re-emit the same dict schema so downstream stages (12) consume it.
    labeled_families = {}
    total_applied = 0
    total_rejected = 0
    stage_results: list[tuple[str, object]] = []

    for family_id, details in families_data.items():
        labeled_details = dict(details)
        fields = details.get("field_hypotheses", [])

        if not fields:
            print(f"[*] Skipping {family_id}: no fields")
            labeled_families[family_id] = labeled_details
            continue

        print(f"\n[*] Processing {family_id} ({len(fields)} fields)")

        # Get family role from role hints
        family_role = role_hints.get(family_id, {}).get("role_hint", "unknown")

        # Get relations for this family
        family_relations = relations_by_family.get(family_id, [])

        # Get field statistics from features
        field_statistics = {}
        if family_id in features_by_family:
            family_features = features_by_family[family_id]
            # Extract field-level statistics if available
            # This would need to be structured properly in the features JSON
            field_statistics = family_features.get("field_statistics", {})
        else:
            family_features = {}

        # Run semantic labeling stage
        result = run_semantic_labeling_stage(
            family_id=family_id,
            fields=fields,
            config=stage_config,
            llm_config=llm_config,
            field_statistics=field_statistics,
            relations=family_relations,
            family_role=family_role,
            messages=messages_by_family.get(family_id, []),
            family_features=family_features,
            segments=details.get("segments", []),
        )

        stage_results.append((family_id, result))

        # Save stage result
        result_path = results_dir / f"semantic_labeling_{family_id}.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump({
                "family_id": family_id,
                "success": result.success,
                "applied_count": result.applied_count,
                "rejected_count": result.rejected_count,
                "validation_log": result.validation_log,
                "response": result.response,
                "error": result.error,
            }, f, indent=2)

        if args.render_only:
            prompt_path = results_dir / f"semantic_labeling_{family_id}_prompt.md"
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(result.prompt)
            print(f"[+] Saved prompt to {prompt_path}")
            labeled_families[family_id] = labeled_details
            continue

        if not result.success:
            print(f"[!] Error processing {family_id}: {result.error}")
            labeled_families[family_id] = labeled_details
            continue

        print(f"[+] Applied: {result.applied_count}, Rejected: {result.rejected_count}")
        total_applied += result.applied_count
        total_rejected += result.rejected_count

        # Apply semantic labels to family
        if result.applied_count > 0:
            # Apply labels from validation log
            labeled_fields = [dict(f) for f in fields]
            for log_entry in result.validation_log:
                if log_entry.get("applied", False):
                    label = log_entry.get("label", {})
                    field_index = label.get("field_index")
                    if field_index is not None and field_index < len(labeled_fields):
                        labeled_fields[field_index]["semantic_role"] = label.get("semantic_role")
                        labeled_fields[field_index]["semantic_confidence"] = label.get("confidence")
                        labeled_fields[field_index]["semantic_evidence"] = label.get("evidence", [])

            labeled_details["field_hypotheses"] = labeled_fields
            labeled_details["llm_semantic_labeling"] = {
                "applied": result.applied_count,
                "rejected": result.rejected_count,
                "stage": "semantic_labeling",
            }

        labeled_families[family_id] = labeled_details

    # Save labeled families, preserving the stage-07 dict schema
    output_data = labeled_families

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"\n[+] Wrote labeled families to {args.output_json}")
    print(f"[+] Total labels applied: {total_applied}")
    print(f"[+] Total labels rejected: {total_rejected}")
    print(f"[+] Stage results saved to {args.results_dir}")

    # Surface per-family failures loudly (swallowed exceptions / empty prompts).
    failures = collect_stage_failures(stage_results, render_only=args.render_only)
    fail_loudly_if_any(failures, stage_name="11b_label_semantics_llm", logger=logger)


if __name__ == "__main__":
    main()
