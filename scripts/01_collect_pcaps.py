#!/usr/bin/env python3
from __future__ import annotations

import argparse

from protocol_re.io.pcap_collect import collect_pcaps


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect PCAP files from a source tree into one normalized directory.")
    parser.add_argument("source_root")
    parser.add_argument("output_dir")
    args = parser.parse_args()

    collected = collect_pcaps(args.source_root, args.output_dir)
    print(f"[+] Collected {len(collected)} PCAP files into {args.output_dir}")


if __name__ == "__main__":
    main()
