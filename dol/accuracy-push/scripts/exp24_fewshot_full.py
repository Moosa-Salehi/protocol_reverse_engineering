"""Exp 24 (FEW-SHOT, full procedure in one place). For each target protocol H:
  1. choose k messages to label: 'strat' (round-robin over (family, length) groups) or 'kcenter'
     (farthest-first on 1 - difflib ratio of the first 128 bytes, over a sample of <= 1500 messages)
  2. stage-1 group model on the other 13 protocols + H's labelled groups (weight BETA)
  3. pure learned edges per group, threshold = best F1 on the labelled messages
  4. alignment hybrid: edges transferred from the most similar labelled message inside matching blocks,
     model edges elsewhere
  5. post-processors (strings / embedded BER / CRC blocks) chosen by leave-one-out on the labelled messages
Scores on H's UNSEEN annotated messages only. No TLV layout (labels decide the convention).
Usage: exp24_fewshot_full.py <strategy> <k> [beta] [protocols]"""
import difflib
import itertools
import pickle
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import plans as PL  # noqa: E402

STRATEGY = sys.argv[1] if len(sys.argv) > 1 else 'strat'
K = int(sys.argv[2]) if len(sys.argv) > 2 else 20
BETA = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
protos = sys.argv[4].split(',') if len(sys.argv) > 4 else qh.PROTOS
import os
SEED = int(os.environ.get('SEED', '20261017'))
STAG = '' if SEED == 20261017 else f'-s{SEED}'
data, prs, ctxs = gm.setup()
POSTS = [gm.post_strings, gm.post_ber, gm.post_crc(False)]
NAMES = ('strings', 'ber', 'crc')


def select(pr, H, k, rnd):
    ann = sorted(pr.ann)
    if STRATEGY == 'strat':
        pools = [sorted(m for m in g['mids'] if m in pr.ann) for g in sorted(data[H], key=lambda g: -g['nann'])]
        pools = [rnd.sample(x, len(x)) for x in pools if x]
        seen, r = [], 0
        while len(seen) < min(k, len(ann)) and any(len(x) > r for x in pools):
            for x in pools:
                if len(x) > r and len(seen) < k:
                    seen.append(x[r])
            r += 1
        return set(seen)
    if STRATEGY == 'lstrat':
        # strata = (family, log2 length bucket), visited round-robin by total bytes (where the edges are)
        import math
        strata = defaultdict(list)
        for m in ann:
            strata[(pr.msgs[m]['family'], int(math.log2(max(2, len(pr.msgs[m]['payload'])))))].append(m)
        pools = sorted(strata.values(), key=lambda x: -sum(len(pr.msgs[m]['payload']) for m in x))
        pools = [rnd.sample(x, len(x)) for x in pools]
        seen, r = [], 0
        while len(seen) < min(k, len(ann)) and any(len(x) > r for x in pools):
            for x in pools:
                if len(x) > r and len(seen) < k:
                    seen.append(x[r])
            r += 1
        return set(seen)
    cand = rnd.sample(ann, min(1500, len(ann)))
    heads = {m: pr.msgs[m]['payload'][:128] for m in cand}
    seen = [cand[0]]
    dmin = {m: 1.0 for m in cand}
    while len(seen) < min(k, len(cand)):
        last = heads[seen[-1]]
        sm = difflib.SequenceMatcher(None, autojunk=False)
        sm.set_seq2(last)
        for m in cand:
            if dmin[m] > 0:
                sm.set_seq1(heads[m])
                dmin[m] = min(dmin[m], 1 - sm.ratio())
        for m in seen:
            dmin[m] = -1
        seen.append(max(cand, key=lambda m: dmin[m]))
    return set(seen)


