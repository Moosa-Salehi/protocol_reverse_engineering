"""
Learned hybrid feature fusion with adaptive weighting.

This module implements intelligent fusion of neural and structural features:
1. Small MLP to learn optimal feature weights
2. Feature importance analysis
3. Adaptive weighting based on feature quality
4. Automatic override when structural features are more confident
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

try:
    import numpy as np
except ImportError:
    np = None


@dataclass
class FusionWeights:
    """Learned or computed fusion weights."""
    neural_weight: float
    structural_weight: float
    feature_importance: Optional[object] = None  # numpy array
    quality_score: float = 0.0
    method: str = "adaptive"  # adaptive, learned, fixed


class SimpleFusionMLP:
    """
    Simple MLP for learning feature fusion weights.

    Architecture:
    - Input: concatenated [neural_features, structural_features]
    - Hidden: small layer (16-32 units)
    - Output: weighted combination

    This is lightweight and doesn't require training data - uses
    unsupervised quality metrics to learn weights.
    """

    def __init__(self, neural_dim: int, structural_dim: int, hidden_dim: int = 16):
        """
        Initialize fusion MLP.

        Args:
            neural_dim: Dimension of neural features
            structural_dim: Dimension of structural features
            hidden_dim: Hidden layer size (default: 16)
        """
        if np is None:
            raise RuntimeError("NumPy required for learned fusion")

        self.neural_dim = neural_dim
        self.structural_dim = structural_dim
        self.hidden_dim = hidden_dim

        # Initialize weights with Xavier initialization
        input_dim = neural_dim + structural_dim
        self.W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden_dim)

        # Output layer learns feature importance weights
        self.W2 = np.random.randn(hidden_dim, input_dim) * np.sqrt(2.0 / hidden_dim)
        self.b2 = np.zeros(input_dim)

    def forward(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Forward pass through MLP.

        Args:
            features: [N, neural_dim + structural_dim] concatenated features

        Returns:
            weighted_features: [N, neural_dim + structural_dim] weighted features
            importance: [neural_dim + structural_dim] feature importance weights
        """
        # Hidden layer with ReLU
        hidden = np.maximum(0, features @ self.W1 + self.b1)

        # Output layer with sigmoid (importance weights in [0, 1])
        importance = 1.0 / (1.0 + np.exp(-(hidden @ self.W2 + self.b2)))

        # Apply importance weights
        weighted = features * importance

        return weighted, importance.mean(axis=0)

    def compute_adaptive_weights(
        self,
        neural_features: np.ndarray,
        structural_features: np.ndarray
    ) -> FusionWeights:
        """
        Compute adaptive weights based on feature quality.

        Uses unsupervised metrics:
        - Variance (higher = more informative)
        - Separation (higher = better clustering potential)
        - Stability (lower variance in variance = more stable)

        Args:
            neural_features: [N, neural_dim]
            structural_features: [N, structural_dim]

        Returns:
            FusionWeights with computed weights
        """
        # Compute quality metrics for each feature type
        neural_quality = self._compute_feature_quality(neural_features)
        structural_quality = self._compute_feature_quality(structural_features)

        # Normalize weights (sum to 1)
        total_quality = neural_quality + structural_quality
        if total_quality > 0:
            neural_weight = neural_quality / total_quality
            structural_weight = structural_quality / total_quality
        else:
            # Fallback to equal weights
            neural_weight = 0.5
            structural_weight = 0.5

        # Compute per-feature importance
        concat_features = np.concatenate([neural_features, structural_features], axis=1)
        feature_importance = self._compute_feature_importance(concat_features)

        return FusionWeights(
            neural_weight=float(neural_weight),
            structural_weight=float(structural_weight),
            feature_importance=feature_importance,
            quality_score=float(total_quality),
            method="adaptive"
        )

    def _compute_feature_quality(self, features: np.ndarray) -> float:
        """
        Compute quality score for a feature matrix.

        Quality = variance * separation * (1 - instability)

        Args:
            features: [N, D] feature matrix

        Returns:
            Quality score (higher = better)
        """
        if features.shape[0] < 2:
            return 0.0

        # Variance: how much information is preserved
        variance = np.var(features, axis=0).mean()

        # Separation: how well-separated are the points
        # Use ratio of between-cluster to within-cluster variance
        mean = features.mean(axis=0)
        distances = np.linalg.norm(features - mean, axis=1)
        separation = distances.std() / (distances.mean() + 1e-8)

        # Stability: consistency of variance across dimensions
        dim_variances = np.var(features, axis=0)
        instability = dim_variances.std() / (dim_variances.mean() + 1e-8)
        stability = 1.0 / (1.0 + instability)

        # Combined quality score
        quality = variance * separation * stability

        return float(quality)

    def _compute_feature_importance(self, features: np.ndarray) -> np.ndarray:
        """
        Compute per-feature importance scores.

        Importance based on:
        - Variance (information content)
        - Correlation with other features (redundancy penalty)

        Args:
            features: [N, D] feature matrix

        Returns:
            importance: [D] importance scores
        """
        if features.shape[0] < 2:
            return np.ones(features.shape[1])

        # Variance-based importance
        variances = np.var(features, axis=0)
        variance_importance = variances / (variances.sum() + 1e-8)

        # Correlation-based redundancy penalty
        # Features highly correlated with others are less important
        correlation = np.corrcoef(features.T)
        np.fill_diagonal(correlation, 0)  # Ignore self-correlation
        redundancy = np.abs(correlation).mean(axis=1)
        redundancy_penalty = 1.0 - redundancy

        # Combined importance
        importance = variance_importance * redundancy_penalty

        # Normalize to [0, 1]
        importance = importance / (importance.max() + 1e-8)

        return importance


