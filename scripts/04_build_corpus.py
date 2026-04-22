#!/usr/bin/env python3
from __future__ import annotations

import argparse

from protocol_re.corpus.message_corpus import build_corpus, write_corpus_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a canonical message corpus from extracted session JSON files.")
    parser.add_argument("input_dir", help="Directory containing extracted session JSON files")
    parser.add_argument("output_jsonl", help="Output path for the canonical corpus JSONL file")
    parser.add_argument("--service-port", type=int, default=502, help="Service TCP port used for direction inference")
    parser.add_argument("--deduplicate-payloads", action="store_true", help="Drop globally duplicated payloads")
    args = parser.parse_args()

    records = build_corpus(
        args.input_dir,
        service_port=args.service_port,
        deduplicate_payloads=args.deduplicate_payloads,
    )
    write_corpus_jsonl(records, args.output_jsonl)
    print(f"[+] Wrote {len(records)} canonical message records to {args.output_jsonl}")


if __name__ == "__main__":
    main()
