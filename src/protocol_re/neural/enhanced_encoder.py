"""
Enhanced neural encoder with preprocessing and quality checks.
"""
from __future__ import annotations

from typing import List, Sequence, Set

from protocol_re.neural.preprocessing import (
    preprocess_payloads_batch,
    check_neural_feature_quality,
)

try:
    import numpy as np
except Exception:
    np = None

try:
    import torch
except Exception:
    torch = None


class EnhancedTorchPayloadEncoder:
    """
    Enhanced neural encoder with preprocessing to avoid feature collapse.

    Improvements over TorchPayloadEncoder:
    1. Automatic detection and masking of variable fields
    2. Quality checks on encoded features
    3. Fallback detection when features are poor
    """

    def __init__(
        self,
        model: object,
        latent_dim: int = 32,
        max_length: int = 256,
        auto_preprocess: bool = True,
        quality_check: bool = True
    ) -> None:
        if torch is None:
            raise RuntimeError("PyTorch is required for neural clustering features")
        if np is None:
            raise RuntimeError("NumPy is required for neural clustering features")

        self.model = model
        self.latent_dim = latent_dim
        self.max_length = max_length
        self.auto_preprocess = auto_preprocess
        self.quality_check = quality_check
        self.device = torch.device("cpu")

        if hasattr(self.model, "eval"):
            self.model.eval()

        # Track preprocessing metadata
        self.variable_offsets: Set[int] = set()
        self.last_quality_check: tuple[bool, str] = (True, "not_checked")

    def encode_payloads(
        self,
        payloads: Sequence[bytes],
        batch_size: int = 256
    ) -> tuple[List[List[float]], dict]:
        """
        Encode payloads with preprocessing and quality checks.

        Returns:
            Tuple of (latent_vectors, metadata)
        """
        if not payloads:
            return [], {"error": "empty_input"}

        # Preprocess payloads
        if self.auto_preprocess:
            preprocessed, variable_offsets = preprocess_payloads_batch(
                payloads,
                max_length=self.max_length,
                auto_detect_variable=True
            )
            self.variable_offsets = variable_offsets
        else:
            # Simple normalization without masking
            preprocessed = []
            for p in payloads:
                clipped = p[:self.max_length]
                row = [b / 255.0 for b in clipped]
                row.extend([0.0] * (self.max_length - len(row)))
                preprocessed.append(row)
            self.variable_offsets = set()

        # Encode in batches
        latents: List[List[float]] = []
        with torch.no_grad():
            for start in range(0, len(preprocessed), batch_size):
                batch = preprocessed[start : start + batch_size]
                tensor = torch.tensor(batch, dtype=torch.float32, device=self.device)

                # Forward pass
                output = self.model(tensor)
                latent = self._extract_latent(output)
                latents.extend(latent)

        # Quality check
        metadata = {
            "preprocessed": self.auto_preprocess,
            "variable_offsets_count": len(self.variable_offsets),
            "variable_offsets": sorted(list(self.variable_offsets))[:10],  # First 10
        }

        if self.quality_check and latents:
            latent_matrix = np.array(latents, dtype=np.float32)
            is_good, reason = check_neural_feature_quality(latent_matrix)
            self.last_quality_check = (is_good, reason)
            metadata["quality_check"] = {"passed": is_good, "reason": reason}

            if not is_good:
                metadata["warning"] = f"Neural features may be poor quality: {reason}"

        return latents, metadata

    def _extract_latent(self, output: object) -> List[List[float]]:
        """Extract latent vectors from model output."""
        if isinstance(output, (tuple, list)):
            # ConvVAE.forward returns (reconstruction, mu, logvar) — take mu (idx 1)
            if len(output) == 3:
                output = output[1]   # mu, shape (B, latent_dim)
            else:
                output = output[0]   # fallback

        if isinstance(output, dict):
            for key in ("z", "latent", "mu", "embedding"):
                if key in output:
                    output = output[key]
                    break

        if hasattr(output, "detach"):
            array = output.detach().cpu().float().numpy()
        elif np is not None:
            array = np.asarray(output, dtype=np.float32)
        else:
            raise RuntimeError("Cannot convert model output without NumPy")

        if array.ndim == 1:
            array = array.reshape(1, -1)

        # Pad if needed
        if array.shape[1] < self.latent_dim:
            padding = np.zeros((array.shape[0], self.latent_dim - array.shape[1]), dtype=np.float32)
            array = np.concatenate([array, padding], axis=1)

        return array[:, :self.latent_dim].astype("float32").tolist()

    def get_quality_status(self) -> tuple[bool, str]:
        """Get the last quality check result."""
        return self.last_quality_check
