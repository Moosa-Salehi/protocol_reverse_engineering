#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from protocol_re.io.extract_payloads import write_messages_from_pcaps_jsonl, write_messages_from_pcaps_tshark_jsonl


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
    parser.add_argument("--tshark-filter", help="TShark display filter for the target protocol, for example mbtcp or s7comm.")
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
    parser.add_argument("--max-messages", type=int, help="Maximum number of messages to extract.")
    parser.add_argument(
        "--reassembly-mode",
        choices=["packet", "stream"],
        default="packet",
        help="Use packet payloads directly or reconstruct directional TCP streams first.",
    )
    args = parser.parse_args()

    Path(args.output_jsonl).parent.mkdir(parents=True, exist_ok=True)
    if args.extraction_method == "tshark":
        if not args.tshark_filter:
            raise SystemExit("--tshark-filter is required when --extraction-method tshark.")
        count = write_messages_from_pcaps_tshark_jsonl(
            args.pcap_dir,
            args.output_jsonl,
            tshark_filter=args.tshark_filter,
            packets_dir=args.packets_dir,
            payloads_dir=args.payloads_dir,
            max_messages=args.max_messages,
        )
    else:
        count = write_messages_from_pcaps_jsonl(
            args.pcap_dir,
            args.output_jsonl,
            service_port=args.service_port,
            reassembly_mode=args.reassembly_mode,
            max_messages=args.max_messages,
        )
    print(f"[+] Wrote {count} extracted messages to {args.output_jsonl}")


if __name__ == "__main__":
    main()
