"""Label-free detection of repeating fixed-width structure (arrays) inside varying regions.

For one family (its payloads) and the edges a boundary method already predicted:

1. Candidate regions: maximal runs of varying offsets (family entropy > 0 on the
   messages that reach the offset); single constant bytes inside a run are kept
   (a constant high byte of every register would otherwise break the run).
2. Period test, for p in PERIODS: per-offset statistics (entropy, high/low-nibble
   entropy, zero share, value range, mean, top-value share) are grouped by phase
   (offset - start) mod p. R^2 of that grouping, adjusted for the p groups, says how
   much of the variation across the region the phase explains. It is checked against
   a permutation null (offsets shuffled) and by split-half replication (the phase
   profile of even-numbered elements must correlate with that of odd-numbered ones).
3. Cross-length evidence, which does not need the statistics:
     * gcd of the family's message-length differences: a tail array of p-byte
       elements makes every length difference a multiple of p;
     * tail phase: messages end inside the region at offsets congruent mod p;
     * a count / byte-count field before the region: value * p (or value) equals the
       bytes from the array start to the message end in nearly every message.
4. Edges are added every p bytes inside the region, aligned to the phase from the
   count field, else the message ends, else the region start.

Modes (what is accepted):
  strict  cross-length evidence (gcd/tail or count field) AND significant statistics
  length  cross-length evidence alone (statistics only pick p when they can)
  loose   strict + statistics alone with tighter thresholds (fixed-length families)
"""
from __future__ import annotations

import math
from functools import reduce

import numpy as np

MAXLEN = 256
CAP = 2000
PERIODS = (2, 4, 8)
MIN_REPEATS = 4
R2_MIN = 0.1
STATS_SPLIT = 0.8  # stats-only (loose) acceptance: split-half correlation
STATS_REPEATS = 8  # ... and at least this many elements in the region
R2_RATIO = 0.7   # prefer the smallest period that explains this share of the best R^2
FEATURES = ('H', 'Hhi', 'Hlo', 'zero', 'range', 'mean', 'top')


def _entropy(counts, total, bits):
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum() / bits)


def to_matrix(msgs):
    lens = np.array([min(len(m), MAXLEN) for m in msgs])
    M = np.zeros((len(msgs), MAXLEN), dtype=np.uint8)
    for i, m in enumerate(msgs):
        M[i, :lens[i]] = np.frombuffer(m[:MAXLEN], dtype=np.uint8)
    return M, lens, np.array([len(m) for m in msgs])


def column_stats(M, lens):
    valid = np.arange(MAXLEN)[None, :] < lens[:, None]
    st = {k: np.zeros(MAXLEN) for k in FEATURES}
    st['n'] = valid.sum(0)
    for j in range(MAXLEN):
        v = M[valid[:, j], j]
        if v.size == 0:
            continue
        c = np.bincount(v, minlength=256)
        st['H'][j] = _entropy(c, v.size, 8)
        st['Hhi'][j] = _entropy(np.bincount(v >> 4, minlength=16), v.size, 4)
        st['Hlo'][j] = _entropy(np.bincount(v & 15, minlength=16), v.size, 4)
        st['zero'][j] = c[0] / v.size
        st['range'][j] = (int(v.max()) - int(v.min())) / 255
        st['mean'][j] = v.mean() / 255
        st['top'][j] = c.max() / v.size
    return valid, st


def varying_runs(st, min_msgs):
    """Maximal runs of varying offsets; one constant byte between varying ones is bridged."""
    reach = st['n'] >= min_msgs
    var = (st['H'] > 1e-9) & reach
    upto = int(np.nonzero(reach)[0].max()) + 1 if reach.any() else 0
    bridged = var.copy()
    for j in range(1, upto - 1):
        if not var[j] and var[j - 1] and var[j + 1]:
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


def _phase_r2(F, phase, p):
    """Adjusted R^2 of grouping the rows of F (offsets x standardized features) by phase."""
    total = ((F - F.mean(0)) ** 2).sum()
    if total < 1e-12:
        return 0.0
    within = 0.0
    for q in range(p):
        G = F[phase == q]
        if len(G):
            within += ((G - G.mean(0)) ** 2).sum()
    n = len(F)
    r2 = 1 - within / total
    return 1 - (1 - r2) * (n - 1) / max(n - p, 1)


def period_test(st, start, end, p, rng, n_perm=300):
    """(adjusted R^2, permutation p-value, split-half correlation) for period p on [start, end)."""
    offs = np.arange(start, end)
    offs = offs[st['n'][offs] >= 8]
    if len(offs) < MIN_REPEATS * p:
        return None
    F = np.stack([st[k][offs] for k in FEATURES], axis=1)
    sd = F.std(0)
    F = F[:, sd > 1e-6]
    if F.shape[1] == 0:
        return None
    F = (F - F.mean(0)) / F.std(0)
    phase = (offs - start) % p
    r2 = _phase_r2(F, phase, p)
    null = np.array([_phase_r2(F, rng.permutation(phase), p) for _ in range(n_perm)])
    pval = (1 + (null >= r2).sum()) / (n_perm + 1)
    elem = (offs - start) // p
    prof = []
    for half in (0, 1):
        sel = elem % 2 == half
        if len(set(phase[sel])) < p:
            return dict(r2=r2, pval=pval, split=0.0)
        prof.append(np.stack([F[sel & (phase == q)].mean(0) for q in range(p)]).ravel())
    a, b = prof
    split = float(np.corrcoef(a, b)[0, 1]) if a.std() > 1e-9 and b.std() > 1e-9 else 0.0
    return dict(r2=float(r2), pval=float(pval), split=split)


