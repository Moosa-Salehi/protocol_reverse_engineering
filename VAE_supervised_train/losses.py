from __future__ import annotations

import torch
from torch.nn import functional as F


def supervised_contrastive(z: torch.Tensor, labels: torch.Tensor, temperature: float) -> torch.Tensor:
    z = F.normalize(z, dim=1)
    similarity = z @ z.T / temperature
    eye = torch.eye(len(z), dtype=torch.bool, device=z.device)
    positive = labels[:, None].eq(labels[None, :]) & ~eye
    logits = similarity.masked_fill(eye, -1e4)
    log_prob = logits - torch.logsumexp(logits, dim=1, keepdim=True)
    valid = positive.sum(1) > 0
    if not valid.any():
        return z.sum() * 0.0
    return -(log_prob * positive).sum(1)[valid].div(positive.sum(1)[valid]).mean()


def batch_hard_triplet(z: torch.Tensor, labels: torch.Tensor, margin: float) -> torch.Tensor:
    distances = torch.cdist(F.normalize(z, dim=1), F.normalize(z, dim=1))
    same = labels[:, None].eq(labels[None, :])
    eye = torch.eye(len(z), dtype=torch.bool, device=z.device)
    positives = distances.masked_fill(~same | eye, -1.0).amax(1)
    negatives = distances.masked_fill(same, float("inf")).amin(1)
    valid = (same & ~eye).any(1) & (~same).any(1)
    return F.relu(positives[valid] - negatives[valid] + margin).mean() if valid.any() else z.sum() * 0.0


def centroid_loss(z: torch.Tensor, labels: torch.Tensor, margin: float) -> tuple[torch.Tensor, torch.Tensor]:
    unique = labels.unique()
    centroids = torch.stack([z[labels == label].mean(0) for label in unique])
    compact = torch.stack([((z[labels == label] - center) ** 2).sum(1).mean()
                           for label, center in zip(unique, centroids)]).mean()
    if len(centroids) < 2:
        return compact, z.sum() * 0.0
    distances = torch.pdist(F.normalize(centroids, dim=1))
    return compact, F.relu(margin - distances).mean()


def collapse_loss(z: torch.Tensor, target_std: float = 0.5) -> torch.Tensor:
    std_loss = F.relu(target_std - torch.sqrt(z.var(dim=0, unbiased=False) + 1e-4)).mean()
    centered = z - z.mean(0)
    covariance = centered.T @ centered / max(1, len(z) - 1)
    off_diagonal = covariance - torch.diag(torch.diag(covariance))
    return std_loss + off_diagonal.square().sum() / z.shape[1]


def vae_kl(mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
    return (-0.5 * (1 + logvar - mu.square() - logvar.exp()).sum(1)).mean()
