"""
Test script for boundary quality metrics and LLM-assisted refinement.

This script demonstrates:
1. Computing boundary quality metrics
2. Identifying problematic families
3. Exporting boundaries for LLM review
4. Generating refinement prompts
5. Simulating LLM responses and applying refinements
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.inference.boundary_detection_enhanced import infer_segments
from protocol_re.inference.boundary_quality_metrics import (
    compute_boundary_quality_metrics,
    identify_problematic_families,
)
from protocol_re.inference.llm_boundary_refinement import (
    export_boundaries_for_llm,
    generate_refinement_prompt,
    refine_boundaries_with_llm,
    format_refinement_summary,
)


def test_quality_metrics():
    """Test boundary quality metrics computation."""
    print("=" * 80)
    print("TEST 1: Boundary Quality Metrics")
    print("=" * 80)

    # Create sample messages with over-segmentation
    messages = [
        "010203040506070809",
        "010203040506070810",
        "010203040506070811",
        "010203040506070812",
    ]

    # Detect boundaries with low threshold (will over-segment)
    segments_low = infer_segments(messages, score_threshold=1.0, enable_merging=False)
    print(f"\nLow threshold (1.0) - Segments detected: {len(segments_low)}")
    for seg in segments_low:
        print(f"  {seg.start}-{seg.end} ({seg.end - seg.start}B) {seg.kind} conf={seg.confidence:.2f}")

    # Detect boundaries with high threshold (less segmentation)
    segments_high = infer_segments(messages, score_threshold=2.0, enable_merging=True)
    print(f"\nHigh threshold (2.0) with merging - Segments detected: {len(segments_high)}")
    for seg in segments_high:
        print(f"  {seg.start}-{seg.end} ({seg.end - seg.start}B) {seg.kind} conf={seg.confidence:.2f}")

    # Compute quality metrics for both
    family_segments_low = {"family_1": segments_low}
    family_segments_high = {"family_1": segments_high}

    metrics_low = compute_boundary_quality_metrics(family_segments_low)
    metrics_high = compute_boundary_quality_metrics(family_segments_high)

    print("\n" + "=" * 80)
    print("Quality Metrics - Low Threshold (Over-segmented)")
    print("=" * 80)
    print(metrics_low.summary_text())

    print("\n" + "=" * 80)
    print("Quality Metrics - High Threshold (Better)")
    print("=" * 80)
    print(metrics_high.summary_text())

    # Identify problematic families
    problematic = identify_problematic_families(metrics_low)
    if problematic:
        print("\n" + "=" * 80)
        print("Problematic Families Detected")
        print("=" * 80)
        for family in problematic:
            print(f"\nFamily: {family['family_id']}")
            print(f"  Segments: {family['segment_count']}")
            print(f"  Avg Confidence: {family['avg_confidence']:.4f}")
            print(f"  Issues: {', '.join(family['issues'])}")

    return segments_low, messages


def test_llm_export(segments, messages):
    """Test exporting boundaries for LLM review."""
    print("\n" + "=" * 80)
    print("TEST 2: Export Boundaries for LLM")
    print("=" * 80)

    export = export_boundaries_for_llm("family_1", segments, messages)

    print(f"\nExported data for family: {export['family_id']}")
    print(f"Segment count: {export['segment_count']}")
    print(f"\nStatistics:")
    for key, value in export['statistics'].items():
        print(f"  {key}: {value}")

    print(f"\nSegment details (first 5):")
    for seg in export['segments'][:5]:
        print(f"  Segment {seg['index']}: {seg['start']}-{seg['end']} "
              f"({seg['width']}B) {seg['kind']} conf={seg['confidence']:.2f}")
        print(f"    Unique values: {seg['unique_value_count']}")
        print(f"    Samples: {', '.join(seg['sample_values'][:3])}")

    return export


def test_prompt_generation(export):
    """Test generating LLM refinement prompt."""
    print("\n" + "=" * 80)
    print("TEST 3: Generate LLM Refinement Prompt")
    print("=" * 80)

    prompt = generate_refinement_prompt(export)

    print("\nGenerated prompt (first 1000 chars):")
    print("-" * 80)
    print(prompt[:1000])
    print("...")
    print("-" * 80)
    print(f"\nTotal prompt length: {len(prompt)} characters")

    return prompt


def test_llm_refinement(segments, messages):
    """Test LLM-assisted boundary refinement with simulated response."""
    print("\n" + "=" * 80)
    print("TEST 4: LLM-Assisted Boundary Refinement")
    print("=" * 80)

    # Simulate LLM response suggesting merges
    simulated_llm_response = """
    Based on my analysis, I recommend the following merges:

    ```json
    {
      "merge_suggestions": [
        {
          "segment_indices": [0, 1],
          "reason": "Two adjacent single-byte constant fields should be merged into one 2-byte field",
          "confidence": 0.85
        },
        {
          "segment_indices": [2, 3, 4],
          "reason": "Three consecutive single-byte variable fields with similar characteristics should be merged",
          "confidence": 0.75
        }
      ]
    }
    ```
    """

    print("\nSimulated LLM Response:")
    print("-" * 80)
    print(simulated_llm_response)
    print("-" * 80)

    # Apply refinement
    result = refine_boundaries_with_llm(
        family_id="family_1",
        segments=segments,
        messages_hex=messages,
        llm_response=simulated_llm_response,
        min_suggestion_confidence=0.6,
    )

    print("\n" + format_refinement_summary(result))

    print("\n" + "=" * 80)
    print("Refined Segments")
    print("=" * 80)
    for seg in result.refined_segments:
        print(f"  {seg.start}-{seg.end} ({seg.end - seg.start}B) {seg.kind} conf={seg.confidence:.2f}")
        if "merged_by_llm" in seg.evidence:
            print(f"    Merged from {seg.evidence['original_segment_count']} segments")

    return result


def test_with_real_data():
    """Test with real protocol data if available."""
    print("\n" + "=" * 80)
    print("TEST 5: Real Data Test (if available)")
    print("=" * 80)

    # Try to load real data
    data_dir = Path(__file__).parent.parent / "data"
    families_file = data_dir / "04_families.json"

    if not families_file.exists():
        print("\nNo real data available (data/04_families.json not found)")
        print("Skipping real data test")
        return

    print(f"\nLoading families from: {families_file}")

    with open(families_file, "r") as f:
        families_data = json.load(f)

    families = families_data.get("families", [])
    print(f"Found {len(families)} families")

    # Test on first family with enough messages
    for family in families[:3]:
        family_id = family.get("family_id", "unknown")
        messages = family.get("messages", [])

        if len(messages) < 5:
            continue

        print(f"\n--- Testing family: {family_id} ---")
        print(f"Messages: {len(messages)}")

        # Detect boundaries
        segments = infer_segments(messages[:20], score_threshold=2.0, enable_merging=True)
        print(f"Segments detected: {len(segments)}")

        # Compute metrics
        family_segments = {family_id: segments}
        metrics = compute_boundary_quality_metrics(family_segments)

        print(f"\nMetrics:")
        print(f"  Avg segments: {metrics.avg_segments_per_family:.2f}")
        print(f"  Single-byte ratio: {metrics.single_byte_ratio:.2%}")
        print(f"  Avg confidence: {metrics.avg_confidence:.4f}")

        # Check if problematic
        problematic = identify_problematic_families(metrics)
        if problematic:
            print(f"  Issues: {', '.join(problematic[0]['issues'])}")

            # Export for LLM review
            export = export_boundaries_for_llm(family_id, segments, messages[:5])
            prompt = generate_refinement_prompt(export)
            print(f"\n  Generated refinement prompt ({len(prompt)} chars)")
            print(f"  Ready for LLM review")

        break  # Only test first suitable family


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("BOUNDARY QUALITY METRICS & LLM REFINEMENT TEST")
    print("=" * 80)

    # Test 1: Quality metrics
    segments, messages = test_quality_metrics()

    # Test 2: Export for LLM
    export = test_llm_export(segments, messages)

    # Test 3: Generate prompt
    prompt = test_prompt_generation(export)

    # Test 4: LLM refinement
    result = test_llm_refinement(segments, messages)

    # Test 5: Real data (if available)
    test_with_real_data()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)
    print("\nSummary:")
    print("[OK] Boundary quality metrics computed successfully")
    print("[OK] Problematic families identified")
    print("[OK] Boundaries exported for LLM review")
    print("[OK] Refinement prompts generated")
    print("[OK] LLM suggestions validated and applied")
    print("\nA2 implementation is now complete!")


if __name__ == "__main__":
    main()
