"""Few-shot field boundaries: a learned boundary model adapted to a target protocol from a few labelled messages.

The analyst labels a few messages of the target capture (field boundaries in the truth-file convention); the
pipeline then

  1. scores every offset of every (family, exact length) group with a gradient-boosted classifier trained on
     the shipped multi-protocol training rows plus the labelled groups of the target;
  2. takes per-message edges at the threshold that best reproduces the labelled messages;
  3. carries the labelled edges over to every other message by byte alignment with its most similar labelled
     message (difflib matching blocks), keeping model edges where nothing aligns;
  4. applies the structural post-processors (length-prefixed strings / ASCII runs, embedded BER, CRC-16 blocks)
     that leave-one-out on the labelled messages favours;
  5. optionally splits each family by predicted layout (families mixing several message types), and after
     stage 07 rebuilds every family's fields from the majority of its messages' edges.

Feature rows are those of dol/boundary-recall-experiments/scripts/learned_boundaries_v2.py (copied verbatim so the
shipped training rows and the runtime rows agree). Experiments and validation: dol/accuracy-push (LOG.md).
"""
from __future__ import annotations

import difflib
import itertools
import math
import random
from collections import Counter, defaultdict
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import numpy as np

from protocol_re.config.thresholds import FewShotBoundaries as _FS
from protocol_re.inference.tlv import parse_ber_elements

MAXLEN = 256
CAP = 2000
STATS = ('H', 'distinct', 'top', 'zero', 'mean', 'ascii', 'Hhi', 'Hlo', 'lencorr')
NOISE = '__noise__'


# ---------------------------------------------------------------- feature rows (learned-v2, verbatim)

def to_matrix(msgs: Sequence[bytes]):
    lens = np.array([min(len(m), MAXLEN) for m in msgs])
    M = np.zeros((len(msgs), MAXLEN), dtype=np.uint8)
    for i, m in enumerate(msgs):
        M[i, :lens[i]] = np.frombuffer(m[:MAXLEN], dtype=np.uint8)
    full = np.array([len(m) for m in msgs], dtype=float)
    return M, lens, full


def _entropy(counts, total, bits):
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum() / bits)


def column_stats(M, lens, full):
    valid = np.arange(MAXLEN)[None, :] < lens[:, None]
    out = {name: np.zeros(MAXLEN) for name in STATS}
    out['cov'] = valid.mean(0)
    for j in range(MAXLEN):
        v = M[valid[:, j], j]
        if v.size == 0:
            continue
        c = np.bincount(v, minlength=256)
        out['H'][j] = _entropy(c, v.size, 8)
        out['distinct'][j] = min(1.0, (c > 0).sum() / min(v.size, 256))
        out['top'][j] = c.max() / v.size
        out['zero'][j] = c[0] / v.size
        out['mean'][j] = v.mean() / 255
        out['ascii'][j] = c[32:127].sum() / v.size
        out['Hhi'][j] = _entropy(np.bincount(v >> 4, minlength=16), v.size, 4)
        out['Hlo'][j] = _entropy(np.bincount(v & 15, minlength=16), v.size, 4)
        length = full[valid[:, j]]
        if v.std() > 0 and length.std() > 0:
            out['lencorr'][j] = abs(float(np.corrcoef(v, length)[0, 1]))
    return valid, out


def _pair_stats(M, valid, H, i):
    both = valid[:, i]
    a, b = M[both, i - 1], M[both, i]
    change = float((a != b).mean())
    joint = np.bincount(a.astype(np.int32) * 256 + b, minlength=65536)
    hj = _entropy(joint, a.size, 8)
    low = min(H[i - 1], H[i])
    nmi = min(1.0, max(0.0, H[i - 1] + H[i] - hj) / low) if low > 1e-6 else 0.0
    return change, nmi


def change_features(M, valid, i):
    """Co-variation of offsets i-1 and i over consecutive messages of a group (capture order), and NEMESYS-style bit
    congruence: bytes of one field tend to change together and look alike bit-wise; a field boundary separates
    independently changing parts (an 8-byte address changes as a whole, a counter's low byte alone)."""
    both = valid[:, i] & valid[:, i - 1]
    a, b = M[both, i - 1].astype(np.int32), M[both, i].astype(np.int32)
    if a.size < 3:
        return [0.0] * 8
    ca, cb = a[1:] != a[:-1], b[1:] != b[:-1]
    any_change = ca | cb
    together = float((ca & cb).sum() / any_change.sum()) if any_change.any() else 1.0
    only_left = float((ca & ~cb).mean()); only_right = float((~ca & cb).mean())
    pop = np.array([bin(x).count('1') for x in range(256)])
    bc = 1.0 - pop[a ^ b] / 8.0                       # bit congruence of the adjacent byte pair, per message
    prev = 1.0 - pop[M[both, i - 2] ^ M[both, i - 1]] / 8.0 if i >= 2 else bc
    c = valid[:, i - 1] & valid[:, i] & (valid[:, i + 1] if i + 1 < M.shape[1] else valid[:, i])
    nxt = 1.0 - pop[M[c, i] ^ M[c, i + 1]] / 8.0 if i + 1 < M.shape[1] and c.any() else bc
    return [together, only_left, only_right, float(any_change.mean()),
            float(bc.mean()), float(bc.mean() - prev.mean()), float(nxt.mean() - bc.mean()),
            float((nxt.mean() - bc.mean()) - (bc.mean() - prev.mean()))]


