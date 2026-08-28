from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class ResidualBlock(nn.Module):
    def __init__(self, channels: int, dilation: int = 1) -> None:
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv1d(channels, channels, 3, padding=dilation, dilation=dilation, bias=False),
            nn.GroupNorm(8, channels),
            nn.GELU(),
            nn.Conv1d(channels, channels, 3, padding=dilation, dilation=dilation, bias=False),
            nn.GroupNorm(8, channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.gelu(x + self.block(x))


class SupervisedVAE(nn.Module):
    """Length-aware byte VAE whose deterministic mean is the clustering embedding."""

    def __init__(self, max_len: int = 256, latent_dim: int = 32, byte_dim: int = 32) -> None:
        super().__init__()
        self.max_len = max_len
        self.latent_dim = latent_dim
        self.byte_embedding = nn.Embedding(257, byte_dim, padding_idx=256)
        self.position = nn.Parameter(torch.zeros(1, byte_dim, max_len))
        self.encoder = nn.Sequential(
            nn.Conv1d(byte_dim + 1, 64, 7, padding=3, bias=False),
            nn.GroupNorm(8, 64), nn.GELU(),
            ResidualBlock(64, 1), ResidualBlock(64, 2),
            nn.Conv1d(64, 128, 5, stride=2, padding=2, bias=False),
            nn.GroupNorm(8, 128), nn.GELU(),
            ResidualBlock(128, 2), ResidualBlock(128, 4),
        )
        self.attention = nn.Conv1d(128, 1, 1)
        self.fc_mu = nn.Linear(256, latent_dim)
        self.fc_logvar = nn.Linear(256, latent_dim)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 256), nn.GELU(), nn.Linear(256, max_len * 256)
        )
        nn.init.normal_(self.position, std=0.01)

    def encode(self, byte_ids: torch.Tensor, mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        tokens = self.byte_embedding(byte_ids).transpose(1, 2) + self.position[:, :, : byte_ids.shape[1]]
        h = self.encoder(torch.cat((tokens, mask.unsqueeze(1)), dim=1))
        reduced_mask = F.interpolate(mask.unsqueeze(1), size=h.shape[-1], mode="nearest")
        logits = self.attention(h).masked_fill(reduced_mask == 0, -1e4)
        pooled = (h * logits.softmax(dim=-1)).sum(dim=-1)
        maximum = h.masked_fill(reduced_mask == 0, -1e4).amax(dim=-1)
        summary = torch.cat((pooled, maximum), dim=1)
        return self.fc_mu(summary), self.fc_logvar(summary).clamp(-8.0, 4.0)

    def forward(self, byte_ids: torch.Tensor, mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, logvar = self.encode(byte_ids, mask)
        z = mu + torch.randn_like(mu) * torch.exp(0.5 * logvar) if self.training else mu
        return self.decoder(z).view(-1, self.max_len, 256), mu, logvar


def save_checkpoint(path: str, model: SupervisedVAE, config: dict, metrics: dict, epoch: int) -> None:
    torch.save({"format": "protocol-re-supervised-vae-v1", "model_state": model.state_dict(),
                "model_config": {"max_len": model.max_len, "latent_dim": model.latent_dim},
                "training_config": config, "metrics": metrics, "epoch": epoch}, path)


def load_checkpoint(path: str, device: str | torch.device = "cpu") -> tuple[SupervisedVAE, dict]:
    payload = torch.load(path, map_location=device, weights_only=False)
    if payload.get("format") != "protocol-re-supervised-vae-v1":
        raise ValueError("Not a supervised VAE checkpoint")
    model = SupervisedVAE(**payload["model_config"]).to(device)
    model.load_state_dict(payload["model_state"])
    model.eval()
    return model, payload
