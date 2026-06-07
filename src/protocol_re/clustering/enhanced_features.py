"""
Enhanced hybrid feature builder with automatic fallback and quality checks.
"""
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
from protocol_re.neural.enhanced_encoder import EnhancedTorchPayloadEncoder
from protocol_re.utils.bytes import hex_to_bytes

try:
    import numpy as np
except Exception:
    np = None


@dataclass
class EnhancedFeatureBuildResult:
    matrix: object
    feature_mode: str
    requested_feature_mode: str
    neural_model: str | None = None
    latent_dim: int = 0
    latent_cache: str | None = None
    symbolic_feature_count: int = 0
    fallback_reason: str | None = None
    preprocessing_enabled: bool = False
    variable_offsets_detected: int = 0
    quality_check_passed: bool = True
    quality_check_reason: str = "not_checked"
    extra_metadata: Dict[str, object] = field(default_factory=dict)


def build_enhanced_feature_matrix(
    records: Sequence[MessageRecord],
    corpus_records: Sequence[MessageRecord],
    feature_mode: str,
    model_path: str | None = None,
    latent_cache_path: str | None = None,
    neural_batch_size: int = 256,
    latent_dim: int = 32,
    enable_preprocessing: bool = True,
    enable_quality_check: bool = True,
    auto_fallback: bool = True,
    latent_standardizer: LatentStandardizer | None = None,
) -> EnhancedFeatureBuildResult:
    """
    Build feature matrix with enhanced neural encoding and automatic fallback.

    New features:
    - Automatic detection and masking of variable fields
    - Quality checks on neural features
    - Automatic fallback to structural features if neural fails
    - Detailed metadata about preprocessing and quality

    Args:
        records: Messages to encode
        corpus_records: Full corpus for context
        feature_mode: "raw_bytes", "structural", "neural", or "hybrid"
        model_path: Path to neural model
        latent_cache_path: Path to latent cache
        neural_batch_size: Batch size for neural encoding
        latent_dim: Latent dimension
        enable_preprocessing: Enable variable field masking
        enable_quality_check: Enable quality checks
        auto_fallback: Automatically fall back to structural if neural fails

    Returns:
        EnhancedFeatureBuildResult with matrix and metadata
    """
    if np is None:
        raise RuntimeError("NumPy is required for feature matrix construction")

    # Structural mode - no changes
    if feature_mode == "structural":
        matrix = vectorize_structural_features(records, corpus_records=corpus_records)
        return EnhancedFeatureBuildResult(
            matrix=matrix,
            feature_mode="structural",
            requested_feature_mode=feature_mode,
            symbolic_feature_count=summarize_symbolic_feature_count(),
        )

    # Neural or hybrid mode
    if feature_mode in {"neural", "hybrid"}:
        neural_result = _build_enhanced_neural_matrix(
            records,
            model_path,
            latent_cache_path,
            neural_batch_size,
            latent_dim,
            enable_preprocessing,
            enable_quality_check,
        )

        neural_matrix = neural_result["matrix"]
        neural_metadata = neural_result["metadata"]
        neural_unavailable_reason = neural_result["unavailable_reason"]
        quality_passed = neural_metadata.get("quality_check_passed", True)
        quality_reason = neural_metadata.get("quality_check_reason", "not_checked")

        # Check if neural failed or quality is poor
        should_fallback = (
            neural_matrix is None
            or (auto_fallback and not quality_passed)
        )

        if should_fallback:
            # Fall back to structural features
            matrix = vectorize_structural_features(records, corpus_records=corpus_records)
            fallback_reason = neural_unavailable_reason or f"poor_quality:{quality_reason}"

            return EnhancedFeatureBuildResult(
                matrix=matrix,
                feature_mode="structural",
                requested_feature_mode=feature_mode,
                neural_model=str(model_path or DEFAULT_MODEL_PATH),
                latent_dim=0,
                latent_cache=latent_cache_path,
                symbolic_feature_count=summarize_symbolic_feature_count(),
                fallback_reason=fallback_reason,
                preprocessing_enabled=enable_preprocessing,
                quality_check_passed=False,
                quality_check_reason=quality_reason,
            )

        # Deterministic per-corpus latent standardization (fit once, transform every
        # batch). Applied only AFTER the raw-latent quality/fallback decision above, so
        # z-scoring can never mask a collapsed latent from the quality gate.
        def _standardize(neural_block):
            if latent_standardizer is None:
                return neural_block, False
            if not latent_standardizer.fitted:
                latent_standardizer.fit(neural_block)
            return latent_standardizer.transform(neural_block), True

        # Neural mode succeeded
        if feature_mode == "neural":
            neural_std, standardized = _standardize(neural_matrix)
            neural_metadata = {**neural_metadata, "latent_standardized": standardized}
            return EnhancedFeatureBuildResult(
                matrix=neural_std,
                feature_mode="neural",
                requested_feature_mode=feature_mode,
                neural_model=str(model_path or DEFAULT_MODEL_PATH),
                latent_dim=latent_dim,
                latent_cache=latent_cache_path,
                preprocessing_enabled=neural_metadata.get("preprocessing_enabled", False),
                variable_offsets_detected=neural_metadata.get("variable_offsets_count", 0),
                quality_check_passed=quality_passed,
                quality_check_reason=quality_reason,
                extra_metadata=neural_metadata,
            )

        # Hybrid mode - concatenate neural + structural
        neural_std, standardized = _standardize(neural_matrix)
        neural_metadata = {**neural_metadata, "latent_standardized": standardized}
        structural = vectorize_structural_features(records, corpus_records=corpus_records)
        matrix = np.concatenate([neural_std, structural], axis=1).astype(np.float32)

        return EnhancedFeatureBuildResult(
            matrix=matrix,
            feature_mode="hybrid",
            requested_feature_mode=feature_mode,
            neural_model=str(model_path or DEFAULT_MODEL_PATH),
            latent_dim=latent_dim,
            latent_cache=latent_cache_path,
            symbolic_feature_count=int(structural.shape[1]),
            preprocessing_enabled=neural_metadata.get("preprocessing_enabled", False),
            variable_offsets_detected=neural_metadata.get("variable_offsets_count", 0),
            quality_check_passed=quality_passed,
            quality_check_reason=quality_reason,
            extra_metadata=neural_metadata,
        )

    raise ValueError(f"Unsupported feature mode: {feature_mode}")