def family_rows(msgs: Sequence[bytes], corpus, body_start: Optional[int]):
    """Feature rows for the offsets 1.. of one group of messages; returns (rows, offsets)."""
    msgs = msgs[:CAP]
    n = len(msgs)
    M, lens, full = to_matrix(msgs)
    valid, st = column_stats(M, lens, full)
    cvalid, cst, cM = corpus
    med = float(np.median(full))
    distinct_lengths = len(set(full.tolist()))
    get = lambda arr, j: float(arr[j]) if 0 <= j < MAXLEN else 0.0  # noqa: E731
    rows, offs = [], []
    for i in range(1, int(lens.max())):
        if valid[:, i].sum() < max(3, 0.05 * n):
            break
        change, nmi = _pair_stats(M, valid, st['H'], i)
        cchange, cnmi = _pair_stats(cM, cvalid, cst['H'], i) if cvalid[:, i].sum() >= 3 else (0.0, 0.0)
        row = []
        for name in STATS:
            row += [get(st[name], j) for j in range(i - 3, i + 3)]
        for name in ('H', 'distinct', 'top', 'zero', 'Hhi', 'Hlo', 'lencorr'):
            row += [get(cst[name], j) for j in range(i - 2, i + 2)]
        row += [
            st['H'][i] - st['H'][i - 1], abs(st['H'][i] - st['H'][i - 1]),
            cst['H'][i] - cst['H'][i - 1], abs(cst['H'][i] - cst['H'][i - 1]),
            change, nmi, cchange, cnmi,
            st['cov'][i], get(st['cov'], i - 1) - st['cov'][i], st['cov'][i] - get(st['cov'], i + 1),
            cst['cov'][i], get(cst['cov'], i - 1) - cst['cov'][i],
            float(st['H'][i - 1] < 1e-9), float(st['H'][i] < 1e-9),
            float(cst['H'][i - 1] < 1e-9), float(cst['H'][i] < 1e-9),
            i % 2 == 0, i % 4 == 0, min(i, 64) / 64, i / max(med, 1), (med - i) / max(med, 1),
            float(body_start is not None), float(body_start is not None and i == body_start),
            float(body_start is not None and i > body_start),
            ((i - body_start) % 2 == 0) if body_start is not None else 0.0,
            min((i - body_start), 64) / 64 if body_start is not None and i >= body_start else -1.0,
            np.log2(n) / 15, min(distinct_lengths, 32) / 32, min(med, 512) / 512,
        ]
        if _FS.CHANGE_FEATURES:
            row += change_features(M, valid, i)
        rows.append(row)
        offs.append(i)
    return np.array(rows, dtype=float), offs


def corpus_stats(payloads_in_order: Sequence[bytes]):
    step = max(1, len(payloads_in_order) // 8000)
    cM, clens, cfull = to_matrix(list(payloads_in_order)[::step])
    cvalid, cst = column_stats(cM, clens, cfull)
    return cvalid, cst, cM


# ---------------------------------------------------------------- groups

def make_groups(order: Sequence[int], family_of: Dict[int, Optional[str]], payload: Dict[int, bytes],
                min_group: int = _FS.MIN_GROUP) -> List[Tuple[str, Optional[int], List[int]]]:
    """(family, exact length, message ids) groups; small lengths and noise form per-family remainder groups."""
    fams: Dict[str, List[int]] = defaultdict(list)
    for m in order:
        f = family_of.get(m)
        fams[NOISE if f in (None, 'noise') else str(f)].append(m)
    groups = []
    for fam, mids in fams.items():
        by: Dict[int, List[int]] = defaultdict(list)
        for m in mids:
            by[len(payload[m])].append(m)
        rest: List[int] = []
        for ln, g in sorted(by.items()):
            if len(g) >= min_group:
                groups.append((fam, ln, g))
            else:
                rest += g
        if rest:
            groups.append((fam, None, rest))
    return groups


def group_labels(mids: Sequence[int], offs: Sequence[int], labels: Dict[int, Sequence[int]],
                 payload: Dict[int, bytes]) -> Tuple[Optional[np.ndarray], np.ndarray]:
    """Majority labels of a group from its labelled messages, and which offsets any of them reaches."""
    a = [m for m in mids if m in labels]
    if not a:
        return None, np.zeros(len(offs), dtype=bool)
    c = Counter(e for m in a for e in labels[m])
    reach = Counter(o for m in a for o in range(1, len(payload[m])))
    y = np.array([c[o] >= 0.5 * max(1, reach[o]) for o in offs])
    return y, np.array([reach[o] > 0 for o in offs])


def build_rows(order, family_of, payload, body_start_of, labels):
    """Feature rows of every group (and labels where labelled messages exist)."""
    corpus = corpus_stats([payload[m] for m in order])
    out = []
    for fam, ln, mids in make_groups(order, family_of, payload):
        msgs = [payload[m] for m in mids[:_FS.GROUP_CAP]]
        X, offs = family_rows(msgs, corpus, None if fam == NOISE else body_start_of.get(fam))
        if not offs:
            continue
        y, reach = group_labels(mids, offs, labels, payload)
        out.append(dict(fam=fam, len=ln, mids=mids, X=X.astype(np.float32), offs=offs, y=y, reach=reach,
                        nann=sum(1 for m in mids if m in labels)))
    return out


# ---------------------------------------------------------------- training set (shipped rows)

def save_training_set(path, per_protocol: Dict[str, List[Dict[str, Any]]],
                      zs_thresholds: Optional[Dict[str, float]] = None) -> None:
    X, y, proto, weight = [], [], [], []
    names = sorted(per_protocol)
    for k, p in enumerate(names):
        gs = [g for g in per_protocol[p] if g['y'] is not None and g['nann']]
        tot = sum(g['nann'] * len(g['offs']) for g in gs)
        for g in gs:
            X.append(g['X']); y.append(g['y'])
            proto.append(np.full(len(g['offs']), k, dtype=np.int16))
            weight.append(np.full(len(g['offs']), g['nann'] / tot, dtype=np.float32))
    extra = {}
    if zs_thresholds:
        extra = {'zs_threshold_protocols': np.array(list(zs_thresholds)), 'zs_thresholds': np.array(list(zs_thresholds.values()))}
    np.savez_compressed(path, X=np.vstack(X).astype(np.float32), y=np.concatenate(y), proto=np.concatenate(proto),
                        weight=np.concatenate(weight), protocols=np.array(names), **extra)


def load_training_set(path, exclude: Iterable[str] = ()):
    d = np.load(path, allow_pickle=False)
    names = [str(x) for x in d['protocols']]
    keep_ids = [k for k, p in enumerate(names) if p not in set(exclude)]
    mask = np.isin(d['proto'], keep_ids)
    w = d['weight'][mask].astype(float)        # every protocol sums to 1
    return d['X'][mask], d['y'][mask], w * len(w) / w.sum(), len(keep_ids)


def hgb():
    from sklearn.ensemble import HistGradientBoostingClassifier
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, max_depth=5, l2_regularization=1.0,
                                          random_state=0)


