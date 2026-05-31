#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.framing import infer_framing_hypotheses
from protocol_re.utils.logging import setup_stage_logging


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
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("05_infer_framing", Path(args.log_dir))

    logger.info(f"Loading messages from {args.input_jsonl}")
    logger.decision(
        decision="Framing inference configuration",
        reason="User configuration",
        max_header_bytes=args.max_header_bytes,
        detect_layers=args.detect_layers,
        layer_min_confidence=args.layer_min_confidence if args.detect_layers else None,
    )

    with logger.stage("load_corpus"):
        records = load_corpus_jsonl(args.input_jsonl)
        logger.metric("message_count", len(records), "messages")

    with logger.stage("load_assignments"):
        logger.info(f"Loading family assignments from {args.assignments_json}")
        with open(args.assignments_json, "r", encoding="utf-8") as handle:
            assignment_payload = json.load(handle)
        family_by_msg_id = {item["msg_id"]: item["family_id"] for item in assignment_payload.get("assignments", [])}
        logger.metric("assignments_loaded", len(family_by_msg_id), "assignments")

    with logger.stage("group_messages"):
        grouped = defaultdict(list)
        for record in records:
            family_id = family_by_msg_id.get(record.msg_id)
            if family_id is None and not args.include_unassigned:
                continue
            grouped[family_id or "unassigned"].append(record.payload_hex)
        logger.metric("family_count", len(grouped), "families")
        logger.info(f"Grouped messages into {len(grouped)} families")

    with logger.stage("infer_framing"):
        result = infer_framing_hypotheses(
            grouped,
            max_header_bytes=args.max_header_bytes,
            max_hypotheses_per_family=args.max_hypotheses_per_family,
            min_messages=args.min_messages,
            detect_layers=args.detect_layers,
            layer_min_confidence=args.layer_min_confidence,
        )

    fallback_counts = {}
    for family in result.get("families", {}).values():
        best = (family.get("layout_hypotheses") or [{}])[0]
        reason = ((best.get("evidence") or {}).get("fallback_reason"))
        if reason:
            fallback_counts[reason] = fallback_counts.get(reason, 0) + 1

    logger.metric("families_processed", len(result.get('families', {})), "families")

    if fallback_counts:
        total_fallbacks = sum(fallback_counts.values())
        logger.warning(
            f"Framing fallback applied for {total_fallbacks} families",
            fallback_counts=fallback_counts
        )
        for reason, count in fallback_counts.items():
            logger.metric(f"fallback_{reason}", count, "families")

    if args.detect_layers:
        layered_count = result.get('metadata', {}).get('families_with_layers', 0)
        logger.metric("families_with_layers", layered_count, "families")
        if layered_count > 0:
            logger.info(f"Detected layers in {layered_count} families")

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
        logger.info(f"Wrote framing hypotheses to {args.output_json}")

    print(f"[+] Framing inference algorithm: {result.get('metadata', {}).get('algorithm', 'unknown')}")
    if detect_layers := result.get('metadata', {}).get('layer_detection_enabled', False):
        layered_count = result.get('metadata', {}).get('families_with_layers', 0)
        print(f"[+] Layer detection enabled: {layered_count} families with detected layers")
    if fallback_counts:
        reasons = ", ".join(f"{reason}={count}" for reason, count in sorted(fallback_counts.items()))
        print(f"[!] Warning: framing fallback applied for {sum(fallback_counts.values())} families ({reasons})", file=sys.stderr)
    print(f"[+] Wrote framing hypotheses for {len(result.get('families', {}))} families to {args.output_json}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
