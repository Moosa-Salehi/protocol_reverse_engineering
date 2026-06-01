#!/usr/bin/env python3
"""
Diagnostic tool to analyze neural feature collapse in clustering.

This script:
1. Loads messages and extracts neural features
2. Analyzes latent space distribution
3. Compares neural vs raw_bytes clustering quality
4. Identifies why neural features fail to discriminate
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, stdev

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.clustering.hybrid_features import build_feature_matrix
from protocol_re.utils.bytes import hex_to_bytes
from protocol_re.utils.logging import setup_stage_logging

try:
    import numpy as np
except ImportError:
    print("Error: NumPy is required for this diagnostic tool")
    sys.exit(1)


def analyze_latent_distribution(latent_matrix: np.ndarray, records, ground_truth_families=None):
    """Analyze the distribution of latent vectors."""
    print("\n" + "="*80)
    print("LATENT SPACE DISTRIBUTION ANALYSIS")
    print("="*80)

    # Basic statistics
    print(f"\nLatent matrix shape: {latent_matrix.shape}")
    print(f"Latent dimension: {latent_matrix.shape[1]}")
    print(f"Number of samples: {latent_matrix.shape[0]}")

    # Per-dimension statistics
    print("\nPer-dimension statistics:")
    for dim in range(min(10, latent_matrix.shape[1])):
        values = latent_matrix[:, dim]
        print(f"  Dim {dim:2d}: mean={np.mean(values):7.4f}, std={np.std(values):7.4f}, "
              f"min={np.min(values):7.4f}, max={np.max(values):7.4f}")

    if latent_matrix.shape[1] > 10:
        print(f"  ... ({latent_matrix.shape[1] - 10} more dimensions)")

    # Overall variance
    total_variance = np.var(latent_matrix, axis=0).sum()
    print(f"\nTotal variance across all dimensions: {total_variance:.6f}")
    print(f"Average variance per dimension: {total_variance / latent_matrix.shape[1]:.6f}")

    # Check for collapsed dimensions (very low variance)
    variances = np.var(latent_matrix, axis=0)
    collapsed_dims = np.where(variances < 0.001)[0]
    if len(collapsed_dims) > 0:
        print(f"\n[WARNING] {len(collapsed_dims)} dimensions have collapsed (variance < 0.001)")
        print(f"   Collapsed dimensions: {collapsed_dims[:20].tolist()}")

    # Pairwise distances
    print("\nPairwise distance analysis (sample 1000 pairs):")
    sample_size = min(1000, latent_matrix.shape[0])
    sample_indices = np.random.choice(latent_matrix.shape[0], sample_size, replace=False)
    sample_latents = latent_matrix[sample_indices]

    distances = []
    for i in range(min(100, sample_size)):
        for j in range(i+1, min(i+10, sample_size)):
            dist = np.linalg.norm(sample_latents[i] - sample_latents[j])
            distances.append(dist)

    if distances:
        print(f"  Mean distance: {mean(distances):.4f}")
        print(f"  Std distance: {stdev(distances):.4f}")
        print(f"  Min distance: {min(distances):.4f}")
        print(f"  Max distance: {max(distances):.4f}")

        if mean(distances) < 0.1:
            print(f"\n[WARNING] Very small pairwise distances - latent space is collapsed!")

    # Analyze by ground truth families if available
    if ground_truth_families:
        print("\nAnalyzing latent separation by ground truth families:")
        family_latents = defaultdict(list)
        for idx, family in enumerate(ground_truth_families):
            if idx < len(latent_matrix):
                family_latents[family].append(latent_matrix[idx])

        # Compute within-family vs between-family distances
        within_distances = []
        between_distances = []

        families = list(family_latents.keys())[:5]  # Sample first 5 families
        for family in families:
            latents = np.array(family_latents[family])
            if len(latents) < 2:
                continue

            # Within-family distances
            for i in range(min(10, len(latents))):
                for j in range(i+1, min(i+5, len(latents))):
                    dist = np.linalg.norm(latents[i] - latents[j])
                    within_distances.append(dist)

        # Between-family distances
        for i, fam1 in enumerate(families[:3]):
            for fam2 in families[i+1:i+3]:
                latents1 = np.array(family_latents[fam1])
                latents2 = np.array(family_latents[fam2])
                for l1 in latents1[:5]:
                    for l2 in latents2[:5]:
                        dist = np.linalg.norm(l1 - l2)
                        between_distances.append(dist)

        if within_distances and between_distances:
            print(f"  Within-family distance: {mean(within_distances):.4f} ± {stdev(within_distances):.4f}")
            print(f"  Between-family distance: {mean(between_distances):.4f} ± {stdev(between_distances):.4f}")
            separation_ratio = mean(between_distances) / mean(within_distances) if within_distances else 0
            print(f"  Separation ratio (between/within): {separation_ratio:.2f}")

            if separation_ratio < 1.5:
                print(f"\n[WARNING] Poor separation - families are not well separated in latent space!")


def analyze_payload_characteristics(records):
    """Analyze characteristics of the payloads."""
    print("\n" + "="*80)
    print("PAYLOAD CHARACTERISTICS ANALYSIS")
    print("="*80)

    lengths = [r.payload_len for r in records]
    print(f"\nPayload lengths:")
    print(f"  Min: {min(lengths)}, Max: {max(lengths)}, Mean: {mean(lengths):.1f}")
    print(f"  Length distribution:")
    length_counts = Counter(lengths)
    for length, count in sorted(length_counts.items())[:10]:
        pct = 100 * count / len(records)
        print(f"    {length:3d} bytes: {count:6d} messages ({pct:5.2f}%)")

    # Analyze first few bytes (potential discriminators)
    print(f"\nFirst byte distribution (potential discriminator):")
    first_bytes = []
    for r in records[:10000]:  # Sample
        payload = hex_to_bytes(r.payload_hex)
        if len(payload) > 0:
            first_bytes.append(payload[0])

    if first_bytes:
        byte_counts = Counter(first_bytes)
        print(f"  Unique values: {len(byte_counts)}")
        print(f"  Top 10 values:")
        for byte_val, count in byte_counts.most_common(10):
            pct = 100 * count / len(first_bytes)
            print(f"    0x{byte_val:02x}: {count:6d} ({pct:5.2f}%)")

    # Analyze byte 7 (potential function code in layered protocols)
    print(f"\nByte 7 distribution (potential inner discriminator):")
    byte7_values = []
    for r in records[:10000]:
        payload = hex_to_bytes(r.payload_hex)
        if len(payload) > 7:
            byte7_values.append(payload[7])

    if byte7_values:
        byte_counts = Counter(byte7_values)
        print(f"  Unique values: {len(byte_counts)}")
        print(f"  Top 10 values:")
        for byte_val, count in byte_counts.most_common(10):
            pct = 100 * count / len(byte7_values)
            print(f"    0x{byte_val:02x}: {count:6d} ({pct:5.2f}%)")


def compare_feature_modes(records, model_path, latent_cache_path):
    """Compare neural vs raw_bytes feature quality."""
    print("\n" + "="*80)
    print("FEATURE MODE COMPARISON")
    print("="*80)

    # Build neural features
    print("\nBuilding neural features...")
    neural_result = build_feature_matrix(
        records[:10000],  # Sample for speed
        records,
        feature_mode="neural",
        model_path=model_path,
        latent_cache_path=latent_cache_path,
        latent_dim=32,
    )

    if neural_result.fallback_reason:
        print(f"⚠️  Neural features failed: {neural_result.fallback_reason}")
        return

    print(f"Neural feature matrix shape: {neural_result.matrix.shape}")
    print(f"Neural feature mode: {neural_result.feature_mode}")

    # Build structural features
    print("\nBuilding structural features...")
    structural_result = build_feature_matrix(
        records[:10000],
        records,
        feature_mode="structural",
    )
    print(f"Structural feature matrix shape: {structural_result.matrix.shape}")
    print(f"Structural feature count: {structural_result.symbolic_feature_count}")

    # Compare variance
    neural_variance = np.var(neural_result.matrix, axis=0).sum()
    structural_variance = np.var(structural_result.matrix, axis=0).sum()

    print(f"\nTotal variance comparison:")
    print(f"  Neural: {neural_variance:.6f}")
    print(f"  Structural: {structural_variance:.6f}")
    print(f"  Ratio (structural/neural): {structural_variance / neural_variance:.2f}x")

    if structural_variance > neural_variance * 2:
        print(f"\n[WARNING] Structural features have much higher variance - neural features are too compressed!")


def main():
    parser = argparse.ArgumentParser(description="Diagnose neural feature collapse")
    parser.add_argument("messages_jsonl", help="Path to messages JSONL file")
    parser.add_argument("--model-path", default="industrial_VAE.pth", help="Path to neural model")
    parser.add_argument("--latent-cache", default="data/latent_cache.json", help="Path to latent cache")
    parser.add_argument("--sample-size", type=int, default=10000, help="Number of messages to analyze")
    parser.add_argument("--ground-truth", help="Optional ground truth family assignments JSON")
    args = parser.parse_args()

    print("="*80)
    print("NEURAL FEATURE DIAGNOSTIC TOOL")
    print("="*80)
    print(f"\nLoading messages from: {args.messages_jsonl}")

    records = load_corpus_jsonl(args.messages_jsonl)
    print(f"Loaded {len(records)} messages")

    # Sample if needed
    if len(records) > args.sample_size:
        print(f"Sampling {args.sample_size} messages for analysis...")
        import random
        records = random.sample(records, args.sample_size)

    # Load ground truth if provided
    ground_truth_families = None
    if args.ground_truth:
        print(f"Loading ground truth from: {args.ground_truth}")
        with open(args.ground_truth, 'r') as f:
            gt_data = json.load(f)
            family_by_msg_id = {a['msg_id']: a['family_id'] for a in gt_data['assignments']}
            ground_truth_families = [family_by_msg_id.get(r.msg_id, 'unknown') for r in records]

    # Analyze payload characteristics
    analyze_payload_characteristics(records)

    # Compare feature modes
    compare_feature_modes(records, args.model_path, args.latent_cache)

    # Build neural features for detailed analysis
    print("\n" + "="*80)
    print("BUILDING NEURAL FEATURES FOR DETAILED ANALYSIS")
    print("="*80)

    result = build_feature_matrix(
        records,
        records,
        feature_mode="neural",
        model_path=args.model_path,
        latent_cache_path=args.latent_cache,
        latent_dim=32,
    )

    if result.fallback_reason:
        print(f"\n[ERROR] Failed to build neural features: {result.fallback_reason}")
        print("\nPossible causes:")
        print("  - PyTorch not installed")
        print("  - Neural model file not found")
        print("  - Model architecture mismatch")
        return

    print(f"\n[OK] Successfully built neural features")
    print(f"  Feature mode: {result.feature_mode}")
    print(f"  Matrix shape: {result.matrix.shape}")
    print(f"  Latent dim: {result.latent_dim}")

    # Analyze latent distribution
    analyze_latent_distribution(result.matrix, records, ground_truth_families)

    # Summary and recommendations
    print("\n" + "="*80)
    print("SUMMARY AND RECOMMENDATIONS")
    print("="*80)

    print("\nKey findings:")
    print("  1. Check if latent space has collapsed (low variance)")
    print("  2. Check if pairwise distances are too small")
    print("  3. Check if families are well-separated in latent space")
    print("  4. Compare neural vs structural feature variance")

    print("\nRecommended fixes:")
    print("  1. Increase latent dimension (32 -> 64 or 128)")
    print("  2. Add discriminative loss to VAE training")
    print("  3. Mask variable fields (transaction IDs) before encoding")
    print("  4. Use attention mechanism to focus on discriminative bytes")
    print("  5. Add contrastive learning to separate different message types")


if __name__ == "__main__":
    main()
