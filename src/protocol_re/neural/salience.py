from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from protocol_re.neural.model_loader import load_optional_encoder

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
except Exception:  # pragma: no cover - optional dependency
    torch = None
    nn = None
    F = None


def _payload_cache_key(payloads: Sequence[bytes], labels: Sequence[str], max_length: int) -> str:
    digest = hashlib.sha256()
    digest.update(str(max_length).encode("ascii"))
    for payload, label in zip(payloads, labels):
        digest.update(label.encode("utf-8", errors="ignore"))
        digest.update(b"\0")
        digest.update(payload[:max_length])
        digest.update(b"\xff")
    return digest.hexdigest()


def load_salience_cache(cache_path: Optional[str]) -> Dict[str, Any]:
    if not cache_path:
        return {}
    path = Path(cache_path)
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def save_salience_cache(cache_path: Optional[str], cache: Dict[str, Any]) -> None:
    if not cache_path:
        return
    path = Path(cache_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(cache, handle)


if nn is not None:
    class _OffsetAttentionClassifier(nn.Module):
        def __init__(self, max_length: int, class_count: int) -> None:
            super().__init__()
            self.position_weight = nn.Parameter(torch.zeros(max_length))
            self.value_proj = nn.Linear(1, 8)
            self.classifier = nn.Linear(8, class_count)

        def forward(self, batch: Any) -> Any:
            mask = (batch >= 0).float()
            values = torch.clamp(batch, min=0.0).unsqueeze(-1)
            features = torch.tanh(self.value_proj(values))
            attention = torch.softmax(self.position_weight.unsqueeze(0).masked_fill(mask <= 0, -1e4), dim=1)
            pooled = (features * attention.unsqueeze(-1)).sum(dim=1)
            return self.classifier(pooled), attention
else:  # pragma: no cover - only used without torch
    _OffsetAttentionClassifier = object  # type: ignore


def attention_offset_salience(
    payloads: Sequence[bytes],
    labels: Sequence[str],
    max_length: int = 128,
    epochs: int = 35,
    cache_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Train a tiny attention classifier and return per-offset family-separation salience."""
    if torch is None or nn is None or F is None or len(payloads) < 4 or len(set(labels)) < 2:
        return {"available": False, "reason": "torch_or_labels_unavailable", "offset_scores": []}

    cache = load_salience_cache(cache_path)
    key = _payload_cache_key(payloads, labels, max_length)
    cached = cache.get(key)
    if isinstance(cached, dict):
        cached["cache_hit"] = True
        return cached

    label_values = sorted(set(labels))
    label_index = {label: index for index, label in enumerate(label_values)}
    rows: List[List[float]] = []
    for payload in payloads:
        clipped = payload[:max_length]
        row = [value / 255.0 for value in clipped]
        row.extend([-1.0] * (max_length - len(row)))
        rows.append(row)

    x = torch.tensor(rows, dtype=torch.float32)
    y = torch.tensor([label_index[label] for label in labels], dtype=torch.long)
    model = _OffsetAttentionClassifier(max_length, len(label_values))
    optimizer = torch.optim.Adam(model.parameters(), lr=0.035)
    for _ in range(max(1, epochs)):
        optimizer.zero_grad()
        logits, _ = model(x)
        loss = F.cross_entropy(logits, y)
        loss.backward()
        optimizer.step()

    with torch.no_grad():
        logits, attention = model(x)
        accuracy = float((logits.argmax(dim=1) == y).float().mean().item())
        scores = attention.mean(dim=0).detach().cpu().tolist()
    result = {
        "available": True,
        "method": "attention_classifier",
        "class_count": len(label_values),
        "message_count": len(payloads),
        "training_accuracy": round(accuracy, 6),
        "offset_scores": [round(float(score), 8) for score in scores],
        "cache_hit": False,
    }
    cache[key] = result
    save_salience_cache(cache_path, cache)
    return result


def encoder_gradient_salience(
    payloads: Sequence[bytes],
    model_path: Optional[str] = None,
    max_length: int = 128,
    sample_limit: int = 512,
) -> Dict[str, Any]:
    """Return gradient salience for compatible torch encoders, or an unavailable marker."""
    if torch is None or not payloads:
        return {"available": False, "reason": "torch_or_payloads_unavailable", "offset_scores": []}
    encoder = load_optional_encoder(model_path=model_path)
    if encoder is None:
        return {"available": False, "reason": "encoder_unavailable", "offset_scores": []}
    try:
        rows: List[List[float]] = []
        for payload in payloads[:sample_limit]:
            clipped = payload[:max_length]
            row = [value / 255.0 for value in clipped]
            row.extend([0.0] * (max_length - len(row)))
            rows.append(row)
        x = torch.tensor(rows, dtype=torch.float32, requires_grad=True)
        output = encoder.model(x)
        if isinstance(output, (tuple, list)):
            output = output[0]
        if isinstance(output, dict):
            for key in ("z", "latent", "mu", "embedding"):
                if key in output:
                    output = output[key]
                    break
        score = output.float().pow(2).mean()
        score.backward()
        salience = x.grad.detach().abs().mean(dim=0).cpu().tolist()
    except Exception as exc:  # pragma: no cover - depends on external model shape
        return {"available": False, "reason": f"gradient_failed:{exc.__class__.__name__}", "offset_scores": []}
    max_score = max(salience) if salience else 0.0
    if max_score > 0:
        salience = [value / max_score for value in salience]
    return {
        "available": True,
        "method": "encoder_gradient",
        "message_count": min(len(payloads), sample_limit),
        "offset_scores": [round(float(score), 8) for score in salience],
    }


def merge_salience_scores(attention: Dict[str, Any], gradient: Dict[str, Any], max_length: int) -> List[float]:
    merged: List[float] = []
    attn = attention.get("offset_scores", []) if attention.get("available") else []
    grad = gradient.get("offset_scores", []) if gradient.get("available") else []
    for offset in range(max_length):
        values = []
        if offset < len(attn):
            values.append(float(attn[offset]))
        if offset < len(grad):
            values.append(float(grad[offset]))
        merged.append(sum(values) / len(values) if values else 0.0)
    max_score = max(merged) if merged else 0.0
    return [score / max_score if max_score > 0 else 0.0 for score in merged]
