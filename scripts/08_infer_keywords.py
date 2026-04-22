#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.keyword_detection import split_family_by_keyword


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer candidate keyword bytes and keyword-based subformats.")
    parser.add_argument("input_jsonl")
    parser.add_argument("output_json")
    parser.add_argument("--assignments-json", help="Optional family assignment JSON from 05_discover_families.py")
    parser.add_argument("--include-unassigned", action="store_true", help="Include records missing a family assignment")
    parser.add_argument("--family-mode", choices=["length", "prefix2"], default="length")
    args = parser.parse_args()

    records = load_corpus_jsonl(args.input_jsonl)
    grouped = defaultdict(list)
    if args.assignments_json:
        with open(args.assignments_json, "r", encoding="utf-8") as handle:
            assignment_payload = json.load(handle)
        family_by_msg_id = {item["msg_id"]: item["family_id"] for item in assignment_payload["assignments"]}
        for record in records:
            family_id = family_by_msg_id.get(record.msg_id)
            if family_id is None and not args.include_unassigned:
                continue
            grouped[family_id or "unassigned"].append(record.payload_hex)
    else:
        for record in records:
            family_id = f"len_{record.payload_len}" if args.family_mode == "length" else f"prefix2_{record.payload_hex[:4] or 'empty'}"
            grouped[family_id].append(record.payload_hex)

    output = {family_id: split_family_by_keyword(messages_hex) for family_id, messages_hex in grouped.items()}
    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)

    print(f"[+] Wrote keyword hypotheses for {len(output)} families to {args.output_json}")


if __name__ == "__main__":
    main()
