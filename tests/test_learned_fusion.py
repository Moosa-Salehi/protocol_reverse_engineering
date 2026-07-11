from __future__ import annotations

import warnings
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.clustering.learned_fusion import SimpleFusionMLP


def test_feature_importance_handles_constant_columns_without_runtime_warning() -> None:
    features = np.array(
        [
            [1.0, 0.0, 5.0, 10.0],
            [1.0, 0.1, 5.0, 11.0],
            [1.0, 0.2, 5.0, 12.0],
            [1.0, 0.3, 5.0, 13.0],
        ],
        dtype=np.float32,
    )
    mlp = SimpleFusionMLP(neural_dim=2, structural_dim=2)

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        importance = mlp._compute_feature_importance(features)

    assert importance.shape == (4,)
    assert np.isfinite(importance).all()


def test_feature_importance_handles_non_finite_values_without_runtime_warning() -> None:
    features = np.array(
        [
            [1.0, 0.0, np.nan, 10.0],
            [1.0, 0.1, np.inf, 11.0],
            [1.0, 0.2, -np.inf, 12.0],
            [1.0, 0.3, 5.0, 13.0],
        ],
        dtype=np.float32,
    )
    mlp = SimpleFusionMLP(neural_dim=2, structural_dim=2)

    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        importance = mlp._compute_feature_importance(features)

    assert importance.shape == (4,)
    assert np.isfinite(importance).all()