# ---------------------------------------------------------------- structural post-processors

PRINT = set(range(0x20, 0x7f))


def lv_strings(b: bytes, min_len: int = 3):
    out, n, p = [], len(b), 0
    while p < n:
        hit = None
        for w in (4, 2, 1):
            if p + w >= n:
                continue
            for order in (('little', 'big') if w > 1 else ('little',)):
                k = int.from_bytes(b[p:p + w], order)
                if min_len <= k <= n - p - w and all(c in PRINT for c in b[p + w:p + w + k]):
                    if p + w + k < n and b[p + w + k] in PRINT and k < 64:
                        continue
                    hit = (p, p + w, p + w + k)
                    break
            if hit:
                break
        if hit:
            out.append(hit); p = hit[2]
        else:
            p += 1
    return out


def ascii_runs(b: bytes, min_len: int = 6):
    out, s = [], None
    for i, c in enumerate(b + b'\x00'):
        if c in PRINT:
            s = i if s is None else s
        else:
            if s is not None and i - s >= min_len:
                out.append((s, i))
            s = None
    return out


def post_strings(b: bytes, e: Set[int]) -> Set[int]:
    lv = lv_strings(b)
    e = {x for x in e if not any(vs < x < ve for _, vs, ve in lv)} | {x for ps, vs, ve in lv for x in (ps, vs, ve)}
    return {x for x in e if not any(s < x < t for s, t in ascii_runs(b))}


def embedded_ber(b: bytes, min_span: int = 64):
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
                    out.append((p, end, edges)); p = end
                    continue
        p += 1
    return out


def post_ber(b: bytes, e: Set[int]) -> Set[int]:
    for s, t, inner in embedded_ber(b):
        e = {x for x in e if not s < x < t} | {x for x in inner if s <= x <= t}
    return e


CRC_CATALOGUE = [('ARC', 0x8005, 0x0000, True, 0x0000), ('MODBUS', 0x8005, 0xFFFF, True, 0x0000),
                 ('USB', 0x8005, 0xFFFF, True, 0xFFFF), ('CCITT-FALSE', 0x1021, 0xFFFF, False, 0x0000),
                 ('XMODEM', 0x1021, 0x0000, False, 0x0000), ('KERMIT', 0x1021, 0x0000, True, 0x0000),
                 ('X25', 0x1021, 0xFFFF, True, 0xFFFF), ('DNP', 0x3D65, 0x0000, True, 0xFFFF),
                 ('EN13757', 0x3D65, 0x0000, False, 0xFFFF), ('BUYPASS', 0x8005, 0x0000, False, 0x0000),
                 ('DECT-X', 0x0589, 0x0000, False, 0x0000), ('GENIBUS', 0x1021, 0xFFFF, False, 0xFFFF)]


@lru_cache(maxsize=None)
def _crc_table(poly: int, reflected: bool):
    t = []
    for i in range(256):
        if reflected:
            c, p = i, int(f'{poly:016b}'[::-1], 2)
            for _ in range(8):
                c = (c >> 1) ^ p if c & 1 else c >> 1
        else:
            c = i << 8
            for _ in range(8):
                c = ((c << 1) ^ poly) & 0xFFFF if c & 0x8000 else (c << 1) & 0xFFFF
        t.append(c)
    return t


def crc16(data: bytes, spec) -> int:
    _, poly, init, refl, xorout = spec
    t = _crc_table(poly, refl)
    c = init
    for x in data:
        c = (c >> 8) ^ t[(c ^ x) & 0xFF] if refl else ((c << 8) & 0xFFFF) ^ t[((c >> 8) ^ x) & 0xFF]
    return c ^ xorout


