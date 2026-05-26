from __future__ import annotations

from collections import Counter
from math import log2
from typing import Dict, Optional, Sequence

from protocol_re.inference.discriminator_fields import split_messages_by_discriminator
from protocol_re.utils.bytes import hex_to_bytes


def shannon_entropy(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = float(sum(counts.values()))
    return -sum((count / total) * log2(count / total) for count in counts.values())


def find_keyword_byte(messages_hex: Sequence[str], search_range: range = range(4, 20)) -> Optional[Dict[str, float]]:
    """Backward-compatible wrapper for discriminator/opcode candidate discovery."""
    summary = split_messages_by_discriminator(messages_hex, search_range=search_range)
    keyword = summary.get("keyword") if isinstance(summary, dict) else None
    return keyword if isinstance(keyword, dict) else None


def split_family_by_keyword(messages_hex: Sequence[str], search_range: range = range(4, 20)) -> Dict[str, object]:
    """Backward-compatible output name for discriminator/opcode subformat discovery."""
    return split_messages_by_discriminator(messages_hex, search_range=search_range)
