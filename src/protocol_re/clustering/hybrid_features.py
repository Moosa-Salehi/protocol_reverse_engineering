from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from protocol_re.clustering.structural_features import (
    payload_hash,
    summarize_symbolic_feature_count,
    vectorize_structural_features,
)
from protocol_re.clustering.latent_standardize import LatentStandardizer
from protocol_re.model.schema import MessageRecord
from protocol_re.neural.artifacts import load_latent_cache, save_latent_cache
from protocol_re.neural.model_loader import DEFAULT_MODEL_PATH, load_optional_encoder_with_reason
from protocol_re.utils.bytes import hex_to_bytes

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None

try:
    from protocol_re.clustering.learned_fusion import (
        fuse_features_adaptive,
        should_override_with_structural,
    )
    LEARNED_FUSION_AVAILABLE = True
except ImportError:
    LEARNED_FUSION_AVAILABLE = False


@dataclass
class FeatureBuildResult:
    matrix: object
    feature_mode: str
    requested_feature_mode: str
    neural_model: str | None = None
    latent_dim: int = 0
    latent_cache: str | None = None
    symbolic_feature_count: int = 0
    fallback_reason: str | None = None
    extra_metadata: Dict[str, object] = field(default_factory=dict)
    # New fields for learned fusion
    fusion_method: str | None = None
    neural_weight: float | None = None
    structural_weight: float | None = None
    feature_importance: object | None = None  # numpy array
    fusion_quality_score: float | None = None


