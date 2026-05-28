from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from protocol_re.neural.encoder import TorchPayloadEncoder

try:
    import torch
except Exception:  # pragma: no cover - optional dependency
    torch = None


DEFAULT_MODEL_PATH = "industrial_encoder_only.pth"


@dataclass(frozen=True)
class EncoderLoadResult:
    encoder: Optional[TorchPayloadEncoder]
    model_path: str
    available: bool
    reason: str | None = None


def load_optional_encoder(model_path: str | None = None, latent_dim: int = 32) -> Optional[TorchPayloadEncoder]:
    return load_optional_encoder_with_reason(model_path=model_path, latent_dim=latent_dim).encoder


def load_optional_encoder_with_reason(model_path: str | None = None, latent_dim: int = 32) -> EncoderLoadResult:
    resolved_path = str(Path(model_path or DEFAULT_MODEL_PATH))
    if torch is None:
        return EncoderLoadResult(None, resolved_path, False, "pytorch_unavailable")
    path = Path(model_path or DEFAULT_MODEL_PATH)
    if not path.exists():
        return EncoderLoadResult(None, str(path), False, "model_file_not_found")
    try:
        artifact = torch.load(str(path), map_location="cpu")
    except Exception as exc:
        return EncoderLoadResult(None, str(path), False, f"model_load_failed:{exc.__class__.__name__}")
    model = _extract_model(artifact)
    if model is None:
        return EncoderLoadResult(None, str(path), False, "compatible_encoder_not_found_in_artifact")
    try:
        encoder = TorchPayloadEncoder(model, latent_dim=latent_dim)
    except Exception as exc:
        return EncoderLoadResult(None, str(path), False, f"encoder_initialization_failed:{exc.__class__.__name__}")
    return EncoderLoadResult(encoder, str(path), True)


def _extract_model(artifact: object) -> object | None:
    if hasattr(artifact, "eval") and callable(artifact):
        return artifact
    if isinstance(artifact, dict):
        for key in ("encoder", "model", "module"):
            candidate = artifact.get(key)
            if hasattr(candidate, "eval") and callable(candidate):
                return candidate
    return None
