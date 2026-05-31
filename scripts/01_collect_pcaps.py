#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.io.pcap_collect import collect_pcaps
from protocol_re.utils.logging import setup_stage_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect PCAP files from a source tree into one normalized directory.")
    parser.add_argument("source_root")
    parser.add_argument("output_dir")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("01_collect_pcaps", Path(args.log_dir))

    logger.info(f"Collecting PCAP files from {args.source_root}")
    logger.info(f"Output directory: {args.output_dir}")

    with logger.stage("collect_pcaps"):
        collected = collect_pcaps(args.source_root, args.output_dir)
        logger.metric("pcaps_collected", len(collected), "files")
        logger.info(f"Collected {len(collected)} PCAP files")

    print(f"[+] Collected {len(collected)} PCAP files into {args.output_dir}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
