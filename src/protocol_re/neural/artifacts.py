from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Iterable, List


def model_fingerprint(model_path: str | None) -> str | None:
    """Cheap content-identity tag for a model file (size + mtime).

    Used to bind a latent cache to the exact model that produced it. A full content hash
    would be more precise but needlessly slow on a multi-hundred-MB .pth; size+mtime is the
    standard make-style heuristic and changes whenever the model is retrained/overwritten.
    """
    if not model_path:
        return None
    try:
        st = os.stat(model_path)
    except OSError:
        return None
    return f"{st.st_size}:{st.st_mtime_ns}"


def load_latent_cache(
    cache_path: str | None,
    expected_fingerprint: str | None = None,
    expected_latent_dim: int | None = None,
) -> Dict[str, List[float]]:
    """Load cached latents, invalidating the cache when it does not match the model.

    The cache is keyed only by payload hash, so without this guard a retrained model would
    silently reuse latents produced by the previous model (mixing two latent spaces in one
    clustering run). When expected_fingerprint/expected_latent_dim are supplied and the
    stored metadata disagrees (or predates fingerprinting), we return an empty cache so the
    caller re-encodes everything with the current model.
    """
    if not cache_path:
        return {}
    path = Path(cache_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}

    # Model-identity guard: mismatch (or a pre-fingerprint cache) => treat as empty.
    if expected_fingerprint is not None and metadata.get("model_fingerprint") != expected_fingerprint:
        return {}
    # Dimension guard: a cache built at a different latent_dim is unusable.
    if (
        expected_latent_dim is not None
        and metadata.get("latent_dim") is not None
        and metadata.get("latent_dim") != expected_latent_dim
    ):
        return {}

    if isinstance(payload, dict) and "latents" in payload:
        payload = payload["latents"]
    if not isinstance(payload, dict):
        return {}
    return {
        str(key): [float(value) for value in values]
        for key, values in payload.items()
        if isinstance(values, list)
    }


def save_latent_cache(
    cache_path: str | None,
    cache: Dict[str, List[float]],
    latent_dim: int = 32,
    fingerprint: str | None = None,
) -> None:
    if not cache_path:
        return
    path = Path(cache_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "latent_dim": latent_dim,
            "entry_count": len(cache),
            "model_fingerprint": fingerprint,
        },
        "latents": cache,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def missing_hashes(cache: Dict[str, List[float]], payload_hashes: Iterable[str]) -> List[str]:
    return [item for item in payload_hashes if item not in cache]
