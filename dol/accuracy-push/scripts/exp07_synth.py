"""Exp 07: add synthetic protocols (fixed generator) to the training set of the stage-1 group model.
alpha = total weight of all synthetic protocols relative to the total weight of the real training protocols.
Compare with exp02 (0.632 pure / 0.641 open).
Usage: exp07_synth.py [n_synth] [alphas]
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import synth  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
ALPHAS = [float(a) for a in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['0.5', '1'])]
data, prs, ctxs = gm.setup()
syn = synth.synth_set(N)
print('synthetic protocols', len(syn), 'groups', sum(len(v) for v in syn.values()), flush=True)

for alpha in ALPHAS:
    tag = f'exp07-n{N}-a{alpha}'
    path = qh.OUT / 'preds' / f'scores-{tag}.pkl'
    if path.exists():
        import pickle
        sc = pickle.load(open(path, 'rb'))
    else:
        sc = {}
        both = dict(data, **syn)
        for H in qh.PROTOS:
            real = [p for p in qh.PROTOS if p != H]
            Xr, yr, wr = gm.stack(both, real)
            Xs, ys, ws = gm.stack(both, list(syn))
            ws = ws * alpha * wr.sum() / ws.sum()
            m = gm.hgb().fit(np.vstack([Xr, Xs]), np.concatenate([yr, ys]), sample_weight=np.concatenate([wr, ws]))
            sc[H] = [m.predict_proba(g['X'])[:, 1] for g in data[H]]
        import pickle
        pickle.dump(sc, open(path, 'wb'))
    for mode in ('pure', 'open'):
        res, thr, _ = gm.shared_threshold(sc, mode)
        print(qh.report(res, f'{tag} {mode} thr {sorted(set(thr.values()))}'))