def crc_layout(b: bytes, max_header: int = 32, blocks=(16, 8, 32, 64)):
    """(header, block size, spec, byte order) of a CRC-blocked frame with >= 2 verified CRCs, else None."""
    def ok(a, z, spec, order):
        return z + 2 <= len(b) and int.from_bytes(b[z:z + 2], order) == crc16(b[a:z], spec)
    for spec in CRC_CATALOGUE:
        for order in ('little', 'big'):
            for h in range(2, min(max_header, len(b) - 2)):
                if not ok(0, h, spec, order):
                    continue
                for k in blocks:
                    pos, n, good = h + 2, 1, True
                    while pos < len(b):
                        z = min(pos + k, len(b) - 2)
                        if z <= pos or not ok(pos, z, spec, order):
                            good = False
                            break
                        pos, n = z + 2, n + 1
                    if good and pos == len(b) and n >= 2:
                        return h, k, spec, order
                if len(b) == h + 2:
                    return None
    return None


def post_crc(b: bytes, e: Set[int]) -> Set[int]:
    lay = crc_layout(b)
    if not lay:
        return e
    h, k = lay[0], lay[1]
    edges, spans, pos = {h, h + 2}, [], h + 2
    while pos < len(b):
        z = min(pos + k, len(b) - 2)
        edges.update((pos, z, z + 2)); spans.append((pos, z)); pos = z + 2
    for s, t in spans:
        e = {x for x in e if not s < x < t}
    return {x for x in e if not any(t < x < t + 2 for s, t in spans)} | edges


POSTS = (('strings', post_strings), ('ber', post_ber), ('crc', post_crc))


# ---------------------------------------------------------------- alignment transfer

def transfer(a: bytes, ea: Iterable[int], b: bytes):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out, cov = set(), np.zeros(len(b) + 1, dtype=bool)
    ea = list(ea)
    for i, j, n in sm.get_matching_blocks():
        if n:
            cov[j:j + n + 1] = True
            out.update(j + (e - i) for e in ea if i <= e <= i + n)
    return out, cov


def neighbour(b: bytes, candidates: Sequence[int], payload: Dict[int, bytes]) -> int:
    cands = sorted(candidates, key=lambda m: abs(len(payload[m]) - len(b)))[:8]
    return max(cands, key=lambda m: difflib.SequenceMatcher(None, payload[m][:256], b[:256], autojunk=False).quick_ratio())


# ---------------------------------------------------------------- selection of messages to label

def select_messages(order: Sequence[int], family_of: Dict[int, Optional[str]], payload: Dict[int, bytes],
                    k: int, seed: int = 20261017) -> List[int]:
    """Messages to label: strata = (family, log2 length) visited round-robin by total bytes (where the edges are)."""
    rnd = random.Random(seed)
    strata: Dict[Tuple[str, int], List[int]] = defaultdict(list)
    for m in sorted(order):
        f = family_of.get(m)
        strata[(str(f), int(math.log2(max(2, len(payload[m])))))].append(m)
    pools = sorted(strata.values(), key=lambda x: -sum(len(payload[m]) for m in x))
    pools = [rnd.sample(x, len(x)) for x in pools]
    seen: List[int] = []
    r = 0
    while len(seen) < min(k, len(order)) and any(len(x) > r for x in pools):
        for x in pools:
            if len(x) > r and len(seen) < k:
                seen.append(x[r])
        r += 1
    return seen


# ---------------------------------------------------------------- prediction

def _f1(pred: Dict[int, Set[int]], labels: Dict[int, Sequence[int]], payload: Dict[int, bytes]) -> float:
    tp = fp = fn = 0
    for m, t in labels.items():
        n = len(payload[m])
        t = {x for x in t if 0 < x < n}
        e = {x for x in pred.get(m, ()) if 0 < x < n}
        tp += len(e & t); fp += len(e - t); fn += len(t - e)
    return 2 * tp / max(1, 2 * tp + fp + fn)


