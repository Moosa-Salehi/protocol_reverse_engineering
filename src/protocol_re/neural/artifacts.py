from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List


def load_latent_cache(cache_path: str | None) -> Dict[str, List[float]]:
    if not cache_path:
        return {}
    path = Path(cache_path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, dict) and "latents" in payload:
        payload = payload["latents"]
    if not isinstance(payload, dict):
        return {}
    return {
        str(key): [float(value) for value in values]
        for key, values in payload.items()
        if isinstance(values, list)
    }


def save_latent_cache(cache_path: str | None, cache: Dict[str, List[float]], latent_dim: int = 32) -> None:
    if not cache_path:
        return
    path = Path(cache_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "metadata": {
            "latent_dim": latent_dim,
            "entry_count": len(cache),
        },
        "latents": cache,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle)


def missing_hashes(cache: Dict[str, List[float]], payload_hashes: Iterable[str]) -> List[str]:
    return [item for item in payload_hashes if item not in cache]
