"""Merge families that are one message type (zero-shot, label-free), 2026-10-29.

The oracle diagnostic (dol/oracle-ceilings, content pairing) showed that types spread over several families cost more
than types merged into one: fixing splits alone is worth +0.030 (zero-shot), fixing merges alone nothing.

Two families A, B (each >= MIN messages, same majority direction) are merged when no offset o < K "conflicts":
a conflict is an offset where A is (nearly) constant, B is (nearly) constant, and the two constants differ, i.e. a
byte that behaves like a type code. Bytes that vary inside a family (sequence numbers, invoke ids, control bits,
lengths) never block a merge. Offsets beyond the shorter family's median length are not compared. Merging is
transitive (union-find), but a merged group must stay conflict-free with every member (checked pairwise).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Optional

K = 32
MIN = 20
CONST = 0.95      # a family is "constant" at an offset when one value covers >= 95% of its messages


def _profile(mids: List[int], payload: Dict[int, bytes]):
    lens = sorted(len(payload[m]) for m in mids)
    med = lens[len(lens) // 2]
    const = {}
    for o in range(min(K, med)):
        c = Counter(payload[m][o] for m in mids if len(payload[m]) > o)
        v, k = c.most_common(1)[0]
        if k >= CONST * sum(c.values()):
            const[o] = v
    return med, const


def _conflict(pa, pb) -> bool:
    (ma, ca), (mb, cb) = pa, pb
    for o in range(min(K, ma, mb)):
        if o in ca and o in cb and ca[o] != cb[o]:
            return True
    return False


def merge_families(order: List[int], payload: Dict[int, bytes], family_of: Dict[int, Optional[str]],
                   direction: Dict[int, str]):
    fams: Dict[str, List[int]] = defaultdict(list)
    for m in order:
        f = family_of.get(m)
        if f not in (None, "noise"):
            fams[str(f)].append(m)
    names = [f for f, ms in fams.items() if len(ms) >= MIN]
    prof = {f: _profile(fams[f], payload) for f in names}
    dirn = {f: Counter(direction.get(m, "") for m in fams[f]).most_common(1)[0][0] for f in names}
    # greedy agglomeration, largest families first; a family joins a group only if conflict-free with every member
    groups: List[List[str]] = []
    for f in sorted(names, key=lambda x: -len(fams[x])):
        for g in groups:
            if dirn[g[0]] == dirn[f] and not any(_conflict(prof[f], prof[h]) for h in g):
                g.append(f)
                break
        else:
            groups.append([f])
    new = dict(family_of)
    log = []
    for g in groups:
        if len(g) < 2:
            continue
        for f in g[1:]:
            for m in fams[f]:
                new[m] = g[0]
        log.append(dict(into=g[0], merged=g[1:]))
    return new, log