def main_lengths(full, share=0.95):
    """Lengths that together cover `share` of the messages (rare outlier lengths dropped)."""
    vals, counts = np.unique(full, return_counts=True)
    order = np.argsort(-counts)
    keep, covered = [], 0
    for i in order:
        keep.append(vals[i])
        covered += counts[i]
        if covered >= share * len(full):
            break
    return np.array(sorted(keep))


def length_gcd(full):
    keep = main_lengths(full)
    if len(keep) < 3:
        return 0, len(keep)
    return int(reduce(math.gcd, (int(x - keep[0]) for x in keep[1:]))), len(keep)


def count_field(M, lens, full, start, p, region_end):
    """A 1- or 2-byte field before the array whose value counts its elements or bytes.

    Returns the array start s' (within p bytes of the run start) or None. Needs at least
    three distinct message lengths, so the match cannot be a coincidence of one length.
    """
    if len(set(full.tolist())) < 3:
        return None
    for s in range(max(1, start - p), start + p + 1):
        remain = full - s
        if (remain < 0).any():
            continue
        for c in range(0, s):
            for width, order in ((1, None), (2, 'big'), (2, 'little')):
                if c + width > s or (lens < c + width).any():
                    continue
                if width == 1:
                    v = M[:, c].astype(int)
                elif order == 'big':
                    v = M[:, c].astype(int) * 256 + M[:, c + 1]
                else:
                    v = M[:, c + 1].astype(int) * 256 + M[:, c]
                if len(set(v.tolist())) < 3:
                    continue
                for unit in (p, 1):
                    if (v * unit == remain).mean() >= 0.95:
                        return dict(start=s, at=c, width=width, order=order, unit='elements' if unit == p else 'bytes')
    return None


def choose_period(sig):
    """Smallest significant period whose R^2 is within R2_RATIO of the best one.

    Periods nest (p=8 can express anything p=4 can), so the largest period always fits
    at least as well; the smallest one that explains most of it is the element width.
    """
    if not sig:
        return None
    best = max(t['r2'] for t in sig.values())
    return min(q for q, t in sig.items() if t['r2'] >= R2_RATIO * best)


def detect_family(msgs, mode='strict', periods=PERIODS, seed=0):
    """Array regions of one family: list of dicts with start, end, p, phase, evidence."""
    msgs = msgs[:CAP]
    if len(msgs) < 5:
        return []
    rng = np.random.default_rng(seed)
    M, lens, full = to_matrix(msgs)
    valid, st = column_stats(M, lens)
    min_msgs = max(3, int(0.05 * len(msgs)))
    g, n_lengths = length_gcd(full)
    max_reach = int(np.nonzero(st['n'] >= min_msgs)[0].max()) + 1
    found = []
    for start, end in varying_runs(st, min_msgs):
        tail = end >= max_reach - 1 and n_lengths >= 3
        tests = {p: period_test(st, start, end, p, rng) for p in periods}
        tests = {p: t for p, t in tests.items() if t}
        sig = {p: t for p, t in tests.items() if t['pval'] < 0.01 and t['split'] > 0.5 and t['r2'] > R2_MIN}

        # cross-length evidence: which periods are compatible with the length differences
        len_ok = [p for p in periods if tail and g and g % p == 0 and (end - start) >= MIN_REPEATS * p]
        cnt = None
        if tail:
            for p in sorted(len_ok or periods):
                cnt = count_field(M, lens, full, start, p, end)
                if cnt:
                    cnt['p'] = p if cnt['unit'] == 'elements' else None
                    break
        cross = sorted(set(len_ok) | ({cnt['p']} if cnt and cnt.get('p') else set()))
        evidence, p = None, None
        both = choose_period({q: sig[q] for q in sig if q in cross})
        if both:
            evidence, p = ('count+stats' if cnt and cnt.get('p') == both else 'length+stats'), both
        elif mode == 'length' and cross:
            p = choose_period({q: sig[q] for q in sig if q in cross}) or (cnt['p'] if cnt and cnt.get('p') else max(cross))
            evidence = 'count' if cnt and cnt.get('p') == p else 'length'
        elif mode == 'loose':
            strong = {q: t for q, t in sig.items() if t['split'] > STATS_SPLIT and (end - start) >= STATS_REPEATS * q}
            if strong:
                evidence, p = 'stats', choose_period(strong)
        if p is None:
            continue
        # phase: count field start, else message ends of a tail array, else run start
        if cnt and cnt.get('start') is not None:
            phase, how = cnt['start'] % p, 'count'
        elif tail:
            ends = full[(full > start) & (full <= MAXLEN)]
            shares = [float(np.mean(ends % p == q)) for q in range(p)]
            q = int(np.argmax(shares))
            phase, how = (q, 'ends') if shares[q] >= 0.9 else (start % p, 'start')
        else:
            phase, how = start % p, 'start'
        first = start + ((phase - start) % p)
        last = MAXLEN if tail else end
        found.append(dict(start=int(start), end=int(end), tail=bool(tail), p=int(p), phase=int(phase),
                          phase_from=how, evidence=evidence, gcd=g, count_field=cnt,
                          stats={str(k): v for k, v in tests.items()},
                          edges=[int(e) for e in range(first, last + 1, p) if start <= e <= last]))
    return found
