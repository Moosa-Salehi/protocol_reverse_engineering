from __future__ import annotations

import argparse
import logging
import os
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

# Ensure child scripts can import the local package without installation.
os.environ["PYTHONPATH"] = str(SRC_PATH)

logger.info("-" * 109)
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
    features_dir = data_dir / "03_features"
    family_features_json = features_dir / "family_features.json"
    families_json = data_dir / "04_families.json"
    pairs_json = data_dir / "05_pairs.json"
    keywords_json = data_dir / "06_keywords.json"
    subclusters_json = data_dir / "07_subcluster_hypotheses.json"
    relations_json = data_dir / "08_relations.json"
    semantics_json = data_dir / "09_semantics.json"
    model_json = data_dir / "10_protocol_model.json"
    evaluation_json = data_dir / "11_evaluation.json"
    protocol_spec_md = output_dir / "protocol_spec.md"
    llm_evidence_json = output_dir / "llm_evidence.json"

    pipeline: list[tuple[str, list[str]]] = []

    if args.legacy_json:
        corpus_step = [
            _script("03_alt_build_corpus.py"),
            _path(args.legacy_json),
            _path(messages_jsonl),
        ]
        if args.service_port is not None:
            corpus_step.extend(["--service-port", str(args.service_port)])
        if args.deduplicate_payloads:
            corpus_step.append("--deduplicate-payloads")
        pipeline.append(("03_alt_build_corpus", corpus_step))
    else:
        if not args.skip_collect:
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
                    "--max-workers",
                    str(args.max_workers),
                    "--reassembly-mode",
                    args.reassembly_mode,
                ],
            )
        )
        if args.service_port is not None:
            pipeline[-1][1].extend(["--service-port", str(args.service_port)])

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
                ],
            ),
            (
                "05_extract_features",
                [
                    _script("05_extract_features.py"),
                    _path(messages_jsonl),
                    _path(features_dir),
                    "--assignments-json",
                    _path(assignments_json),
                ],
            ),
            (
                "06_infer_boundaries",
                [
                    _script("06_infer_boundaries.py"),
                    _path(messages_jsonl),
                    _path(families_json),
                    "--assignments-json",
                    _path(assignments_json),
                    "--features-json",
                    _path(family_features_json),
                ],
            ),
            (
                "07_pair_requests_responses",
                [
                    _script("07_pair_requests_responses.py"),
                    _path(messages_jsonl),
                    _path(pairs_json),
                    "--assignments-json",
                    _path(assignments_json),
                ],
            ),
            (
                "08_infer_keywords",
                [
                    _script("08_infer_keywords.py"),
                    _path(messages_jsonl),
                    _path(keywords_json),
                    "--assignments-json",
                    _path(assignments_json),
                ],
            ),
            (
                "09_compare_subcluster",
                [
                    _script("09_compare_subcluster_hypotheses.py"),
                    _path(messages_jsonl),
                    _path(subclusters_json),
                    "--assignments-json",
                    _path(assignments_json),
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
                    "--relations-json",
                    _path(relations_json),
                    "--semantics-json",
                    _path(semantics_json),
                ],
            ),
            ("13_export_markdown", [_script("13_export_markdown.py"), _path(model_json), _path(protocol_spec_md)]),
            (
                "14_export_llm_evidence",
                [_script("14_export_llm_evidence.py"), _path(model_json), _path(llm_evidence_json)],
            ),
            (
                "15_evaluate_pipeline",
                [
                    _script("15_evaluate_pipeline.py"),
                    _path(messages_jsonl),
                    _path(assignments_json),
                    _path(families_json),
                    _path(pairs_json),
                    _path(relations_json),
                    _path(evaluation_json),
                ],
            ),
        ]
    )

    if args.stop_after:
        for index, (name, _) in enumerate(pipeline):
            if name == args.stop_after:
                return pipeline[: index + 1]
        raise ValueError(f"Unknown --stop-after step: {args.stop_after}")

    return pipeline


