#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.io.dedup_pcaps import find_duplicate_pcaps, remove_duplicates
from protocol_re.utils.logging import setup_stage_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Find and optionally delete duplicate PCAP files.")
    parser.add_argument("pcap_dir")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("02_dedup_pcaps", Path(args.log_dir))

    logger.info(f"Scanning for duplicate PCAPs in {args.pcap_dir}")
    logger.decision(
        decision="Delete duplicates" if args.delete else "Find duplicates only",
        reason="User configuration",
        delete_enabled=args.delete,
    )

    with logger.stage("find_duplicates"):
        duplicates = find_duplicate_pcaps(args.pcap_dir)
        logger.metric("duplicates_found", len(duplicates), "files")
        logger.info(f"Found {len(duplicates)} duplicate PCAPs")

    print(f"[+] Found {len(duplicates)} duplicate PCAPs")
    for duplicate in duplicates[:20]:
        print(f"    {duplicate.duplicate_path} == {duplicate.original_path}")

    if args.delete and duplicates:
        with logger.stage("remove_duplicates"):
            removed = remove_duplicates(duplicates)
            logger.metric("duplicates_removed", removed, "files")
            logger.info(f"Removed {removed} duplicate PCAPs")
        print(f"[+] Removed {removed} duplicate PCAPs")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
