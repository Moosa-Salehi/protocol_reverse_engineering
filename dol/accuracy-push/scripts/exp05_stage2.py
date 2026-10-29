"""Exp 05: group model + stage 2 (neighbour scores i-3..i+3, out-of-fold stage-1 scores from 4 protocol
groups inside the training protocols), and a larger stage-1 model.
Usage: exp05_stage2.py
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import pred  # noqa: E402

data, prs, ctxs = gm.setup()


def stage2_scores(tag, **kw):
    path = qh.OUT / 'preds' / f'scores-{tag}{qh.SUFFIX}.pkl'
    if path.exists():
        import pickle
        return pickle.load(open(path, 'rb'))
    out = {}
    for H in qh.PROTOS:
        train = [p for p in qh.PROTOS if p != H]
        folds = [train[k::4] for k in range(4)]
        oof = {}
        for f in folds:
            m = gm.hgb(**kw).fit(*gm.stack(data, [p for p in train if p not in f]))
            for p in f:
                oof[p] = [m.predict_proba(g['X'])[:, 1] for g in data[p]]
        s1 = gm.hgb(**kw).fit(*gm.stack(data, train))
        for p in [H]:
            oof[p] = [s1.predict_proba(g['X'])[:, 1] for g in data[p]]
        # attach neighbour scores as features (stage 2)
        for p in train + [H]:
            for g, q in zip(data[p], oof[p]):
                g['X2'] = pred.v2.neighbour_features(g['X'], q)
        s2 = gm.hgb(**kw).fit(*gm.stack(data, train, feat=lambda g: g['X2']))
        out[H] = [s2.predict_proba(g['X2'])[:, 1] for g in data[H]]
        print(H, 'done', flush=True)
    import pickle
    pickle.dump(out, open(path, 'wb'))
    return out


for tag, kw in (('exp05-s2', {}), ('exp05-s2-big', dict(max_iter=600, max_depth=8, learning_rate=0.05))):
    sc = stage2_scores(tag, **kw)
    for mode in ('pure', 'open'):
        res, thr, _ = gm.shared_threshold(sc, mode)
        print(qh.report(res, f'{tag} {mode} thr {sorted(set(thr.values()))}'))
