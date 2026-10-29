"""Exp 02: learned-v2 stage-1 edge model trained and applied per (family, length) group.

LOPO over the 14 protocols. Threshold for held-out H: best macro per-message F1 over the other
protocols, using each one's own LOPO scores (quick variant; H's labels only enter through the
other protocols' models). Variants: pure learned edges, and gated on stage-07 fields.
Usage: exp02_group_model.py [min_group]
"""
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import pred  # noqa: E402
import groups as G  # noqa: E402

MIN = int(sys.argv[1]) if len(sys.argv) > 1 else G.MIN_GROUP
import os
CTXF = bool(os.environ.get('CTX_FEATS'))
TAGX = os.environ.get('TAG', 'exp02')
data = {p: [g for g in G.build(p, MIN, CTXF)] for p in qh.PROTOS}
prs = {p: qh.load(p) for p in qh.PROTOS}
ctxs = {p: pred.Ctx(prs[p]) for p in qh.PROTOS}


def fit(protos):
    rows = [(g['X'], g['y'], g['nann']) for p in protos for g in data[p] if g['y'] is not None and g['nann']]
    X = np.vstack([r[0] for r in rows]); y = np.concatenate([r[1] for r in rows])
    # protocols weigh equally; inside a protocol a group weighs by its annotated messages
    w = []
    for p in protos:
        gs = [g for g in data[p] if g['y'] is not None and g['nann']]
        tot = sum(g['nann'] * len(g['offs']) for g in gs)
        w += [np.full(len(g['offs']), g['nann'] / tot) for g in gs]
    w = np.concatenate(w); w *= len(w) / w.sum()
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, max_depth=5, l2_regularization=1.0, random_state=0).fit(X, y, sample_weight=w)


def predict(p, scores, t, gated):
    """gated: False (pure learned), 'inside' (stage-07 fields > 2 bytes), 'open' (also the uncovered tail)."""
    pr, ctx = prs[p], ctxs[p]
    out = {}
    for g, q in zip(data[p], scores):
        e = {o for o, s in zip(g['offs'], q) if s >= t}
        fam = g['fam']
        for m in g['mids']:
            if m not in pr.ann:
                continue
            if gated == 'open' and fam in ctx.fields07:
                out[m] = pred.apply_layout(ctx, m, pred.gated_open(ctx.fields07[fam], e, len(pr.msgs[m]['payload'])))
            elif gated and fam in ctx.fields07:
                out[m] = pred.apply_layout(ctx, m, pred.gated_edges(ctx.fields07[fam], e))
            else:
                out[m] = pred.apply_layout(ctx, m, set(e))
    return out


models = {p: fit([q for q in qh.PROTOS if q != p]) for p in qh.PROTOS}
scores = {p: [models[p].predict_proba(g['X'])[:, 1] for g in data[p]] for p in qh.PROTOS}
TH = np.arange(0.05, 0.71, 0.05)
for gated in [v for v in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['pure', 'inside', 'open'])]:
    gated = False if gated == 'pure' else gated
    # per-message F1 of every protocol at every threshold (from its own LOPO scores)
    f1 = {p: [qh.score(prs[p], predict(p, scores[p], t, gated))['f1'] for t in TH] for p in qh.PROTOS}
    res = {}
    for H in qh.PROTOS:
        k = int(np.argmax([np.mean([f1[p][i] for p in qh.PROTOS if p != H]) for i in range(len(TH))]))
        res[H] = qh.score(prs[H], predict(H, scores[H], TH[k], gated))
        res[H]['thr'] = float(TH[k])
        import pickle; (qh.OUT / 'preds').mkdir(exist_ok=True)
        pickle.dump(predict(H, scores[H], TH[k], gated), open(qh.OUT / 'preds' / f'{TAGX}-{gated or "pure"}-{H}.pkl', 'wb'))
    print(qh.report(res, f"{TAGX} group model min{MIN} ctx={CTXF} {gated or 'pure'}  thr {sorted({r['thr'] for r in res.values()})}"))
