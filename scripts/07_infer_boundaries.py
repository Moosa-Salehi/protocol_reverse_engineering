#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.boundary_detection import infer_field_hypotheses, infer_segments, infer_template


def main() -> None:
    parser = argparse.ArgumentParser(description="Infer field boundaries and coarse field types from message families.")
    parser.add_argument("input_jsonl", help="Canonical message corpus JSONL")
    parser.add_argument("output_json", help="Output JSON file for family templates and segment hypotheses")
    parser.add_argument("--assignments-json", help="Optional family assignment JSON from 04_discover_families.py")
    parser.add_argument("--include-unassigned", action="store_true", help="Include records missing a family assignment")
    parser.add_argument("--family-mode", choices=["length", "prefix2"], default="length", help="Cheap family grouping heuristic")
    parser.add_argument("--score-threshold", type=float, default=1.5, help="Boundary score threshold")
    parser.add_argument("--features-json", help="Optional family feature JSON from 06_extract_features.py")
    parser.add_argument("--framing-json", help="Optional framing hypotheses from 05_infer_framing.py")
    args = parser.parse_args()

    records = load_corpus_jsonl(args.input_jsonl)
    feature_by_family = {}
    if args.features_json:
        with open(args.features_json, "r", encoding="utf-8") as handle:
            feature_by_family = json.load(handle)
    framing_by_family = {}
    if args.framing_json:
        with open(args.framing_json, "r", encoding="utf-8") as handle:
            framing_payload = json.load(handle)
        framing_by_family = framing_payload.get("families", {}) or {}

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
        grouping_mode = "family_assignments"
    else:
        for record in records:
            if args.family_mode == "length":
                family_id = f"len_{record.payload_len}"
            else:
                family_id = f"prefix2_{record.payload_hex[:4] or 'empty'}"
            grouped[family_id].append(record.payload_hex)
        grouping_mode = f"heuristic_{args.family_mode}"

    result = {}
    for family_id, messages_hex in grouped.items():
        segments = infer_segments(
            messages_hex,
            score_threshold=args.score_threshold,
            family_features=feature_by_family.get(family_id),
            framing_summary=framing_by_family.get(family_id),
        )
        hypotheses = infer_field_hypotheses(family_id, messages_hex, segments)
        result[family_id] = {
            "message_count": len(messages_hex),
            "template": infer_template(messages_hex),
            "segments": [segment.to_dict() for segment in segments],
            "field_hypotheses": [hypothesis.to_dict() for hypothesis in hypotheses],
        }

    with open(args.output_json, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    print(f"[+] Boundary inference grouping mode: {grouping_mode}")
    print(f"[+] Wrote {len(result)} family boundary summaries to {args.output_json}")


if __name__ == "__main__":
    main()
