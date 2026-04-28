from __future__ import annotations

from collections import Counter, defaultdict
from math import log2
from statistics import mean, stdev
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilyAssignment, MessageRecord
from protocol_re.utils.bytes import hex_to_bytes


NGRAM_SIZES = (2, 3, 4)
TOP_VALUES_LIMIT = 8
TOP_MOTIFS_LIMIT = 10


def shannon_entropy(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = float(sum(counts.values()))
    return -sum((count / total) * log2(count / total) for count in counts.values())


def sparse_byte_histogram(payload: bytes) -> Dict[str, int]:
    histogram = Counter(payload)
    return {f"{value:02x}": count for value, count in sorted(histogram.items())}


def top_byte_values(payload: bytes, limit: int = TOP_VALUES_LIMIT) -> List[Dict[str, object]]:
    counts = Counter(payload)
    return [
        {"byte": f"{value:02x}", "count": count}
        for value, count in counts.most_common(limit)
    ]


def run_length_stats(payload: bytes) -> Dict[str, int]:
    if not payload:
        return {
            "max_run_length": 0,
            "repeated_run_count": 0,
            "adjacent_repeat_pairs": 0,
        }

    max_run_length = 1
    repeated_run_count = 0
    adjacent_repeat_pairs = 0
    current_run = 1

    for index in range(1, len(payload)):
        if payload[index] == payload[index - 1]:
            current_run += 1
            adjacent_repeat_pairs += 1
        else:
            if current_run > 1:
                repeated_run_count += 1
            max_run_length = max(max_run_length, current_run)
            current_run = 1
    if current_run > 1:
        repeated_run_count += 1
    max_run_length = max(max_run_length, current_run)

    return {
        "max_run_length": max_run_length,
        "repeated_run_count": repeated_run_count,
        "adjacent_repeat_pairs": adjacent_repeat_pairs,
    }


def ngram_counts(payload: bytes, n: int) -> Counter[bytes]:
    if len(payload) < n:
        return Counter()
    return Counter(payload[index : index + n] for index in range(0, len(payload) - n + 1))


def repeated_ngram_summary(payload: bytes) -> Dict[str, object]:
    repeated_total = 0
    top_motifs: List[Dict[str, object]] = []

    for n in NGRAM_SIZES:
        counts = ngram_counts(payload, n)
        repeated = {gram: count for gram, count in counts.items() if count > 1}
        repeated_total += sum(count - 1 for count in repeated.values())
        for gram, count in Counter(repeated).most_common(TOP_MOTIFS_LIMIT):
            top_motifs.append({"ngram": gram.hex(), "count": count, "width": n})

    top_motifs.sort(key=lambda item: (-int(item["count"]), -int(item["width"]), str(item["ngram"])))
    return {
        "repeated_ngram_instances": repeated_total,
        "top_repeated_motifs": top_motifs[:TOP_MOTIFS_LIMIT],
    }


def ngram_frequency_distribution(payload: bytes) -> List[Dict[str, object]]:
    """Compute n-gram frequency distributions for n in NGRAM_SIZES."""
    result = {}
    for n in NGRAM_SIZES:
        counts = ngram_counts(payload, n)
        if counts:
            total = sum(counts.values())
            freq_dist = [
                {"ngram": gram.hex(), "count": count, "frequency": round(count / total, 6)}
                for gram, count in counts.most_common(20)
            ]
            result[f"ngram_{n}"] = freq_dist
    return result


def position_entropy_vector(payload: bytes, context_window: int = 1) -> List[float]:
    """Compute entropy vector across payload positions."""
    if not payload:
        return []
    
    max_pos = len(payload)
    entropy_vector = []
    
    for pos in range(max_pos):
        values = []
        for offset in range(-context_window, context_window + 1):
            idx = pos + offset
            if 0 <= idx < len(payload):
                values.append(payload[idx])
        if values:
            entropy_vector.append(round(shannon_entropy(values), 6))
    
    return entropy_vector


def byte_uniqueness_ratio(payload: bytes) -> float:
    """Ratio of unique bytes to total bytes."""
    if not payload:
        return 0.0
    return len(set(payload)) / len(payload)


def payload_checksum(payload: bytes) -> Dict[str, str]:
    """Compute various checksums for payload integrity checking."""
    if not payload:
        return {"sum": "00", "xor": "00", "crc32": "00000000"}
    
    byte_sum = sum(payload) & 0xFF
    xor_all = 0
    for b in payload:
        xor_all ^= b
    
    # Simple CRC-like checksum
    crc = 0
    for byte in payload:
        crc = (crc + byte) & 0xFFFFFFFF
    
    return {
        "sum": f"{byte_sum:02x}",
        "xor": f"{xor_all:02x}",
        "crc32": f"{crc:08x}",
    }


def message_feature_record(record: MessageRecord) -> Dict[str, object]:
    payload = hex_to_bytes(record.payload_hex)
    run_stats = run_length_stats(payload)
    motif_stats = repeated_ngram_summary(payload)
    histogram = sparse_byte_histogram(payload)
    values = list(payload)

    return {
        "msg_id": record.msg_id,
        "session_id": record.session_id,
        "direction": record.direction,
        "payload_len": record.payload_len,
        "byte_entropy": round(shannon_entropy(values), 6),
        "unique_byte_count": len(set(values)),
        "unique_byte_ratio": round(byte_uniqueness_ratio(payload), 6),
        "byte_histogram": histogram,
        "top_byte_values": top_byte_values(payload),
        "ngram_frequency": ngram_frequency_distribution(payload),
        "position_entropy": position_entropy_vector(payload),
        "checksums": payload_checksum(payload),
        **run_stats,
        **motif_stats,
    }


def _family_lookup(assignments: Sequence[FamilyAssignment]) -> Dict[int, str]:
    return {assignment.msg_id: assignment.family_id for assignment in assignments}


def group_records_by_family(
    records: Sequence[MessageRecord],
    assignments: Optional[Sequence[FamilyAssignment]] = None,
    include_unassigned: bool = False,
) -> Dict[str, List[MessageRecord]]:
    grouped: Dict[str, List[MessageRecord]] = defaultdict(list)
    family_by_msg_id = _family_lookup(assignments or [])

    if assignments:
        for record in records:
            family_id = family_by_msg_id.get(record.msg_id)
            if family_id is None and not include_unassigned:
                continue
            grouped[family_id or "unassigned"].append(record)
    else:
        for record in records:
            grouped[f"len_{record.payload_len}"].append(record)

    return dict(grouped)


def _family_length_stats_from_features(features: Sequence[Dict[str, object]]) -> Dict[str, object]:
    lengths = [item["payload_len"] for item in features]
    counts = Counter(lengths)
    return {
        "min": min(lengths) if lengths else 0,
        "max": max(lengths) if lengths else 0,
        "mean": round(mean(lengths), 6) if lengths else 0.0,
        "std_dev": round(stdev(lengths), 6) if len(lengths) > 1 else 0.0,
        "distinct_lengths": len(counts),
        "length_histogram": {str(length): count for length, count in sorted(counts.items())},
    }


def _family_position_stats_from_features(features: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """Compute position stats using pre-computed per-position entropy vectors from messages."""
    # Collect all position entropy vectors
    position_entropy_vectors = [item["position_entropy"] for item in features if "position_entropy" in item]
    if not position_entropy_vectors:
        return {"entropy_vector": [], "uniqueness_ratio_vector": [], "coverage_vector": []}
    
    max_len = max((len(v) for v in position_entropy_vectors), default=0)
    num_messages = len(position_entropy_vectors)
    
    entropy_vector: List[float] = []
    uniqueness_ratio_vector: List[float] = []
    coverage_vector: List[float] = []
    
    for pos in range(max_len):
        values = []
        for vec in position_entropy_vectors:
            if pos < len(vec):
                values.append(vec[pos])
        
        coverage = len(values) / num_messages if num_messages else 0.0
        entropy_vector.append(round(mean(values), 6) if values else 0.0)
        # Approximate uniqueness: all values are floats, so uniqueness = 1.0 if any values
        uniqueness_ratio_vector.append(1.0 if values else 0.0)
        coverage_vector.append(round(coverage, 6))
    
    return {
        "entropy_vector": entropy_vector,
        "uniqueness_ratio_vector": uniqueness_ratio_vector,
        "coverage_vector": coverage_vector,
    }


def _family_byte_histogram_from_features(features: Sequence[Dict[str, object]]) -> Dict[str, int]:
    histogram: Dict[str, int] = {}
    for feat in features:
        hist = feat.get("byte_histogram", {})
        for byte_val, count in hist.items():
            histogram[byte_val] = histogram.get(byte_val, 0) + count
    return histogram


def _family_motif_stats_from_features(features: Sequence[Dict[str, object]]) -> Dict[str, object]:
    """Aggregate motif stats from pre-computed per-message motifs."""
    total_repeated_instances = 0
    repeated_message_count = 0
    aggregate_counts: Dict[int, Counter[bytes]] = {width: Counter() for width in NGRAM_SIZES}
    
    for feat in features:
        motif = feat.get("motif_stats", {})
        if motif.get("repeated_ngram_instances", 0) > 0:
            repeated_message_count += 1
        total_repeated_instances += motif.get("repeated_ngram_instances", 0)
        
        for motif_item in motif.get("top_repeated_motifs", []):
            gram = bytes.fromhex(motif_item["ngram"])
            width = motif_item["width"]
            if width in aggregate_counts:
                aggregate_counts[width][gram] += motif_item["count"]
    
    top_motifs: List[Dict[str, object]] = []
    for width, counts in aggregate_counts.items():
        for gram, count in counts.most_common(TOP_MOTIFS_LIMIT):
            top_motifs.append({"ngram": gram.hex(), "count": count, "width": width})
    top_motifs.sort(key=lambda item: (-int(item["count"]), -int(item["width"]), str(item["ngram"])))

    return {
        "messages_with_repetition": repeated_message_count,
        "messages_with_repetition_ratio": round(repeated_message_count / len(features), 6) if features else 0.0,
        "repeated_ngram_instances": total_repeated_instances,
        "top_motifs": top_motifs[:TOP_MOTIFS_LIMIT],
    }


def family_feature_record(family_id: str, records: Sequence[MessageRecord], message_features: Optional[Sequence[Dict[str, object]]] = None) -> Dict[str, object]:
    """Compute family-level features, preferring pre-computed message_features."""
    if message_features is None:
        message_features = [message_feature_record(record) for record in records]
    
    entropy_values = [item["byte_entropy"] for item in message_features]
    unique_ratios = [item["unique_byte_ratio"] for item in message_features]
    max_run_lengths = [item["max_run_length"] for item in message_features]

    return {
        "family_id": family_id,
        "message_count": len(records),
        "length_stats": _family_length_stats_from_features(message_features),
        "position_stats": _family_position_stats_from_features(message_features),
        "aggregate_byte_histogram": _family_byte_histogram_from_features(message_features),
        "entropy_summary": {
            "min": round(min(entropy_values), 6) if entropy_values else 0.0,
            "max": round(max(entropy_values), 6) if entropy_values else 0.0,
            "mean": round(mean(entropy_values), 6) if entropy_values else 0.0,
        },
        "unique_ratio_summary": {
            "min": round(min(unique_ratios), 6) if unique_ratios else 0.0,
            "max": round(max(unique_ratios), 6) if unique_ratios else 0.0,
            "mean": round(mean(unique_ratios), 6) if unique_ratios else 0.0,
        },
        "run_length_summary": {
            "max": max(max_run_lengths) if max_run_lengths else 0,
            "mean": round(mean(max_run_lengths), 6) if max_run_lengths else 0.0,
        },
        "motif_stats": _family_motif_stats_from_features(message_features),
        "example_msg_ids": [item["msg_id"] for item in message_features[:10]],
    }


def extract_feature_artifacts(
    records: Sequence[MessageRecord],
    assignments: Optional[Sequence[FamilyAssignment]] = None,
    include_unassigned: bool = False,
) -> Tuple[List[Dict[str, object]], Dict[str, Dict[str, object]]]:
    message_features = [message_feature_record(record) for record in records]
    grouped = group_records_by_family(records, assignments=assignments, include_unassigned=include_unassigned)
    
    family_features = {}
    for family_id, family_records in grouped.items():
        family_features[family_id] = family_feature_record(family_id, family_records, message_features=message_features)
    
    return message_features, family_features
