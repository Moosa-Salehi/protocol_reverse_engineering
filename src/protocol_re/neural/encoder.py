from __future__ import annotations

from typing import List, Sequence

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None

try:
    import torch
except Exception:  # pragma: no cover - optional dependency
    torch = None


class TorchPayloadEncoder:
    def __init__(self, model: object, latent_dim: int = 32, max_length: int = 512) -> None:
        if torch is None:
            raise RuntimeError("PyTorch is required for neural clustering features")
        self.model = model
        self.latent_dim = latent_dim
        self.max_length = max_length
        self.device = torch.device("cpu")
        if hasattr(self.model, "eval"):
            self.model.eval()

    def encode_payloads(self, payloads: Sequence[bytes], batch_size: int = 256) -> List[List[float]]:
        latents: List[List[float]] = []
        with torch.no_grad():
            for start in range(0, len(payloads), batch_size):
                batch = payloads[start : start + batch_size]
                tensor = self._batch_tensor(batch)
                output = self.model(tensor)
                latent = self._extract_latent(output)
                latents.extend(latent)
        return latents

    def _batch_tensor(self, payloads: Sequence[bytes]) -> object:
        rows = []
        for payload in payloads:
            clipped = payload[: self.max_length]
            row = [value / 255.0 for value in clipped]
            row.extend([0.0] * (self.max_length - len(row)))
            rows.append(row)
        return torch.tensor(rows, dtype=torch.float32, device=self.device)

    def _extract_latent(self, output: object) -> List[List[float]]:
        if isinstance(output, (tuple, list)):
            # ConvVAE.forward returns (reconstruction, mu, logvar) — take mu (idx 1)
            if len(output) == 3:
                output = output[1]   # <-- mu, shape (B, latent_dim)
            else:
                output = output[0]   # fallback for other models

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
            raise RuntimeError("Neural model output could not be converted without NumPy")

        if array.ndim == 1:
            array = array.reshape(1, -1)
        if array.shape[1] < self.latent_dim:
            if np is None:
                raise RuntimeError("NumPy is required to pad neural latent vectors")
            padding = np.zeros((array.shape[0], self.latent_dim - array.shape[1]), dtype=np.float32)
            array = np.concatenate([array, padding], axis=1)

        return array[:, :self.latent_dim].astype("float32").tolist()
