"""Exp 15: parametric gate between stage-07 rules and learned scores, parameters chosen on the other 13.
edges = {stage-07 edges with score >= t_keep (edges without a score are kept)}
      | {learned >= t_add inside stage-07 fields of >= 3 bytes or past the last field / no stage-07 family}
      | {learned >= t_add2 inside 2-byte stage-07 fields}
then the string post-process. Usage: exp15_param_gate.py [scores-tag]"""
import itertools
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import pred  # noqa: E402
import plans as PL  # noqa: E402
import post  # noqa: E402

tag = sys.argv[1] if len(sys.argv) > 1 else 'exp05-s2'
data, prs, ctxs = gm.setup()
sc = pickle.load(open(qh.OUT / 'preds' / f'scores-{tag}.pkl', 'rb'))
P = {p: PL.plans(p) for p in qh.PROTOS}
GRID = list(itertools.product((0.15, 0.2, 0.25, 0.3), (0.5, 0.7, 0.9, 1.01), (0.0, 0.03, 0.1)))


def predict(p, t_add, t_add2, t_keep):
    pr, ctx = prs[p], ctxs[p]
    out = {}
    for g, q in zip(data[p], sc[p]):
        s = dict(zip(g['offs'], q))
        fields = ctx.fields07.get(g['fam'], []) if g['fam'] != '__noise__' else []
        end = max((b for a, b in fields), default=0)
        add = set()
        for a, b in fields:
            thr = t_add if b - a >= 3 else (t_add2 if b - a == 2 else 9)
            add.update(o for o in range(a + 1, b) if s.get(o, 0) >= thr)
        add.update(o for o, v in s.items() if o >= end and v >= t_add)
        keep = {x for a, b in fields for x in (a, b) if s.get(x, 1.0) >= t_keep}
        e = keep | add
        for m in g['mids']:
            if m in pr.ann:
                n = len(pr.msgs[m]['payload'])
                em = e if end else e
                out[m] = post.apply_plan(pred.apply_layout(ctx, m, {x for x in em if x < n} if fields else set(add)), P[p][m])
    return out


f1 = {}
for p in qh.PROTOS:
    f1[p] = [qh.score(prs[p], predict(p, *c))['f1'] for c in GRID]
    print(p, 'best own', f'{max(f1[p]):.3f}', GRID[int(np.argmax(f1[p]))], flush=True)
res = {}
for H in qh.PROTOS:
    k = int(np.argmax([np.mean([f1[p][i] for p in qh.PROTOS if p != H]) for i in range(len(GRID))]))
    res[H] = dict(qh.score(prs[H], predict(H, *GRID[k])), cfg=GRID[k])
print(qh.report(res, f'exp15 param gate {tag} +strings  cfgs {sorted({r["cfg"] for r in res.values()})}'))