def predict_edges(order, family_of, payload, body_start_of, labels: Dict[int, Sequence[int]],
                  training_set, exclude=(), beta: float = _FS.BETA) -> Tuple[Dict[int, Set[int]], Dict[str, Any]]:
    """Per-message edges for every message (labelled messages keep their labels) and a summary."""
    groups = build_rows(order, family_of, payload, body_start_of, labels)
    X, y, w, n_protocols = load_training_set(training_set, exclude)
    hx = [g['X'][g['reach']] for g in groups if g['y'] is not None]
    hy = [g['y'][g['reach']] for g in groups if g['y'] is not None]
    if hx:
        hx, hy = np.vstack(hx), np.concatenate(hy)
        hw = np.full(len(hy), beta * w.sum() / max(1, n_protocols) / max(1, len(hy)))
        X, y, w = np.vstack([X, hx]), np.concatenate([y, hy]), np.concatenate([w, hw])
    model = hgb().fit(X, y, sample_weight=w)
    scores = [model.predict_proba(g['X'])[:, 1] for g in groups]

    def model_edges(t, mids):
        out = {}
        for g, q in zip(groups, scores):
            e = {o for o, s in zip(g['offs'], q) if s >= t}
            for m in g['mids']:
                if m in mids:
                    out[m] = set(e)
        return out

    seen = set(labels)
    unseen = [m for m in order if m not in seen]
    thresholds = np.round(np.arange(0.05, 0.71, 0.05), 2)
    t = float(max(thresholds, key=lambda t: _f1(model_edges(t, seen), labels, payload)))
    model_pred = model_edges(t, set(unseen))
    by_family: Dict[str, List[int]] = defaultdict(list)
    for m in seen:
        by_family[str(family_of.get(m))].append(m)

    def candidates(m, exclude_self=False):
        c = [x for x in by_family.get(str(family_of.get(m)), []) if not (exclude_self and x == m)]
        return c or [x for x in seen if not (exclude_self and x == m)]

    # post-processors chosen by leave-one-out transfer among the labelled messages
    loo = {}
    for s in seen:
        c = candidates(s, exclude_self=True)
        if c:
            a = neighbour(payload[s], c, payload)
            loo[s] = transfer(payload[a], labels[a], payload[s])[0]

    def with_posts(subset, preds):
        out = {}
        for m, e in preds.items():
            z = set(e)
            for i in subset:
                z = POSTS[i][1](payload[m], z)
            out[m] = z
        return out
    subsets = [c for r in range(len(POSTS) + 1) for c in itertools.combinations(range(len(POSTS)), r)]
    chosen = max(subsets, key=lambda c: _f1(with_posts(c, loo), {m: labels[m] for m in loo}, payload)) if loo else ()

    hybrid = {}
    for m in unseen:
        b = payload[m]
        a = neighbour(b, candidates(m), payload)
        e, cov = transfer(payload[a], labels[a], b)
        hybrid[m] = e | {x for x in model_pred.get(m, ()) if 0 < x < len(b) and not cov[x]}
    final = with_posts(chosen, hybrid)
    for m in seen:
        final[m] = {int(x) for x in labels[m]}
    summary = {'labelled_messages': len(seen), 'groups': len(groups), 'threshold': t,
               'posts': [POSTS[i][0] for i in chosen], 'training_protocols': n_protocols}
    return final, summary


# ---------------------------------------------------------------- family split by predicted layout

def root_start(b: bytes, max_start: int = 64) -> Optional[int]:
    for start in range(0, min(max_start, len(b) - 8)):
        el = parse_ber_elements(b, start)
        if not el:
            continue
        _t0, _v0, e0, c0 = el[0]
        if c0 and e0 == len(b) and sum(ve > vo for _t, vo, ve, _c in el) >= 3 and len({b[t] for t, _v, _e, _c in el}) >= 2:
            return start
    return None


def layout_agreement(pred: Dict[int, Set[int]], mids: Sequence[int], payload: Dict[int, bytes]) -> float:
    votes, reach = Counter(), Counter()
    for m in mids:
        n = len(payload[m]); votes.update(e for e in pred[m] if 0 < e < n); reach.update(range(1, n))
    maj = {e for e, c in votes.items() if c >= 0.5 * reach[e]}
    f = []
    for m in mids:
        n = len(payload[m]); a = {e for e in pred[m] if 0 < e < n}; b = {e for e in maj if e < n}
        f.append(1.0 if not a and not b else 2 * len(a & b) / max(1, len(a) + len(b)))
    return sum(f) / max(1, len(f))


def split_families(family_of: Dict[int, Optional[str]], pred: Dict[int, Set[int]], payload: Dict[int, bytes],
                   labels: Optional[Dict[int, Sequence[int]]] = None,
                   support: Optional[int] = None) -> Tuple[Dict[int, str], Dict[str, Any]]:
    """New family id per moved message: a family whose messages disagree on their layout (and is not BER-structured)
    is split by layout signature (edges below SIG_BYTES); a signature becomes a sub-family `<family>_L<k>` when it
    holds >= SPLIT_MIN_SHARE of the family (and >= SPLIT_MIN_SIZE messages), at most SPLIT_MAX per family.

    With ``labels``, the labelled messages decide whether a family really mixes layouts: it is split only when its
    labelled messages show >= SPLIT_LABELLED_LAYOUTS distinct layouts (each seen >= SPLIT_LABELLED_SUPPORT times),
    and only predicted signatures equal to one of those verified layouts become sub-families."""
    fams: Dict[str, List[int]] = defaultdict(list)
    for m, f in family_of.items():
        if f not in (None, 'noise'):
            fams[str(f)].append(m)
    moved, skipped, splits = {}, Counter(), 0
    unverified: List[str] = []
    for fam, rows in fams.items():
        sig = {m: tuple(sorted(e for e in pred[m] if 0 < e < min(len(payload[m]), _FS.SIG_BYTES))) for m in rows if m in pred}
        if not sig:
            continue
        if layout_agreement(pred, list(sig), payload) >= _FS.SPLIT_AGREE:
            skipped['homogeneous'] += 1
            continue
        sample = [payload[m] for m in list(sig)[:200]]
        if sum(root_start(b) is not None for b in sample) >= 0.6 * len(sample):
            skipped['ber'] += 1
            continue
        min_size = max(_FS.SPLIT_MIN_SIZE, int(_FS.SPLIT_MIN_SHARE * len(rows)))
        verified = None
        if labels is not None:
            lab = Counter(tuple(sorted(e for e in labels[m] if 0 < e < min(len(payload[m]), _FS.SIG_BYTES)))
                          for m in rows if m in labels)
            verified = {s for s, c in lab.items() if c >= (support or _FS.SPLIT_LABELLED_SUPPORT)}
            if len(verified) < _FS.SPLIT_LABELLED_LAYOUTS:
                skipped['labels_show_one_layout'] += 1
                unverified.append(fam)        # mixed layouts the labels cannot resolve: gate instead of rebuild
                continue
        keep = [s for s, c in Counter(sig.values()).most_common(_FS.SPLIT_MAX)
                if c >= min_size and (verified is None or s in verified)]
        if len(keep) <= 1:
            continue
        label = {s: f'{fam}_L{k}' for k, s in enumerate(keep)}
        for m, s in sig.items():
            if s in label:
                moved[m] = label[s]
        splits += len(keep)
    return moved, {'moved_messages': len(moved), 'sub_families': splits, 'skipped': dict(skipped),
                   'unverified_families': sorted(unverified)}


