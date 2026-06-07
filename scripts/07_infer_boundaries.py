#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.boundary_detection import infer_field_hypotheses, infer_segments, infer_template
from protocol_re.utils.logging import setup_stage_logging, ProgressTracker


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
    parser.add_argument("--entropy-weight", type=float, default=None, help="Entropy-jump weight for boundary scoring")
    parser.add_argument(
        "--merge-width-targets",
        default="2,4",
        help="Comma-separated merged widths allowed by standard-width merge rules (default: 2,4)",
    )
    parser.add_argument(
        "--length-match-threshold",
        type=float,
        default=0.8,
        help="Minimum match ratio for statistical length-field boundary protection",
    )
    parser.add_argument(
        "--disable-length-validator",
        action="store_true",
        help="Disable statistical length-field detection/protection",
    )
    parser.add_argument(
        "--boundary-confidence-weight",
        type=float,
        default=0.45,
        help="Weight for boundary-support term in segment confidence (0.0-1.0)",
    )

    # Enhanced boundary detection options (A2) - now default
    parser.add_argument("--enhanced", action="store_true", help="(Deprecated: enhanced mode is now default)")
    parser.add_argument("--max-fields", type=int, default=15, help="Maximum fields per family")
    parser.add_argument("--enable-merging", action="store_true", default=True, help="Enable segment merging")
    parser.add_argument("--no-merging", dest="enable_merging", action="store_false", help="Disable segment merging")
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")

    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("07_infer_boundaries", Path(args.log_dir))

    logger.info(f"Loading messages from {args.input_jsonl}")
    logger.decision(
        decision="Using enhanced boundary detection",
        reason="Default mode with anti-fragmentation",
        score_threshold=args.score_threshold,
        max_fields=args.max_fields,
        merging_enabled=args.enable_merging,
        entropy_weight=args.entropy_weight,
        merge_width_targets=args.merge_width_targets,
        length_match_threshold=args.length_match_threshold,
        length_validator_enabled=not args.disable_length_validator,
        boundary_confidence_weight=args.boundary_confidence_weight,
    )

    with logger.stage("load_corpus"):
        records = load_corpus_jsonl(args.input_jsonl)
        logger.metric("message_count", len(records), "messages")
    with logger.stage("load_features_and_framing"):
        feature_by_family = {}
        if args.features_json:
            logger.info(f"Loading features from {args.features_json}")
            with open(args.features_json, "r", encoding="utf-8") as handle:
                feature_by_family = json.load(handle)
            logger.metric("families_with_features", len(feature_by_family), "families")

        framing_by_family = {}
        if args.framing_json:
            logger.info(f"Loading framing data from {args.framing_json}")
            with open(args.framing_json, "r", encoding="utf-8") as handle:
                framing_payload = json.load(handle)
            framing_by_family = framing_payload.get("families", {}) or {}
            logger.metric("families_with_framing", len(framing_by_family), "families")

    with logger.stage("group_messages"):
        grouped = defaultdict(list)
        if args.assignments_json:
            logger.info(f"Loading family assignments from {args.assignments_json}")
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
            logger.info(f"Using heuristic grouping mode: {args.family_mode}")
            for record in records:
                if args.family_mode == "length":
                    family_id = f"len_{record.payload_len}"
                else:
                    family_id = f"prefix2_{record.payload_hex[:4] or 'empty'}"
                grouped[family_id].append(record.payload_hex)
            grouping_mode = f"heuristic_{args.family_mode}"

        logger.metric("family_count", len(grouped), "families")
        logger.info(f"Grouped messages into {len(grouped)} families")

    # Enhanced boundary detection is now the default
    if args.enhanced:
        logger.warning("--enhanced flag is deprecated; enhanced mode is now default")
        print("[!] Note: --enhanced flag is deprecated; enhanced mode is now default")

    print(f"[+] Using boundary detection with anti-fragmentation")
    print(f"    - Score threshold: {args.score_threshold}")
    print(f"    - Max fields: {args.max_fields}")
    print(f"    - Merging: {'enabled' if args.enable_merging else 'disabled'}")
    merge_width_targets = tuple(
        int(item.strip())
        for item in args.merge_width_targets.split(",")
        if item.strip()
    )
    print(f"    - Merge width targets: {','.join(str(item) for item in merge_width_targets) or 'none'}")
    print(f"    - Length validator: {'enabled' if not args.disable_length_validator else 'disabled'}")

    result = {}
    total_segments = 0
    total_fields = 0

    with logger.stage("infer_boundaries"):
        progress = ProgressTracker(len(grouped), "Inferring boundaries", logger, update_interval=10)

        for family_id, messages_hex in grouped.items():
            with logger.context(family_id=family_id, message_count=len(messages_hex)):
                # Use enhanced boundary detection (now the only implementation)
                segments = infer_segments(
                    messages_hex,
                    score_threshold=args.score_threshold,
                    family_features=feature_by_family.get(family_id),
                    framing_summary=framing_by_family.get(family_id),
                    max_fields=args.max_fields,
                    enable_merging=args.enable_merging,
                    entropy_weight=args.entropy_weight,
                    merge_width_targets=merge_width_targets,
                    length_match_threshold=args.length_match_threshold,
                    enable_length_validator=not args.disable_length_validator,
                    boundary_confidence_weight=args.boundary_confidence_weight,
                )
                hypotheses = infer_field_hypotheses(family_id, messages_hex, segments)
                template = infer_template(messages_hex)

                total_segments += len(segments)
                total_fields += len(hypotheses)

                logger.debug(
                    f"Family {family_id}: {len(segments)} segments, {len(hypotheses)} fields",
                    segments=len(segments),
                    fields=len(hypotheses),
                )

                result[family_id] = {
                    "message_count": len(messages_hex),
                    "template": template,
                    "segments": [segment.to_dict() for segment in segments],
                    "field_hypotheses": [hypothesis.to_dict() for hypothesis in hypotheses],
                }

            progress.update()

        progress.finish()

    logger.metric("total_segments", total_segments, "segments")
    logger.metric("total_fields", total_fields, "fields")
    logger.metric("avg_segments_per_family", total_segments / len(grouped) if grouped else 0, "segments/family")
    logger.metric("avg_fields_per_family", total_fields / len(grouped) if grouped else 0, "fields/family")

    with logger.stage("write_output"):
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
        logger.info(f"Wrote boundary results to {args.output_json}")

    print(f"[+] Boundary inference grouping mode: {grouping_mode}")
    print(f"[+] Wrote {len(result)} family boundary summaries to {args.output_json}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
