#!/usr/bin/env python3
from __future__ import annotations

import argparse

from protocol_re.io.extract_payloads import extract_messages_from_pcaps, write_messages_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract TCP service payloads from PCAP files into a canonical JSONL corpus.")
    parser.add_argument("pcap_dir")
    parser.add_argument("output_jsonl")
    parser.add_argument("--service-port", type=int, default=502)
    parser.add_argument("--max-workers", type=int, default=4)
    args = parser.parse_args()

    messages = extract_messages_from_pcaps(args.pcap_dir, service_port=args.service_port, max_workers=args.max_workers)
    write_messages_jsonl(messages, args.output_jsonl)
    print(f"[+] Wrote {len(messages)} extracted messages to {args.output_jsonl}")


if __name__ == "__main__":
    main()