def build_feature_matrix(
    records: Sequence[MessageRecord],
    corpus_records: Sequence[MessageRecord],
    feature_mode: str,
    model_path: str | None = None,
    latent_cache_path: str | None = None,
    neural_batch_size: int = 256,
    latent_dim: int = 32,
    fusion_method: str = "adaptive",  # New parameter
    neural_weight: float | None = None,
    structural_weight: float | None = None,
    latent_standardizer: LatentStandardizer | None = None,
) -> FeatureBuildResult:
    if np is None:
        raise RuntimeError("NumPy is required for feature matrix construction")
    if feature_mode == "structural":
        matrix = vectorize_structural_features(records, corpus_records=corpus_records)
        return FeatureBuildResult(
            matrix=matrix,
            feature_mode="structural",
            requested_feature_mode=feature_mode,
            symbolic_feature_count=summarize_symbolic_feature_count(),
        )
    if feature_mode in {"neural", "hybrid"}:
        neural, neural_unavailable_reason = _build_neural_matrix(records, model_path, latent_cache_path, neural_batch_size, latent_dim)
        if neural is None:
            matrix = vectorize_structural_features(records, corpus_records=corpus_records)
            return FeatureBuildResult(
                matrix=matrix,
                feature_mode="structural",
                requested_feature_mode=feature_mode,
                neural_model=str(model_path or DEFAULT_MODEL_PATH),
                latent_dim=0,
                latent_cache=latent_cache_path,
                symbolic_feature_count=summarize_symbolic_feature_count(),
                fallback_reason=neural_unavailable_reason or "neural_model_or_dependency_unavailable",
            )
        # Deterministic per-corpus latent standardization. Fit once (on the clustering
        # sample) and reuse for every later batch so the latent coordinate system is
        # stable across sampled centroids and unsampled assignments. Run this AFTER any
        # collapse detection below, never before, so z-scoring cannot mask a dead dim.
        def _standardize(neural_matrix):
            if latent_standardizer is None:
                return neural_matrix, False
            if not latent_standardizer.fitted:
                latent_standardizer.fit(neural_matrix)
            return latent_standardizer.transform(neural_matrix), True

        if feature_mode == "neural":
            neural_std, standardized = _standardize(neural)
            return FeatureBuildResult(
                matrix=neural_std,
                feature_mode="neural",
                requested_feature_mode=feature_mode,
                neural_model=str(model_path or DEFAULT_MODEL_PATH),
                latent_dim=latent_dim,
                latent_cache=latent_cache_path,
                extra_metadata={"latent_standardized": standardized},
            )

        # Build structural features
        structural = vectorize_structural_features(records, corpus_records=corpus_records)

        # Check if structural should override neural (collapse detection) — on RAW latents.
        if LEARNED_FUSION_AVAILABLE:
            should_override, override_reason = should_override_with_structural(neural, structural)
            if should_override:
                return FeatureBuildResult(
                    matrix=structural,
                    feature_mode="structural",
                    requested_feature_mode=feature_mode,
                    neural_model=str(model_path or DEFAULT_MODEL_PATH),
                    latent_dim=latent_dim,
                    latent_cache=latent_cache_path,
                    symbolic_feature_count=int(structural.shape[1]),
                    fallback_reason=f"neural_override:{override_reason}",
                )

        # Standardize the latent block (pre-fusion) so fusion weighting operates on
        # comparable, per-dimension unit-scale latents rather than raw VAE outputs.
        neural_std, standardized = _standardize(neural)

        # Hybrid mode: fuse neural and structural features
        if LEARNED_FUSION_AVAILABLE and fusion_method != "concat":
            # Use learned fusion
            try:
                matrix, fusion_weights = fuse_features_adaptive(
                    neural_features=neural_std,
                    structural_features=structural,
                    method=fusion_method,
                    neural_weight=neural_weight,
                    structural_weight=structural_weight,
                )

                return FeatureBuildResult(
                    matrix=matrix,
                    feature_mode="hybrid",
                    requested_feature_mode=feature_mode,
                    neural_model=str(model_path or DEFAULT_MODEL_PATH),
                    latent_dim=latent_dim,
                    latent_cache=latent_cache_path,
                    symbolic_feature_count=int(structural.shape[1]),
                    fusion_method=fusion_weights.method,
                    neural_weight=fusion_weights.neural_weight,
                    structural_weight=fusion_weights.structural_weight,
                    feature_importance=fusion_weights.feature_importance,
                    fusion_quality_score=fusion_weights.quality_score,
                    extra_metadata={"latent_standardized": standardized},
                )
            except Exception as exc:
                # Fallback to simple concatenation if learned fusion fails
                matrix = np.concatenate([neural_std, structural], axis=1).astype(np.float32)
                return FeatureBuildResult(
                    matrix=matrix,
                    feature_mode="hybrid",
                    requested_feature_mode=feature_mode,
                    neural_model=str(model_path or DEFAULT_MODEL_PATH),
                    latent_dim=latent_dim,
                    latent_cache=latent_cache_path,
                    symbolic_feature_count=int(structural.shape[1]),
                    fallback_reason=f"learned_fusion_failed:{exc.__class__.__name__}",
                    extra_metadata={"latent_standardized": standardized},
                )
        else:
            # Simple concatenation (original behavior)
            matrix = np.concatenate([neural_std, structural], axis=1).astype(np.float32)
            return FeatureBuildResult(
                matrix=matrix,
                feature_mode="hybrid",
                requested_feature_mode=feature_mode,
                neural_model=str(model_path or DEFAULT_MODEL_PATH),
                latent_dim=latent_dim,
                latent_cache=latent_cache_path,
                symbolic_feature_count=int(structural.shape[1]),
                fusion_method="concat",
                extra_metadata={"latent_standardized": standardized},
            )
    raise ValueError(f"Unsupported feature mode: {feature_mode}")


def _build_neural_matrix(
    records: Sequence[MessageRecord],
    model_path: str | None,
    latent_cache_path: str | None,
    batch_size: int,
    latent_dim: int,
) -> tuple[object | None, str | None]:
    load_result = load_optional_encoder_with_reason(model_path, latent_dim=latent_dim)
    encoder = load_result.encoder
    if encoder is None:
        return None, load_result.reason
    cache = load_latent_cache(latent_cache_path)
    hashes = [payload_hash(record.payload_hex) for record in records]
    missing_indexes = [index for index, item in enumerate(hashes) if item not in cache]
    if missing_indexes:
        payloads = [hex_to_bytes(records[index].payload_hex) for index in missing_indexes]
        try:
            latents = encoder.encode_payloads(payloads, batch_size=max(1, batch_size))
        except Exception as exc:
            return None, f"neural_encoding_failed:{exc.__class__.__name__}"
        for index, latent in zip(missing_indexes, latents):
            cache[hashes[index]] = [float(value) for value in latent[:latent_dim]]
        save_latent_cache(latent_cache_path, cache, latent_dim=latent_dim)
    rows: List[List[float]] = []
    for item in hashes:
        latent = list(cache.get(item, []))[:latent_dim]
        latent.extend([0.0] * (latent_dim - len(latent)))
        rows.append(latent)
    return np.asarray(rows, dtype=np.float32), None
