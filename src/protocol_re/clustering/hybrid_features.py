from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from protocol_re.clustering.structural_features import (
    payload_hash,
    summarize_symbolic_feature_count,
    vectorize_structural_features,
)
from protocol_re.model.schema import MessageRecord
from protocol_re.neural.artifacts import load_latent_cache, save_latent_cache
from protocol_re.neural.model_loader import DEFAULT_MODEL_PATH, load_optional_encoder_with_reason
from protocol_re.utils.bytes import hex_to_bytes

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None


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


def build_feature_matrix(
    records: Sequence[MessageRecord],
    corpus_records: Sequence[MessageRecord],
    feature_mode: str,
    model_path: str | None = None,
    latent_cache_path: str | None = None,
    neural_batch_size: int = 256,
    latent_dim: int = 32,
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
        if feature_mode == "neural":
            return FeatureBuildResult(
                matrix=neural,
                feature_mode="neural",
                requested_feature_mode=feature_mode,
                neural_model=str(model_path or DEFAULT_MODEL_PATH),
                latent_dim=latent_dim,
                latent_cache=latent_cache_path,
            )
        structural = vectorize_structural_features(records, corpus_records=corpus_records)
        matrix = np.concatenate([neural, structural], axis=1).astype(np.float32)
        return FeatureBuildResult(
            matrix=matrix,
            feature_mode="hybrid",
            requested_feature_mode=feature_mode,
            neural_model=str(model_path or DEFAULT_MODEL_PATH),
            latent_dim=latent_dim,
            latent_cache=latent_cache_path,
            symbolic_feature_count=int(structural.shape[1]),
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
