#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.boundary_detection import infer_field_hypotheses, infer_segments, infer_template
from protocol_re.model.schema import Segment
from protocol_re.utils.logging import setup_stage_logging, ProgressTracker


def _derive_body_start(framing_payload: dict, framing_by_family: dict) -> int:
    """Common transport-header end shared by the families (body start offset)."""
    global_block = (framing_payload or {}).get("global", {}) or {}
    header_ends = global_block.get("common_header_ends") or []
    if header_ends:
        best = max(header_ends, key=lambda item: float(item.get("family_ratio", 0.0) or 0.0))
        if float(best.get("family_ratio", 0.0) or 0.0) >= 0.5 and int(best.get("header_end", 0) or 0) > 0:
            return int(best["header_end"])
    starts = []
    for summary in (framing_by_family or {}).values():
        layouts = (summary or {}).get("layout_hypotheses") or []
        if layouts:
            value = layouts[0].get("body_start", layouts[0].get("header_end"))
            if value:
                starts.append(int(value))
    if starts:
        return Counter(starts).most_common(1)[0][0]
    return 0


def _segment_boundaries(segments, lo: int, hi: int) -> set:
    """Boundary positions (segment edges) falling within [lo, hi]."""
    positions = set()
    for segment in segments:
        for edge in (segment.start, segment.end):
            if lo <= edge <= hi:
                positions.add(edge)
    return positions