# ---------------------------------------------------------------- rebuild family fields from predictions

def rebuild_fields(details: Dict[str, Any], edges: Sequence[int], end_hint: int) -> Tuple[Dict[str, Any], int]:
    """Fields at the given cut points; stage-07 records kept where a field is unchanged or split, `blob` where
    differently typed fields merge."""
    hyps = sorted(details.get('field_hypotheses', []) or [], key=lambda h: int(h.get('start', 0) or 0))
    if not hyps:
        return details, 0
    end = max(end_hint, max(int(h['start']) + int(h['length']) for h in hyps))
    cuts = sorted({0, end, *[e for e in edges if 0 < e < end]})
    old = [(int(h['start']), int(h['start']) + int(h['length']), h) for h in hyps]
    fam_id = hyps[0].get('family_id')
    new = []
    for a, b in zip(cuts, cuts[1:]):
        over = [(s, e, h) for s, e, h in old if s < b and e > a]
        same = [h for s, e, h in over if (s, e) == (a, b)]
        if same:
            new.append(same[0]); continue
        if len(over) == 1 or (over and len({h.get('field_type') for _, _, h in over}) == 1):
            piece = dict(over[0][2], start=a, length=b - a)
        else:
            piece = {'family_id': fam_id, 'start': a, 'length': b - a, 'field_type': 'blob', 'confidence': 0.5,
                     'endian': None, 'evidence': {}, 'attributes': {}}
        piece['attributes'] = dict(piece.get('attributes') or {}, fewshot_edges=True)
        new.append(piece)
    changed = len({(int(h['start']), int(h['length'])) for h in new} ^ {(s, e - s) for s, e, _ in old})
    return dict(details, field_hypotheses=new), changed


def apply_to_families(families: Dict[str, Any], family_of: Dict[int, Optional[str]], pred: Dict[int, Set[int]],
                      payload_len: Dict[int, int]) -> Dict[str, Any]:
    """Replace every family's fields with the majority of its messages' predicted edges (in place). Families with
    TLV-tagged element fields keep that chain (matched by tag downstream); only the prefix before it is rebuilt."""
    votes, reach, lengths = defaultdict(Counter), defaultdict(Counter), defaultdict(list)
    for m, edges in pred.items():
        fam, n = family_of.get(m), payload_len.get(m)
        if fam is None or n is None:
            continue
        votes[fam].update(e for e in edges if 0 < e < n); reach[fam].update(range(1, n)); lengths[fam].append(n)
    # fields end at the family's median length: a few long outliers must not add a tail most messages never reach
    maxlen = {fam: int(np.median(ls)) for fam, ls in lengths.items()}
    touched = changed = kept_tlv = 0
    for fam, det in families.items():
        if fam not in votes or not isinstance(det, dict):
            continue
        edges = sorted(e for e, c in votes[fam].items() if c >= 0.5 * reach[fam][e])
        hyps = sorted(det.get('field_hypotheses', []) or [], key=lambda h: int(h.get('start', 0) or 0))
        tagged = [h for h in hyps if (h.get('attributes') or {}).get('tlv_tag') is not None
                  or (h.get('attributes') or {}).get('tlv_tag_hex') is not None]
        if tagged:
            s0 = int(tagged[0]['start'])
            prefix = dict(det, field_hypotheses=[h for h in hyps if int(h['start']) + int(h['length']) <= s0])
            rebuilt, k = rebuild_fields(prefix, [e for e in edges if e < s0], s0) if prefix['field_hypotheses'] else (prefix, 0)
            families[fam] = dict(det, field_hypotheses=rebuilt['field_hypotheses']
                                 + [h for h in hyps if int(h['start']) + int(h['length']) > s0])
            kept_tlv += 1
        else:
            families[fam], k = rebuild_fields(det, edges, maxlen[fam])
        changed += k; touched += 1
    return {'families_rebuilt': touched, 'tlv_chains_kept': kept_tlv, 'field_changes': changed}


# ---------------------------------------------------------------- zero-shot mode (no labels)

TH_GRID = tuple(np.round(np.arange(0.05, 0.71, 0.05), 2))


