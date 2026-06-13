from __future__ import annotations

import argparse
import importlib.metadata
import os
import re
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path

# Import structured logging
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from protocol_re.utils.logging import setup_pipeline_logging

# ---------------------------------------------------------
# Color output (fallback if colorama absent)
# ---------------------------------------------------------
try:
    from colorama import Fore, Style, init

    init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    CYAN = Fore.CYAN
    YELLOW = Fore.YELLOW
    RESET = Style.RESET_ALL
except Exception:
    GREEN = RED = CYAN = YELLOW = RESET = ""

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
DEFAULT_MAX_MESSAGES = 200_000

# Ensure child scripts can import the local package without installation.
os.environ["PYTHONPATH"] = str(SRC_PATH)

# Setup structured logging
log_dir = PROJECT_ROOT / "logs"
logger = setup_pipeline_logging(log_dir)

def _script(name: str) -> str:
    return str(PROJECT_ROOT / "scripts" / name)


def _path(path: Path) -> str:
    return str(path)


def build_pipeline(args: argparse.Namespace) -> list[tuple[str, list[str]]]:
    data_dir = args.data_dir
    pcap_dir = args.pcap_dir
    output_dir = args.output_dir

    messages_jsonl = data_dir / "01_messages.jsonl"
    assignments_json = data_dir / "02_family_assignments.json"
    family_features_json = data_dir / "03_family_features.json"
    framing_json = data_dir / "04_framing.json"
    families_json = data_dir / "05_families.json"
    families_refined_json = data_dir / "05_families_refined.json" 
    families_labeled_json = data_dir / "05_families_labeled.json"
    pairs_json = data_dir / "06_pairs.json"
    keywords_json = data_dir / "07_keywords.json"
    relations_json = data_dir / "08_relations.json"
    relations_validated_json = data_dir / "08_relations_validated.json"
    semantics_json = data_dir / "09_semantics.json"
    model_json = data_dir / "10_protocol_model.json"
    refined_model_json = data_dir / "10_protocol_model.refined.json"
    evaluation_json = data_dir / "11_evaluation.json"
    protocol_spec_md = output_dir / "protocol_report.md"
    llm_evidence_json = data_dir / "12_llm_evidence.json"
    llm_analysis_json = data_dir / "13_llm_analysis.json"
    llm_prompt_md = data_dir / "13_llm_prompt.md"
    llm_patches_json = data_dir / "13_llm_patches.json"
    llm_patch_validation_json = data_dir / "13_llm_patch_validation.json"
    evaluation_model_data_json = data_dir / "14_evaluation_model_data.json"
    final_evaluation_json = data_dir / "15_evaluation_result.json"
    html_report = output_dir / "protocol_report.html"
    llm_stage_results_dir = data_dir / "llm_stage_results"

    pipeline: list[tuple[str, list[str]]] = []

    if not args.use_existing_messages:
        if args.collect:
            pipeline.extend(
                [
                    ("01_collect_pcaps", [_script("01_collect_pcaps.py"), _path(args.input_folder), _path(pcap_dir)]),
                    ("02_dedup_pcaps", [_script("02_dedup_pcaps.py"), _path(pcap_dir), "--delete"]),
                ]
            )
            extraction_input = pcap_dir
        else:
            extraction_input = args.input_folder

        pipeline.append(
            (
                "03_extract_messages",
                [
                    _script("03_extract_messages.py"),
                    _path(extraction_input),
                    _path(messages_jsonl),
                    "--extraction-method",
                    args.extraction_method,
                    "--reassembly-mode",
                    args.reassembly_mode,
                ],
            )
        )
        if args.service_port is not None:
            pipeline[-1][1].extend(["--service-port", str(args.service_port)])
        if args.tshark_filter:
            pipeline[-1][1].extend(["--tshark-filter", args.tshark_filter])
        if args.extraction_method == "tshark":
            pipeline[-1][1].extend(
                [
                    "--packets-dir",
                    _path(args.data_dir / "payload_extraction" / "packets"),
                    "--payloads-dir",
                    _path(args.data_dir / "payload_extraction" / "payloads"),
                    "--tshark-workers",
                    str(args.tshark_workers),
                ]
            )
        if args.max_messages is not None:
            pipeline[-1][1].extend(["--max-messages", str(args.max_messages)])

    pipeline.extend(
        [
            (
                "04_discover_families",
                [
                    _script("04_discover_families.py"),
                    _path(messages_jsonl),
                    _path(assignments_json),
                    "--sample-size",
                    str(args.family_sample_size),
                    "--feature-mode",
                    args.family_feature_mode,
                    "--neural-model-path",
                    _path(args.family_neural_model_path),
                    "--neural-batch-size",
                    str(args.family_neural_batch_size),
                ],
            ),
            (
                "05_infer_framing",
                [
                    _script("05_infer_framing.py"),
                    _path(messages_jsonl),
                    _path(assignments_json),
                    _path(framing_json),
                ],
            ),
            (
                "06_extract_features",
                [
                    _script("06_extract_features.py"),
                    _path(messages_jsonl),
                    _path(family_features_json),
                    "--assignments-json",
                    _path(assignments_json),
                    "--feature-mode",
                    args.family_feature_mode,
                    "--neural-model-path",
                    _path(args.family_neural_model_path),
                    "--neural-batch-size",
                    str(args.family_neural_batch_size),
                ],
            ),
            (
                "07_infer_boundaries",
                [
                    _script("07_infer_boundaries.py"),
                    _path(messages_jsonl),
                    _path(families_json),
                    "--assignments-json",
                    _path(assignments_json),
                    "--features-json",
                    _path(family_features_json),
                    "--framing-json",
                    _path(framing_json),
                    "--score-threshold",
                    str(args.boundary_score_threshold),
                ],
            ),
        ]
    )

    # Stage 07b - LLM Boundary Refinement
    pipeline.append(
        (
            "07b_refine_boundaries_llm",
            [
                _script("07b_refine_boundaries_llm.py"),
                _path(messages_jsonl),
                _path(families_json),
                _path(families_refined_json),
                "--assignments-json",
                _path(assignments_json),
                "--features-json",
                _path(family_features_json),
                "--llm-config",
                _path(args.llm_config),
                "--min-confidence",
                str(args.llm_boundary_confidence),
                "--results-dir",
                _path(llm_stage_results_dir),
            ]
            + (["--render-only"] if args.llm_render_only else [])
            + (["--use-user-provided-response"] if args.use_user_provided_response else []),
        )
    )
    # Use refined families for subsequent stages
    families_for_model = families_refined_json

    pipeline.extend([
            (
                "08_pair_requests_responses",
                [
                    _script("08_pair_requests_responses.py"),
                    _path(messages_jsonl),
                    _path(pairs_json),
                    "--assignments-json",
                    _path(assignments_json),
                ],
            ),
            (
                "09_infer_keywords",
                [
                    _script("09_infer_keywords.py"),
                    _path(messages_jsonl),
                    _path(keywords_json),
                    "--assignments-json",
                    _path(assignments_json),
                    "--features-json",
                    _path(family_features_json),
                    "--framing-json",
                    _path(framing_json),
                    "--neural-model-path",
                    _path(args.family_neural_model_path),
                    "--salience-cache-path",
                    _path(args.discriminator_salience_cache_path),
                ],
            ),
            (
                "10_infer_relations",
                [
                    _script("10_infer_relations.py"),
                    _path(messages_jsonl),
                    _path(assignments_json),
                    _path(pairs_json),
                    _path(relations_json),
                    "--min-edge-pairs",
                    str(args.min_edge_pairs),
                    "--min-edge-lift",
                    str(args.min_edge_lift),
                    "--max-response-families-per-request",
                    str(args.max_response_families_per_request),
                    "--min-echo-support",
                    str(args.min_echo_support),
                    "--min-length-support",
                    str(args.min_length_support),
                    "--min-relation-confidence",
                    str(args.min_relation_confidence),
                ],
            ),
        ])

    # Stage 10b - LLM Relation Validation
    pipeline.append(
        (
            "10b_validate_relations_llm",
            [
                _script("10b_validate_relations_llm.py"),
                _path(relations_json),
                _path(relations_validated_json),
                "--families-json",
                _path(families_for_model),
                "--llm-config",
                _path(args.llm_config),
                "--min-confidence",
                str(args.llm_relation_confidence),
                "--results-dir",
                _path(llm_stage_results_dir),
            ]
            + (["--render-only"] if args.llm_render_only else [])
            + (["--use-user-provided-response"] if args.use_user_provided_response else []),
        )
    )
    # Use validated relations for subsequent stages
    relations_for_model = relations_validated_json

    pipeline.extend([
            (
                "11_infer_semantics",
                [
                    _script("11_infer_semantics.py"),
                    _path(families_for_model),
                    _path(relations_for_model),
                    _path(semantics_json),
                    "--framing-json",
                    _path(framing_json),
                    "--features-json",
                    _path(family_features_json),
                    "--keywords-json",
                    _path(keywords_json),
                ],
            ),
        ])

    # Stage 11b - LLM Semantic Labeling
    pipeline.append(
        (
            "11b_label_semantics_llm",
            [
                _script("11b_label_semantics_llm.py"),
                _path(families_for_model),
                _path(families_labeled_json),
                "--relations-json",
                _path(relations_for_model),
                "--features-json",
                _path(family_features_json),
                "--messages-jsonl",
                _path(messages_jsonl),
                "--assignments-json",
                _path(assignments_json),
                "--llm-config",
                _path(args.llm_config),
                "--min-confidence",
                str(args.llm_semantic_confidence),
                "--results-dir",
                _path(llm_stage_results_dir),
            ]
            + (["--render-only"] if args.llm_render_only else [])
            + (["--use-user-provided-response"] if args.use_user_provided_response else []),
        )
    )
    # Use labeled families for protocol model
    families_for_model = families_labeled_json

    pipeline.extend([
            (
                "12_build_protocol_model",
                [
                    _script("12_build_protocol_model.py"),
                    _path(families_for_model),
                    _path(model_json),
                    "--features-json",
                    _path(family_features_json),
                    "--keywords-json",
                    _path(keywords_json),
                    "--relations-json",
                    _path(relations_for_model),
                    "--semantics-json",
                    _path(semantics_json),
                    "--framing-json",
                    _path(framing_json),
                ],
            ),
            (
                "13_evaluate_pipeline",
                [
                    _script("13_evaluate_pipeline.py"),
                    _path(messages_jsonl),
                    _path(assignments_json),
                    _path(families_json),
                    _path(pairs_json),
                    _path(relations_json),
                    _path(evaluation_json),
                    "--semantics-json",
                    _path(semantics_json),
                    "--framing-json",
                    _path(framing_json),
                ],
            ),
            (
                "18_export_markdown",
                [
                    _script("18_export_markdown.py"),
                    _path(refined_model_json),
                    _path(protocol_spec_md),
                    "--evaluation-json",
                    _path(evaluation_json),
                ],
            ),
            (
                "19_export_html",
                [
                    _script("19_export_html.py"),
                    _path(refined_model_json),
                    _path(html_report),
                    "--evaluation-json",
                    _path(evaluation_json),
                    "--llm-stage-results-dir",
                    _path(llm_stage_results_dir),
                ],
            ),
        ]
    )
    if args.allow_self_relations:
        for step_name, step_args in pipeline:
            if step_name == "10_infer_relations":
                step_args.append("--allow-self-relations")
                break
    if args.family_latent_cache_path:
        for step_name, step_args in pipeline:
            if step_name in {"04_discover_families", "06_extract_features"}:
                step_args.extend(["--latent-cache-path", _path(args.family_latent_cache_path)])

    if args.family_standardize_latent:
        for step_name, step_args in pipeline:
            if step_name == "04_discover_families":
                step_args.append("--standardize-latent")
                break

    for step_name, step_args in pipeline:
        if step_name == "04_discover_families":
            step_args.append(
                "--refine-discriminator" if not args.no_family_refine_discriminator else "--no-refine-discriminator"
            )
            break

    # Add fusion method for hybrid mode
    if args.family_feature_mode == "hybrid":
        for step_name, step_args in pipeline:
            if step_name == "04_discover_families":
                step_args.extend(["--fusion-method", args.fusion_method])
                if args.fusion_method == "fixed":
                    step_args.extend([
                        "--fusion-neural-weight", str(args.fusion_neural_weight),
                        "--fusion-structural-weight", str(args.fusion_structural_weight),
                    ])
                break

    # Add layer detection flags if enabled
    if args.enable_layer_detection:
        for step_name, step_args in pipeline:
            if step_name == "05_infer_framing":
                step_args.extend(["--detect-layers", "--layer-min-confidence", str(args.layer_min_confidence)])
            elif step_name == "04_discover_families":
                step_args.extend(["--layer-aware", "--framing-json", _path(framing_json), "--layer-min-confidence", str(args.layer_min_confidence)])

    # Add boundary detection parameters
    for step_name, step_args in pipeline:
        if step_name == "07_infer_boundaries":
            step_args.extend(["--max-fields", str(args.boundary_max_fields)])
            step_args.extend(["--merge-width-targets", args.boundary_merge_width_targets])
            step_args.extend(["--length-match-threshold", str(args.boundary_length_match_threshold)])
            step_args.extend(["--boundary-confidence-weight", str(args.boundary_confidence_weight)])
            if args.boundary_entropy_weight is not None:
                step_args.extend(["--entropy-weight", str(args.boundary_entropy_weight)])
            if args.disable_boundary_length_validator:
                step_args.extend(["--disable-length-validator"])
            if args.no_boundary_merging:
                step_args.extend(["--no-merging"])
            break

    llm_steps = [
        (
            "15_analyze_with_llm",
            [
                _script("15_analyze_with_llm.py"),
                _path(model_json),  # Changed from llm_evidence_json to model_json
                _path(llm_analysis_json),
                "--config",
                _path(args.llm_config),
                "--prompt-out",
                _path(llm_prompt_md),
                "--evaluation-json",
                _path(evaluation_json),
                # Multi-stage summaries (auto-detected if files exist)
                "--boundary-summary",
                _path(families_refined_json),
                "--semantic-summary",
                _path(families_labeled_json),
                "--relation-summary",
                _path(relations_validated_json),
            ],
        ),
        (
            "15b_apply_llm_refinement",
            [
                _script("15b_apply_llm_refinement.py"),
                _path(model_json),
                _path(llm_analysis_json),
                _path(refined_model_json),
                "--evidence-json",
                _path(llm_evidence_json),
                "--schema-json",
                _path(PROJECT_ROOT / "assets" / "schema" / "protocol_model.schema.json"),
                "--patches-out",
                _path(llm_patches_json),
                "--validation-out",
                _path(llm_patch_validation_json),
            ],
        ),
        (
            "16_prepare_evaluation_data",
            [
                _script("16_prepare_evaluation_data.py"),
                _path(model_json),
                _path(evaluation_json),
                _path(llm_analysis_json),
                _path(evaluation_model_data_json),
                "--refined-protocol-model-json",
                _path(refined_model_json),
                "--patch-validation-json",
                _path(llm_patch_validation_json),
            ],
        ),
    ]

    if args.ground_truth_json:
        llm_steps.append(
            (
                "17_evaluate_protocol_spec",
                [
                    _script("17_evaluate_protocol_spec.py"),
                    _path(evaluation_model_data_json),
                    _path(args.ground_truth_json),
                    _path(final_evaluation_json),
                ],
            )
        )
    if args.llm_render_only:
        for step_name, step_args in llm_steps:
            if step_name == "15_analyze_with_llm":
                step_args.append("--render-only")
    if args.use_user_provided_response:
        for step_name, step_args in llm_steps:
            if step_name == "15_analyze_with_llm":
                step_args.append("--use-user-provided-response")
    if args.llm_template:
        for step_name, step_args in llm_steps:
            if step_name == "15_analyze_with_llm":
                step_args.extend(["--template", _path(args.llm_template)])
    if args.reuse_llm_responses:
        for step_name, step_args in pipeline + llm_steps:
            if step_name in {
                "07b_refine_boundaries_llm",
                "10b_validate_relations_llm",
                "11b_label_semantics_llm",
                "15_analyze_with_llm",
            }:
                step_args.append("--reuse-llm-responses")
    insert_at = next(index for index, (step_name, _) in enumerate(pipeline) if step_name == "18_export_markdown")
    pipeline[insert_at:insert_at] = llm_steps
    for step_name, step_args in pipeline:
            if step_name in {"18_export_markdown", "19_export_html"}:
                step_args.extend(["--llm-analysis-json", _path(llm_analysis_json)])
                if step_name == "19_export_html":
                    step_args.extend(["--patch-validation-json", _path(llm_patch_validation_json)])
                if args.ground_truth_json:
                    step_args.extend(["--final-evaluation-json", _path(final_evaluation_json)])

    if args.stop_after:
        for index, (name, _) in enumerate(pipeline):
            if name == args.stop_after:
                return pipeline[: index + 1]
        raise ValueError(f"Unknown --stop-after step: {args.stop_after}")

    return pipeline


