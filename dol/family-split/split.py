"""Second-level family split selected by request/response determinism (zero-shot, label-free).

For every family with >= 2*MIN messages, candidate keys are (offset < 48, width 1/2) byte positions with 2..32
frequent values (>= max(MIN, 5%) of the family each) and no value above 95%. A key is scored by
  determinism  I(key; partner family) / H(partner family) over the family's request/response pairs (needs pairs for
               >= 30% of the family and more than one partner family), else
  length       share of the message-length variance the key explains (eta^2).
The best key splits the family when its score reaches T_DET (determinism) or T_LEN (length): every frequent value
becomes a family, rare values stay with the largest part. One level (no recursion).
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Dict, List, Optional

import numpy as np

MIN = 20


def _H(c: Counter) -> float:
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values() if v) if n else 0.0


def _key(b: bytes, o: int, w: int):
    return b[o:o + w] if len(b) >= o + w else None


def choose_key(mids: List[int], payload: Dict[int, bytes], family_of: Dict[int, Optional[str]], partner: Dict[int, int]):
    med = int(np.median([len(payload[m]) for m in mids]))
    pairs = [(m, partner[m]) for m in mids if m in partner]
    use_det = len(pairs) >= 0.3 * len(mids) and _H(Counter(family_of.get(b) for _, b in pairs)) > 0
    L = np.array([len(payload[m]) for m in mids], float)
    best = None
    for o in range(0, min(48, med)):
        for w in (1, 2):
            keys = [_key(payload[m], o, w) for m in mids]
            c = Counter(k for k in keys if k is not None)
            if sum(c.values()) < 0.9 * len(mids):
                continue
            big = [v for v, k in c.items() if k >= max(MIN, 0.05 * len(mids))]
            if not 2 <= len(big) <= 32 or c.most_common(1)[0][1] >= 0.95 * sum(c.values()):
                continue
            if use_det:
                pf = [(_key(payload[a], o, w), family_of.get(b)) for a, b in pairs]
                hp = _H(Counter(x[1] for x in pf))
                g = defaultdict(Counter)
                for k, f in pf:
                    g[k][f] += 1
                score = (hp - sum(sum(v.values()) * _H(v) for v in g.values()) / len(pf)) / hp
                kind = "determinism"
            else:
                if L.var() == 0:
                    continue
                gm = defaultdict(list)
                for k, l in zip(keys, L):
                    gm[k].append(l)
                score = sum(len(v) * (np.mean(v) - L.mean()) ** 2 for v in gm.values()) / (len(L) * L.var())
                kind = "length"
            if best is None or score > best[0]:
                best = (score, kind, o, w, set(big))
    return best


def split_families(order: List[int], payload: Dict[int, bytes], family_of: Dict[int, Optional[str]],
                   partner: Dict[int, int], t_det: float = 0.5, t_len: float = 0.5):
    fams: Dict[str, List[int]] = defaultdict(list)
    for m in order:
        f = family_of.get(m)
        if f not in (None, "noise"):
            fams[str(f)].append(m)
    new = dict(family_of)
    log = []
    for f, mids in fams.items():
        if len(mids) < 2 * MIN:
            continue
        best = choose_key(mids, payload, family_of, partner)
        if best is None:
            continue
        score, kind, o, w, big = best
        if score < (t_det if kind == "determinism" else t_len):
            continue
        groups = defaultdict(list)
        for m in mids:
            k = _key(payload[m], o, w)
            groups[k if k in big else None].append(m)
        largest = max((k for k in groups if k is not None), key=lambda k: len(groups[k]))
        groups[largest] += groups.pop(None, [])
        for k, ms in groups.items():
            name = f if k == largest else f"{f}_s{o}x{k.hex()}"
            for m in ms:
                new[m] = name
        log.append(dict(family=f, kind=kind, score=round(float(score), 3), offset=o, width=w, parts=len(groups)))
    return new, log
