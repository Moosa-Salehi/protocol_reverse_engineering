from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from math import log2, sqrt
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilyAssignment, MessageRecord
from protocol_re.utils.bytes import hex_to_bytes


NGRAM_SIZES = (2, 3)
TOP_VALUES_LIMIT = 8
TOP_MOTIFS_LIMIT = 10


def shannon_entropy_from_counts(counts: Counter[int]) -> float:
    total = float(sum(counts.values()))
    if total <= 0:
        return 0.0
    return -sum((count / total) * log2(count / total) for count in counts.values())


def shannon_entropy(values: Sequence[int]) -> float:
    return shannon_entropy_from_counts(Counter(values))


def sparse_byte_histogram(payload: bytes) -> Dict[str, int]:
    return {f"{value:02x}": count for value, count in sorted(Counter(payload).items())}


def top_byte_values(payload: bytes, limit: int = TOP_VALUES_LIMIT) -> List[Dict[str, object]]:
    return [
        {"byte": f"{value:02x}", "count": count}
        for value, count in Counter(payload).most_common(limit)
    ]


def run_length_stats(payload: bytes) -> Dict[str, int]:
    if not payload:
        return {"max_run_length": 0, "repeated_run_count": 0, "adjacent_repeat_pairs": 0}

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


def ngram_counts(payload: bytes, width: int) -> Counter[bytes]:
    if len(payload) < width:
        return Counter()
    return Counter(payload[index : index + width] for index in range(0, len(payload) - width + 1))


def repeated_ngram_summary(payload: bytes) -> Dict[str, object]:
    repeated_total = 0
    top_motifs: List[Dict[str, object]] = []

    for width in NGRAM_SIZES:
        counts = ngram_counts(payload, width)
        repeated = {gram: count for gram, count in counts.items() if count > 1}
        repeated_total += sum(count - 1 for count in repeated.values())
        for gram, count in Counter(repeated).most_common(TOP_MOTIFS_LIMIT):
            top_motifs.append({"ngram": gram.hex(), "count": count, "width": width})

    top_motifs.sort(key=lambda item: (-int(item["count"]), -int(item["width"]), str(item["ngram"])))
    return {
        "repeated_ngram_instances": repeated_total,
        "top_repeated_motifs": top_motifs[:TOP_MOTIFS_LIMIT],
    }


def message_feature_record(record: MessageRecord) -> Dict[str, object]:
    payload = hex_to_bytes(record.payload_hex)
    values = list(payload)
    return {
        "msg_id": record.msg_id,
        "session_id": record.session_id,
        "direction": record.direction,
        "payload_len": record.payload_len,
        "byte_entropy": round(shannon_entropy(values), 6),
        "unique_byte_count": len(set(values)),
        "unique_byte_ratio": round(len(set(values)) / len(values), 6) if values else 0.0,
        "byte_histogram": sparse_byte_histogram(payload),
        "top_byte_values": top_byte_values(payload),
        **run_length_stats(payload),
        **repeated_ngram_summary(payload),
    }


def _family_lookup(assignments: Sequence[FamilyAssignment]) -> Dict[int, str]:
    return {assignment.msg_id: assignment.family_id for assignment in assignments}


@dataclass
class RunningStats:
    count: int = 0
    total: float = 0.0
    total_sq: float = 0.0
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def update(self, value: float) -> None:
        self.count += 1
        self.total += value
        self.total_sq += value * value
        self.min_value = value if self.min_value is None else min(self.min_value, value)
        self.max_value = value if self.max_value is None else max(self.max_value, value)

    def mean(self) -> float:
        return self.total / self.count if self.count else 0.0

    def std_dev(self) -> float:
        if self.count <= 1:
            return 0.0
        variance = (self.total_sq - (self.total * self.total / self.count)) / (self.count - 1)
        return sqrt(max(0.0, variance))

    def summary(self, include_std: bool = False) -> Dict[str, float]:
        data = {
            "min": round(self.min_value or 0.0, 6),
            "max": round(self.max_value or 0.0, 6),
            "mean": round(self.mean(), 6),
        }
        if include_std:
            data["std_dev"] = round(self.std_dev(), 6)
        return data


