#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.discriminator_fields import infer_discriminator_candidates
from protocol_re.inference.keyword_detection import split_family_by_keyword


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer discriminator/opcode candidate bytes and backward-compatible keyword subformats.")
    parser.add_argument("input_jsonl")
    parser.add_argument("output_json")
    parser.add_argument("--assignments-json", help="Optional family assignment JSON from 04_discover_families.py")
    parser.add_argument("--include-unassigned", action="store_true", help="Include records missing a family assignment")
    parser.add_argument("--family-mode", choices=["length", "prefix2"], default="length")
    parser.add_argument("--features-json", help="Optional family feature JSON from 06_extract_features.py")
    parser.add_argument("--framing-json", help="Optional framing JSON from 05_infer_framing.py")
    parser.add_argument("--neural-model-path", default=None, help="Optional encoder checkpoint for gradient salience")
    parser.add_argument("--salience-cache-path", default=None, help="Optional cache for trained salience scores")
    parser.add_argument("--max-offset", type=int, default=128, help="Maximum plausible offset to scan")
    args = parser.parse_args()

    records = load_corpus_jsonl(args.input_jsonl)
    features_payload = {}
    if args.features_json:
        with open(args.features_json, "r", encoding="utf-8") as handle:
            features_payload = json.load(handle)
    framing_payload = {}
    if args.framing_json:
        with open(args.framing_json, "r", encoding="utf-8") as handle:
            framing_payload = json.load(handle)

    if args.assignments_json:
        with open(args.assignments_json, "r", encoding="utf-8") as handle:
            assignment_payload = json.load(handle)
        assignment_map = {item["msg_id"]: item["family_id"] for item in assignment_payload["assignments"]}
        family_by_msg_id = {}
        for record in records:
            family_id = assignment_map.get(record.msg_id)
            if family_id is None and not args.include_unassigned:
                continue
            family_by_msg_id[record.msg_id] = family_id or "unassigned"
        output = infer_discriminator_candidates(
            records,
            family_by_msg_id,
            features=features_payload,
            framing=framing_payload,
            neural_model_path=args.neural_model_path,
            salience_cache_path=args.salience_cache_path,
            max_offset=args.max_offset,
        )
        print("[+] Discriminator discovery grouping mode: family_assignments")
    else:
        grouped = defaultdict(list)
        for record in records:
            family_id = f"len_{record.payload_len}" if args.family_mode == "length" else f"prefix2_{record.payload_hex[:4] or 'empty'}"
            grouped[family_id].append(record.payload_hex)
        output = {family_id: split_family_by_keyword(messages_hex, search_range=range(0, args.max_offset)) for family_id, messages_hex in grouped.items()}
        print(f"[+] Discriminator discovery grouping mode: heuristic_{args.family_mode}")
        print("[!] Warning: discriminator discovery used heuristic family grouping because --assignments-json was not provided", file=sys.stderr)

    unavailable_counts = {}
    for family in output.values():
        salience_metadata = family.get("salience_metadata", {}) if isinstance(family, dict) else {}
        for key in ("attention", "gradient"):
            salience = salience_metadata.get(key) if isinstance(salience_metadata, dict) else None
            if isinstance(salience, dict) and salience.get("available") is False:
                reason = str(salience.get("reason") or "unspecified")
                unavailable_counts[reason] = unavailable_counts.get(reason, 0) + 1
    if unavailable_counts:
        reasons = ", ".join(f"{reason}={count}" for reason, count in sorted(unavailable_counts.items()))
        print(f"[!] Warning: optional discriminator salience fallback/unavailable ({reasons})", file=sys.stderr)

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)

    print(f"[+] Wrote discriminator/keyword hypotheses for {len(output)} families to {args.output_json}")


if __name__ == "__main__":
    main()
