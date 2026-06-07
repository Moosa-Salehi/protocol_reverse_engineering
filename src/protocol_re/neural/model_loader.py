from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from protocol_re.config.thresholds import NeuralModel as _NM
from protocol_re.neural.encoder import TorchPayloadEncoder

try:
    from protocol_re.neural.enhanced_encoder import EnhancedTorchPayloadEncoder
    ENHANCED_ENCODER_AVAILABLE = True
except ImportError:
    ENHANCED_ENCODER_AVAILABLE = False
    EnhancedTorchPayloadEncoder = None

try:
    import torch # type: ignore
    import torch.nn as nn # type: ignore
except Exception:  # pragma: no cover - optional dependency
    torch = None


# Re-export for backward compatibility
DEFAULT_MODEL_PATH = _NM.DEFAULT_MODEL_PATH

class ConvVAE(nn.Module):
    def __init__(self, latent_dim=32, max_len=256):
        super().__init__()
        self.compressed_len = max_len // 8
        self.flattened_size = 128 * self.compressed_len

        self.encoder = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(64, 128, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Flatten()
        )

        self.fc_mu = nn.Linear(self.flattened_size, latent_dim)
        self.fc_logvar = nn.Linear(self.flattened_size, latent_dim)

        self.decoder_input = nn.Linear(latent_dim, self.flattened_size)
        self.decoder = nn.Sequential(
            nn.Unflatten(1, (128, self.compressed_len)),
            nn.ConvTranspose1d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.ConvTranspose1d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.ConvTranspose1d(32, 1, kernel_size=4, stride=2, padding=1)
        )

    def encode_mu(self, x: torch.Tensor) -> torch.Tensor:
        # Accept (B,L) or (B,1,L)
        if x.dim() == 2:
            x = x.unsqueeze(1)
        elif x.dim() == 3:
            pass
        else:
            raise ValueError(f"Expected x dim 2 or 3, got shape {tuple(x.shape)}")

        h = self.encoder(x)
        mu = self.fc_mu(h)
        return mu

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        if x.dim() == 2:
            x = x.unsqueeze(1)
        h = self.encoder(x)
        mu, logvar = self.fc_mu(h), self.fc_logvar(h)
        z = self.reparameterize(mu, logvar)
        logits = self.decoder(self.decoder_input(z))
        return logits.squeeze(1), mu, logvar

def load_full_vae_from_state_dict(path: str, latent_dim: int = 32, max_len: int = 256, device="cpu") -> ConvVAE:
    sd = torch.load(path, map_location=device, weights_only=True)  # sd is a dict of tensors
    model = ConvVAE(latent_dim=latent_dim, max_len=max_len).to(device)
    model.load_state_dict(sd)
    model.eval()
    return model

@dataclass(frozen=True)
class EncoderLoadResult:
    encoder: Optional[TorchPayloadEncoder | EnhancedTorchPayloadEncoder]
    model_path: str
    available: bool
    reason: str | None = None


def load_optional_encoder(
    model_path: str | None = None,
    latent_dim: int = 32,
    use_enhanced: bool = False
) -> Optional[TorchPayloadEncoder | EnhancedTorchPayloadEncoder]:
    """
    Load a neural encoder for payload encoding.

    Args:
        model_path: Path to model file (default: industrial_VAE.pth)
        latent_dim: Latent dimension (default: 32)
        use_enhanced: Use EnhancedTorchPayloadEncoder with preprocessing (default: False)

    Returns:
        Encoder instance or None if unavailable
    """
    return load_optional_encoder_with_reason(
        model_path=model_path,
        latent_dim=latent_dim,
        use_enhanced=use_enhanced
    ).encoder

def load_optional_encoder_with_reason(
    model_path: str | None = None,
    latent_dim: int = 32,
    max_len: int = 256,
    use_enhanced: bool = False
) -> EncoderLoadResult:
    resolved_path = str(Path(model_path or DEFAULT_MODEL_PATH))

    if torch is None:
        return EncoderLoadResult(None, resolved_path, False, "pytorch_unavailable")

    path = Path(model_path or DEFAULT_MODEL_PATH)
    if not path.exists():
        return EncoderLoadResult(None, str(path), False, "model_file_not_found")

    try:
        artifact = _torch_load_model_artifact(path)
    except Exception as exc:
        return EncoderLoadResult(None, str(path), False, f"model_load_failed:{exc.__class__.__name__}")

    model = _extract_model(artifact, latent_dim=latent_dim, max_len=max_len)
    if model is None:
        return EncoderLoadResult(None, str(path), False, "compatible_encoder_not_found_in_artifact")

    try:
        # Choose encoder type based on use_enhanced flag
        if use_enhanced and ENHANCED_ENCODER_AVAILABLE:
            encoder = EnhancedTorchPayloadEncoder(
                model,
                latent_dim=latent_dim,
                max_length=max_len,
                auto_preprocess=True,
                quality_check=True
            )
        else:
            # Use standard encoder
            encoder = TorchPayloadEncoder(model, latent_dim=latent_dim, max_length=max_len)
    except Exception as exc:
        return EncoderLoadResult(None, str(path), False, f"encoder_initialization_failed:{exc.__class__.__name__}")

    return EncoderLoadResult(encoder, str(path), True)


def _extract_model(artifact: object, *, latent_dim: int = 32, max_len: int = 256) -> object | None:
    # Case 1: already a full module
    if hasattr(artifact, "eval") and callable(getattr(artifact, "eval", None)):
        return artifact

    # Case 2: dict containing a module under known keys
    if isinstance(artifact, dict):
        for key in ("encoder", "model", "module"):
            candidate = artifact.get(key)
            if hasattr(candidate, "eval") and callable(getattr(candidate, "eval", None)):
                return candidate

        # Case 3: plain state_dict — instantiate ConvVAE and load
        if any(isinstance(k, str) and (k.startswith("encoder.") or k.startswith("fc_mu."))
               for k in artifact.keys()):
            model = ConvVAE(latent_dim=latent_dim, max_len=max_len)
            model.load_state_dict(artifact)
            model.eval()
            return model

    return None

def _torch_load_model_artifact(path: Path) -> object:
    try:
        return torch.load(str(path), map_location="cpu", weights_only=True)
    except TypeError:
        return torch.load(str(path), map_location="cpu")
    except Exception:
        return torch.load(str(path), map_location="cpu", weights_only=False)
