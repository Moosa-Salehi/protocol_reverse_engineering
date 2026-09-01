from __future__ import annotations

import torch
from pathlib import Path

from protocol_re.neural.supervised_vae import ResidualBlock, SupervisedVAE


def _atomic_torch_save(payload: dict, path: str) -> None:
    destination = Path(path)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    torch.save(payload, temporary)
    temporary.replace(destination)


def save_checkpoint(path: str, model: SupervisedVAE, config: dict, metrics: dict, epoch: int) -> None:
    _atomic_torch_save({"format": "protocol-re-supervised-vae-v1", "model_state": model.state_dict(),
                        "model_config": {"max_len": model.max_len, "latent_dim": model.latent_dim},
                        "input_contract": {"payload_source": "tshark_transport_or_l2_payload",
                                           "max_len": model.max_len, "latent_scaling": "standard_scaler"},
                        "training_config": config, "metrics": metrics, "epoch": epoch}, path)


def save_training_checkpoint(path: str, model: SupervisedVAE, optimizer, scaler, config: dict,
                             epoch: int, best_key, subset_best_key, stale: int,
                             best_metrics: dict | None) -> None:
    _atomic_torch_save({"format": "protocol-re-supervised-vae-training-v1", "model_state": model.state_dict(),
                        "model_config": {"max_len": model.max_len, "latent_dim": model.latent_dim},
                        "input_contract": {"payload_source": "tshark_transport_or_l2_payload",
                                           "max_len": model.max_len, "latent_scaling": "standard_scaler"},
                        "optimizer_state": optimizer.state_dict(), "scaler_state": scaler.state_dict(),
                        "training_config": config, "epoch": epoch, "best_key": best_key,
                        "subset_best_key": subset_best_key, "selection_scope": "full_corpus",
                        "stale": stale, "best_metrics": best_metrics}, path)


def load_training_checkpoint(path: str, model: SupervisedVAE, optimizer, scaler,
                             device: str | torch.device = "cpu") -> dict:
    payload = torch.load(path, map_location=device, weights_only=False)
    if payload.get("format") != "protocol-re-supervised-vae-training-v1":
        raise ValueError("Resume requires a latest training checkpoint, not a best model checkpoint")
    if (payload.get("input_contract") or {}).get("payload_source") != "tshark_transport_or_l2_payload":
        raise ValueError("Resume checkpoint uses the legacy dissector-level payload representation")
    expected = {"max_len": model.max_len, "latent_dim": model.latent_dim}
    if payload.get("model_config") != expected:
        raise ValueError(f"Resume model configuration mismatch: {payload.get('model_config')} != {expected}")
    model.load_state_dict(payload["model_state"])
    optimizer.load_state_dict(payload["optimizer_state"])
    scaler.load_state_dict(payload.get("scaler_state", {}))
    return payload


def load_checkpoint(path: str, device: str | torch.device = "cpu") -> tuple[SupervisedVAE, dict]:
    payload = torch.load(path, map_location=device, weights_only=False)
    if payload.get("format") != "protocol-re-supervised-vae-v1":
        raise ValueError("Not a supervised VAE checkpoint")
    model = SupervisedVAE(**payload["model_config"]).to(device)
    model.load_state_dict(payload["model_state"])
    model.eval()
    return model, payload
