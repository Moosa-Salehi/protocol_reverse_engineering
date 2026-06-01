#!/usr/bin/env python3
"""
Test script for learned hybrid feature fusion (A1 completion).

Tests:
1. Adaptive fusion with quality-based weighting
2. Learned fusion with MLP
3. Neural collapse detection
4. Structural override when neural fails
5. Feature importance analysis
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import json
import numpy as np
from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.clustering.hybrid_features import build_feature_matrix
from protocol_re.clustering.learned_fusion import (
    fuse_features_adaptive,
    detect_neural_collapse,
    should_override_with_structural,
)
from protocol_re.utils.logging import setup_stage_logging


def test_fusion_methods(records, corpus_records, model_path="assets/pre_trained/industrial_VAE.pth"):
    """Test different fusion methods."""
    print("\n" + "="*80)
    print("TESTING FUSION METHODS")
    print("="*80)

    # Build neural features
    print("\nBuilding neural features...")
    neural_result = build_feature_matrix(
        records[:1000],
        corpus_records,
        feature_mode="neural",
        model_path=model_path,
        latent_cache_path="data/02_latent_cache.json",
    )

    if neural_result.fallback_reason:
        print(f"[!] Neural features unavailable: {neural_result.fallback_reason}")
        return

    neural_features = neural_result.matrix

    # Build structural features
    print("Building structural features...")
    structural_result = build_feature_matrix(
        records[:1000],
        corpus_records,
        feature_mode="structural",
    )
    structural_features = structural_result.matrix

    print(f"\nNeural features shape: {neural_features.shape}")
    print(f"Structural features shape: {structural_features.shape}")

    # Test 1: Simple concatenation (baseline)
    print("\n" + "-"*80)
    print("TEST 1: Simple Concatenation (baseline)")
    print("-"*80)
    concat_result = build_feature_matrix(
        records[:1000],
        corpus_records,
        feature_mode="hybrid",
        model_path=model_path,
        latent_cache_path="data/02_latent_cache.json",
        fusion_method="concat",
    )
    print(f"Fused features shape: {concat_result.matrix.shape}")
    print(f"Fusion method: {concat_result.fusion_method}")
    if concat_result.fallback_reason:
        print(f"[!] Fallback: {concat_result.fallback_reason}")

    # Test 2: Adaptive fusion
    print("\n" + "-"*80)
    print("TEST 2: Adaptive Fusion (quality-based)")
    print("-"*80)
    adaptive_result = build_feature_matrix(
        records[:1000],
        corpus_records,
        feature_mode="hybrid",
        model_path=model_path,
        latent_cache_path="data/02_latent_cache.json",
        fusion_method="adaptive",
    )
    print(f"Fused features shape: {adaptive_result.matrix.shape}")
    print(f"Fusion method: {adaptive_result.fusion_method}")
    if adaptive_result.fallback_reason:
        print(f"[!] Fallback: {adaptive_result.fallback_reason}")
    if adaptive_result.neural_weight is not None:
        print(f"Neural weight: {adaptive_result.neural_weight:.4f}")
        print(f"Structural weight: {adaptive_result.structural_weight:.4f}")
        print(f"Quality score: {adaptive_result.fusion_quality_score:.4f}")
    else:
        print("[!] Fusion not applied (structural override or fallback)")

    # Test 3: Learned fusion
    print("\n" + "-"*80)
    print("TEST 3: Learned Fusion (MLP)")
    print("-"*80)
    learned_result = build_feature_matrix(
        records[:1000],
        corpus_records,
        feature_mode="hybrid",
        model_path=model_path,
        latent_cache_path="data/02_latent_cache.json",
        fusion_method="learned",
    )
    print(f"Fused features shape: {learned_result.matrix.shape}")
    print(f"Fusion method: {learned_result.fusion_method}")
    if learned_result.fallback_reason:
        print(f"[!] Fallback: {learned_result.fallback_reason}")
    if learned_result.neural_weight is not None:
        print(f"Neural weight: {learned_result.neural_weight:.4f}")
        print(f"Structural weight: {learned_result.structural_weight:.4f}")
        print(f"Quality score: {learned_result.fusion_quality_score:.4f}")

        if learned_result.feature_importance is not None:
            importance = learned_result.feature_importance
            print(f"\nFeature importance (top 10):")
            top_indices = np.argsort(importance)[-10:][::-1]
            for idx in top_indices:
                print(f"  Feature {idx}: {importance[idx]:.4f}")
    else:
        print("[!] Fusion not applied (structural override or fallback)")

    # Test 4: Neural collapse detection
    print("\n" + "-"*80)
    print("TEST 4: Neural Collapse Detection")
    print("-"*80)
    collapsed, reason = detect_neural_collapse(neural_features)
    print(f"Neural collapsed: {collapsed}")
    if collapsed:
        print(f"Reason: {reason}")
    else:
        print("Neural features are healthy")

    # Test 5: Structural override check
    print("\n" + "-"*80)
    print("TEST 5: Structural Override Check")
    print("-"*80)
    should_override, override_reason = should_override_with_structural(
        neural_features, structural_features
    )
    print(f"Should override with structural: {should_override}")
    if should_override:
        print(f"Reason: {override_reason}")
    else:
        print("Neural features are acceptable")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nConcat:   shape={concat_result.matrix.shape}, fallback={concat_result.fallback_reason or 'none'}")
    if adaptive_result.neural_weight:
        print(f"Adaptive: shape={adaptive_result.matrix.shape}, "
              f"neural_w={adaptive_result.neural_weight:.3f}, "
              f"struct_w={adaptive_result.structural_weight:.3f}")
    else:
        print(f"Adaptive: shape={adaptive_result.matrix.shape}, fallback={adaptive_result.fallback_reason}")

    if learned_result.neural_weight:
        print(f"Learned:  shape={learned_result.matrix.shape}, "
              f"neural_w={learned_result.neural_weight:.3f}, "
              f"struct_w={learned_result.structural_weight:.3f}")
    else:
        print(f"Learned:  shape={learned_result.matrix.shape}, fallback={learned_result.fallback_reason}")

    # Recommendation
    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)

    if should_override:
        print("\n[!] Neural features have collapsed - use structural mode only")
        print(f"    Reason: {override_reason}")
    elif adaptive_result.structural_weight > 0.7:
        print("\n[!] Structural features dominate - consider using structural mode")
        print(f"    Structural weight: {adaptive_result.structural_weight:.2%}")
    elif adaptive_result.neural_weight > 0.7:
        print("\n[OK] Neural features dominate - hybrid mode working well")
        print(f"    Neural weight: {adaptive_result.neural_weight:.2%}")
    else:
        print("\n[OK] Balanced fusion - hybrid mode recommended")
        print(f"    Neural: {adaptive_result.neural_weight:.2%}, "
              f"Structural: {adaptive_result.structural_weight:.2%}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test learned hybrid feature fusion")
    parser.add_argument("messages_jsonl", help="Path to messages JSONL")
    parser.add_argument("--sample-size", type=int, default=1000, help="Number of messages to test")
    parser.add_argument("--model-path", default="assets/pre_trained/industrial_VAE.pth",
                        help="Path to neural VAE model checkpoint")
    args = parser.parse_args()

    print("="*80)
    print("LEARNED HYBRID FEATURE FUSION TEST (A1 Completion)")
    print("="*80)

    print(f"\nLoading messages from: {args.messages_jsonl}")
    records = load_corpus_jsonl(args.messages_jsonl)
    print(f"Loaded {len(records)} messages")

    sample_records = records[:args.sample_size]
    print(f"Testing with {len(sample_records)} messages")

    test_fusion_methods(sample_records, records, model_path=args.model_path)

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
