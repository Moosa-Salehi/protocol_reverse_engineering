from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Sequence

from protocol_re.inference.boundary_detection import infer_template
from protocol_re.utils.bytes import hex_to_bytes


def vectorize_hex_messages(messages_hex: Sequence[str]) -> List[List[int]]:
    messages = [hex_to_bytes(message) for message in messages_hex]
    max_len = max((len(message) for message in messages), default=0)
    matrix = [[0 for _ in range(max_len)] for _ in range(len(messages))]
    for idx, message in enumerate(messages):
        for pos, value in enumerate(message):
            matrix[idx][pos] = value
    return matrix


def total_variance(index_groups: Sequence[Sequence[int]], matrix: List[List[int]]) -> float:
    variance_sum = 0.0
    for indices in index_groups:
        indices = list(indices)
        if len(indices) <= 1:
            continue
        points = [matrix[index] for index in indices]
        dimensions = len(points[0]) if points else 0
        centroid = [
            sum(point[dim] for point in points) / len(points)
            for dim in range(dimensions)
        ]
        for point in points:
            variance_sum += sum(
                (point[dim] - centroid[dim]) ** 2 for dim in range(dimensions)
            )
    return variance_sum



def analyze_subcluster_hypotheses(messages_hex: Sequence[str], candidate_byte_range: range = range(4, 20)) -> Dict[str, object]:
    if not messages_hex:
        return {"best_strategy": "single", "formats": {}}

    matrix = vectorize_hex_messages(messages_hex)
    messages = [hex_to_bytes(message) for message in messages_hex]
    hypotheses: Dict[str, Dict[str, object]] = {}

    best_keyword_score = float("inf")
    best_keyword_split = None
    for width in (1, 2):
        for offset in candidate_byte_range:
            groups: Dict[bytes, List[int]] = defaultdict(list)
            for idx, message in enumerate(messages):
                if offset + width <= len(message):
                    groups[message[offset : offset + width]].append(idx)
            if 1 < len(groups) < min(100, len(messages)):
                score = total_variance(groups.values(), matrix)
                if score < best_keyword_score:
                    best_keyword_score = score
                    best_keyword_split = groups
    if best_keyword_split:
        hypotheses["keyword"] = {"score": best_keyword_score, "split": best_keyword_split}

    length_groups: Dict[int, List[int]] = defaultdict(list)
    for idx, message in enumerate(messages):
        length_groups[len(message)].append(idx)
    if 1 < len(length_groups) < min(100, len(messages)):
        hypotheses["length"] = {"score": total_variance(length_groups.values(), matrix), "split": length_groups}

    hypotheses["single"] = {"score": total_variance([range(len(messages))], matrix), "split": {"all": list(range(len(messages)))}}

    best_strategy = min(hypotheses.items(), key=lambda item: item[1]["score"])[0]
    best_split = hypotheses[best_strategy]["split"]

    formats = {}
    for idx, (subcluster_id, indices) in enumerate(best_split.items()):
        members = [messages_hex[i] for i in indices]
        if not members:
            continue
        formats[f"format_{idx}"] = {
            "source_subcluster_id": subcluster_id.hex() if isinstance(subcluster_id, bytes) else str(subcluster_id),
            "message_count": len(members),
            "template": infer_template(members),
        }

    return {
        "best_strategy": best_strategy,
        "formats": formats,
        "scores": {name: round(details["score"], 4) for name, details in hypotheses.items()},
    }
