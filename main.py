from __future__ import annotations

import argparse
import importlib.metadata
import logging
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------
# Logging setup
# ---------------------------------------------------------
logging.basicConfig(
    filename="main.log",
    filemode="a",
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

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

logger.info("\n")
logger.info("-" * 110)
logger.info('-' + " " * 108 + '-')
logger.info("-" * 110)
logger.info("Project root: %s", PROJECT_ROOT)
logger.info("PYTHONPATH set to: %s", SRC_PATH)


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
    pairs_json = data_dir / "06_pairs.json"
    keywords_json = data_dir / "07_keywords.json"
    relations_json = data_dir / "08_relations.json"
    semantics_json = data_dir / "09_semantics.json"
    model_json = data_dir / "10_protocol_model.json"
    evaluation_json = data_dir / "11_evaluation.json"
    protocol_spec_md = output_dir / "protocol_report.md"
    llm_evidence_json = data_dir / "12_llm_evidence.json"
    llm_analysis_json = data_dir / "13_llm_analysis.json"
    llm_prompt_md = data_dir / "13_llm_prompt.md"
    evaluation_model_data_json = data_dir / "14_evaluation_model_data.json"
    final_evaluation_json = data_dir / "15_evaluation_result.json"
    html_report = output_dir / "protocol_report.html"

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
                ],
            ),
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
                ],
            ),
            (
                "11_infer_semantics",
                [_script("11_infer_semantics.py"), _path(families_json), _path(relations_json), _path(semantics_json)],
            ),
            (
                "12_build_protocol_model",
                [
                    _script("12_build_protocol_model.py"),
                    _path(families_json),
                    _path(model_json),
                    "--features-json",
                    _path(family_features_json),
                    "--keywords-json",
                    _path(keywords_json),
                    "--relations-json",
                    _path(relations_json),
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
                    _path(model_json),
                    _path(protocol_spec_md),
                    "--evaluation-json",
                    _path(evaluation_json),
                ],
            ),
            (
                "19_export_html",
                [
                    _script("19_export_html.py"),
                    _path(model_json),
                    _path(html_report),
                    "--evaluation-json",
                    _path(evaluation_json),
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

    llm_steps = [
        (
            "14_export_llm_evidence",
            [
                _script("14_export_llm_evidence.py"),
                _path(model_json),
                _path(llm_evidence_json),
                "--evaluation-json",
                _path(evaluation_json),
            ],
        ),
        (
            "15_analyze_with_llm",
            [
                _script("15_analyze_with_llm.py"),
                _path(llm_evidence_json),
                _path(llm_analysis_json),
                "--config",
                _path(args.llm_config),
                "--prompt-out",
                _path(llm_prompt_md),
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
        llm_steps[1][1].append("--render-only")
    if args.llm_template:
        llm_steps[1][1].extend(["--template", _path(args.llm_template)])
    if args.llm_temperature is not None:
        llm_steps[1][1].extend(["--temperature", str(args.llm_temperature)])
    if args.llm_max_tokens is not None:
        llm_steps[1][1].extend(["--max-tokens", str(args.llm_max_tokens)])
    insert_at = next(index for index, (step_name, _) in enumerate(pipeline) if step_name == "18_export_markdown")
    pipeline[insert_at:insert_at] = llm_steps
    for step_name, step_args in pipeline:
            if step_name in {"18_export_markdown", "19_export_html"}:
                step_args.extend(["--llm-analysis-json", _path(llm_analysis_json)])
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
    logger.info(" ")
    logger.info("------------------------------------- Starting step: %s", name)

    start = time.time()
    cmd = [sys.executable] + step_args
    cmd_str = " ".join(shlex.quote(part) for part in cmd)

    print(f"{YELLOW}Command: {cmd_str}{RESET}")
    logger.info("Command: %s", cmd_str)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_PATH)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, env=env)
        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        logger.info("STDOUT:\n%s", result.stdout.strip())
        if result.stderr:
            logger.warning("STDERR:\n%s", result.stderr)
        result.check_returncode()
        elapsed = time.time() - start
        print(f"{GREEN}[OK]{RESET} {name} completed in {elapsed:.2f}s")
        logger.info("Step completed: %s (%.2fs)", name, elapsed)
        return True
    except subprocess.CalledProcessError:
        elapsed = time.time() - start
        print(f"{RED}[FAILED]{RESET} {name} (after {elapsed:.2f}s)")
        logger.error("Step FAILED: %s (%.2fs)", name, elapsed)
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Protocol RE Pipeline Runner")
    runner_group = parser.add_argument_group("Runner - inputs, outputs, and execution control")
    collect_group = parser.add_argument_group("Stage 01 - collect_pcaps / Stage 02 - dedup_pcaps")
    extract_group = parser.add_argument_group("Stage 03 - extract_messages")
    family_group = parser.add_argument_group("Stage 04 - discover_families")
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
        help="Feature encoding for family discovery.",
    )
    family_group.add_argument(
        "--family-neural-model-path",
        type=Path,
        default=Path("pre_trained/industrial_VAE.pth"),
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

    llm_analysis_group.add_argument("--llm-config", type=Path, default=Path("LLM_config.json"), help="LLM config JSON for stage 15.")
    llm_analysis_group.add_argument("--llm-template", type=Path, help="Optional custom prompt template for stage 15 LLM analysis.")
    llm_analysis_group.add_argument("--llm-render-only", action="store_true", help="Only render the stage 15 LLM prompt; do not call the API.")
    llm_analysis_group.add_argument("--llm-temperature", type=float, default=0.1, help="Sampling temperature for stage 15 LLM analysis.")
    llm_analysis_group.add_argument("--llm-max-tokens", type=int, default=6000, help="Max output tokens for stage 15 LLM analysis.")

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
    if not args.llm_render_only and not args.llm_config.is_file():
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
    warn_missing_requirements()
    validate_args(args)
    prepare_output_dirs(args)

    if args.use_existing_messages:
        source = args.data_dir / "01_messages.jsonl"
        mode = "existing corpus"
    else:
        source = args.input_folder
        mode = "PCAP"
    logger.info("Input %s folder: %s", mode, source)
    print(f"{GREEN}{mode} input:{RESET} {source}\n")

    try:
        pipeline = build_pipeline(args)
    except ValueError as exc:
        raise SystemExit(f"{RED}Error:{RESET} {exc}") from exc

    for name, step_args in pipeline:
        ok = run_step(name, step_args)
        if not ok:
            print(f"{RED}\nPipeline aborted due to failure in step: {name}{RESET}")
            logger.error("Pipeline aborted at step: %s", name)
            sys.exit(1)

    elapsed = time.time() - start
    print(f"\n{GREEN}Pipeline completed successfully!{RESET}")
    print(f"{GREEN}Total execution time:{RESET} {elapsed:.2f}s")
    print(f"{GREEN}Output files:{RESET}")
    for path in output_paths(args):
        print(f"  - {path}")
    logger.info("Pipeline finished successfully")
    logger.info(f"Total execution time: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
