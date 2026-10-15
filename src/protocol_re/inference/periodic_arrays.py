"""Label-free detection of arrays of fixed-width elements inside a message family.

Register blocks, sample arrays and repeated datagram words are runs of varying
bytes in which the byte statistics repeat every p bytes. Entropy segmentation sees
no edge between two varying bytes, so such arrays end up as one wide field or as
arbitrary chunks. This module finds them from the family's messages alone:

1. Candidate regions are maximal runs of varying offsets (family entropy > 0 on
   the messages reaching the offset); one constant byte between varying ones is
   bridged, so a constant high byte in every element does not break the run.
2. For each period p, per-offset statistics (entropy, high/low-nibble entropy,
   zero share, value range, mean, top-value share) are grouped by phase
   (offset - start) mod p. The adjusted R^2 of that grouping is tested against a
   permutation null and must replicate between even- and odd-numbered elements.
3. Cross-length evidence: the gcd of the family's message-length differences,
   and a 1-/2-byte count or byte-count field whose value matches the bytes from
   the array start to the message end.
4. Edges are placed every p bytes inside the region, phase-aligned to the count
   field, else the message ends, else the region start.

Modes: ``strict`` needs cross-length evidence and significant statistics;
``loose`` additionally accepts significant statistics alone on long regions.
See :class:`protocol_re.config.thresholds.PeriodicArrays`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import reduce
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

from protocol_re.config.thresholds import BoundaryDetection, PeriodicArrays

MODES = ("off", "strict", "loose")
_FEATURES = ("H", "Hhi", "Hlo", "zero", "range", "mean", "top")


@dataclass
class ArrayRegion:
    """A detected array: offsets [start, end), element width, and the added edges."""

    start: int
    end: int
    period: int
    phase: int
    evidence: str
    phase_from: str
    tail: bool
    edges: List[int] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "period": self.period,
            "phase": self.phase,
            "evidence": self.evidence,
            "phase_from": self.phase_from,
            "tail": self.tail,
            "edges": list(self.edges),
            "stats": self.stats,
        }


def _entropy(counts: np.ndarray, total: int, bits: int) -> float:
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum() / bits)


def _matrix(messages: Sequence[bytes], maxlen: int):
    lens = np.array([min(len(m), maxlen) for m in messages])
    matrix = np.zeros((len(messages), maxlen), dtype=np.uint8)
    for i, message in enumerate(messages):
        matrix[i, : lens[i]] = np.frombuffer(message[:maxlen], dtype=np.uint8)
    return matrix, lens, np.array([len(m) for m in messages])


def _column_stats(matrix: np.ndarray, lens: np.ndarray, maxlen: int) -> Dict[str, np.ndarray]:
    valid = np.arange(maxlen)[None, :] < lens[:, None]
    stats = {name: np.zeros(maxlen) for name in _FEATURES}
    stats["n"] = valid.sum(0)
    for j in range(maxlen):
        values = matrix[valid[:, j], j]
        if values.size == 0:
            continue
        counts = np.bincount(values, minlength=256)
        stats["H"][j] = _entropy(counts, values.size, 8)
        stats["Hhi"][j] = _entropy(np.bincount(values >> 4, minlength=16), values.size, 4)
        stats["Hlo"][j] = _entropy(np.bincount(values & 15, minlength=16), values.size, 4)
        stats["zero"][j] = counts[0] / values.size
        stats["range"][j] = (int(values.max()) - int(values.min())) / 255
        stats["mean"][j] = values.mean() / 255
        stats["top"][j] = counts.max() / values.size
    return stats


def _varying_runs(stats: Dict[str, np.ndarray], min_messages: int) -> List[tuple[int, int]]:
    reach = stats["n"] >= min_messages
    varying = (stats["H"] > 1e-9) & reach
    upto = int(np.nonzero(reach)[0].max()) + 1 if reach.any() else 0
    bridged = varying.copy()
    for j in range(1, upto - 1):
        if not varying[j] and varying[j - 1] and varying[j + 1]:
            bridged[j] = True
    runs, j = [], 0
    while j < upto:
        if bridged[j]:
            k = j
            while k < upto and bridged[k]:
                k += 1
            runs.append((j, k))
            j = k
        else:
            j += 1
    return runs


def _phase_r2(features: np.ndarray, phase: np.ndarray, period: int) -> float:
    total = ((features - features.mean(0)) ** 2).sum()
    if total < 1e-12:
        return 0.0
    within = 0.0
    for q in range(period):
        group = features[phase == q]
        if len(group):
            within += ((group - group.mean(0)) ** 2).sum()
    n = len(features)
    r2 = 1 - within / total
    return 1 - (1 - r2) * (n - 1) / max(n - period, 1)


def _period_test(stats, start: int, end: int, period: int, rng) -> Optional[Dict[str, float]]:
    offsets = np.arange(start, end)
    offsets = offsets[stats["n"][offsets] >= 8]
    if len(offsets) < PeriodicArrays.MIN_REPEATS * period:
        return None
    features = np.stack([stats[name][offsets] for name in _FEATURES], axis=1)
    features = features[:, features.std(0) > 1e-6]
    if features.shape[1] == 0:
        return None
    features = (features - features.mean(0)) / features.std(0)
    phase = (offsets - start) % period
    r2 = _phase_r2(features, phase, period)
    null = np.array([_phase_r2(features, rng.permutation(phase), period) for _ in range(PeriodicArrays.PERMUTATIONS)])
    pvalue = (1 + (null >= r2).sum()) / (PeriodicArrays.PERMUTATIONS + 1)
    element = (offsets - start) // period
    profiles = []
    for half in (0, 1):
        selected = element % 2 == half
        if len(set(phase[selected])) < period:
            return {"r2": float(r2), "pval": float(pvalue), "split": 0.0}
        profiles.append(np.stack([features[selected & (phase == q)].mean(0) for q in range(period)]).ravel())
    a, b = profiles
    split = float(np.corrcoef(a, b)[0, 1]) if a.std() > 1e-9 and b.std() > 1e-9 else 0.0
    return {"r2": float(r2), "pval": float(pvalue), "split": split}


def _length_gcd(full_lengths: np.ndarray) -> tuple[int, int]:
    values, counts = np.unique(full_lengths, return_counts=True)
    keep, covered = [], 0
    for i in np.argsort(-counts):
        keep.append(int(values[i]))
        covered += counts[i]
        if covered >= PeriodicArrays.LENGTH_SHARE * len(full_lengths):
            break
    keep.sort()
    if len(keep) < 3:
        return 0, len(keep)
    return int(reduce(math.gcd, (x - keep[0] for x in keep[1:]))), len(keep)


def _count_field(matrix, lens, full_lengths, start: int, period: int) -> Optional[Dict[str, Any]]:
    """A 1-/2-byte field before the run counting its elements or bytes (needs 3+ lengths)."""
    if len(set(full_lengths.tolist())) < 3:
        return None
    for array_start in range(max(1, start - period), start + period + 1):
        remain = full_lengths - array_start
        if (remain < 0).any():
            continue
        for at in range(array_start):
            for width, order in ((1, None), (2, "big"), (2, "little")):
                if at + width > array_start or (lens < at + width).any():
                    continue
                if width == 1:
                    value = matrix[:, at].astype(int)
                elif order == "big":
                    value = matrix[:, at].astype(int) * 256 + matrix[:, at + 1]
                else:
                    value = matrix[:, at + 1].astype(int) * 256 + matrix[:, at]
                if len(set(value.tolist())) < 3:
                    continue
                for unit in (period, 1):
                    if (value * unit == remain).mean() >= PeriodicArrays.COUNT_FIELD_MATCH:
                        return {"start": array_start, "at": at, "width": width, "order": order,
                                "period": period if unit == period else None}
    return None


def _choose_period(significant: Dict[int, Dict[str, float]]) -> Optional[int]:
    if not significant:
        return None
    best = max(t["r2"] for t in significant.values())
    return min(p for p, t in significant.items() if t["r2"] >= PeriodicArrays.R2_RATIO * best)


def detect_array_regions(messages: Sequence[bytes], mode: str = "loose", seed: int = 0) -> List[ArrayRegion]:
    """Array regions of one family (empty for mode "off" or too few messages)."""
    if mode == "off":
        return []
    if mode not in MODES:
        raise ValueError(f"unknown periodic-array mode: {mode}")
    messages = [m for m in messages[: PeriodicArrays.SAMPLE_CAP] if m]
    if len(messages) < 5:
        return []
    maxlen = BoundaryDetection.MAX_BOUNDARY_DETECTION_LENGTH
    rng = np.random.default_rng(seed)
    matrix, lens, full_lengths = _matrix(messages, maxlen)
    stats = _column_stats(matrix, lens, maxlen)
    min_messages = max(3, int(PeriodicArrays.MIN_OFFSET_COVERAGE * len(messages)))
    reached = np.nonzero(stats["n"] >= min_messages)[0]
    if not len(reached):
        return []
    max_reach = int(reached.max()) + 1
    gcd, n_lengths = _length_gcd(full_lengths)
    periods = PeriodicArrays.PERIODS
    regions: List[ArrayRegion] = []
    for start, end in _varying_runs(stats, min_messages):
        tail = end >= max_reach - 1 and n_lengths >= 3
        tests = {p: t for p in periods if (t := _period_test(stats, start, end, p, rng))}
        significant = {
            p: t for p, t in tests.items()
            if t["pval"] < PeriodicArrays.MAX_PVALUE and t["split"] > PeriodicArrays.MIN_SPLIT_HALF and t["r2"] > PeriodicArrays.R2_MIN
        }
        length_ok = [p for p in periods if tail and gcd and gcd % p == 0 and end - start >= PeriodicArrays.MIN_REPEATS * p]
        count = None
        if tail:
            for p in sorted(length_ok or periods):
                count = _count_field(matrix, lens, full_lengths, start, p)
                if count:
                    break
        cross = set(length_ok) | ({count["period"]} if count and count.get("period") else set())
        period = _choose_period({p: t for p, t in significant.items() if p in cross})
        evidence = None
        if period:
            evidence = "count+stats" if count and count.get("period") == period else "length+stats"
        elif mode == "loose":
            strong = {
                p: t for p, t in significant.items()
                if t["split"] > PeriodicArrays.STATS_ONLY_SPLIT_HALF and end - start >= PeriodicArrays.STATS_ONLY_REPEATS * p
            }
            period = _choose_period(strong)
            evidence = "stats" if period else None
        if not period:
            continue
        if count:
            phase, phase_from = count["start"] % period, "count"
        elif tail:
            ends = full_lengths[(full_lengths > start) & (full_lengths <= maxlen)]
            shares = [float(np.mean(ends % period == q)) for q in range(period)] if len(ends) else [0.0] * period
            q = int(np.argmax(shares))
            phase, phase_from = (q, "ends") if shares[q] >= 0.9 else (start % period, "start")
        else:
            phase, phase_from = start % period, "start"
        first = start + ((phase - start) % period)
        last = maxlen if tail else end
        regions.append(ArrayRegion(
            start=int(start), end=int(end), period=int(period), phase=int(phase), evidence=evidence,
            phase_from=phase_from, tail=bool(tail),
            edges=[int(e) for e in range(first, last + 1, period) if start <= e <= last],
            stats={str(p): {k: round(v, 4) for k, v in t.items()} for p, t in tests.items()},
        ))
    return regions


def split_positions_at_arrays(positions: set[int], regions: Sequence[ArrayRegion]) -> set[int]:
    """Segment boundary positions with the array edges added inside the covered span.

    Edges beyond the last existing boundary are not added, so the family's field
    span (and its length handling) is unchanged.
    """
    if not regions or not positions:
        return set(positions)
    hi = max(positions)
    extra = {edge for region in regions for edge in region.edges if 0 < edge < hi}
    return set(positions) | extra
