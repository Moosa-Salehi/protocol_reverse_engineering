from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from math import log2, sqrt
from statistics import mean
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilyAssignment, MessageRecord
from protocol_re.utils.bytes import hex_to_bytes


NGRAM_SIZES = (2, 3)
STRUCTURAL_MOTIF_SIZES = (4, 5, 6, 8)
TOP_VALUES_LIMIT = 8
TOP_MOTIFS_LIMIT = 10
TOP_NGRAM_FREQUENCIES_LIMIT = 20
TOP_STRUCTURAL_MOTIFS_LIMIT = 15
TRAILING_SUFFIX_SIZES = (1, 2, 4, 8)
MAX_POSITION_STATS_LENGTH = 512  # Limit position-by-position analysis to first 512 bytes
MAX_NGRAM_ANALYSIS_LENGTH = 1024  # Limit n-gram analysis to first 1024 bytes


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


def trailing_run(payload: bytes) -> Tuple[Optional[int], int]:
    if not payload:
        return None, 0
    byte_value = payload[-1]
    run_length = 1
    for index in range(len(payload) - 2, -1, -1):
        if payload[index] != byte_value:
            break
        run_length += 1
    return byte_value, run_length


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
    trailing_byte, trailing_run_length = trailing_run(payload)
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
        "trailing_byte": f"{trailing_byte:02x}" if trailing_byte is not None else None,
        "trailing_run_length": trailing_run_length,
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
    structural_motif_counts: Dict[int, Counter[bytes]] = field(default_factory=lambda: {width: Counter() for width in STRUCTURAL_MOTIF_SIZES})
    repeated_message_count: int = 0
    repeated_ngram_instances: int = 0
    wide_repeated_message_count: int = 0
    wide_repeated_instances: int = 0
    trailing_run_length_stats: RunningStats = field(default_factory=RunningStats)
    trailing_byte_counts: Counter[int] = field(default_factory=Counter)
    suffix_counts: Dict[int, Counter[bytes]] = field(default_factory=lambda: {width: Counter() for width in TRAILING_SUFFIX_SIZES})
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
        self.trailing_run_length_stats.update(float(feature_record["trailing_run_length"]))
        trailing_byte, _ = trailing_run(payload)
        if trailing_byte is not None:
            self.trailing_byte_counts.update([trailing_byte])
        if len(self.example_msg_ids) < 10:
            self.example_msg_ids.append(record.msg_id)

        # Limit position-by-position analysis to avoid performance issues with large payloads
        position_analysis_payload = payload[:MAX_POSITION_STATS_LENGTH]
        for offset, byte_value in enumerate(position_analysis_payload):
            while len(self.position_counts) <= offset:
                self.position_counts.append(Counter())
                self.position_coverage.append(0)
            self.position_counts[offset].update([byte_value])
            self.position_coverage[offset] += 1

        # Limit n-gram analysis to avoid performance issues with large payloads
        ngram_analysis_payload = payload[:MAX_NGRAM_ANALYSIS_LENGTH]
        has_repetition = False
        for width in NGRAM_SIZES:
            counts = ngram_counts(ngram_analysis_payload, width)
            repeated = {gram: count for gram, count in counts.items() if count > 1}
            if repeated:
                has_repetition = True
            self.repeated_ngram_instances += sum(count - 1 for count in repeated.values())
            self.motif_counts[width].update(counts)
        if has_repetition:
            self.repeated_message_count += 1

        has_wide_repetition = False
        for width in STRUCTURAL_MOTIF_SIZES:
            counts = ngram_counts(ngram_analysis_payload, width)
            repeated = {gram: count for gram, count in counts.items() if count > 1}
            if repeated:
                has_wide_repetition = True
            self.wide_repeated_instances += sum(count - 1 for count in repeated.values())
            self.structural_motif_counts[width].update(counts)
        if has_wide_repetition:
            self.wide_repeated_message_count += 1

        for width in TRAILING_SUFFIX_SIZES:
            if len(payload) >= width:
                self.suffix_counts[width].update([payload[-width:]])

    def position_stats(self) -> Dict[str, List[float]]:
        entropy_vector: List[float] = []
        uniqueness_ratio_vector: List[float] = []
        coverage_vector: List[float] = []
        for counts, coverage_count in zip(self.position_counts, self.position_coverage):
            entropy_vector.append(round(shannon_entropy_from_counts(counts), 6))
            uniqueness_ratio_vector.append(round(len(counts) / coverage_count, 6) if coverage_count else 0.0)
            coverage_vector.append(round(coverage_count / self.message_count, 6) if self.message_count else 0.0)
        discriminator_offsets = []
        for offset, (counts, coverage_count) in enumerate(zip(self.position_counts, self.position_coverage)):
            if not counts or not coverage_count:
                continue
            cardinality = len(counts)
            unique_ratio = cardinality / coverage_count
            if 1 < cardinality <= 32 and unique_ratio <= 0.5:
                value, count = counts.most_common(1)[0]
                discriminator_offsets.append(
                    {
                        "offset": offset,
                        "cardinality": cardinality,
                        "entropy": round(shannon_entropy_from_counts(counts), 6),
                        "unique_ratio": round(unique_ratio, 6),
                        "coverage": round(coverage_count / self.message_count, 6) if self.message_count else 0.0,
                        "dominant_value_hex": f"{value:02x}",
                        "dominant_ratio": round(count / coverage_count, 6),
                    }
                )
        discriminator_offsets.sort(key=lambda item: (-float(item["entropy"]), int(item["cardinality"]), int(item["offset"])))
        return {
            "entropy_vector": entropy_vector,
            "uniqueness_ratio_vector": uniqueness_ratio_vector,
            "coverage_vector": coverage_vector,
            "discriminator_position_stats": discriminator_offsets[:20],
        }

    def motif_stats(self) -> Dict[str, object]:
        top_motifs: List[Dict[str, object]] = []
        ngram_frequencies: Dict[str, List[Dict[str, object]]] = {}
        for width, counts in self.motif_counts.items():
            total_width_ngrams = sum(counts.values())
            ngram_frequencies[str(width)] = [
                {
                    "ngram": gram.hex(),
                    "count": count,
                    "frequency": round(count / total_width_ngrams, 6) if total_width_ngrams else 0.0,
                }
                for gram, count in counts.most_common(TOP_NGRAM_FREQUENCIES_LIMIT)
            ]
            for gram, count in counts.most_common(TOP_MOTIFS_LIMIT):
                top_motifs.append({"ngram": gram.hex(), "count": count, "width": width})
        top_motifs.sort(key=lambda item: (-int(item["count"]), -int(item["width"]), str(item["ngram"])))

        wide_motifs: List[Dict[str, object]] = []
        for width, counts in self.structural_motif_counts.items():
            for gram, count in counts.most_common(TOP_STRUCTURAL_MOTIFS_LIMIT):
                if count <= 1:
                    continue
                wide_motifs.append(
                    {
                        "ngram": gram.hex(),
                        "count": count,
                        "width": width,
                        "message_support_estimate": round(min(1.0, count / max(self.message_count, 1)), 6),
                    }
                )
        wide_motifs.sort(key=lambda item: (-int(item["count"]), -int(item["width"]), str(item["ngram"])))
        return {
            "messages_with_repetition": self.repeated_message_count,
            "messages_with_repetition_ratio": round(self.repeated_message_count / self.message_count, 6) if self.message_count else 0.0,
            "repeated_ngram_instances": self.repeated_ngram_instances,
            "top_motifs": top_motifs[:TOP_MOTIFS_LIMIT],
            "ngram_frequencies": ngram_frequencies,
            "wide_repeated_message_count": self.wide_repeated_message_count,
            "wide_repeated_message_ratio": round(self.wide_repeated_message_count / self.message_count, 6) if self.message_count else 0.0,
            "wide_repeated_instances": self.wide_repeated_instances,
            "wide_repeated_motifs": wide_motifs[:TOP_STRUCTURAL_MOTIFS_LIMIT],
        }

    def length_profile(self) -> Dict[str, object]:
        if not self.length_histogram:
            return {"kind": "empty", "modal_length": 0, "modal_ratio": 0.0}
        modal_length, modal_count = self.length_histogram.most_common(1)[0]
        modal_ratio = modal_count / max(self.message_count, 1)
        distinct_lengths = len(self.length_histogram)
        if distinct_lengths == 1:
            kind = "fixed"
        elif modal_ratio >= 0.9:
            kind = "mostly_fixed"
        else:
            kind = "variable"
        return {
            "kind": kind,
            "modal_length": modal_length,
            "modal_ratio": round(modal_ratio, 6),
            "distinct_lengths": distinct_lengths,
            "length_std_dev": round(self.length_stats.std_dev(), 6),
        }

    def trailing_block_stats(self) -> Dict[str, object]:
        top_trailing_bytes = [
            {
                "byte": f"{byte_value:02x}",
                "count": count,
                "support": round(count / max(self.message_count, 1), 6),
            }
            for byte_value, count in self.trailing_byte_counts.most_common(5)
        ]
        top_suffixes = {}
        for width, counts in self.suffix_counts.items():
            top_suffixes[str(width)] = [
                {
                    "suffix_hex": suffix.hex(),
                    "count": count,
                    "support": round(count / max(self.message_count, 1), 6),
                }
                for suffix, count in counts.most_common(5)
            ]
        padding_candidates = [
            item
            for item in top_trailing_bytes
            if float(item["support"]) >= 0.8 and self.trailing_run_length_stats.mean() >= 2.0
        ]
        return {
            "trailing_run_length": self.trailing_run_length_stats.summary(include_std=True),
            "top_trailing_bytes": top_trailing_bytes,
            "top_suffixes": top_suffixes,
            "padding_candidates": padding_candidates,
        }

    def recurring_field_groups(self, min_support: float = 0.95, min_coverage: float = 0.8) -> List[Dict[str, object]]:
        groups: List[Dict[str, object]] = []
        current_start: Optional[int] = None
        current_bytes: List[int] = []
        current_supports: List[float] = []
        current_coverages: List[float] = []

        def flush(end_offset: int) -> None:
            nonlocal current_start, current_bytes, current_supports, current_coverages
            if current_start is None or not current_bytes:
                return
            groups.append(
                {
                    "start": current_start,
                    "end": end_offset,
                    "kind": "fixed_position_group",
                    "value_hex": bytes(current_bytes).hex(),
                    "mean_support": round(mean(current_supports), 6),
                    "mean_coverage": round(mean(current_coverages), 6),
                }
            )
            current_start = None
            current_bytes = []
            current_supports = []
            current_coverages = []

        for offset, counts in enumerate(self.position_counts):
            coverage = self.position_coverage[offset] / max(self.message_count, 1)
            if not counts or coverage < min_coverage:
                flush(offset)
                continue
            value, count = counts.most_common(1)[0]
            support = count / max(self.position_coverage[offset], 1)
            if support < min_support:
                flush(offset)
                continue
            if current_start is None:
                current_start = offset
            current_bytes.append(value)
            current_supports.append(support)
            current_coverages.append(coverage)
        flush(len(self.position_counts))
        return groups[:20]

    def structure_stats(self) -> Dict[str, object]:
        return {
            "length_profile": self.length_profile(),
            "trailing_block_stats": self.trailing_block_stats(),
            "recurring_field_groups": self.recurring_field_groups(),
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
            "structure_stats": self.structure_stats(),
            "example_msg_ids": self.example_msg_ids,
        }


def stream_feature_artifacts(
    records: Iterable[MessageRecord],
    assignments: Optional[Sequence[FamilyAssignment]] = None,
    include_unassigned: bool = False,
) -> Dict[str, Dict[str, object]]:
    family_by_msg_id = _family_lookup(assignments or [])
    family_accumulators: Dict[str, FamilyFeatureAccumulator] = {}

    for record in records:
        payload = hex_to_bytes(record.payload_hex)
        values = list(payload)
        _, trailing_run_length = trailing_run(payload)
        feature_record = {
            "byte_entropy": round(shannon_entropy(values), 6),
            "unique_byte_ratio": round(len(set(values)) / len(values), 6) if values else 0.0,
            "max_run_length": run_length_stats(payload)["max_run_length"],
            "trailing_run_length": trailing_run_length,
        }

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
) -> Dict[str, Dict[str, object]]:
    return stream_feature_artifacts(records, assignments=assignments, include_unassigned=include_unassigned)