def run_step(name: str, step_args: list[str]) -> bool:
    print(f"\n{CYAN}--- Running step: {name} ---{RESET}")
    # These mirror the print()s above/below for the on-disk log; file_only keeps
    # them out of the console so output isn't duplicated.
    logger.info(" ", file_only=True)
    logger.info("------------------------------------- Starting step: %s", name, file_only=True)

    start = time.time()
    cmd = [sys.executable, "-u"] + step_args
    cmd_str = " ".join(shlex.quote(part) for part in cmd)

    print(f"{YELLOW}Command: {cmd_str}{RESET}")
    logger.info("Command: %s", cmd_str, file_only=True)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_PATH)
    env["PYTHONUNBUFFERED"] = "1"

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=PROJECT_ROOT,
            env=env,
        )

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        def stream_output(stream, target, sink: list[str]) -> None:
            try:
                for line in stream:
                    sink.append(line)
                    print(line, end="", file=target, flush=True)
            finally:
                stream.close()

        assert proc.stdout is not None
        assert proc.stderr is not None
        stdout_thread = threading.Thread(target=stream_output, args=(proc.stdout, sys.stdout, stdout_lines))
        stderr_thread = threading.Thread(target=stream_output, args=(proc.stderr, sys.stderr, stderr_lines))
        stdout_thread.start()
        stderr_thread.start()

        return_code = proc.wait()
        stdout_thread.join()
        stderr_thread.join()

        stdout = "".join(stdout_lines)
        stderr = "".join(stderr_lines)
        logger.info("STDOUT:\n%s", stdout.strip(), file_only=True)
        if stderr:
            logger.warning("STDERR:\n%s", stderr, file_only=True)
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, cmd, output=stdout, stderr=stderr)
        elapsed = time.time() - start
        print(f"{GREEN}[OK]{RESET} {name} completed in {elapsed:.2f}s")
        logger.info("Step completed: %s (%.2fs)", name, elapsed, file_only=True)
        return True
    except subprocess.CalledProcessError:
        elapsed = time.time() - start
        print(f"{RED}[FAILED]{RESET} {name} (after {elapsed:.2f}s)")
        logger.error("Step FAILED: %s (%.2fs)", name, elapsed, file_only=True)
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Protocol RE Pipeline Runner")
    runner_group = parser.add_argument_group("Runner - inputs, outputs, and execution control")
    collect_group = parser.add_argument_group("Stage 01 - collect_pcaps / Stage 02 - dedup_pcaps")
    extract_group = parser.add_argument_group("Stage 03 - extract_messages")
    family_group = parser.add_argument_group("Stage 04 - discover_families")
    boundary_group = parser.add_argument_group("Stage 07 - infer_boundaries")
    discriminator_group = parser.add_argument_group("Stage 09 - discriminator/opcode discovery")
    relations_group = parser.add_argument_group("Stage 10 - infer_relations")
    llm_analysis_group = parser.add_argument_group("Stage 15 - analyze_with_llm")
    final_eval_group = parser.add_argument_group("Stage 17 - evaluate_protocol_spec")

    runner_group.add_argument(
        "input_folder",
        nargs="?",
        type=Path,
        help="Folder containing PCAP files. By default, this is treated as an existing normalized PCAP directory.",
    )
    runner_group.add_argument(
        "--use-existing-messages",
        action="store_true",
        help="Skip corpus extraction/building and use data/01_messages.jsonl from --data-dir.",
    )
    runner_group.add_argument("--pcap-dir", type=Path, default=Path("pcaps"), help="Normalized PCAP output/input directory.")
    runner_group.add_argument("--data-dir", type=Path, default=Path("data"), help="Pipeline data artifact directory.")
    runner_group.add_argument("--output-dir", type=Path, default=Path("output"), help="Rendered report output directory.")
    runner_group.add_argument("--stop-after", help="Run through the named pipeline step and then stop; useful for smoke tests.")

    collect_group.add_argument(
        "--collect",
        action="store_true",
        help="Collect PCAP files into --pcap-dir and deduplicate before extraction.",
    )

    extract_group.add_argument("--max-messages", type=int, default=DEFAULT_MAX_MESSAGES, help="Maximum messages to extract/write.")
    extract_group.add_argument(
        "--extraction-method",
        choices=["tshark", "tcp"],
        default="tshark",
        help="Message extraction method. tshark uses --tshark-filter; tcp is the legacy Scapy TCP port extractor.",
    )
    extract_group.add_argument("--tshark-filter", help="TShark display filter for the target protocol, for example mbtcp or s7comm.")
    extract_group.add_argument("--tshark-workers", type=int, default=4, help="Maximum parallel TShark worker processes.")
    extract_group.add_argument("--service-port", type=int, help="Legacy TCP extractor port filter. Used with --extraction-method tcp.")
    extract_group.add_argument(
        "--reassembly-mode",
        choices=["packet", "stream"],
        default="stream",
        help="Legacy TCP extraction mode: packet payloads or reconstructed directional TCP streams.",
    )

    family_group.add_argument("--family-sample-size", type=int, default=100000, help="Max unique messages for clustering.")
    family_group.add_argument(
        "--family-feature-mode",
        choices=["raw_bytes", "structural", "neural", "hybrid"],
        default="hybrid",
        help="Feature encoding for family discovery. Default: raw_bytes.",
    )
    family_group.add_argument(
        "--family-neural-model-path",
        type=Path,
        default=Path("assets/pre_trained/industrial_VAE.pth"),
        help="Optional VAE encoder checkpoint for neural/hybrid family discovery.",
    )
    family_group.add_argument(
        "--family-latent-cache-path",
        type=Path,
        default=Path("data/02_latent_cache.json"),
        help="Cache path for payload-hash neural latent vectors.",
    )
    family_group.add_argument(
        "--family-neural-batch-size",
        type=int,
        default=256,
        help="Batch size for optional neural latent extraction.",
    )
    family_group.add_argument(
        "--family-standardize-latent",
        dest="family_standardize_latent",
        action="store_true",
        help="Opt in to per-corpus z-score of neural latent features for family discovery. "
             "Default off: it amplifies noise latent dimensions and lowered message-type F1 in testing.",
    )
    family_group.set_defaults(family_standardize_latent=False)
    family_group.add_argument(
        "--no-family-refine-discriminator",
        action="store_true",
        help="disable discriminator-aware family refinement after clustering: re-derive family identity "
             "from the data-detected type-discriminator so families become opcode-pure and "
             "role-consistent. No-op when no discriminator is detected.",
    )
    family_group.add_argument(
        "--enable-neural-preprocessing",
        action="store_true",
        help="Enable enhanced neural preprocessing (masks variable fields like transaction IDs). Experimental.",
    )
    family_group.add_argument(
        "--enable-neural-quality-check",
        action="store_true",
        help="Enable neural feature quality checks with automatic fallback to raw_bytes if quality is poor. Experimental.",
    )
    family_group.add_argument(
        "--fusion-method",
        choices=["concat", "adaptive", "learned", "fixed"],
        default="adaptive",
        help="Hybrid feature fusion method: concat (simple), adaptive (quality-based), learned (MLP), fixed (manual weights). Default: adaptive.",
    )
    family_group.add_argument(
        "--fusion-neural-weight",
        type=float,
        default=0.5,
        help="Neural feature weight for fixed fusion method (0.0-1.0). Default: 0.5.",
    )
    family_group.add_argument(
        "--fusion-structural-weight",
        type=float,
        default=0.5,
        help="Structural feature weight for fixed fusion method (0.0-1.0). Default: 0.5.",
    )
    boundary_group.add_argument(
        "--boundary-score-threshold",
        type=float,
        default=2.0,
        help="Boundary score threshold (default: 2.0). Higher = fewer boundaries.",
    )
    boundary_group.add_argument(
        "--boundary-max-fields",
        type=int,
        default=15,
        help="Maximum fields per family (default: 15). Prevents excessive segmentation.",
    )
    boundary_group.add_argument(
        "--no-boundary-merging",
        action="store_true",
        help="Disable multi-pass segment merging (not recommended).",
    )
    boundary_group.add_argument(
        "--boundary-entropy-weight",
        type=float,
        default=None,
        help="Override entropy-jump weight for boundary scoring.",
    )
    boundary_group.add_argument(
        "--boundary-merge-width-targets",
        default="2,4",
        help="Comma-separated merged widths allowed by standard-width merge rules (default: 2,4).",
    )
    boundary_group.add_argument(
        "--boundary-length-match-threshold",
        type=float,
        default=0.8,
        help="Minimum corpus match ratio for length-field boundary protection (default: 0.8).",
    )
    boundary_group.add_argument(
        "--disable-boundary-length-validator",
        action="store_true",
        help="Disable statistical length-field boundary protection.",
    )
    boundary_group.add_argument(
        "--boundary-confidence-weight",
        type=float,
        default=0.45,
        help="Weight for corpus boundary-support term in segment confidence (default: 0.45).",
    )

    layer_group = parser.add_argument_group("Multi-layer protocol detection")
    layer_group.add_argument(
        "--enable-layer-detection",
        action="store_true",
        help="Enable multi-layer protocol detection. Detects transport headers and clusters on inner protocol only. Experimental.",
    )
    layer_group.add_argument(
        "--layer-min-confidence",
        type=float,
        default=0.6,
        help="Minimum confidence for layer boundary detection (default: 0.6).",
    )

    discriminator_group.add_argument(
        "--discriminator-salience-cache-path",
        type=Path,
        default=Path("data/07_salience_cache.json"),
        help="Cache path for learned discriminator/opcode salience scores.",
    )

    relations_group.add_argument("--min-edge-pairs", type=int, default=2, help="Minimum pair count for relation edge pruning.")
    relations_group.add_argument("--min-edge-lift", type=float, default=1.0, help="Minimum lift for relation edge pruning.")
    relations_group.add_argument(
        "--max-response-families-per-request",
        type=int,
        default=5,
        help="Maximum candidate response families to retain per request family before relation analysis.",
    )
    relations_group.add_argument("--allow-self-relations", action="store_true", help="Keep same-family request/response relation candidates.")
    relations_group.add_argument("--min-echo-support", type=float, default=0.95, help="Minimum support threshold for echo field detection (default: 0.95).")
    relations_group.add_argument("--min-length-support", type=float, default=0.95, help="Minimum support threshold for length relation detection (default: 0.95).")
    relations_group.add_argument("--min-relation-confidence", type=float, default=0.7, help="Minimum confidence threshold for keeping a relation (default: 0.7).")

    llm_analysis_group.add_argument("--llm-config", type=Path, default=Path("config/llm_config.json"), help="LLM config JSON for stage 15.")
    llm_analysis_group.add_argument("--llm-template", type=Path, help="Optional custom prompt template for stage 15 LLM analysis.")
    llm_analysis_group.add_argument("--llm-render-only", action="store_true", help="Only render the stage 15 LLM prompt; do not call the API.")
    llm_analysis_group.add_argument(
        "--reuse-llm-responses",
        action="store_true",
        help="Before each LLM API call, reuse an existing stage result JSON response when present.",
    )
    llm_analysis_group.add_argument(
        "--use-user-provided-response",
        action="store_true",
        help="Use filled response files from data/user_provided_LLM_responses before calling the LLM API.",
    )

    llm_analysis_group.add_argument("--llm-boundary-confidence", type=float, default=0.6, help="Minimum confidence for LLM boundary merge suggestions (default: 0.6).")
    llm_analysis_group.add_argument("--llm-semantic-confidence", type=float, default=0.5, help="Minimum confidence for LLM semantic labels (default: 0.5).")
    llm_analysis_group.add_argument("--llm-relation-confidence", type=float, default=0.7, help="Minimum confidence for LLM relation validation (default: 0.7).")

    final_eval_group.add_argument("--ground-truth-json", type=Path, help="Ground truth protocol JSON for final evaluation.")
    return parser.parse_args()


