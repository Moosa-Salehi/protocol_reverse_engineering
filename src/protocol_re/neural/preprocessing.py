"""
Improved neural feature extraction with protocol-agnostic preprocessing.

This module addresses neural feature collapse by:
1. Detecting and masking variable fields (transaction IDs, counters)
2. Normalizing payload lengths
3. Adding position-aware encoding
4. Implementing fallback detection
"""
from __future__ import annotations

from typing import List, Sequence, Set
from collections import Counter

try:
    import numpy as np
except ImportError:
    np = None


def detect_variable_offsets(payloads: Sequence[bytes], threshold: float = 0.75) -> Set[int]:
    """
    Detect byte offsets that are highly variable (likely transaction IDs, counters, timestamps).

    Protocol-agnostic detection based on:
    - High cardinality (many unique values)
    - Low stability (no dominant value)
    - High entropy

    Args:
        payloads: List of payload bytes
        threshold: Uniqueness ratio threshold (default 0.75)

    Returns:
        Set of offsets to mask
    """
    if not payloads or len(payloads) < 10:
        return set()

    max_len = max(len(p) for p in payloads)
    variable_offsets: Set[int] = set()

    # Analyze first 32 bytes (typical header region)
    for offset in range(min(32, max_len)):
        values = [p[offset] for p in payloads if offset < len(p)]
        if len(values) < 10:
            continue

        # Calculate metrics
        unique_count = len(set(values))
        unique_ratio = unique_count / len(values)

        # Most common value frequency
        if values:
            most_common_count = Counter(values).most_common(1)[0][1]
            stability = most_common_count / len(values)
        else:
            stability = 0.0

        # Mark as variable if:
        # - High uniqueness (many different values)
        # - Low stability (no dominant value)
        if unique_ratio >= threshold and stability < 0.35:
            variable_offsets.add(offset)

    return variable_offsets


def detect_stable_prefix_length(payloads: Sequence[bytes], stability_threshold: float = 0.90) -> int:
    """
    Detect the length of stable prefix (potential outer header).

    Returns the offset where stability drops below threshold.
    """
    if not payloads or len(payloads) < 10:
        return 0

    max_len = min(32, max(len(p) for p in payloads))

    for offset in range(max_len):
        values = [p[offset] for p in payloads if offset < len(p)]
        if len(values) < len(payloads) * 0.8:  # Coverage check
            return offset

        if values:
            most_common_count = Counter(values).most_common(1)[0][1]
            stability = most_common_count / len(values)

            if stability < stability_threshold:
                return offset

    return 0


def preprocess_payload_for_neural(
    payload: bytes,
    variable_offsets: Set[int],
    max_length: int = 256,
    mask_value: float = 0.5
) -> List[float]:
    """
    Preprocess a single payload for neural encoding.

    Steps:
    1. Mask variable offsets (transaction IDs, counters)
    2. Normalize bytes to [0, 1]
    3. Pad/truncate to max_length
    4. Add position embeddings (optional)

    Args:
        payload: Raw payload bytes
        variable_offsets: Set of offsets to mask
        max_length: Maximum length for padding/truncation
        mask_value: Value to use for masked bytes (0.5 = neutral)

    Returns:
        Preprocessed feature vector
    """
    # Clip to max length
    clipped = payload[:max_length]

    # Normalize and mask
    features = []
    for offset, byte_val in enumerate(clipped):
        if offset in variable_offsets:
            # Mask variable fields with neutral value
            features.append(mask_value)
        else:
            # Normalize to [0, 1]
            features.append(byte_val / 255.0)

    # Pad to max_length
    features.extend([0.0] * (max_length - len(features)))

    return features


def preprocess_payloads_batch(
    payloads: Sequence[bytes],
    max_length: int = 256,
    auto_detect_variable: bool = True
) -> tuple[List[List[float]], Set[int]]:
    """
    Preprocess a batch of payloads for neural encoding.

    Args:
        payloads: List of payload bytes
        max_length: Maximum length for padding/truncation
        auto_detect_variable: Automatically detect and mask variable fields

    Returns:
        Tuple of (preprocessed_features, variable_offsets)
    """
    if not payloads:
        return [], set()

    # Detect variable offsets if enabled
    variable_offsets: Set[int] = set()
    if auto_detect_variable and len(payloads) >= 10:
        variable_offsets = detect_variable_offsets(payloads)

    # Preprocess each payload
    preprocessed = [
        preprocess_payload_for_neural(p, variable_offsets, max_length)
        for p in payloads
    ]

    return preprocessed, variable_offsets


def check_neural_feature_quality(
    feature_matrix: np.ndarray,
    min_variance: float = 0.01,
    min_mean_distance: float = 0.1
) -> tuple[bool, str]:
    """
    Check if neural features have sufficient quality for clustering.

    Returns:
        Tuple of (is_good, reason)
    """
    if np is None:
        return False, "numpy_unavailable"

    if feature_matrix.size == 0:
        return False, "empty_matrix"

    # Check total variance
    total_variance = np.var(feature_matrix, axis=0).sum()
    if total_variance < min_variance:
        return False, f"low_variance:{total_variance:.6f}"

    # Check pairwise distances (sample)
    if feature_matrix.shape[0] >= 100:
        sample_size = min(100, feature_matrix.shape[0])
        sample_indices = np.random.choice(feature_matrix.shape[0], sample_size, replace=False)
        sample = feature_matrix[sample_indices]

        distances = []
        for i in range(min(20, sample_size)):
            for j in range(i+1, min(i+5, sample_size)):
                dist = np.linalg.norm(sample[i] - sample[j])
                distances.append(dist)

        if distances:
            mean_dist = np.mean(distances)
            if mean_dist < min_mean_distance:
                return False, f"collapsed_latent_space:mean_dist={mean_dist:.4f}"

    return True, "ok"


def compute_feature_importance(
    feature_matrix: np.ndarray,
    top_k: int = 10
) -> List[tuple[int, float]]:
    """
    Compute feature importance based on variance.

    Returns:
        List of (dimension_index, variance) tuples, sorted by variance
    """
    if np is None or feature_matrix.size == 0:
        return []

    variances = np.var(feature_matrix, axis=0)
    importance = [(i, float(v)) for i, v in enumerate(variances)]
    importance.sort(key=lambda x: -x[1])

    return importance[:top_k]
