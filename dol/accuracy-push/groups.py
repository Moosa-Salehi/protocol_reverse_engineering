"""Groups of messages for boundary prediction, and learned-v2 feature rows per group (cached).

group = (family, exact length) with >= MIN_GROUP messages; the rest of a family (and the noise /
unassigned messages) form one remainder group per family. Labels: majority of the group's
annotated messages (edge in >= half of those that reach the offset).
"""
import pickle
from collections import Counter, defaultdict

import numpy as np

import qh
import pred

MIN_GROUP = 20
CAPG = 1000


def make_groups(pr, min_group=MIN_GROUP):
    groups = []
    fams = dict(pr.families)
    noise = [m for m in pr.order if pr.msgs[m]['family'] in (None, 'noise')]
    if noise:
        fams['__noise__'] = noise
    for fam, mids in fams.items():
        by = defaultdict(list)
        for m in mids:
            by[len(pr.msgs[m]['payload'])].append(m)
        rest = []
        for ln, g in sorted(by.items()):
            if len(g) >= min_group:
                groups.append((fam, ln, g))
            else:
                rest += g
        if rest:
            groups.append((fam, None, rest))
    return groups


def labels(pr, mids, offs):
    a = [m for m in mids if m in pr.ann]
    if not a:
        return None
    c = Counter(e for m in a for e in pr.ann[m])
    reach = Counter(o for m in a for o in range(1, len(pr.msgs[m]['payload'])))
    return np.array([c[o] >= 0.5 * max(1, reach[o]) for o in offs])


def _runs(mask, i, cap=32):
    """Consecutive True columns ending at i-1 (left) and starting at i (right)."""
    l = 0
    while l < cap and i - 1 - l >= 0 and mask[i - 1 - l]:
        l += 1
    r = 0
    while r < cap and i + r < len(mask) and mask[i + r]:
        r += 1
    return l / cap, r / cap


def family_stats(payloads):
    """Column stats of a family, left-aligned and right-aligned (position from the end)."""
    M, lens, full = pred.v2.to_matrix(payloads)
    _, left = pred.v2.column_stats(M, lens, full)
    R = [b[::-1] for b in payloads]
    M2, lens2, full2 = pred.v2.to_matrix(R)
    _, right = pred.v2.column_stats(M2, lens2, full2)
    return left, right


def context_rows(X, offs, msgs, fam_left, fam_right):
    """Region-level context for each offset of a group (exact length or remainder)."""
    M, lens, full = pred.v2.to_matrix(msgs)
    _, st = pred.v2.column_stats(M, lens, full)
    H, asc, cov = st['H'], st['ascii'], st['cov']
    L = int(np.median(lens))
    hi = H >= 0.85
    ascm = asc >= 0.9
    const = H < 1e-9
    rows = []
    g = lambda a, j: float(a[j]) if 0 <= j < pred.MAXLEN else 0.0
    for i in offs:
        sim = np.abs(H - H[i]) < 0.08
        f = [*_runs(hi, i), *_runs(ascm, i), *_runs(const, i), *_runs(sim, i),
             min(L - i, 64) / 64, i / max(L, 1), float(L > pred.MAXLEN),
             g(fam_left['H'], i - 1), g(fam_left['H'], i), g(fam_left['cov'], i),
             g(fam_left['zero'], i - 1), g(fam_left['zero'], i), g(fam_left['distinct'], i - 1), g(fam_left['distinct'], i)]
        r = L - i   # position from the end (right-aligned index of byte i is r-1)
        f += [g(fam_right['H'], r - 1), g(fam_right['H'], r), g(fam_right['zero'], r - 1), g(fam_right['zero'], r), g(fam_right['cov'], r - 1)]
        rows.append(f)
    return np.hstack([X, np.array(rows, dtype=float)])


def build(p, min_group=MIN_GROUP, ctx_feats=False):
    path = qh.CACHE / f'groups-{p}-{min_group}{"-ctx" if ctx_feats else ""}{"" if pred.MAXLEN == 256 else f"-L{pred.MAXLEN}"}{qh.SUFFIX}.pkl'
    if path.exists():
        return pickle.load(open(path, 'rb'))
    pr = qh.load(p)
    ctx = pred.Ctx(pr)
    out = []
    fstats = {}
    for fam, ln, mids in make_groups(pr, min_group):
        msgs = [pr.msgs[m]['payload'] for m in mids[:CAPG]]
        bfam = fam if fam != '__noise__' else None
        X, offs = pred.v2.family_rows(msgs, ctx.corpus, ctx.body_start(bfam) if bfam else None)
        if not offs:
            continue
        if ctx_feats:
            if fam not in fstats:
                fm = pr.families.get(fam) or [m for m in pr.order if pr.msgs[m]['family'] in (None, 'noise')]
                fstats[fam] = family_stats([pr.msgs[m]['payload'] for m in fm[:3000]])
            X = context_rows(X, offs, msgs, *fstats[fam])
        out.append(dict(fam=fam, len=ln, mids=mids, X=X, offs=offs, y=labels(pr, mids, offs),
                        nann=sum(1 for m in mids if m in pr.ann)))
    pickle.dump(out, open(path, 'wb'))
    return out