def zeroshot_thresholds(per_protocol: Dict[str, List[Dict[str, Any]]]) -> Dict[str, float]:
    """Leave-one-protocol-out threshold choice for zero-shot use: for every protocol p, the threshold that maximises
    the mean (over the other protocols q) of q's offset-level F1 under a model trained without q; key '*' is the
    choice over all protocols (for captures of unknown protocols)."""
    names = sorted(per_protocol)
    f1 = {}
    for q in names:
        tmp = {p: per_protocol[p] for p in names if p != q}
        X, y, w = _stack_rows(tmp)
        model = hgb().fit(X, y, sample_weight=w)
        gs = [g for g in per_protocol[q] if g['y'] is not None and g['nann']]
        tp = np.zeros(len(TH_GRID)); fp = np.zeros(len(TH_GRID)); fn = np.zeros(len(TH_GRID))
        for g in gs:
            s = model.predict_proba(g['X'])[:, 1]
            for k, t in enumerate(TH_GRID):
                pr = s >= t
                tp[k] += g['nann'] * (pr & g['y']).sum(); fp[k] += g['nann'] * (pr & ~g['y']).sum(); fn[k] += g['nann'] * (~pr & g['y']).sum()
        f1[q] = 2 * tp / np.maximum(1, 2 * tp + fp + fn)
    out = {p: float(TH_GRID[int(np.argmax(np.mean([f1[q] for q in names if q != p], axis=0)))]) for p in names}
    out['*'] = float(TH_GRID[int(np.argmax(np.mean([f1[q] for q in names], axis=0)))])
    return out


def _stack_rows(per_protocol):
    X, y, w = [], [], []
    for p, groups in per_protocol.items():
        gs = [g for g in groups if g['y'] is not None and g['nann']]
        tot = sum(g['nann'] * len(g['offs']) for g in gs)
        for g in gs:
            X.append(g['X']); y.append(g['y']); w.append(np.full(len(g['offs']), g['nann'] / tot))
    w = np.concatenate(w)
    return np.vstack(X), np.concatenate(y), w * len(w) / w.sum()


def load_zeroshot_threshold(path, exclude: Iterable[str] = ()) -> float:
    d = np.load(path, allow_pickle=False)
    names = [str(x) for x in d['zs_threshold_protocols']]
    values = [float(x) for x in d['zs_thresholds']]
    table = dict(zip(names, values))
    excl = [p for p in exclude if p in table]
    return table[excl[0]] if excl else table['*']


def save_reference_messages(path, per_protocol_messages: Dict[str, List[Tuple[bytes, Sequence[int]]]]) -> None:
    import gzip
    import json
    with gzip.open(path, 'wt', encoding='utf-8') as fh:
        for p, rows in sorted(per_protocol_messages.items()):
            for b, edges in rows:
                fh.write(json.dumps({'protocol': p, 'payload_hex': b.hex(), 'boundaries': [int(e) for e in edges]}) + '\n')


def load_reference_messages(path, exclude: Iterable[str] = ()):
    import gzip
    import json
    excl = set(exclude)
    out = []
    with gzip.open(path, 'rt', encoding='utf-8') as fh:
        for line in fh:
            r = json.loads(line)
            if r['protocol'] not in excl:
                out.append((r['protocol'], bytes.fromhex(r['payload_hex']), r['boundaries']))
    return out


def shared_layer_edges(b: bytes, reference, min_block: int = _FS.SHARED_MIN_BLOCK, min_ratio: float = _FS.SHARED_MIN_RATIO):
    """Edges carried over from the most similar reference message of a known protocol, inside matching blocks of
    >= min_block bytes (a shared lower layer such as TPKT/COTP or an EtherNet/IP encapsulation), and the mask of the
    positions those blocks cover. Nothing when the best similarity is below min_ratio."""
    best = (0.0, None)
    sm = difflib.SequenceMatcher(None, autojunk=False)
    sm.set_seq2(b[:128])
    for k, (_p, a, _e) in enumerate(reference):
        sm.set_seq1(a[:128])
        if sm.real_quick_ratio() <= best[0] or sm.quick_ratio() <= best[0]:
            continue
        r = sm.ratio()
        if r > best[0]:
            best = (r, k)
    cov = np.zeros(len(b) + 1, dtype=bool)
    if best[1] is None or best[0] < min_ratio:
        return set(), cov, None
    _p, a, ea = reference[best[1]]
    out = set()
    for i, j, n in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        if n >= min_block:
            cov[j + 1:j + n] = True
            out.update(j + (e - i) for e in ea if i < e < i + n)
    return out, cov, _p