def fuse_features_adaptive(
    neural_features: np.ndarray,
    structural_features: np.ndarray,
    method: str = "adaptive",
    neural_weight: Optional[float] = None,
    structural_weight: Optional[float] = None,
) -> Tuple[np.ndarray, FusionWeights]:
    """
    Fuse neural and structural features with adaptive or learned weighting.

    Args:
        neural_features: [N, neural_dim] neural feature matrix
        structural_features: [N, structural_dim] structural feature matrix
        method: Fusion method - "adaptive", "learned", "fixed", "concat"
        neural_weight: Fixed neural weight (for method="fixed")
        structural_weight: Fixed structural weight (for method="fixed")

    Returns:
        fused_features: [N, D] fused feature matrix
        weights: FusionWeights object with computed weights and importance
    """
    if np is None:
        raise RuntimeError("NumPy required for feature fusion")

    if neural_features.shape[0] != structural_features.shape[0]:
        raise ValueError("Neural and structural features must have same number of samples")

    # Simple concatenation (baseline)
    if method == "concat":
        fused = np.concatenate([neural_features, structural_features], axis=1)
        weights = FusionWeights(
            neural_weight=0.5,
            structural_weight=0.5,
            method="concat"
        )
        return fused, weights

    # Fixed weights
    if method == "fixed":
        if neural_weight is None or structural_weight is None:
            raise ValueError("Fixed method requires neural_weight and structural_weight")

        # Normalize weights
        total = neural_weight + structural_weight
        neural_weight = neural_weight / total
        structural_weight = structural_weight / total

        # Scale features by weights
        neural_scaled = neural_features * neural_weight
        structural_scaled = structural_features * structural_weight
        fused = np.concatenate([neural_scaled, structural_scaled], axis=1)

        weights = FusionWeights(
            neural_weight=neural_weight,
            structural_weight=structural_weight,
            method="fixed"
        )
        return fused, weights

    # Adaptive weighting based on feature quality
    if method == "adaptive":
        mlp = SimpleFusionMLP(
            neural_dim=neural_features.shape[1],
            structural_dim=structural_features.shape[1]
        )

        weights = mlp.compute_adaptive_weights(neural_features, structural_features)

        # Scale features by computed weights
        neural_scaled = neural_features * weights.neural_weight
        structural_scaled = structural_features * weights.structural_weight
        fused = np.concatenate([neural_scaled, structural_scaled], axis=1)

        return fused, weights

    # Learned weighting with MLP
    if method == "learned":
        mlp = SimpleFusionMLP(
            neural_dim=neural_features.shape[1],
            structural_dim=structural_features.shape[1]
        )

        # Concatenate features
        concat_features = np.concatenate([neural_features, structural_features], axis=1)

        # Forward pass to get weighted features and importance
        fused, importance = mlp.forward(concat_features)

        # Compute weights from importance
        neural_importance = importance[:neural_features.shape[1]].mean()
        structural_importance = importance[neural_features.shape[1]:].mean()
        total_importance = neural_importance + structural_importance

        if total_importance > 0:
            neural_weight = neural_importance / total_importance
            structural_weight = structural_importance / total_importance
        else:
            neural_weight = 0.5
            structural_weight = 0.5

        weights = FusionWeights(
            neural_weight=float(neural_weight),
            structural_weight=float(structural_weight),
            feature_importance=importance,
            quality_score=float(total_importance),
            method="learned"
        )

        return fused, weights

    raise ValueError(f"Unknown fusion method: {method}")


