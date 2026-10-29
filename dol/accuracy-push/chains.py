"""Length-prefixed chains (BinaryInferno-style pattern search, label-free).

A format is (tag_width, len_width, byte order, start offset): from `start`, every element is
[tag (tag_width bytes)] [length (len_width bytes)] [value (length bytes)], repeated until the end.
A message parses if the chain ends exactly at the message end (at most `slack` trailing bytes) with
>= MIN_ELEMS elements. A format is accepted for a group if >= ACCEPT of its messages parse, the
lengths are not all equal (otherwise it is a fixed layout), and >= 2 elements have non-empty values.
Element edges per message: tag start, length start, value start (convention chosen elsewhere).
"""
from collections import Counter

MIN_ELEMS = 2
ACCEPT = 0.9
FORMATS = [(t, l, o) for t in (0, 1, 2) for l in (1, 2, 4) for o in ('<', '>') if not (l == 1 and o == '>')]


def parse(b, start, fmt, slack=0, max_elems=512):
    t, l, o = fmt
    pos, elems = start, []
    n = len(b)
    while pos < n - slack:
        if pos + t + l > n:
            return None
        ln = int.from_bytes(b[pos + t:pos + t + l], 'little' if o == '<' else 'big')
        if l == 4 and ln == 0xFFFFFFFF:      # OPC UA style null (-1)
            ln = 0
        vs = pos + t + l
        if vs + ln > n:
            return None
        elems.append((pos, pos + t, vs, vs + ln))
        pos = vs + ln
        if len(elems) > max_elems:
            return None
    if n - pos > slack or len(elems) < MIN_ELEMS:
        return None
    return elems


def find_format(payloads, max_start=48, slack=0):
    """Best accepted (format, start) for a list of payloads, or None. Prefers the earliest start,
    then the format explaining the most bytes as values."""
    sample = payloads[:400]
    best = None
    for start in range(0, max_start):
        for fmt in FORMATS:
            ok, val_bytes, lens = 0, 0, Counter()
            for b in sample:
                el = parse(b, start, fmt, slack)
                if el is None:
                    continue
                ok += 1
                val_bytes += sum(e - v for _, _, v, e in el)
                lens.update(e - v for _, _, v, e in el)
            if ok < ACCEPT * len(sample) or len(lens) < 2 or sum(1 for k in lens if k > 0) < 1:
                continue
            nonempty = sum(c for k, c in lens.items() if k > 0)
            if nonempty < 2 * ok * 0.5:
                continue
            score = val_bytes / max(1, sum(len(b) - start for b in sample))
            if best is None or score > best[2] + 1e-9:
                best = (fmt, start, score)
        if best is not None:
            return best
    return None


def chain_edges(b, start, fmt, convention=('tag', 'len', 'val')):
    el = parse(b, start, fmt)
    if el is None:
        return None
    out = set()
    for ts, ls, vs, ve in el:
        if 'tag' in convention:
            out.add(ts)
        if 'len' in convention and ls != ts:
            out.add(ls)
        if 'val' in convention and vs != ve:
            out.add(vs)
        out.add(ve)
    return out