def run_step(name: str, step_args: list[str]) -> bool:
    print(f"\n{CYAN}--- Running step: {name} ---{RESET}")
    logger.info("Starting step: %s", name)

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
        logger.info("STDOUT:\n%s", result.stdout)
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
    parser.add_argument(
        "input_folder",
        nargs="?",
        type=Path,
        help="Folder containing PCAP files, or an existing pcap dir when --skip-collect is used.",
    )
    parser.add_argument(
        "--legacy-json",
        type=Path,
        help="Use an extracted protocol-x-payloads JSON folder instead of PCAP input.",
    )
    parser.add_argument(
        "--skip-collect",
        action="store_true",
        help="Treat input_folder as the already-normalized PCAP directory and skip collect/dedup stages.",
    )
    parser.add_argument("--service-port", type=int, help="Optional TCP port filter. If omitted, all TCP payloads are extracted.")
    parser.add_argument("--max-workers", type=int, default=4, help="Parallel workers for PCAP extraction.")
    parser.add_argument(
        "--reassembly-mode",
        choices=["packet", "stream"],
        default="packet",
        help="PCAP extraction mode: packet payloads or reconstructed directional TCP streams.",
    )
    parser.add_argument("--family-sample-size", type=int, default=100000, help="Max unique messages for clustering.")
    parser.add_argument("--deduplicate-payloads", action="store_true", help="Drop duplicate payloads in --legacy-json mode.")
    parser.add_argument("--pcap-dir", type=Path, default=Path("pcaps"), help="Normalized PCAP output/input directory.")
    parser.add_argument("--data-dir", type=Path, default=Path("data"), help="Pipeline data artifact directory.")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Rendered report output directory.")
    parser.add_argument("--stop-after", help="Run through the named pipeline step and then stop; useful for smoke tests.")
    return parser.parse_args()


def _resolve_under_project(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def validate_args(args: argparse.Namespace) -> None:
    args.pcap_dir = _resolve_under_project(args.pcap_dir)
    args.data_dir = _resolve_under_project(args.data_dir)
    args.output_dir = _resolve_under_project(args.output_dir)

    if args.legacy_json:
        args.legacy_json = args.legacy_json.resolve()
        if not args.legacy_json.is_dir():
            raise SystemExit(f"{RED}Error:{RESET} legacy JSON folder does not exist: {args.legacy_json}")
        if args.input_folder is not None:
            print(f"{YELLOW}Note:{RESET} ignoring input_folder because --legacy-json was provided.")
        return

    if args.input_folder is None:
        raise SystemExit(f"{RED}Error:{RESET} input_folder is required unless --legacy-json is provided.")

    args.input_folder = args.input_folder.resolve()
    if not args.input_folder.is_dir():
        raise SystemExit(f"{RED}Error:{RESET} input folder does not exist: {args.input_folder}")


def prepare_output_dirs(args: argparse.Namespace) -> None:
    args.data_dir.mkdir(parents=True, exist_ok=True)
    (args.data_dir / "03_features").mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if not args.legacy_json and not args.skip_collect:
        args.pcap_dir.mkdir(parents=True, exist_ok=True)


def main() -> None:
    print(f"{CYAN}=== Protocol RE Pipeline Runner ==={RESET}")
    logger.info("Pipeline started")

    args = parse_args()
    validate_args(args)
    prepare_output_dirs(args)

    source = args.legacy_json if args.legacy_json else args.input_folder
    mode = "legacy JSON" if args.legacy_json else "PCAP"
    logger.info("Input %s folder: %s", mode, source)
    print(f"{GREEN}{mode} input folder:{RESET} {source}\n")

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

    print(f"\n{GREEN}Pipeline completed successfully!{RESET}")
    logger.info("Pipeline finished successfully")


if __name__ == "__main__":
    main()
