#!/usr/bin/env python3
from __future__ import annotations

import argparse

from protocol_re.io.extract_payloads import write_messages_from_pcaps_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract TCP service payloads from PCAP files into a canonical JSONL corpus.")
    parser.add_argument("pcap_dir")
    parser.add_argument("output_jsonl")
    parser.add_argument("--service-port", type=int, help="Optional TCP port filter. If omitted, all TCP payloads are extracted.")
    parser.add_argument("--max-messages", type=int, help="Maximum number of messages to extract.")
    parser.add_argument(
        "--reassembly-mode",
        choices=["packet", "stream"],
        default="packet",
        help="Use packet payloads directly or reconstruct directional TCP streams first.",
    )
    args = parser.parse_args()

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