def transfer(a, ea, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out, cov = set(), np.zeros(len(b) + 1, dtype=bool)
    for i, j, n in sm.get_matching_blocks():
        if n:
            cov[j:j + n + 1] = True
            out.update(j + (e - i) for e in ea if i <= e <= i + n)
    return out, cov


def neighbour(pr, b, fam, pool, byfam, exclude=None):
    cands = [m for m in byfam.get(fam, []) if m != exclude] or [m for m in pool if m != exclude]
    cands = sorted(cands, key=lambda m: abs(len(pr.msgs[m]['payload']) - len(b)))[:8]
    return max(cands, key=lambda m: difflib.SequenceMatcher(None, pr.msgs[m]['payload'][:256], b[:256], autojunk=False).quick_ratio())


def sub(pr, keep):
    s = qh.Proto.__new__(qh.Proto)
    s.__dict__.update(pr.__dict__)
    s.ann = {m: t for m, t in pr.ann.items() if m in keep}
    return s


res = {}
for H in protos:
    pr = prs[H]
    PP = {H: PL.plans(H)}
    seen = select(pr, H, K, random.Random(SEED))
    unseen = set(pr.ann) - seen
    # 2. model
    X, y, w = gm.stack(data, [p for p in qh.PROTOS if p != H])
    hx, hy = [], []
    for g in data[H]:
        a = [m for m in g['mids'] if m in seen]
        if not a:
            continue
        c = Counter(e for m in a for e in pr.ann[m])
        reach = Counter(o for m in a for o in range(1, len(pr.msgs[m]['payload'])))
        ok = np.array([reach[o] > 0 for o in g['offs']])
        hx.append(g['X'][ok]); hy.append(np.array([c[o] >= 0.5 * max(1, reach[o]) for o in g['offs']])[ok])
    hx, hy = np.vstack(hx), np.concatenate(hy)
    hw = np.full(len(hy), BETA * w.sum() / 13 / len(hy))
    mdl = gm.hgb().fit(np.vstack([X, hx]), np.concatenate([y, hy]), sample_weight=np.concatenate([w, hw]))
    sc = [mdl.predict_proba(g['X'])[:, 1] for g in data[H]]

    def model_edges(t, mids):
        out = {}
        for g, q in zip(data[H], sc):
            e = {o for o, s in zip(g['offs'], q) if s >= t}
            for m in g['mids']:
                if m in mids:
                    out[m] = set(e)
        return out
    # 3. threshold on the labelled messages
    t = max(gm.TH, key=lambda t: qh.score(sub(pr, seen), model_edges(t, seen))['f1'])
    model = model_edges(t, unseen)
    # 4. alignment hybrid
    byfam = defaultdict(list)
    for m in seen:
        byfam[pr.msgs[m]['family']].append(m)
    hybrid = {}
    for u in unseen:
        b = pr.msgs[u]['payload']
        a = neighbour(pr, b, pr.msgs[u]['family'], seen, byfam)
        e, cov = transfer(pr.msgs[a]['payload'], pr.ann[a], b)
        hybrid[u] = e | {x for x in model.get(u, ()) if 0 < x < len(b) and not cov[x]}
    # 5. post-processors by leave-one-out on the labelled messages
    loo = {}
    for s_ in seen:
        bs = pr.msgs[s_]['payload']
        a = neighbour(pr, bs, pr.msgs[s_]['family'], seen, byfam, exclude=s_)
        loo[s_] = transfer(pr.msgs[a]['payload'], pr.ann[a], bs)[0]

    def cfg(c, preds):
        out = {}
        for m_, e_ in preds.items():
            z = set(e_)
            for i in c:
                z = POSTS[i](H, m_, pr.msgs[m_]['payload'], z, PP)
            out[m_] = z
        return out
    subsets = [c for r in range(4) for c in itertools.combinations(range(3), r)]
    chosen = max(subsets, key=lambda c: qh.score(sub(pr, seen), cfg(c, loo))['f1'])
    final = cfg(chosen, hybrid)
    pickle.dump(final, open(qh.OUT / 'preds' / f'fs-{STRATEGY}{K}{STAG}{qh.SUFFIX}-{H}.pkl', 'wb'))
    pickle.dump(sorted(seen), open(qh.OUT / 'preds' / f'fs-{STRATEGY}{K}{STAG}{qh.SUFFIX}-seen-{H}.pkl', 'wb'))
    res[H] = qh.score(sub(pr, unseen), final)
    res[H]['model_only'] = qh.score(sub(pr, unseen), model)['f1']
    print(f"{H:10s} k={K} {STRATEGY}: model {res[H]['model_only']:.3f}  final {res[H]['f1']:.3f}  thr {t}  posts {[NAMES[i] for i in chosen]}", flush=True)
print(qh.report(res, f'exp24 FEW-SHOT {STRATEGY} k={K} beta={BETA} seed={SEED}{qh.SUFFIX}'))