@dataclass
class FamilyFeatureAccumulator:
    family_id: str
    message_count: int = 0
    length_stats: RunningStats = field(default_factory=RunningStats)
    length_histogram: Counter[int] = field(default_factory=Counter)
    aggregate_byte_histogram: Counter[int] = field(default_factory=Counter)
    entropy_stats: RunningStats = field(default_factory=RunningStats)
    unique_ratio_stats: RunningStats = field(default_factory=RunningStats)
    max_run_stats: RunningStats = field(default_factory=RunningStats)
    position_counts: List[Counter[int]] = field(default_factory=list)
    position_coverage: List[int] = field(default_factory=list)
    motif_counts: Dict[int, Counter[bytes]] = field(default_factory=lambda: {width: Counter() for width in NGRAM_SIZES})
    repeated_message_count: int = 0
    repeated_ngram_instances: int = 0
    example_msg_ids: List[int] = field(default_factory=list)

    def update(self, record: MessageRecord, feature_record: Dict[str, object]) -> None:
        payload = hex_to_bytes(record.payload_hex)
        self.message_count += 1
        self.length_stats.update(record.payload_len)
        self.length_histogram.update([record.payload_len])
        self.aggregate_byte_histogram.update(payload)
        self.entropy_stats.update(float(feature_record["byte_entropy"]))
        self.unique_ratio_stats.update(float(feature_record["unique_byte_ratio"]))
        self.max_run_stats.update(float(feature_record["max_run_length"]))
        if len(self.example_msg_ids) < 10:
            self.example_msg_ids.append(record.msg_id)

        for offset, byte_value in enumerate(payload):
            while len(self.position_counts) <= offset:
                self.position_counts.append(Counter())
                self.position_coverage.append(0)
            self.position_counts[offset].update([byte_value])
            self.position_coverage[offset] += 1

        has_repetition = False
        for width in NGRAM_SIZES:
            counts = ngram_counts(payload, width)
            repeated = {gram: count for gram, count in counts.items() if count > 1}
            if repeated:
                has_repetition = True
            self.repeated_ngram_instances += sum(count - 1 for count in repeated.values())
            self.motif_counts[width].update(counts)
        if has_repetition:
            self.repeated_message_count += 1

    def position_stats(self) -> Dict[str, List[float]]:
        entropy_vector: List[float] = []
        uniqueness_ratio_vector: List[float] = []
        coverage_vector: List[float] = []
        for counts, coverage_count in zip(self.position_counts, self.position_coverage):
            entropy_vector.append(round(shannon_entropy_from_counts(counts), 6))
            uniqueness_ratio_vector.append(round(len(counts) / coverage_count, 6) if coverage_count else 0.0)
            coverage_vector.append(round(coverage_count / self.message_count, 6) if self.message_count else 0.0)
        return {
            "entropy_vector": entropy_vector,
            "uniqueness_ratio_vector": uniqueness_ratio_vector,
            "coverage_vector": coverage_vector,
        }

    def motif_stats(self) -> Dict[str, object]:
        top_motifs: List[Dict[str, object]] = []
        for width, counts in self.motif_counts.items():
            for gram, count in counts.most_common(TOP_MOTIFS_LIMIT):
                top_motifs.append({"ngram": gram.hex(), "count": count, "width": width})
        top_motifs.sort(key=lambda item: (-int(item["count"]), -int(item["width"]), str(item["ngram"])))
        return {
            "messages_with_repetition": self.repeated_message_count,
            "messages_with_repetition_ratio": round(self.repeated_message_count / self.message_count, 6) if self.message_count else 0.0,
            "repeated_ngram_instances": self.repeated_ngram_instances,
            "top_motifs": top_motifs[:TOP_MOTIFS_LIMIT],
        }

    def to_record(self) -> Dict[str, object]:
        return {
            "family_id": self.family_id,
            "message_count": self.message_count,
            "length_stats": {
                **self.length_stats.summary(include_std=True),
                "distinct_lengths": len(self.length_histogram),
                "length_histogram": {str(length): count for length, count in sorted(self.length_histogram.items())},
            },
            "position_stats": self.position_stats(),
            "aggregate_byte_histogram": {f"{value:02x}": count for value, count in sorted(self.aggregate_byte_histogram.items())},
            "entropy_summary": self.entropy_stats.summary(),
            "unique_ratio_summary": self.unique_ratio_stats.summary(),
            "run_length_summary": {
                "max": int(self.max_run_stats.max_value or 0),
                "mean": round(self.max_run_stats.mean(), 6),
            },
            "motif_stats": self.motif_stats(),
            "example_msg_ids": self.example_msg_ids,
        }


def stream_feature_artifacts(
    records: Iterable[MessageRecord],
    message_output_handle,
    assignments: Optional[Sequence[FamilyAssignment]] = None,
    include_unassigned: bool = False,
) -> Dict[str, Dict[str, object]]:
    family_by_msg_id = _family_lookup(assignments or [])
    family_accumulators: Dict[str, FamilyFeatureAccumulator] = {}
    message_count = 0

    for record in records:
        feature_record = message_feature_record(record)
        message_output_handle.write(__import__("json").dumps(feature_record, sort_keys=True) + "\n")
        message_count += 1

        if assignments:
            family_id = family_by_msg_id.get(record.msg_id)
            if family_id is None and not include_unassigned:
                continue
            family_id = family_id or "unassigned"
        else:
            family_id = f"len_{record.payload_len}"

        accumulator = family_accumulators.setdefault(family_id, FamilyFeatureAccumulator(family_id=family_id))
        accumulator.update(record, feature_record)

    return {family_id: accumulator.to_record() for family_id, accumulator in family_accumulators.items()}


def extract_feature_artifacts(
    records: Sequence[MessageRecord],
    assignments: Optional[Sequence[FamilyAssignment]] = None,
    include_unassigned: bool = False,
) -> Tuple[List[Dict[str, object]], Dict[str, Dict[str, object]]]:
    message_features: List[Dict[str, object]] = []
    from io import StringIO

    buffer = StringIO()
    family_features = stream_feature_artifacts(records, buffer, assignments=assignments, include_unassigned=include_unassigned)
    buffer.seek(0)
    import json

    for line in buffer:
        message_features.append(json.loads(line))
    return message_features, family_features
