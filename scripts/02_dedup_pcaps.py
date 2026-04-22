#!/usr/bin/env python3
from __future__ import annotations

import argparse

from protocol_re.io.dedup_pcaps import find_duplicate_pcaps, remove_duplicates


def main() -> None:
    parser = argparse.ArgumentParser(description="Find and optionally delete duplicate PCAP files.")
    parser.add_argument("pcap_dir")
    parser.add_argument("--delete", action="store_true")
    args = parser.parse_args()

    duplicates = find_duplicate_pcaps(args.pcap_dir)
    print(f"[+] Found {len(duplicates)} duplicate PCAPs")
    for duplicate in duplicates[:20]:
        print(f"    {duplicate.duplicate_path} == {duplicate.original_path}")

    if args.delete and duplicates:
        removed = remove_duplicates(duplicates)
        print(f"[+] Removed {removed} duplicate PCAPs")


if __name__ == "__main__":
    main()
