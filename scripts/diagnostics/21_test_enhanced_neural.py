#!/usr/bin/env python3
"""
Test script to validate enhanced neural features.

Compares:
1. Original neural features (no preprocessing)
2. Enhanced neural features (with preprocessing)
3. Structural features (baseline)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.clustering.hybrid_features import build_feature_matrix
from protocol_re.clustering.enhanced_features import build_enhanced_feature_matrix
from protocol_re.utils.logging import setup_stage_logging

try:
    import numpy as np
except ImportError:
    print("Error: NumPy is required")
    sys.exit(1)


def analyze_features(matrix: np.ndarray, name: str):
    """Analyze feature matrix quality."""
    print(f"\n{name}:")
    print(f"  Shape: {matrix.shape}")

    # Variance
    total_var = np.var(matrix, axis=0).sum()
    avg_var = total_var / matrix.shape[1]
    print(f"  Total variance: {total_var:.6f}")
    print(f"  Avg variance per dim: {avg_var:.6f}")

    # Pairwise distances (sample)
    if matrix.shape[0] >= 100:
        sample_size = min(100, matrix.shape[0])
        sample_indices = np.random.choice(matrix.shape[0], sample_size, replace=False)
        sample = matrix[sample_indices]

        distances = []
        for i in range(min(20, sample_size)):
            for j in range(i+1, min(i+5, sample_size)):
                dist = np.linalg.norm(sample[i] - sample[j])
                distances.append(dist)

        if distances:
            mean_dist = np.mean(distances)
            print(f"  Mean pairwise distance: {mean_dist:.4f}")

    # Collapsed dimensions
    variances = np.var(matrix, axis=0)
    collapsed = np.sum(variances < 0.001)
    print(f"  Collapsed dimensions (var < 0.001): {collapsed}/{matrix.shape[1]}")


def main():
    parser = argparse.ArgumentParser(description="Test enhanced neural features")
    parser.add_argument("messages_jsonl", help="Path to messages JSONL")
    parser.add_argument("--model-path", default="assets/pre_trained/industrial_VAE.pth")
    parser.add_argument("--latent-cache", default="data/latent_cache_test.json")
    parser.add_argument("--sample-size", type=int, default=5000)
    args = parser.parse_args()

    print("="*80)
    print("ENHANCED NEURAL FEATURES TEST")
    print("="*80)

    # Load messages
    print(f"\nLoading messages from: {args.messages_jsonl}")
    records = load_corpus_jsonl(args.messages_jsonl)
    print(f"Loaded {len(records)} messages")

    # Sample
    if len(records) > args.sample_size:
        import random
        records = random.sample(records, args.sample_size)
        print(f"Sampled {len(records)} messages")

    # Test 1: Original neural features (no preprocessing)
    print("\n" + "="*80)
    print("TEST 1: Original Neural Features (no preprocessing)")
    print("="*80)

    result_original = build_feature_matrix(
        records,
        records,
        feature_mode="neural",
        model_path=args.model_path,
        latent_cache_path=args.latent_cache,
        latent_dim=32,
    )

    if result_original.fallback_reason:
        print(f"FAILED: {result_original.fallback_reason}")
    else:
        analyze_features(result_original.matrix, "Original Neural")

    # Test 2: Enhanced neural features (with preprocessing)
    print("\n" + "="*80)
    print("TEST 2: Enhanced Neural Features (with preprocessing)")
    print("="*80)

    result_enhanced = build_enhanced_feature_matrix(
        records,
        records,
        feature_mode="neural",
        model_path=args.model_path,
        latent_cache_path=args.latent_cache + ".enhanced",
        latent_dim=32,
        enable_preprocessing=True,
        enable_quality_check=True,
        auto_fallback=False,  # Don't fallback, we want to see neural results
    )

    print(f"Feature mode: {result_enhanced.feature_mode}")
    print(f"Preprocessing enabled: {result_enhanced.preprocessing_enabled}")
    print(f"Variable offsets detected: {result_enhanced.variable_offsets_detected}")
    print(f"Quality check passed: {result_enhanced.quality_check_passed}")
    print(f"Quality reason: {result_enhanced.quality_check_reason}")

    if result_enhanced.fallback_reason:
        print(f"FAILED: {result_enhanced.fallback_reason}")
    else:
        analyze_features(result_enhanced.matrix, "Enhanced Neural")

        if result_enhanced.variable_offsets_detected > 0:
            print(f"\nVariable offsets masked: {result_enhanced.extra_metadata.get('variable_offsets', [])}")

    # Test 3: Structural features (baseline)
    print("\n" + "="*80)
    print("TEST 3: Structural Features (baseline)")
    print("="*80)

    result_structural = build_feature_matrix(
        records,
        records,
        feature_mode="structural",
    )

    analyze_features(result_structural.matrix, "Structural")

    # Comparison
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)

    if not result_original.fallback_reason and not result_enhanced.fallback_reason:
        orig_var = np.var(result_original.matrix, axis=0).sum()
        enh_var = np.var(result_enhanced.matrix, axis=0).sum()
        struct_var = np.var(result_structural.matrix, axis=0).sum()

        print(f"\nVariance comparison:")
        print(f"  Original neural: {orig_var:.6f}")
        print(f"  Enhanced neural: {enh_var:.6f}")
        print(f"  Structural:      {struct_var:.6f}")

        improvement = (enh_var / orig_var) if orig_var > 0 else 0
        print(f"\nImprovement: {improvement:.2f}x")

        if improvement > 1.5:
            print("✓ SIGNIFICANT IMPROVEMENT - preprocessing helps!")
        elif improvement > 1.1:
            print("✓ Moderate improvement")
        else:
            print("✗ No significant improvement - may need larger latent dim")

        # Check if enhanced is closer to structural
        ratio_orig = struct_var / orig_var if orig_var > 0 else 0
        ratio_enh = struct_var / enh_var if enh_var > 0 else 0

        print(f"\nGap to structural:")
        print(f"  Original: {ratio_orig:.2f}x")
        print(f"  Enhanced: {ratio_enh:.2f}x")

        if ratio_enh < ratio_orig * 0.8:
            print("✓ Gap reduced significantly!")

    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    if not result_enhanced.fallback_reason:
        enh_var = np.var(result_enhanced.matrix, axis=0).sum()

        if enh_var < 0.01:
            print("\n⚠ Enhanced features still have low variance")
            print("Recommendations:")
            print("  1. Increase latent dimension (32 -> 64 or 128)")
            print("  2. Retrain VAE with discriminative loss")
            print("  3. Use contrastive learning")
        elif enh_var < 0.1:
            print("\n✓ Enhanced features are usable but could be better")
            print("Recommendations:")
            print("  1. Consider increasing latent dimension to 64")
            print("  2. Fine-tune preprocessing thresholds")
        else:
            print("\n✓ Enhanced features look good!")
            print("Ready to use in clustering pipeline")


if __name__ == "__main__":
    main()
