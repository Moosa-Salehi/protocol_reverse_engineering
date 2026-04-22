"""Byte and hex helpers used across the pipeline."""

from __future__ import annotations

from typing import Iterable, List


def hex_to_bytes(payload_hex: str) -> bytes:
    payload_hex = payload_hex.strip().lower()
    if payload_hex.startswith("0x"):
        payload_hex = payload_hex[2:]
    return bytes.fromhex(payload_hex)


def bytes_to_hex(payload: bytes) -> str:
    return payload.hex()


def safe_int_from_bytes(payload: bytes, endian: str = "big") -> int:
    return int.from_bytes(payload, endian, signed=False)


def pad_messages(messages: Iterable[bytes], pad_value: int = 0) -> List[bytes]:
    messages = list(messages)
    max_len = max((len(msg) for msg in messages), default=0)
    return [msg + bytes([pad_value]) * (max_len - len(msg)) for msg in messages]
