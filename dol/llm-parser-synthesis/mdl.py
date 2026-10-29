"""Label-free description length (bits) of a family's messages under a segmentation (ideas 2/3).

A segmentation gives, per message, a list of segments (key, start, end); segments with the same key are one field
observed across messages (key = DSL path for synthesised parsers, start offset for fixed field lists). Each field is
charged a structural cost plus the cheapest of several codes for its values:
  constant | dictionary (entries + entropy) | raw bytes | delta-coded integer (either byte order; counters,
  timestamps, process values) | derived length (value = total / remaining / following-segment length + c).
Bytes no segment covers cost 8 bits each, messages the parser rejects cost their raw size plus a penalty.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

FIELD_COST = 24.0       # bits per field (its type, width and code choice)
FAIL_COST = 32.0        # bits per rejected message on top of its raw bytes
TAIL_COST = 8.0         # bits per message with uncovered trailing bytes


def _H(c: Counter, n: int) -> float:
    return -sum(v * math.log2(v / n) for v in c.values())


def _delta_bits(vals: Sequence[int]) -> float:
    out = 0.0
    for a, b in zip(vals, vals[1:]):
        out += 2 * math.log2(abs(b - a) + 1) + 1
    return out


def field_bits(values: List[bytes], derived: bool = False, size_known: bool = True) -> Tuple[float, str]:
    n = len(values)
    if n == 0:
        return 0.0, "empty"
    lens = {len(v) for v in values}
    fixed = len(lens) == 1
    avg = sum(len(v) for v in values) / n
    c = Counter(values)
    width_bits = 0.0 if (fixed or size_known) else n * math.log2(max(lens) + 1)
    options = {"raw": 8.0 * sum(len(v) for v in values) + width_bits,
               "dict": len(c) * (8.0 * avg + 2) + _H(c, n) + width_bits}
    if len(c) == 1:
        options["const"] = 8.0 * avg
    if fixed and 0 < avg <= 8:
        for order in ("big", "little"):
            ints = [int.from_bytes(v, order) for v in values]
            options["delta_" + order[0]] = 8.0 * avg + _delta_bits(ints)
    if derived:
        options["derived"] = 8.0 + 0.0 * n
    best = min(options, key=options.get)
    return options[best], best


def length_check(values: List[bytes], totals: List[int], ends: List[int], following: List[Optional[int]]) -> bool:
    """value (either order) == total length - c, remaining bytes after the field - c, or the next segment's length - c,
    for one constant c (|c| <= 8) in >= 98% of the messages."""
    if not values or len({len(v) for v in values}) != 1 or len(values[0]) > 4 or len(values) < 3:
        return False
    for order in ("big", "little"):
        ints = [int.from_bytes(v, order) for v in values]
        for ref in (totals, [t - e for t, e in zip(totals, ends)], following):
            diffs = Counter(r - v for r, v in zip(ref, ints) if r is not None)
            if diffs:
                d, k = diffs.most_common(1)[0]
                if abs(d) <= 8 and k >= 0.98 * len(values) and len(set(ints)) > 1:
                    return True
    return False


def score(payloads: List[bytes], segs: List[Optional[List[Tuple[str, int, int]]]], derived_keys=frozenset(),
          detail: bool = False):
    """segs[i] = list of (key, start, end) for message i, or None when the parser rejects it."""
    vals: Dict[str, List[bytes]] = defaultdict(list)
    meta: Dict[str, Tuple[List[int], List[int], List[Optional[int]]]] = defaultdict(lambda: ([], [], []))
    var_keys = set()
    bits = 0.0
    for b, ss in zip(payloads, segs):
        if ss is None:
            bits += 8.0 * len(b) + FAIL_COST
            continue
        cover = 0
        ss = sorted(ss, key=lambda x: x[1])
        for j, (k, s, e) in enumerate(ss):
            vals[k].append(b[s:e])
            t, en, fo = meta[k]
            t.append(len(b)); en.append(e); fo.append(ss[j + 1][2] - ss[j + 1][1] if j + 1 < len(ss) else None)
            cover = max(cover, e)
        if cover < len(b):
            bits += 8.0 * (len(b) - cover) + TAIL_COST
    codes = {}
    for k, v in vals.items():
        derived = k in derived_keys or length_check(v, *meta[k])
        fb, code = field_bits(v, derived=derived, size_known=True)
        bits += FIELD_COST + fb
        codes[k] = code
    return (bits, codes) if detail else bits


def edges_to_segs(payloads: List[bytes], edges: List[Sequence[int]]):
    """Fixed-offset segmentation (key = start offset) from per-message edge lists."""
    out = []
    for b, e in zip(payloads, edges):
        pts = sorted({0, len(b)} | {x for x in e if 0 < x < len(b)})
        out.append([(f"@{s}", s, t) for s, t in zip(pts, pts[1:])])
    return out
