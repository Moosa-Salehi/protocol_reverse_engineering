#!/usr/bin/env python3
"""
Test script to validate boundary detection with different thresholds.

Tests boundary detection with various score thresholds and parameters.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.boundary_detection import infer_segments


def analyze_segmentation(segments, name: str):
    """Analyze segmentation quality."""
    print(f"\n{name}:")
    print(f"  Total segments: {len(segments)}")

    # Count by width
    width_counts = {}
    for seg in segments:
        width = seg.end - seg.start
        width_counts[width] = width_counts.get(width, 0) + 1

    print(f"  Segments by width:")
    for width in sorted(width_counts.keys()):
        count = width_counts[width]
        pct = 100 * count / len(segments) if segments else 0
        print(f"    {width:2d} byte(s): {count:2d} segments ({pct:5.1f}%)")

    # Count 1-byte segments
    one_byte = sum(1 for seg in segments if seg.end - seg.start == 1)
    if one_byte > 0:
        pct = 100 * one_byte / len(segments)
        print(f"  WARNING: {one_byte} single-byte segments ({pct:.1f}%)")

    # Show segments
    print(f"  Segment details:")
    for seg in segments[:15]:
        width = seg.end - seg.start
        print(f"    [{seg.start:2d}:{seg.end:2d}] len={width:2d} kind={seg.kind:8s} conf={seg.confidence:.2f}")
    if len(segments) > 15:
        print(f"    ... and {len(segments) - 15} more segments")


def main():
    parser = argparse.ArgumentParser(description="Test boundary detection with different thresholds")
    parser.add_argument("messages_jsonl", help="Path to messages JSONL")
    parser.add_argument("--assignments-json", help="Family assignments JSON")
    parser.add_argument("--features-json", help="Family features JSON")
    parser.add_argument("--framing-json", help="Framing JSON")
    parser.add_argument("--family-id", default="family_1", help="Family ID to test")
    args = parser.parse_args()

    print("="*80)
    print("BOUNDARY DETECTION TEST")
    print("="*80)

    # Load messages
    print(f"\nLoading messages from: {args.messages_jsonl}")
    records = load_corpus_jsonl(args.messages_jsonl)
    print(f"Loaded {len(records)} messages")

    # Load assignments
    family_by_msg_id = {}
    if args.assignments_json:
        with open(args.assignments_json, 'r') as f:
            data = json.load(f)
            family_by_msg_id = {a['msg_id']: a['family_id'] for a in data['assignments']}

    # Load features
    family_features = {}
    if args.features_json:
        with open(args.features_json, 'r') as f:
            family_features = json.load(f)

    # Load framing
    framing_by_family = {}
    if args.framing_json:
        with open(args.framing_json, 'r') as f:
            framing_data = json.load(f)
            framing_by_family = framing_data.get('families', {})

    # Filter messages for target family
    family_messages = [
        r.payload_hex for r in records
        if family_by_msg_id.get(r.msg_id) == args.family_id
    ]

    if not family_messages:
        print(f"ERROR: No messages found for family {args.family_id}")
        return

    print(f"\nTesting family: {args.family_id}")
    print(f"Messages in family: {len(family_messages)}")
    print(f"Sample message length: {len(family_messages[0]) // 2} bytes")

    # Get features and framing for this family
    features = family_features.get(args.family_id)
    framing = framing_by_family.get(args.family_id)

    # Test 1: Default settings
    print("\n" + "="*80)
    print("TEST 1: Default Settings (threshold=2.0)")
    print("="*80)

    segments_default = infer_segments(
        family_messages[:1000],  # Sample for speed
        score_threshold=2.0,
        min_segment_width=1,
        family_features=features,
        framing_summary=framing,
        max_fields=15,
        enable_merging=True,
    )

    analyze_segmentation(segments_default, "Default")

    # Test 2: Lower threshold (more boundaries)
    print("\n" + "="*80)
    print("TEST 2: Lower Threshold (threshold=1.5)")
    print("="*80)

    segments_lower = infer_segments(
        family_messages[:1000],
        score_threshold=1.5,
        min_segment_width=1,
        family_features=features,
        framing_summary=framing,
        max_fields=15,
        enable_merging=True,
    )

    analyze_segmentation(segments_lower, "Lower Threshold")

    # Test 3: Stricter settings
    print("\n" + "="*80)
    print("TEST 3: Strict Settings (threshold=2.5, max_fields=10)")
    print("="*80)

    segments_strict = infer_segments(
        family_messages[:1000],
        score_threshold=2.5,
        min_segment_width=1,
        family_features=features,
        framing_summary=framing,
        max_fields=10,
        enable_merging=True,
    )

    analyze_segmentation(segments_strict, "Strict")

    # Comparison
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)

    print(f"\nSegment count:")
    print(f"  Lower threshold:  {len(segments_lower)}")
    print(f"  Default:          {len(segments_default)}")
    print(f"  Strict:           {len(segments_strict)}")

    # Count 1-byte segments
    one_byte_lower = sum(1 for seg in segments_lower if seg.end - seg.start == 1)
    one_byte_default = sum(1 for seg in segments_default if seg.end - seg.start == 1)
    one_byte_strict = sum(1 for seg in segments_strict if seg.end - seg.start == 1)

    print(f"\nSingle-byte segments:")
    print(f"  Lower threshold: {one_byte_lower}")
    print(f"  Default:         {one_byte_default}")
    print(f"  Strict:          {one_byte_strict}")

    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    if one_byte_default == 0:
        print("\n[OK] No single-byte segments with default settings!")
    elif one_byte_default < 3:
        print("\n[OK] Very few single-byte segments.")
    else:
        print("\n[WARNING] Single-byte segments still present.")
        print("  Consider using stricter settings or checking merging logic.")


if __name__ == "__main__":
    main()
