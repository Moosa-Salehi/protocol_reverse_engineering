from __future__ import annotations

from collections import Counter
from math import log2
from statistics import mean
from typing import Dict, List, Sequence

from protocol_re.model.schema import MessageRecord
from protocol_re.utils.bytes import hex_to_bytes, safe_int_from_bytes

try:
    import numpy as np
except Exception:  # pragma: no cover - optional dependency
    np = None


HIGH_VOLATILITY_FIELD_TYPES = {
    "transaction_id",
    "transaction-id",
    "sequence",
    "sequence_number",
    "seq",
    "timestamp",
    "checksum",
    "crc",
    "nonce",
    "random_nonce",
    "payload_blob",
    "blob",
}


def payload_hash(payload_hex: str) -> str:
    import hashlib

    return hashlib.sha256(bytes.fromhex(payload_hex)).hexdigest()


def stable_prefix_mask(records: Sequence[MessageRecord], width: int = 16) -> List[float]:
    payloads = [hex_to_bytes(record.payload_hex) for record in records if record.payload_hex]
    if not payloads:
        return [0.0] * width
    mask: List[float] = []
    for offset in range(width):
        values = [payload[offset] for payload in payloads if offset < len(payload)]
        if not values:
            mask.append(0.0)
            continue
        _, count = Counter(values).most_common(1)[0]
        mask.append(round(count / len(values), 6))
    return mask


def volatile_offsets(records: Sequence[MessageRecord], width: int = 64) -> set[int]:
    payloads = [hex_to_bytes(record.payload_hex) for record in records if record.payload_hex]
    offsets: set[int] = set()
    if len(payloads) < 3:
        return offsets
    for offset in range(width):
        values = [payload[offset] for payload in payloads if offset < len(payload)]
        if len(values) < 3:
            continue
        unique_ratio = len(set(values)) / len(values)
        stable_ratio = Counter(values).most_common(1)[0][1] / len(values)
        if unique_ratio >= 0.75 and stable_ratio <= 0.35:
            offsets.add(offset)
    return offsets


def symbolic_feature_names(prefix_width: int = 16, discriminator_width: int = 8) -> List[str]:
    names = [
        "length_log_bucket",
        "length_mod_2",
        "length_mod_4",
        "length_mod_8",
        "direction_c2s",
        "direction_s2c",
        "direction_unknown",
        "entropy",
        "unique_ratio",
        "candidate_body_start",
        "length_field_evidence",
    ]
    names.extend(f"stable_prefix_{offset}" for offset in range(prefix_width))
    names.extend(f"discriminator_byte_{offset}" for offset in range(discriminator_width))
    return names


def vectorize_structural_features(
    records: Sequence[MessageRecord],
    corpus_records: Sequence[MessageRecord] | None = None,
    prefix_width: int = 16,
    discriminator_width: int = 8,
) -> object:
    if np is None:
        raise RuntimeError("NumPy is required for structural feature clustering")
    context = corpus_records or records
    prefix_mask = stable_prefix_mask(context, prefix_width)
    noisy_offsets = volatile_offsets(context, max(prefix_width, discriminator_width, 32))
    rows = [
        structural_feature_vector(record, prefix_mask, noisy_offsets, prefix_width, discriminator_width)
        for record in records
    ]
    return np.asarray(rows, dtype=np.float32)


def structural_feature_vector(
    record: MessageRecord,
    prefix_mask: Sequence[float],
    noisy_offsets: set[int],
    prefix_width: int,
    discriminator_width: int,
) -> List[float]:
    payload = hex_to_bytes(record.payload_hex)
    length = len(payload)
    direction = (record.direction or "unknown").lower()
    entropy = _entropy(payload)
    candidate_body_start = _candidate_body_start(payload)
    length_field_evidence = _length_field_evidence(payload)
    row = [
        log2(length + 1) / 16.0,
        (length % 2) / 2.0,
        (length % 4) / 4.0,
        (length % 8) / 8.0,
        1.0 if direction in {"c2s", "client_to_server", "request"} else 0.0,
        1.0 if direction in {"s2c", "server_to_client", "response"} else 0.0,
        1.0 if direction in {"", "unknown", "none"} else 0.0,
        entropy / 8.0,
        len(set(payload)) / max(length, 1),
        candidate_body_start / max(length, 1),
        length_field_evidence,
    ]
    for offset in range(prefix_width):
        if offset >= length or offset in noisy_offsets:
            row.append(0.0)
        else:
            row.append(float(prefix_mask[offset]))
    for offset in range(discriminator_width):
        if offset >= length or offset in noisy_offsets:
            row.append(0.0)
        else:
            row.append(payload[offset] / 255.0)
    return row


def downweight_raw_byte_matrix(matrix: object, records: Sequence[MessageRecord], corpus_records: Sequence[MessageRecord] | None = None) -> object:
    if np is None:
        return matrix
    result = np.asarray(matrix, dtype=np.float32, copy=True)
    if result.size == 0:
        return result
    noisy_offsets = volatile_offsets(corpus_records or records, min(result.shape[1], 128))
    for offset in noisy_offsets:
        if offset < result.shape[1]:
            result[:, offset] *= 0.15
    return result


def _entropy(payload: bytes) -> float:
    if not payload:
        return 0.0
    counts = Counter(payload)
    total = float(len(payload))
    return -sum((count / total) * log2(count / total) for count in counts.values())


def _candidate_body_start(payload: bytes) -> int:
    scan_limit = min(len(payload), 32)
    for offset in range(2, scan_limit):
        left = payload[:offset]
        right = payload[offset:]
        if left and right and _entropy(right) > _entropy(left) + 0.5:
            return offset
    return min(0, len(payload))


def _length_field_evidence(payload: bytes) -> float:
    if len(payload) < 4:
        return 0.0
    scores = []
    payload_len = len(payload)
    for offset in range(0, min(len(payload) - 1, 12)):
        for width in (1, 2, 4):
            if offset + width > len(payload):
                continue
            for endian in ("big", "little"):
                value = safe_int_from_bytes(payload[offset : offset + width], endian)
                if value in {payload_len, payload_len - offset - width, payload_len - offset}:
                    scores.append(1.0)
                elif 0 <= value <= payload_len:
                    scores.append(0.25)
    return max(scores) if scores else 0.0


def summarize_symbolic_feature_count(prefix_width: int = 16, discriminator_width: int = 8) -> int:
    return len(symbolic_feature_names(prefix_width, discriminator_width))
