"""Per-message post-processing rules (label-free) applied on top of predicted edges."""

PRINT = set(range(0x20, 0x7f))


def lv_strings(b, min_len=3):
    """Length-prefixed printable strings: (prefix_start, value_start, value_end). Greedy left to right."""
    out = []
    n = len(b)
    p = 0
    while p < n:
        hit = None
        for w in (4, 2, 1):
            if p + w >= n:
                continue
            for order in ('little', 'big') if w > 1 else ('little',):
                k = int.from_bytes(b[p:p + w], order)
                if min_len <= k <= n - p - w and all(c in PRINT for c in b[p + w:p + w + k]):
                    # the byte after the string must not continue the printable run (exact length)
                    if p + w + k < n and b[p + w + k] in PRINT and k < 64:
                        continue
                    hit = (p, p + w, p + w + k)
                    break
            if hit:
                break
        if hit:
            out.append(hit)
            p = hit[2]
        else:
            p += 1
    return out


def ascii_runs(b, min_len=6):
    out, s = [], None
    for i, c in enumerate(b + b'\x00'):
        if c in PRINT:
            s = i if s is None else s
        else:
            if s is not None and i - s >= min_len:
                out.append((s, i))
            s = None
    return out


def apply_strings(b, edges, lv=True, runs=True, add_bounds=True):
    e = set(edges)
    if lv:
        for ps, vs, ve in lv_strings(b):
            e = {x for x in e if not vs < x < ve}
            if add_bounds:
                e.update((ps, vs, ve))
    if runs:
        for s, t in ascii_runs(b):
            e = {x for x in e if not s < x < t}
    return e


def string_plan(b):
    """Threshold-independent string plan for one message: (LV interiors, LV bounds, ASCII-run interiors)."""
    lv = lv_strings(b)
    return [(vs, ve) for _, vs, ve in lv], {x for ps, vs, ve in lv for x in (ps, vs, ve)}, ascii_runs(b)


def apply_plan(edges, plan):
    """Same result as apply_strings(b, edges) with the default arguments."""
    lv_in, lv_add, runs = plan
    e = {x for x in edges if not any(s < x < t for s, t in lv_in)} | lv_add
    return {x for x in e if not any(s < x < t for s, t in runs)}


def embedded_ber(b, min_span=64):
    """Embedded DER/BER structures: constructed elements with a long-form length (0x81-0x84) that span
    >= min_span bytes and whose content parses exactly as BER. Returns [(start, end, edges)]."""
    import sys as _s
    _s.path.insert(0, '/mnt/d/tez/practical/protocol_re/src')
    from protocol_re.inference.tlv import parse_ber_elements
    out, p, n = [], 0, len(b)
    while p < n - 4:
        if b[p] & 0x20 and 0x81 <= b[p + 1] <= 0x84:
            k = b[p + 1] - 0x80
            ln = int.from_bytes(b[p + 2:p + 2 + k], 'big')
            end = p + 2 + k + ln
            if ln >= min_span and end <= n:
                el = parse_ber_elements(b[:end], p)
                if el and el[0][2] == end:
                    edges = set()
                    for t, vo, ve, constructed in el:
                        edges.add(t)
                        if not constructed and ve > vo:
                            edges.add(vo)
                        edges.add(ve)
                    out.append((p, end, edges))
                    p = end
                    continue
        p += 1
    return out


def apply_ber(b, edges):
    e = set(edges)
    for s, t, inner in embedded_ber(b):
        e = {x for x in e if not s < x < t} | {x for x in inner if s <= x <= t}
    return e
