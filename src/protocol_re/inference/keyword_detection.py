from __future__ import annotations

from collections import Counter, defaultdict
from math import log2
from typing import Dict, List, Optional, Sequence

from protocol_re.inference.boundary_detection import infer_template
from protocol_re.utils.bytes import hex_to_bytes



def shannon_entropy(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = float(sum(counts.values()))
    return -sum((count / total) * log2(count / total) for count in counts.values())



def find_keyword_byte(messages_hex: Sequence[str], search_range: range = range(4, 20)) -> Optional[Dict[str, float]]:
    if not messages_hex:
        return None

    messages = [hex_to_bytes(message) for message in messages_hex]
    best = None
    for offset in search_range:
        values = [message[offset] for message in messages if offset < len(message)]
        if not values:
            continue
        current_entropy = shannon_entropy(values)
        cardinality = len(set(values))
        if best is None or current_entropy > best["entropy"]:
            best = {
                "offset": float(offset),
                "entropy": round(current_entropy, 4),
                "cardinality": float(cardinality),
            }
    return best



def split_family_by_keyword(messages_hex: Sequence[str], search_range: range = range(4, 20)) -> Dict[str, object]:
    keyword_info = find_keyword_byte(messages_hex, search_range=search_range)
    if keyword_info is None:
        return {
            "keyword": None,
            "subclusters": {"format_0": {"message_count": len(messages_hex), "template": infer_template(messages_hex)}},
        }

    offset = int(keyword_info["offset"])
    grouped: Dict[int, List[str]] = defaultdict(list)
    for message_hex in messages_hex:
        message = hex_to_bytes(message_hex)
        if offset < len(message):
            grouped[message[offset]].append(message_hex)

    subclusters = {}
    for idx, (keyword_value, members) in enumerate(sorted(grouped.items())):
        subclusters[f"format_{idx}"] = {
            "keyword_value": f"0x{keyword_value:02x}",
            "message_count": len(members),
            "template": infer_template(members),
        }

    return {
        "keyword": keyword_info,
        "subclusters": subclusters,
    }