def predict_edges_zeroshot(order, family_of, payload, body_start_of, training_set, exclude=(),
                           posts: Sequence[str] = ('strings', 'ber', 'crc'), reference=None
                           ) -> Tuple[Dict[int, Set[int]], Dict[str, Any]]:
    """Per-message edges without labels: the generic model trained on all shipped protocols, at the threshold chosen
    leave-one-protocol-out, then the label-free structural post-processors; optionally edges carried over from
    known protocols that share a lower layer (reference messages)."""
    groups = build_rows(order, family_of, payload, body_start_of, {})
    X, y, w, n_protocols = load_training_set(training_set, exclude)
    model = hgb().fit(X, y, sample_weight=w)
    t = load_zeroshot_threshold(training_set, exclude)
    pred: Dict[int, Set[int]] = {}
    donors: Counter = Counter()
    prob_sum: Dict[str, Counter] = defaultdict(Counter)
    prob_n: Dict[str, Counter] = defaultdict(Counter)
    for g in groups:
        s = model.predict_proba(g['X'])[:, 1]
        e = {o for o, v in zip(g['offs'], s) if v >= t}
        for o, v in zip(g['offs'], s):
            prob_sum[g['fam']][o] += float(v); prob_n[g['fam']][o] += 1
        shared = None
        if reference:
            rep = g['mids'][0]
            ce, cov, donor = shared_layer_edges(payload[rep], reference)
            if cov.any():
                shared = (len(payload[rep]), ce, cov)
                donors[donor] += 1
        for m in g['mids']:
            em = set(e)
            if shared and len(payload[m]) == shared[0]:
                em = {x for x in em if not (x < len(shared[2]) and shared[2][x])} | {x for x in shared[1] if x < len(payload[m])}
            pred[m] = em
    funcs = dict(POSTS)
    for m in pred:
        for name in posts:
            pred[m] = funcs[name](payload[m], pred[m])
    family_probability = {fam: {o: prob_sum[fam][o] / prob_n[fam][o] for o in prob_sum[fam]} for fam in prob_sum if fam != NOISE}
    return pred, {'mode': 'zeroshot', 'groups': len(groups), 'threshold': t, 'posts': list(posts),
                  'training_protocols': n_protocols, 'shared_layer_donors': dict(donors),
                  'family_probability': family_probability}


def veto_unlikely_edges(hyps: List[Dict[str, Any]], probability: Dict[int, float],
                        threshold: float = _FS.ZEROSHOT_VETO) -> Tuple[List[Dict[str, Any]], int]:
    """Merge away stage-07 edges the zero-shot model considers very unlikely (family-mean probability < threshold),
    except the edges of fields stage 07 identified with confidence (length / keyword / opcode, confidence >= 0.9)."""
    keep = set()
    for h in hyps:
        if h.get('field_type') in ('length', 'keyword', 'opcode') and float(h.get('confidence', 0) or 0) >= 0.9:
            keep.update((int(h['start']), int(h['start']) + int(h['length'])))
    merged, vetoed = [dict(hyps[0])], 0
    for h in hyps[1:]:
        e = int(h['start']); pv = probability.get(e)
        if e not in keep and pv is not None and pv < threshold:
            last = merged[-1]
            last['length'] = int(h['start']) + int(h['length']) - int(last['start'])
            last['field_type'] = 'blob'
            last['attributes'] = dict(last.get('attributes') or {}, zeroshot_veto=True)
            vetoed += 1
        else:
            merged.append(dict(h))
    return merged, vetoed


def apply_gated(families: Dict[str, Any], family_of: Dict[int, Optional[str]], pred: Dict[int, Set[int]],
                payload_len: Dict[int, int], min_width: int = 3,
                family_probability: Optional[Dict[str, Dict[int, float]]] = None) -> Dict[str, Any]:
    """Zero-shot combination with stage 07 (in place): stage-07 fields and edges are kept; the family-majority
    predicted edges only split stage-07 fields of >= min_width bytes and add fields past the last stage-07 field
    (up to the family's median length). TLV-tagged chains are left alone. With the model's family-mean edge
    probabilities, stage-07 edges it considers very unlikely are first merged away (veto_unlikely_edges)."""
    votes, reach, lengths = defaultdict(Counter), defaultdict(Counter), defaultdict(list)
    for m, edges in pred.items():
        fam, n = family_of.get(m), payload_len.get(m)
        if fam is None or n is None:
            continue
        votes[fam].update(e for e in edges if 0 < e < n); reach[fam].update(range(1, n)); lengths[fam].append(n)
    touched = added = vetoed = 0
    for fam, det in families.items():
        if fam not in votes or not isinstance(det, dict):
            continue
        hyps = sorted(det.get('field_hypotheses', []) or [], key=lambda h: int(h.get('start', 0) or 0))
        if not hyps or any((h.get('attributes') or {}).get('tlv_tag') is not None for h in hyps):
            continue
        if family_probability and str(fam) in family_probability:
            hyps, n_vetoed = veto_unlikely_edges(hyps, {int(k): float(v) for k, v in family_probability[str(fam)].items()})
            vetoed += n_vetoed
        edges = sorted(e for e, c in votes[fam].items() if c >= 0.5 * reach[fam][e])
        end07 = max(int(h['start']) + int(h['length']) for h in hyps)
        median = int(np.median(lengths[fam]))
        out = []
        for h in hyps:
            a, b = int(h['start']), int(h['start']) + int(h['length'])
            cuts = [e for e in edges if a < e < b] if b - a >= min_width else []
            if not cuts:
                out.append(h); continue
            for lo, hi in zip([a] + cuts, cuts + [b]):
                out.append(dict(h, start=lo, length=hi - lo, attributes=dict(h.get('attributes') or {}, zeroshot_split=True)))
            added += len(cuts)
        if median > end07:
            tail = [end07] + [e for e in edges if end07 < e < median] + [median]
            for lo, hi in zip(tail, tail[1:]):
                out.append({'family_id': hyps[0].get('family_id'), 'start': lo, 'length': hi - lo, 'field_type': 'blob',
                            'confidence': 0.5, 'endian': None, 'evidence': {}, 'attributes': {'zeroshot_tail': True}})
            added += len(tail) - 2
        families[fam] = dict(det, field_hypotheses=out)
        touched += 1
    return {'families_gated': touched, 'edges_added': added, 'edges_vetoed': vetoed}
