import subprocess
import sys
import time
import os
import logging
from pathlib import Path
import argparse

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

# ---------------------------------------------------------
# Ensure PYTHONPATH=src
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
os.environ["PYTHONPATH"] = str(SRC_PATH)

logger.info("-------------------------------------------------------------------------------------------------------------")
logger.info("Project root: %s", PROJECT_ROOT)
logger.info("PYTHONPATH set to: %s", SRC_PATH)

# ---------------------------------------------------------
# Pipeline builder
# ---------------------------------------------------------
def build_pipeline(pcap_folder):
    return [
        # ("01_collect_pcaps",      ["scripts/01_collect_pcaps.py", str(pcap_folder), "pcaps"]),
        # ("02_dedup_pcaps",        ["scripts/02_dedup_pcaps.py", "pcaps", "--delete"]),
        # ("03_extract_messages",   ["scripts/03_extract_messages.py", "pcaps", "data/01_messages.jsonl"]),
        ("03_alt_build_corpus",   ["scripts/03_alt_build_corpus.py", "archive/protocol-x-payloads", "data/01_messages.jsonl", "--deduplicate-payloads"]),
        ("04_discover_families",  ["scripts/04_discover_families.py", "data/01_messages.jsonl", "data/02_family_assignments.json"]),
        ("05_extract_features",   ["scripts/05_extract_features.py", "data/01_messages.jsonl", "data/03_features", "--assignments-json", "data/02_family_assignments.json"]),
        ("06_infer_boundaries",   ["scripts/06_infer_boundaries.py", "data/01_messages.jsonl", "data/04_families.json", "--assignments-json", "data/02_family_assignments.json"]),
        ("07_pair_requests_responses", ["scripts/07_pair_requests_responses.py", "data/01_messages.jsonl", "data/05_pairs.json", "--assignments-json", "data/02_family_assignments.json"]),
        ("08_infer_keywords",     ["scripts/08_infer_keywords.py", "data/01_messages.jsonl", "data/06_keywords.json", "--assignments-json", "data/02_family_assignments.json"]),
        ("09_compare_subcluster", ["scripts/09_compare_subcluster_hypotheses.py", "data/01_messages.jsonl", "data/07_subcluster_hypotheses.json", "--assignments-json", "data/02_family_assignments.json"]),
        ("10_infer_relations",    ["scripts/10_infer_relations.py", "data/01_messages.jsonl", "data/02_family_assignments.json", "data/05_pairs.json", "data/08_relations.json"]),
        ("11_infer_semantics",    ["scripts/11_infer_semantics.py", "data/04_families.json", "data/08_relations.json", "data/09_semantics.json"]),
        ("12_build_protocol_model", ["scripts/12_build_protocol_model.py", "data/04_families.json", "data/10_protocol_model.json", "--relations-json", "data/08_relations.json", "--semantics-json", "data/09_semantics.json"]),
        ("13_export_markdown",    ["scripts/13_export_markdown.py", "data/10_protocol_model.json", "output/protocol_spec.md"]),
    ]

# ---------------------------------------------------------
# Execute pipeline step
# ---------------------------------------------------------
def run_step(name, args):

    print(f"\n{CYAN}--- Running step: {name} ---{RESET}")
    logger.info("Starting step: %s", name)

    start = time.time()

    cmd = [sys.executable] + args
    cmd_str = " ".join(cmd)

    print(f"{YELLOW}Command: {cmd_str}{RESET}")
    logger.info("Command: %s", cmd_str)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        logger.info("STDOUT:\n%s", result.stdout)
        if result.stderr:
            logger.warning("STDERR:\n%s", result.stderr)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)
        elapsed = time.time() - start
        print(f"{GREEN}[OK]{RESET} {name} completed in {elapsed:.2f}s")
        logger.info("Step completed: %s (%.2fs)", name, elapsed)
        return True
    except subprocess.CalledProcessError:
        elapsed = time.time() - start
        print(f"{RED}[FAILED]{RESET} {name} (after {elapsed:.2f}s)")
        logger.error("Step FAILED: %s (%.2fs)", name, elapsed)
        return False

# ---------------------------------------------------------
# Argument parser
# ---------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Protocol RE Pipeline Runner"
    )
    parser.add_argument(
        "pcap_folder",
        type=Path,
        help="Path to folder containing PCAP files"
    )
    return parser.parse_args()

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    print(f"{CYAN}=== Protocol RE Pipeline Runner ==={RESET}")
    logger.info("Pipeline started")

    args = parse_args()
    pcap_path = args.pcap_folder.resolve()

    logger.info("Input PCAP folder: %s", pcap_path)
    if not pcap_path.exists() or not pcap_path.is_dir():
        print(f"{RED}Error:{RESET} folder does not exist: {pcap_path}")
        logger.error("PCAP folder does not exist: %s", pcap_path)
        sys.exit(1)

    print(f"{GREEN}PCAP input folder:{RESET} {pcap_path}\n")

    pipeline = build_pipeline(pcap_path)

    for name, args in pipeline:
        ok = run_step(name, args)
        if not ok:
            print(f"{RED}\nPipeline aborted due to failure in step: {name}{RESET}")
            logger.error("Pipeline aborted at step: %s", name)
            sys.exit(1)

    print(f"\n{GREEN}Pipeline completed successfully!{RESET}")

    logger.info("Pipeline finished successfully")
if __name__ == "__main__":
    main()