def _build_enhanced_neural_matrix(
    records: Sequence[MessageRecord],
    model_path: str | None,
    latent_cache_path: str | None,
    batch_size: int,
    latent_dim: int,
    enable_preprocessing: bool,
    enable_quality_check: bool,
) -> Dict[str, object]:
    """
    Build neural feature matrix with enhanced encoder.

    Returns:
        Dict with keys: matrix, metadata, unavailable_reason
    """
    # Load model
    load_result = load_optional_encoder_with_reason(model_path, latent_dim=latent_dim)
    if load_result.encoder is None:
        return {
            "matrix": None,
            "metadata": {},
            "unavailable_reason": load_result.reason,
        }

    # Wrap in enhanced encoder
    try:
        enhanced_encoder = EnhancedTorchPayloadEncoder(
            load_result.encoder.model,
            latent_dim=latent_dim,
            max_length=load_result.encoder.max_length,
            auto_preprocess=enable_preprocessing,
            quality_check=enable_quality_check,
        )
    except Exception as exc:
        return {
            "matrix": None,
            "metadata": {},
            "unavailable_reason": f"enhanced_encoder_init_failed:{exc.__class__.__name__}",
        }

    # Load cache
    cache = load_latent_cache(latent_cache_path)
    hashes = [payload_hash(record.payload_hex) for record in records]

    # Find missing entries
    missing_indexes = [index for index, h in enumerate(hashes) if h not in cache]

    # Encode missing payloads
    encoding_metadata = {}
    if missing_indexes:
        payloads = [hex_to_bytes(records[index].payload_hex) for index in missing_indexes]
        try:
            latents, encoding_metadata = enhanced_encoder.encode_payloads(
                payloads,
                batch_size=max(1, batch_size)
            )
        except Exception as exc:
            return {
                "matrix": None,
                "metadata": {},
                "unavailable_reason": f"neural_encoding_failed:{exc.__class__.__name__}",
            }

        # Update cache
        for index, latent in zip(missing_indexes, latents):
            cache[hashes[index]] = [float(value) for value in latent[:latent_dim]]

        save_latent_cache(latent_cache_path, cache, latent_dim=latent_dim)

    # Build matrix from cache
    rows: List[List[float]] = []
    for h in hashes:
        latent = list(cache.get(h, []))[:latent_dim]
        latent.extend([0.0] * (latent_dim - len(latent)))
        rows.append(latent)

    matrix = np.asarray(rows, dtype=np.float32)

    # Prepare metadata
    quality_passed = encoding_metadata.get("quality_check", {}).get("passed", True)
    quality_reason = encoding_metadata.get("quality_check", {}).get("reason", "not_checked")

    metadata = {
        "preprocessing_enabled": enable_preprocessing,
        "variable_offsets_count": encoding_metadata.get("variable_offsets_count", 0),
        "variable_offsets": encoding_metadata.get("variable_offsets", []),
        "quality_check_passed": quality_passed,
        "quality_check_reason": quality_reason,
        "warning": encoding_metadata.get("warning"),
    }

    return {
        "matrix": matrix,
        "metadata": metadata,
        "unavailable_reason": None,
    }
