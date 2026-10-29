"""Exp 22 (FEW-SHOT): alignment-based edge transfer. Same k stratified labelled messages as exp20.
Each unseen message is aligned (difflib, autojunk off) to its most similar labelled message of the same family
(fallback: the whole protocol); labelled edges inside matching blocks (or at their ends) are carried over.
Variants: transfer only; hybrid = transferred edges inside aligned regions + model edges elsewhere.
Usage: exp22_align.py [k] [protocols]"""
import difflib, pickle, random, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm
K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
protos = sys.argv[2].split(',') if len(sys.argv) > 2 else qh.PROTOS
data, prs, ctxs = gm.setup()


def stratified(pr, H, k, rnd):
    pools = [sorted(m for m in g['mids'] if m in pr.ann) for g in sorted(data[H], key=lambda g: -g['nann'])]
    pools = [rnd.sample(x, len(x)) for x in pools if x]
    seen, r = set(), 0
    while len(seen) < min(k, len(pr.ann)) and any(len(x) > r for x in pools):
        for x in pools:
            if len(x) > r and len(seen) < k:
                seen.add(x[r])
        r += 1
    return seen


def transfer(a, ea, b):
    """Map edges ea of labelled message a onto message b. Returns (edges, covered positions mask)."""
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out, cov = set(), np.zeros(len(b) + 1, dtype=bool)
    for i, j, n in sm.get_matching_blocks():
        if n == 0:
            continue
        cov[j:j + n + 1] = True
        for e in ea:
            if i <= e <= i + n:
                out.add(j + (e - i))
    return out, cov


def sub(pr, keep):
    s = qh.Proto.__new__(qh.Proto); s.__dict__.update(pr.__dict__)
    s.ann = {m: t for m, t in pr.ann.items() if m in keep}
    return s


best0 = {}
res = {'transfer': {}, 'hybrid': {}, 'hybrid+posts': {}, 'hybrid+selected-posts': {}}
import itertools
import plans as PL
POSTS = [gm.post_strings, gm.post_ber, gm.post_crc(False)]
for H in protos:
    pr = prs[H]
    seen = stratified(pr, H, K, random.Random(20261017))
    unseen = set(pr.ann) - seen
    model_pred = pickle.load(open(qh.OUT / 'preds' / f'fewshot20-{H}.pkl', 'rb')) if (qh.OUT / 'preds' / f'fewshot20-{H}.pkl').exists() else None
    byfam = {}
    for m in seen:
        byfam.setdefault(pr.msgs[m]['family'], []).append(m)
    tr, hy, hp = {}, {}, {}
    PP = {H: PL.plans(H)}
    # few-shot choice of post-processors: leave-one-out transfer among the labelled messages
    subsets = [c for r in range(4) for c in itertools.combinations(range(3), r)]
    loo = {}
    for s_ in seen:
        others = [m for m in byfam.get(pr.msgs[s_]['family'], []) if m != s_] or [m for m in seen if m != s_]
        bs = pr.msgs[s_]['payload']
        a = max(sorted(others, key=lambda m: abs(len(pr.msgs[m]['payload']) - len(bs)))[:5],
                key=lambda m: difflib.SequenceMatcher(None, pr.msgs[m]['payload'][:256], bs[:256], autojunk=False).quick_ratio())
        loo[s_] = transfer(pr.msgs[a]['payload'], pr.ann[a], bs)[0]
    def cfg_pred(c, preds):
        out = {}
        for m_, e_ in preds.items():
            z = set(e_)
            for i in c:
                z = POSTS[i](H, m_, pr.msgs[m_]['payload'], z, PP)
            out[m_] = z
        return out
    chosen = max(subsets, key=lambda c: qh.score(sub(pr, seen), cfg_pred(c, loo))['f1'])
    for u in unseen:
        b = pr.msgs[u]['payload']
        cands = byfam.get(pr.msgs[u]['family']) or list(seen)
        # most similar labelled message: closest length first, then a cheap ratio on the first 256 bytes
        cands = sorted(cands, key=lambda m: abs(len(pr.msgs[m]['payload']) - len(b)))[:5]
        a = max(cands, key=lambda m: difflib.SequenceMatcher(None, pr.msgs[m]['payload'][:256], b[:256], autojunk=False).quick_ratio())
        e, cov = transfer(pr.msgs[a]['payload'], pr.ann[a], b)
        tr[u] = e
        if model_pred is not None:
            mp = model_pred.get(u, set())
            hy[u] = e | {x for x in mp if 0 < x < len(b) and not cov[x]}
            z = set(hy[u])
            for f in POSTS:
                z = f(H, u, b, z, PP)
            hp[u] = z
    import os
    if os.environ.get('SAVE'):
        pickle.dump(hy, open(qh.OUT / 'preds' / f'align{K}-{H}.pkl', 'wb'))
    res['transfer'][H] = qh.score(sub(pr, unseen), tr)
    if hy:
        res['hybrid'][H] = qh.score(sub(pr, unseen), hy)
        res['hybrid+posts'][H] = qh.score(sub(pr, unseen), hp)
        res['hybrid+selected-posts'][H] = qh.score(sub(pr, unseen), cfg_pred(chosen, hy))
    print(H, f"transfer {res['transfer'][H]['f1']:.3f}" + (f" hybrid {res['hybrid'][H]['f1']:.3f} +posts {res['hybrid+posts'][H]['f1']:.3f} selected {[('strings','ber','crc')[i] for i in chosen]} {res['hybrid+selected-posts'][H]['f1']:.3f}" if hy else ''), flush=True)
for v, r in res.items():
    if r:
        print(qh.report(r, f'exp22 FEW-SHOT k={K} alignment {v}'))
