#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.framing import infer_framing_hypotheses


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer protocol-agnostic frame/header layout hypotheses from message families.")
    parser.add_argument("input_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("assignments_json", help="Family assignment JSON from discover_families.py")
    parser.add_argument("output_json", help="Output JSON file for framing hypotheses")
    parser.add_argument("--include-unassigned", action="store_true", help="Include records missing a family assignment")
    parser.add_argument("--max-header-bytes", type=int, default=32, help="Maximum prefix bytes to scan for framing fields")
    parser.add_argument("--max-hypotheses-per-family", type=int, default=3, help="Layout hypotheses retained per family")
    parser.add_argument("--min-messages", type=int, default=3, help="Minimum messages needed for non-fallback family inference")
    parser.add_argument("--detect-layers", action="store_true", help="Enable multi-layer protocol detection (A6)")
    parser.add_argument("--layer-min-confidence", type=float, default=0.6, help="Minimum confidence for layer boundary detection (default: 0.6)")
    args = parser.parse_args()

    records = load_corpus_jsonl(args.input_jsonl)
    with open(args.assignments_json, "r", encoding="utf-8") as handle:
        assignment_payload = json.load(handle)
    family_by_msg_id = {item["msg_id"]: item["family_id"] for item in assignment_payload.get("assignments", [])}

    grouped = defaultdict(list)
    for record in records:
        family_id = family_by_msg_id.get(record.msg_id)
        if family_id is None and not args.include_unassigned:
            continue
        grouped[family_id or "unassigned"].append(record.payload_hex)

    result = infer_framing_hypotheses(
        grouped,
        max_header_bytes=args.max_header_bytes,
        max_hypotheses_per_family=args.max_hypotheses_per_family,
        min_messages=args.min_messages,
        detect_layers=args.detect_layers,
        layer_min_confidence=args.layer_min_confidence,
    )

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    fallback_counts = {}
    for family in result.get("families", {}).values():
        best = (family.get("layout_hypotheses") or [{}])[0]
        reason = ((best.get("evidence") or {}).get("fallback_reason"))
        if reason:
            fallback_counts[reason] = fallback_counts.get(reason, 0) + 1

    print(f"[+] Framing inference algorithm: {result.get('metadata', {}).get('algorithm', 'unknown')}")
    if detect_layers := result.get('metadata', {}).get('layer_detection_enabled', False):
        layered_count = result.get('metadata', {}).get('families_with_layers', 0)
        print(f"[+] Layer detection enabled: {layered_count} families with detected layers")
    if fallback_counts:
        reasons = ", ".join(f"{reason}={count}" for reason, count in sorted(fallback_counts.items()))
        print(f"[!] Warning: framing fallback applied for {sum(fallback_counts.values())} families ({reasons})", file=sys.stderr)
    print(f"[+] Wrote framing hypotheses for {len(result.get('families', {}))} families to {args.output_json}")


if __name__ == "__main__":
    main()
