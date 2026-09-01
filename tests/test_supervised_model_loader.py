from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from protocol_re.neural.model_loader import load_optional_encoder_with_reason
from protocol_re.neural.supervised_vae import SupervisedVAE


def test_loads_supervised_checkpoint_and_encodes_payloads(tmp_path) -> None:
    model = SupervisedVAE(max_len=32, latent_dim=4)
    checkpoint = tmp_path / "supervised.pth"
    torch.save(
        {
            "format": "protocol-re-supervised-vae-v1",
            "model_state": model.state_dict(),
            "model_config": {"max_len": 32, "latent_dim": 4},
            "metrics": {"hdbscan_per_protocol": {}},
        },
        checkpoint,
    )

    result = load_optional_encoder_with_reason(
        str(checkpoint), latent_dim=4, max_len=32
    )

    assert result.available is True
    assert result.reason is None
    assert result.encoder is not None
    latents = result.encoder.encode_payloads([b"\x68\x04\x01\x00"])
    assert len(latents) == 1
    assert len(latents[0]) == 4
