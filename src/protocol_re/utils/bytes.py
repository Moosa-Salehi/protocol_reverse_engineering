"""Byte and hex helpers used across the pipeline."""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Sequence, Tuple


def hex_to_bytes(payload_hex: str) -> bytes:
    payload_hex = payload_hex.strip().lower()
    if payload_hex.startswith("0x"):
        payload_hex = payload_hex[2:]
    return bytes.fromhex(payload_hex)


def bytes_to_hex(payload: bytes) -> str:
    return payload.hex()


def safe_int_from_bytes(payload: bytes, endian: str = "big") -> int:
    return int.from_bytes(payload, endian, signed=False)


def numeric_sequence_stats(values: Sequence[int], max_value: int | None = None) -> Dict[str, Any]:
    if not values:
        return {
            "unique_ratio": 0.0,
            "monotonic_ratio": 0.0,
            "small_delta_ratio": 0.0,
            "delta_consistency": 0.0,
            "low_magnitude_score": 0.0,
            "sequence_score": 0.0,
        }

    deltas = [right - left for left, right in zip(values, values[1:])]
    denom = max(len(deltas), 1)
    nonnegative_deltas = [delta for delta in deltas if delta >= 0]
    abs_deltas = [abs(delta) for delta in deltas]
    mean_abs_delta = mean(abs_deltas) if abs_deltas else 0.0
    delta_stdev = pstdev(abs_deltas) if len(abs_deltas) > 1 else 0.0
    delta_consistency = 1.0 / (1.0 + (delta_stdev / (mean_abs_delta + 1.0)))
    max_value = max_value if max_value and max_value > 0 else max(max(values), 1)
    low_magnitude_score = max(0.0, 1.0 - (mean(values) / max_value))

    unique_ratio = len(set(values)) / len(values)
    monotonic_ratio = len(nonnegative_deltas) / denom
    small_delta_ratio = sum(1 for delta in nonnegative_deltas if delta <= 4) / denom
    sequence_score = (
        (0.35 * monotonic_ratio)
        + (0.25 * small_delta_ratio)
        + (0.25 * delta_consistency)
        + (0.15 * low_magnitude_score)
    )
    return {
        "unique_ratio": unique_ratio,
        "monotonic_ratio": monotonic_ratio,
        "small_delta_ratio": small_delta_ratio,
        "delta_consistency": delta_consistency,
        "low_magnitude_score": low_magnitude_score,
        "mean_abs_delta": mean_abs_delta,
        "sequence_score": sequence_score,
    }


def best_numeric_endian(chunks: Sequence[bytes]) -> Tuple[str | None, Dict[str, Dict[str, Any]]]:
    chunks = [bytes(chunk) for chunk in chunks if chunk]
    if not chunks:
        return None, {}
    width = len(chunks[0])
    max_value = (1 << (8 * width)) - 1
    stats: Dict[str, Dict[str, Any]] = {}
    for endian in ("big", "little"):
        values = [safe_int_from_bytes(chunk, endian=endian) for chunk in chunks]
        stats[endian] = numeric_sequence_stats(values, max_value=max_value)
    best_endian = max(
        stats,
        key=lambda endian: (
            float(stats[endian].get("sequence_score", 0.0) or 0.0),
            float(stats[endian].get("monotonic_ratio", 0.0) or 0.0),
            float(stats[endian].get("low_magnitude_score", 0.0) or 0.0),
        ),
    )
    if _big_endian_monotonic_prior_applies(best_endian, stats):
        stats["big"]["selection_prior"] = "high_monotonic_big_endian"
        best_endian = "big"
    return best_endian, stats


def _big_endian_monotonic_prior_applies(
    selected_endian: str,
    stats: Dict[str, Dict[str, Any]],
) -> bool:
    """Prefer big-endian when it is the clearly monotonic interpretation.

    Low-magnitude and delta-consistency terms can make little-endian win by a
    small margin for high-valued big-endian transaction identifiers. A near-
    perfect big-endian monotonic ratio is stronger evidence for network-order
    transaction/counter fields unless the little-endian view is equally
    monotonic.
    """
    if selected_endian != "little" or "big" not in stats or "little" not in stats:
        return False

    big = stats["big"]
    little = stats["little"]
    big_monotonic = float(big.get("monotonic_ratio", 0.0) or 0.0)
    little_monotonic = float(little.get("monotonic_ratio", 0.0) or 0.0)
    score_gap = float(little.get("sequence_score", 0.0) or 0.0) - float(big.get("sequence_score", 0.0) or 0.0)

    return (
        big_monotonic >= 0.99
        and (big_monotonic - little_monotonic) >= 0.02
        and score_gap <= 0.12
    )


def pad_messages(messages: Iterable[bytes], pad_value: int = 0) -> List[bytes]:
    messages = list(messages)
    max_len = max((len(msg) for msg in messages), default=0)
    return [msg + bytes([pad_value]) * (max_len - len(msg)) for msg in messages]