def detect_neural_collapse(
    neural_features: np.ndarray,
    variance_threshold: float = 0.01,
    separation_threshold: float = 0.1
) -> Tuple[bool, str]:
    """
    Detect if neural features have collapsed (lost discriminative power).

    Args:
        neural_features: [N, D] neural feature matrix
        variance_threshold: Minimum acceptable variance
        separation_threshold: Minimum acceptable separation

    Returns:
        collapsed: True if features have collapsed
        reason: Description of why collapse was detected
    """
    if np is None or neural_features.shape[0] < 2:
        return False, ""

    # Check variance
    variance = np.var(neural_features, axis=0).mean()
    if variance < variance_threshold:
        return True, f"low_variance:{variance:.4f}<{variance_threshold}"

    # Check separation
    mean = neural_features.mean(axis=0)
    distances = np.linalg.norm(neural_features - mean, axis=1)
    separation = distances.std() / (distances.mean() + 1e-8)

    if separation < separation_threshold:
        return True, f"low_separation:{separation:.4f}<{separation_threshold}"

    return False, ""


def should_override_with_structural(
    neural_features: np.ndarray,
    structural_features: np.ndarray,
    collapse_threshold: float = 0.3
) -> Tuple[bool, str]:
    """
    Determine if structural features should completely override neural features.

    This happens when:
    1. Neural features have collapsed
    2. Structural features have much higher quality

    Args:
        neural_features: [N, D] neural feature matrix
        structural_features: [N, D] structural feature matrix
        collapse_threshold: Quality ratio threshold for override

    Returns:
        should_override: True if structural should override
        reason: Explanation
    """
    if np is None:
        return False, ""

    # Check for neural collapse
    collapsed, collapse_reason = detect_neural_collapse(neural_features)
    if collapsed:
        return True, f"neural_collapse:{collapse_reason}"

    # Compare feature quality
    mlp = SimpleFusionMLP(
        neural_dim=neural_features.shape[1],
        structural_dim=structural_features.shape[1]
    )

    neural_quality = mlp._compute_feature_quality(neural_features)
    structural_quality = mlp._compute_feature_quality(structural_features)

    # If structural is much better, override
    if structural_quality > 0 and neural_quality / structural_quality < collapse_threshold:
        ratio = neural_quality / structural_quality
        return True, f"quality_ratio:{ratio:.4f}<{collapse_threshold}"

    return False, ""