def warn_missing_requirements() -> None:
    requirements_path = PROJECT_ROOT / "requirements.txt"
    if not requirements_path.is_file():
        return

    missing = []
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        requirement = line.strip()
        if not requirement or requirement.startswith("#"):
            continue
        package_name = re.split(r"[<>=~!]", requirement, maxsplit=1)[0].strip()
        try:
            importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            package_name = package_name.replace("_", "-")
            try:
                importlib.metadata.version(package_name)
            except importlib.metadata.PackageNotFoundError:
                missing.append(requirement)

    if missing:
        print(f"{YELLOW}Warning:{RESET} missing requirements: {', '.join(missing)}")
        print(f"{YELLOW}Install with:{RESET} {sys.executable} -m pip install -r requirements.txt")


def _resolve_under_project(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def validate_args(args: argparse.Namespace) -> None:
    args.pcap_dir = _resolve_under_project(args.pcap_dir)
    args.data_dir = _resolve_under_project(args.data_dir)
    args.output_dir = _resolve_under_project(args.output_dir)
    args.llm_config = _resolve_under_project(args.llm_config)
    args.family_neural_model_path = _resolve_under_project(args.family_neural_model_path)
    if args.family_latent_cache_path:
        args.family_latent_cache_path = _resolve_under_project(args.family_latent_cache_path)
    if args.discriminator_salience_cache_path:
        args.discriminator_salience_cache_path = _resolve_under_project(args.discriminator_salience_cache_path)
    messages_jsonl = args.data_dir / "01_messages.jsonl"
    if args.max_messages is not None and args.max_messages <= 0:
        raise SystemExit(f"{RED}Error:{RESET} --max-messages must be greater than 0.")
    if args.min_edge_pairs <= 0:
        raise SystemExit(f"{RED}Error:{RESET} --min-edge-pairs must be greater than 0.")
    if args.min_edge_lift < 0:
        raise SystemExit(f"{RED}Error:{RESET} --min-edge-lift must be non-negative.")
    if args.max_response_families_per_request <= 0:
        raise SystemExit(f"{RED}Error:{RESET} --max-response-families-per-request must be greater than 0.")
    if args.family_neural_batch_size <= 0:
        raise SystemExit(f"{RED}Error:{RESET} --family-neural-batch-size must be greater than 0.")
    if not args.llm_render_only and not args.use_user_provided_response and not args.llm_config.is_file():
        raise SystemExit(f"{RED}Error:{RESET} LLM config file does not exist: {args.llm_config}")
    if args.llm_template:
        args.llm_template = args.llm_template.resolve()
        if not args.llm_template.is_file():
            raise SystemExit(f"{RED}Error:{RESET} LLM template file does not exist: {args.llm_template}")
    if args.ground_truth_json:
        args.ground_truth_json = args.ground_truth_json.resolve()
        if not args.ground_truth_json.is_file():
            raise SystemExit(f"{RED}Error:{RESET} ground truth JSON file does not exist: {args.ground_truth_json}")

    if args.use_existing_messages:
        if not messages_jsonl.is_file():
            raise SystemExit(f"{RED}Error:{RESET} existing messages file does not exist: {messages_jsonl}")
        if args.input_folder is not None:
            args.input_folder = args.input_folder.resolve()
        return

    if args.extraction_method == "tshark" and not args.tshark_filter:
        raise SystemExit(f"{RED}Error:{RESET} --tshark-filter is required with --extraction-method tshark.")
    if args.tshark_workers <= 0:
        raise SystemExit(f"{RED}Error:{RESET} --tshark-workers must be greater than 0.")

    if args.input_folder is None:
        raise SystemExit(f"{RED}Error:{RESET} input_folder is required unless --use-existing-messages is provided.")

    args.input_folder = args.input_folder.resolve()
    if not args.input_folder.is_dir():
        raise SystemExit(f"{RED}Error:{RESET} input folder does not exist: {args.input_folder}")


def prepare_output_dirs(args: argparse.Namespace) -> None:
    args.data_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.collect:
        args.pcap_dir.mkdir(parents=True, exist_ok=True)


def output_paths(args: argparse.Namespace) -> list[Path]:
    paths = [
        args.output_dir / "protocol_report.md",
        args.output_dir / "protocol_report.html",
    ]
    return paths


def main() -> None:
    print(f"{CYAN}=== Protocol RE Pipeline Runner ==={RESET}")

    logger.info("Pipeline started")
    start = time.time()

    args = parse_args()

    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"PYTHONPATH set to: {SRC_PATH}")

    warn_missing_requirements()
    validate_args(args)
    prepare_output_dirs(args)

    if args.use_existing_messages:
        source = args.data_dir / "01_messages.jsonl"
        mode = "existing corpus"
    else:
        source = args.input_folder
        mode = "PCAP"
    logger.info(f"Input {mode} folder: {source}", file_only=True)
    print(f"{GREEN}{mode} input:{RESET} {source}\n")

    try:
        with logger.stage("build_pipeline"):
            pipeline = build_pipeline(args)
            logger.metric("pipeline_stages", len(pipeline), "stages")
    except ValueError as exc:
        logger.error(f"Pipeline build failed: {exc}")
        raise SystemExit(f"{RED}Error:{RESET} {exc}") from exc

    for idx, (name, step_args) in enumerate(pipeline, 1):
        logger.info(f"Stage {idx}/{len(pipeline)}: {name}")
        with logger.stage(name):
            ok = run_step(name, step_args)
            if not ok:
                print(f"{RED}\nPipeline aborted due to failure in step: {name}{RESET}")
                logger.error(f"Pipeline aborted at step: {name}")
                sys.exit(1)

    elapsed = time.time() - start
    print(f"\n{GREEN}Pipeline completed successfully!{RESET}")
    print(f"{GREEN}Total execution time:{RESET} {elapsed:.2f}s")
    print(f"{GREEN}Output files:{RESET}")
    for path in output_paths(args):
        print(f"  - {path}")

    logger.info("Pipeline finished successfully")
    logger.metric("total_execution_time", elapsed, "seconds")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