def _segments_from_boundaries(positions) -> list:
    ordered = sorted(positions)
    return [
        Segment(start=start, end=end, kind="variable", confidence=1.0, evidence={"source": "hierarchical"})
        for start, end in zip(ordered, ordered[1:])
        if end > start
    ]


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
    parser.add_argument(
        "--no-opcode-isolation",
        dest="isolate_body_opcode",
        action="store_false",
        default=True,
        help="Disable isolating a constant leading body byte (opcode/function code) as its own field",
    )

    parser.add_argument(
        "--hierarchical-boundaries",
        action="store_true",
        default=False,
        help=(
            "Infer field structure on higher-variance pools (transport header on all "
            "messages; body per message length) and impose it on each refined family. "
            "Fixes over-merge on FC-pure/degenerate families. Requires --assignments-json."
        ),
    )
    parser.add_argument(
        "--body-score-threshold",
        type=float,
        default=1.5,
        help="Boundary score threshold for the per-length body pool (hierarchical mode).",
    )
    parser.add_argument(
        "--pool-sample-cap",
        type=int,
        default=20000,
        help="Max messages sampled per pool for hierarchical boundary inference.",
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
        opcode_isolation_enabled=args.isolate_body_opcode,
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
        framing_payload = {}
        if args.framing_json:
            logger.info(f"Loading framing data from {args.framing_json}")
            with open(args.framing_json, "r", encoding="utf-8") as handle:
                framing_payload = json.load(handle)
            framing_by_family = framing_payload.get("families", {}) or {}
            logger.metric("families_with_framing", len(framing_by_family), "families")

    with logger.stage("group_messages"):
        grouped = defaultdict(list)
        discriminator_offset = None
        discriminator_width = 1
        if args.assignments_json:
            logger.info(f"Loading family assignments from {args.assignments_json}")
            with open(args.assignments_json, "r", encoding="utf-8") as handle:
                assignment_payload = json.load(handle)
            family_by_msg_id = {item["msg_id"]: item["family_id"] for item in assignment_payload["assignments"]}
            # The type-discriminator offset (e.g. the Modbus function code) detected in
            # stage 04. Hierarchical body pools group by length, which mixes opcodes, so
            # per-pool opcode isolation cannot see a constant byte there; forcing a cut at
            # this known offset keeps the opcode its own field in every family.
            _refine = (assignment_payload.get("metadata") or {}).get("discriminator_refinement") or {}
            if _refine.get("applied"):
                discriminator_offset = int(_refine.get("offset"))
                discriminator_width = int(_refine.get("width", 1) or 1)
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

    # Hierarchical pools: infer transport-header structure on all messages (where
    # message length varies) and body structure per message length (where the
    # opcode and numeric fields vary), then impose them on each refined family.
    # This avoids over-merge on FC-pure/degenerate families, where per-family
    # inference sees near-constant header/body bytes.
    hierarchical = args.hierarchical_boundaries and grouping_mode == "family_assignments"
    header_boundaries: set = set()
    body_boundaries_by_len: dict = {}
    if hierarchical:
        with logger.stage("hierarchical_pools"):
            body_start = _derive_body_start(framing_payload, framing_by_family)
            all_hex = []
            msgs_by_len = defaultdict(list)
            for record in records:
                fid = family_by_msg_id.get(record.msg_id)
                if fid is None or fid == "noise":
                    continue
                all_hex.append(record.payload_hex)
                msgs_by_len[record.payload_len].append(record.payload_hex)
            cap = args.pool_sample_cap
            if body_start > 0 and all_hex:
                header_segs = infer_segments(
                    all_hex[:cap],
                    score_threshold=args.score_threshold,
                    max_fields=args.max_fields,
                    enable_merging=args.enable_merging,
                    entropy_weight=args.entropy_weight,
                    merge_width_targets=merge_width_targets,
                    length_match_threshold=args.length_match_threshold,
                    enable_length_validator=not args.disable_length_validator,
                    boundary_confidence_weight=args.boundary_confidence_weight,
                    isolate_body_opcode=False,
                )
                header_boundaries = _segment_boundaries(header_segs, 0, body_start) | {0, body_start}
            body_framing = (
                {"layout_hypotheses": [{"confidence": 1.0, "header_start": 0, "header_end": body_start, "body_start": body_start}]}
                if body_start > 0
                else None
            )
            for payload_len, hexes in msgs_by_len.items():
                body_segs = infer_segments(
                    hexes[:cap],
                    score_threshold=args.body_score_threshold,
                    framing_summary=body_framing,
                    max_fields=args.max_fields,
                    enable_merging=args.enable_merging,
                    entropy_weight=args.entropy_weight,
                    merge_width_targets=merge_width_targets,
                    length_match_threshold=args.length_match_threshold,
                    enable_length_validator=not args.disable_length_validator,
                    boundary_confidence_weight=args.boundary_confidence_weight,
                    isolate_body_opcode=args.isolate_body_opcode,
                    require_single_byte_operand=True,
                )
                body_boundaries_by_len[payload_len] = _segment_boundaries(body_segs, body_start, payload_len) | {body_start, payload_len}
            logger.metric("hierarchical_body_start", body_start, "offset")
            logger.metric("hierarchical_length_pools", len(body_boundaries_by_len), "pools")
            print(f"[+] Hierarchical boundaries: body_start={body_start}, {len(body_boundaries_by_len)} length pools")

    with logger.stage("infer_boundaries"):
        progress = ProgressTracker(len(grouped), "Inferring boundaries", logger, update_interval=10)

        for family_id, messages_hex in grouped.items():
            with logger.context(family_id=family_id, message_count=len(messages_hex)):
                if hierarchical:
                    fam_len = Counter(len(h) // 2 for h in messages_hex).most_common(1)[0][0]
                    body_bounds = body_boundaries_by_len.get(fam_len, {0, fam_len})
                    positions = {p for p in (header_boundaries | body_bounds) if 0 <= p <= fam_len} | {0, fam_len}
                    # Force the type-discriminator (opcode) to be its own field. Length
                    # pools mix opcodes, so per-pool isolation misses it; this known
                    # offset is opcode-pure per family and exposes its constant value.
                    if discriminator_offset is not None:
                        for cut in (discriminator_offset, discriminator_offset + discriminator_width):
                            if 0 < cut < fam_len:
                                positions.add(cut)
                    segments = _segments_from_boundaries(positions)
                else:
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
                        isolate_body_opcode=args.isolate_body_opcode,
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
