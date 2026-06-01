#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.io.extract_payloads import write_messages_from_pcaps_jsonl, write_messages_from_pcaps_tshark_jsonl
from protocol_re.utils.logging import setup_stage_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract protocol payloads from PCAP files into a canonical JSONL corpus.")
    parser.add_argument("pcap_dir")
    parser.add_argument("output_jsonl")
    parser.add_argument(
        "--extraction-method",
        choices=["tshark", "tcp"],
        default="tshark",
        help="Use tshark display-filter extraction or legacy Scapy TCP port extraction.",
    )
    parser.add_argument("--service-port", type=int, help="Optional TCP port filter. If omitted, all TCP payloads are extracted.")
    parser.add_argument("--tshark-filter", help="TShark display filter for the target protocol, for example modbus or s7comm.")
    parser.add_argument(
        "--packets-dir",
        default="data/payload_extraction/packets",
        help="Directory for intermediate tshark packet metadata JSON files.",
    )
    parser.add_argument(
        "--payloads-dir",
        default="data/payload_extraction/payloads",
        help="Directory for intermediate carved payload JSON files.",
    )
    parser.add_argument("--tshark-workers", type=int, default=4, help="Maximum parallel TShark worker processes.")
    parser.add_argument("--max-messages", type=int, help="Maximum number of messages to extract.")
    parser.add_argument(
        "--reassembly-mode",
        choices=["packet", "stream"],
        default="packet",
        help="Use packet payloads directly or reconstruct directional TCP streams first.",
    )
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("03_extract_messages", Path(args.log_dir))

    logger.info(f"Extracting messages from {args.pcap_dir}")
    logger.decision(
        decision=f"Using {args.extraction_method} extraction method",
        reason="User configuration",
        tshark_filter=args.tshark_filter if args.extraction_method == "tshark" else None,
        service_port=args.service_port if args.extraction_method == "tcp" else None,
        max_messages=args.max_messages,
    )

    Path(args.output_jsonl).parent.mkdir(parents=True, exist_ok=True)

    with logger.stage("extract_messages"):
        if args.extraction_method == "tshark":
            if not args.tshark_filter:
                logger.error("--tshark-filter is required when --extraction-method tshark")
                raise SystemExit("--tshark-filter is required when --extraction-method tshark.")
            count = write_messages_from_pcaps_tshark_jsonl(
                args.pcap_dir,
                args.output_jsonl,
                tshark_filter=args.tshark_filter,
                packets_dir=args.packets_dir,
                payloads_dir=args.payloads_dir,
                max_messages=args.max_messages,
                max_workers=args.tshark_workers,
            )
        else:
            count = write_messages_from_pcaps_jsonl(
                args.pcap_dir,
                args.output_jsonl,
                service_port=args.service_port,
                reassembly_mode=args.reassembly_mode,
                max_messages=args.max_messages,
            )

        logger.metric("messages_extracted", count, "messages")
        logger.info(f"Extracted {count} messages")

    print(f"[+] Wrote {count} extracted messages to {args.output_jsonl}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
