#!/usr/bin/env python3
"""
Test script to validate enhanced boundary detection (A2 fix).

Compares:
1. Original boundary detection (current)
2. Enhanced boundary detection (with anti-fragmentation)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.boundary_detection import infer_segments as infer_segments_original
from protocol_re.inference.boundary_detection_enhanced import infer_segments as infer_segments_enhanced


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
    parser = argparse.ArgumentParser(description="Test enhanced boundary detection")
    parser.add_argument("messages_jsonl", help="Path to messages JSONL")
    parser.add_argument("--assignments-json", help="Family assignments JSON")
    parser.add_argument("--features-json", help="Family features JSON")
    parser.add_argument("--framing-json", help="Framing JSON")
    parser.add_argument("--family-id", default="family_1", help="Family ID to test")
    args = parser.parse_args()

    print("="*80)
    print("ENHANCED BOUNDARY DETECTION TEST (A2)")
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

    # Test 1: Original boundary detection
    print("\n" + "="*80)
    print("TEST 1: Original Boundary Detection")
    print("="*80)

    segments_original = infer_segments_original(
        family_messages[:1000],  # Sample for speed
        score_threshold=1.5,
        min_segment_width=1,
        family_features=features,
        framing_summary=framing,
    )

    analyze_segmentation(segments_original, "Original")

    # Test 2: Enhanced boundary detection (default settings)
    print("\n" + "="*80)
    print("TEST 2: Enhanced Boundary Detection (default)")
    print("="*80)

    segments_enhanced = infer_segments_enhanced(
        family_messages[:1000],
        score_threshold=2.0,  # Increased
        min_segment_width=1,
        family_features=features,
        framing_summary=framing,
        max_fields=15,
        enable_merging=True,
    )

    analyze_segmentation(segments_enhanced, "Enhanced")

    # Test 3: Enhanced with stricter settings
    print("\n" + "="*80)
    print("TEST 3: Enhanced Boundary Detection (strict)")
    print("="*80)

    segments_strict = infer_segments_enhanced(
        family_messages[:1000],
        score_threshold=2.5,  # Even higher
        min_segment_width=1,
        family_features=features,
        framing_summary=framing,
        max_fields=10,  # Fewer fields
        enable_merging=True,
    )

    analyze_segmentation(segments_strict, "Enhanced (strict)")

    # Comparison
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)

    print(f"\nSegment count:")
    print(f"  Original:         {len(segments_original)}")
    print(f"  Enhanced:         {len(segments_enhanced)}")
    print(f"  Enhanced (strict): {len(segments_strict)}")

    reduction = len(segments_original) - len(segments_enhanced)
    reduction_pct = 100 * reduction / len(segments_original) if segments_original else 0
    print(f"\nReduction: {reduction} segments ({reduction_pct:.1f}%)")

    # Count 1-byte segments
    one_byte_orig = sum(1 for seg in segments_original if seg.end - seg.start == 1)
    one_byte_enh = sum(1 for seg in segments_enhanced if seg.end - seg.start == 1)

    print(f"\nSingle-byte segments:")
    print(f"  Original: {one_byte_orig}")
    print(f"  Enhanced: {one_byte_enh}")
    print(f"  Reduction: {one_byte_orig - one_byte_enh}")

    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    if len(segments_enhanced) < len(segments_original) * 0.7:
        print("\n[OK] Significant reduction in over-segmentation!")
        print("  Enhanced boundary detection is working well.")
    elif len(segments_enhanced) < len(segments_original) * 0.85:
        print("\n[OK] Moderate reduction in over-segmentation.")
        print("  Consider using stricter settings (higher threshold).")
    else:
        print("\n[WARNING] Minimal reduction in over-segmentation.")
        print("  May need to adjust parameters or add more constraints.")

    if one_byte_enh < one_byte_orig * 0.5:
        print("\n[OK] Single-byte segments significantly reduced!")
    elif one_byte_enh < one_byte_orig * 0.8:
        print("\n[OK] Some reduction in single-byte segments.")
    else:
        print("\n[WARNING] Single-byte segments still high.")
        print("  Consider enabling merging or increasing min_segment_width.")


if __name__ == "__main__":
    main()
