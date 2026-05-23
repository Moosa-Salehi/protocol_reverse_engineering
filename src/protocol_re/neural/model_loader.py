from __future__ import annotations

from pathlib import Path
from typing import Optional

from protocol_re.neural.encoder import TorchPayloadEncoder

try:
    import torch
except Exception:  # pragma: no cover - optional dependency
    torch = None


DEFAULT_MODEL_PATH = "industrial_encoder_only.pth"


def load_optional_encoder(model_path: str | None = None, latent_dim: int = 32) -> Optional[TorchPayloadEncoder]:
    if torch is None:
        return None
    path = Path(model_path or DEFAULT_MODEL_PATH)
    if not path.exists():
        return None
    try:
        artifact = torch.load(str(path), map_location="cpu")
    except Exception:
        return None
    model = _extract_model(artifact)
    if model is None:
        return None
    try:
        return TorchPayloadEncoder(model, latent_dim=latent_dim)
    except Exception:
        return None


def _extract_model(artifact: object) -> object | None:
    if hasattr(artifact, "eval") and callable(artifact):
        return artifact
    if isinstance(artifact, dict):
        for key in ("encoder", "model", "module"):
            candidate = artifact.get(key)
            if hasattr(candidate, "eval") and callable(candidate):
                return candidate
    return None
