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

from protocol_re.llm.multi_stage import StageConfig, LLMStage, load_cached_response
from protocol_re.llm.stage_semantics import apply_semantic_label_to_field, run_semantic_labeling_stage
from protocol_re.llm.analyze import LLMRequestConfig
from protocol_re.llm.local_finetuned import (
    LocalInferenceConfig,
    run_local_semantic_labeling,
)
from protocol_re.llm.stage_errors import warn_or_fail_stage_failures
from protocol_re.utils.logging import setup_stage_logging
from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.llm.evidence_builders import index_messages_by_family
from protocol_re.llm.user_responses import (
    ensure_user_response_placeholder,
    load_user_provided_response,
    make_user_response_path,
    save_rendered_prompt,
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
    parser.add_argument("--semantics-json", help="Stage-09 semantics summary JSON to merge consensus labels into (optional)")
    parser.add_argument("--messages-jsonl", help="Canonical message corpus JSONL for sample field values")
    parser.add_argument("--assignments-json", help="Family assignments JSON for sample field values")
    parser.add_argument("--max-samples", type=int, default=10, help="Maximum sample messages per family")
    parser.add_argument("--llm-config", default="config/llm_config.json", help="LLM configuration JSON")
    parser.add_argument("--render-only", action="store_true", help="Only render prompts, don't call LLM")
    parser.add_argument("--min-confidence", type=float, default=0.5, help="Minimum confidence for semantic labels")
    parser.add_argument("--prompt-template", help="Custom prompt template path")
    parser.add_argument("--results-dir", default="data/llm_stage_results", help="Directory for stage results")
    parser.add_argument(
        "--user-response-dir",
        default="data/user_provided_LLM_responses",
        help="Directory for user-provided LLM response placeholders",
    )
    parser.add_argument(
        "--backend",
        choices=["api", "local-finetuned"],
        default="api",
        help="api: OpenAI-compatible endpoint from --llm-config. "
        "local-finetuned: llama.cpp server (llama-server) hosting the fine-tuned "
        "Qwen adapter GGUF, queried per message in its training format.",
    )
    parser.add_argument("--local-base-url", default="http://127.0.0.1:8080", help="Base URL of the local inference server (--backend local-finetuned).")
    parser.add_argument("--local-model", default="qwen25-coder-7b-protocol-re", help="Model name expected by the local server (--backend local-finetuned).")
    parser.add_argument("--local-max-samples", type=int, default=5, help="Sample messages per family sent to the local model (--backend local-finetuned).")
    parser.add_argument("--local-min-support", type=float, default=0.5, help="Consensus threshold for aggregating per-message predictions (0-1].")
    parser.add_argument("--local-timeout", type=float, default=300.0, help="Per-request timeout in seconds for the local server.")
    parser.add_argument("--reuse-llm-responses", action="store_true", help="Reuse existing stage result responses instead of calling the LLM API")
    parser.add_argument("--use-user-provided-response", action="store_true", help="Load filled LLM responses from data/user_provided_LLM_responses before calling the API")
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

    llm_config_dict: dict = {}
    llm_config = None
    local_llm: LocalInferenceConfig | None = None
    with logger.stage("setup_llm"):
        # Load LLM config
        if args.backend == "local-finetuned":
            local_llm = LocalInferenceConfig(
                base_url=args.local_base_url,
                model=args.local_model,
                temperature=0.0,
                max_tokens=512,
                timeout=args.local_timeout,
                max_samples=args.local_max_samples,
                min_support=args.local_min_support,
            )
            logger.info(
                "Local fine-tuned backend configured: base_url=%s model=%s samples=%d support=%.2f",
                local_llm.base_url,
                local_llm.model,
                local_llm.max_samples,
                local_llm.min_support,
            )
        elif not args.render_only and (not args.use_user_provided_response or Path(args.llm_config).is_file()):
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
    llm_semantics: dict = {}
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

        result_path = results_dir / f"semantic_labeling_{family_id}.json"
        user_response_path = make_user_response_path(
            "semantic_labeling",
            family_id,
            response_dir=args.user_response_dir,
        )
        prompt_path = results_dir / f"semantic_labeling_{family_id}_prompt.md"
        ensure_user_response_placeholder(
            user_response_path,
            stage="semantic_labeling",
            prompt_path=prompt_path,
            model=llm_config_dict.get("model", ""),
            request_label=f"stage 11b semantic labeling for {family_id}",
            metadata={"family_id": family_id, "result_path": str(result_path)},
        )

        # Render-only never consults stored/cached/user-provided responses.
        cached_response = None
        if not args.render_only:
            if args.use_user_provided_response:
                cached_response = load_user_provided_response(user_response_path)
                if cached_response is not None:
                    print(f"[*] Using user-provided LLM response from {user_response_path}")
            if cached_response is None and args.reuse_llm_responses:
                cached_response = load_cached_response(result_path)
                if cached_response is not None:
                    print(f"[*] Reusing cached LLM response from {result_path}")

        # Local backend replaces the whole prompt+call: it renders
        # training-format per-message prompts and maps consensus labels onto
        # the family's field_hypotheses.
        llm_call = None
        if local_llm is not None:
            family_samples = messages_by_family.get(family_id, [])

            def local_call(prompt: str, family_id: str = family_id, task: str = "semantic_labeling") -> str:
                raw, _labels, _used = run_local_semantic_labeling(
                    family_id, family_samples, fields, local_llm
                )
                return raw

            llm_call = local_call

        # Run semantic labeling stage
        result = run_semantic_labeling_stage(
            family_id=family_id,
            fields=fields,
            config=stage_config,
            llm_config=llm_config,
            cached_response=cached_response,
            field_statistics=field_statistics,
            relations=family_relations,
            family_role=family_role,
            messages=messages_by_family.get(family_id, []),
            family_features=family_features,
            segments=details.get("segments", []),
            llm_call=llm_call,
        )

        stage_results.append((family_id, result))

        save_rendered_prompt(prompt_path, result.prompt)
        print(f"[+] Saved prompt to {prompt_path}")

        if args.render_only:
            if result_path.exists():
                print(f"[*] Preserved cached LLM response at {result_path}")
            labeled_families[family_id] = labeled_details
            continue

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

        if not result.success:
            print(f"[!] Warning: leaving {family_id} unlabeled: {result.error}")
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
                        apply_semantic_label_to_field(labeled_fields[field_index], label)

            labeled_details["field_hypotheses"] = labeled_fields
            labeled_details["llm_semantic_labeling"] = {
                "applied": result.applied_count,
                "rejected": result.rejected_count,
                "stage": "semantic_labeling",
            }

            # Mirror the consensus labels into the 09_semantics summary shape so
            # stage 12 folds them into FamilySemanticSummary: that is what the
            # evaluator and the HTML/MD "Semantic Labels" tables actually read.
            # Labels carry source=llm_consensus; stage 12 prefers them over the
            # heuristic labels at equal confidence.
            semantic_label_entries = []
            for log_entry in result.validation_log:
                if not log_entry.get("applied", False):
                    continue
                label = log_entry.get("label", {})
                field_index = label.get("field_index")
                if field_index is None or field_index >= len(fields):
                    continue
                target_field = fields[field_index]
                start = int(target_field.get("start", target_field.get("offset", 0)) or 0)
                length = int(target_field.get("length", target_field.get("width", 0)) or 0)
                encoding_type = label.get("encoding_type") or label.get("field_type")
                semantic_label_entries.append({
                    "start": start,
                    "length": length,
                    "label": label.get("semantic_role") or label.get("human_label") or "unknown",
                    "field_type": encoding_type,
                    "encoding_type": encoding_type,
                    "confidence": label.get("confidence", 0.0),
                    "evidence": {
                        "source": "llm_consensus",
                        "support": label.get("evidence", []),
                        "backend": "local_finetuned",
                    },
                })
            if semantic_label_entries:
                llm_semantics[family_id] = {
                    "family_id": family_id,
                    "role": family_role or "unknown",
                    "confidence": max(float(entry["confidence"]) for entry in semantic_label_entries),
                    "field_labels": semantic_label_entries,
                    "notes": [f"{len(semantic_label_entries)} consensus labels from the fine-tuned model (stage 11b)."],
                }

        labeled_families[family_id] = labeled_details

    # Save labeled families, preserving the stage-07 dict schema
    output_data = labeled_families

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    # Merge consensus labels into the stage-09 semantics summary so downstream
    # stages (12, 16, 17, exports) see them without schema changes.
    if llm_semantics:
        semantics_path = Path(args.semantics_json) if args.semantics_json else None
        if semantics_path and semantics_path.is_file():
            with open(semantics_path, "r", encoding="utf-8") as f:
                semantics_summary = json.load(f)
            for family_id, llm_entry in llm_semantics.items():
                base = semantics_summary.get(family_id)
                if isinstance(base, dict) and isinstance(base.get("field_labels"), list):
                    # Keep heuristic labels that do not collide with an LLM label
                    # on the same (start, length) span; LLM labels win there.
                    llm_spans = {(entry["start"], entry["length"]) for entry in llm_entry["field_labels"]}
                    kept = [
                        entry for entry in base.get("field_labels", [])
                        if (int(entry.get("start", 0) or 0), int(entry.get("length", 0) or 0)) not in llm_spans
                    ]
                    base["field_labels"] = llm_entry["field_labels"] + kept
                    base["notes"] = (base.get("notes", []) or []) + llm_entry["notes"]
                else:
                    semantics_summary[family_id] = llm_entry
            with open(semantics_path, "w", encoding="utf-8") as f:
                json.dump(semantics_summary, f, indent=2)
            print(f"[+] Merged {len(llm_semantics)} families' consensus labels into {semantics_path}")

    print(f"\n[+] Wrote labeled families to {args.output_json}")
    print(f"[+] Total labels applied: {total_applied}")
    print(f"[+] Total labels rejected: {total_rejected}")
    print(f"[+] Stage results saved to {args.results_dir}")

    # API failures warn and keep fallback artifacts; other failures remain fatal.
    warn_or_fail_stage_failures(stage_results, render_only=args.render_only, stage_name="11b_label_semantics_llm", logger=logger)


if __name__ == "__main__":
    main()
