"""Deterministic, label-free per-corpus standardization of neural latent features.

The pre-trained VAE is trained on one distribution; a target corpus may differ in the
*scale and offset* of individual latent dimensions even when the directions are fine.
That mismatch (plus a single high-variance dimension dominating Euclidean distance) is a
common cause of poor / collapsed-looking clustering. Z-scoring each latent dimension on
the corpus itself removes both problems without any training, labels, or randomness.

Design notes:
- **Fit once, transform many.** Family discovery fits clustering + PCA + centroids on a
  *sample*, then assigns the rest of the corpus in *batches*. The standardizer must be fit
  on the sample and then applied unchanged to every batch; fitting per-batch would put
  batches in slightly different coordinate systems and break centroid assignment. Hence
  the explicit fit/transform split rather than a stateless function.
- **Cache-compatible.** Standardization is applied to the assembled matrix only; the latent
  cache keeps storing raw encoder outputs, so cached runs stay valid and reproducible.
- **Collapse-preserving.** Dead/constant dimensions (std ~ 0) are divided by 1.0, so they
  stay near zero instead of being amplified to unit-variance noise. Callers must run any
  collapse/quality detection on the RAW latents *before* standardizing, otherwise z-scoring
  would mask a collapsed dimension.
"""
from __future__ import annotations

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None


class LatentStandardizer:
    def __init__(self, *, eps: float = 1e-6, clip: float | None = 8.0) -> None:
        self.eps = eps
        self.clip = clip
        self.mean = None
        self.scale = None

    @property
    def fitted(self) -> bool:
        return self.mean is not None

    def fit(self, matrix: object) -> "LatentStandardizer":
        if np is None:
            return self
        arr = np.asarray(matrix, dtype=np.float32)
        if arr.ndim != 2 or arr.shape[0] == 0:
            return self
        self.mean = arr.mean(axis=0, keepdims=True)
        std = arr.std(axis=0, keepdims=True)
        # Floor near-zero std so constant/collapsed dims are not blown up into noise.
        self.scale = np.where(std < self.eps, 1.0, std).astype(np.float32)
        return self

    def transform(self, matrix: object) -> object:
        if np is None or self.mean is None:
            return matrix
        arr = np.asarray(matrix, dtype=np.float32)
        # Width must match what we fit on; otherwise pass through unchanged.
        if arr.ndim != 2 or arr.shape[1] != self.mean.shape[1]:
            return arr
        out = (arr - self.mean) / self.scale
        if self.clip is not None:
            out = np.clip(out, -self.clip, self.clip)
        return out.astype(np.float32)

    def fit_transform(self, matrix: object) -> object:
        return self.fit(matrix).transform(matrix)
