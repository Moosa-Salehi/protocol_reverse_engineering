"""Exp 16: more training protocols. Extra tshark-annotated protocols (dol/accuracy-push/extra/<name>) are added
to the training set of every LOPO fold; evaluation stays on the 14 benchmark protocols.
Weights: each extra protocol weighs ALPHA x one benchmark protocol.
Usage: exp16_extra.py [alpha,...] [s1|s2]"""
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import pred  # noqa: E402
import groups as G  # noqa: E402

ALPHAS = [float(a) for a in (sys.argv[1].split(',') if len(sys.argv) > 1 else ['1'])]
STAGE = sys.argv[2] if len(sys.argv) > 2 else 's1'
data, prs, ctxs = gm.setup()
extras = []
for d in sorted((qh.EXTRA).iterdir()):
    if (d / 'annotations.jsonl').exists() and (d / 'data' / '04_framing.json').exists():
        name = 'x:' + d.name
        try:
            gs = G.build(name)
        except Exception as exc:          # noqa: BLE001
            print('skip', name, exc); continue
        gs = [g for g in gs if g['y'] is not None and g['nann']]
        pr_ = qh.load(name)
        dens = sum(len(v) for v in pr_.ann.values()) / max(1, sum(len(pr_.msgs[m]['payload']) for m in pr_.ann))
        if sum(g['nann'] for g in gs) >= 30 and dens >= 0.05:
            data[name] = gs; extras.append(name)
print('extra protocols', len(extras), ' '.join(f"{n[2:]}:{sum(g['nann'] for g in data[n])}" for n in extras), flush=True)


def fit_rows(protos, feat=None, alpha=1.0):
    real = [p for p in protos if not p.startswith('x:')]
    X, y, w = gm.stack(data, real, feat)
    if alpha and extras:
        Xe, ye, we = gm.stack(data, extras, feat)
        we = we * alpha * (w.sum() / len(real)) * len(extras) / we.sum()
        X, y, w = np.vstack([X, Xe]), np.concatenate([y, ye]), np.concatenate([w, we])
    return X, y, w


for alpha in ALPHAS:
    tag = f'exp16-{STAGE}-a{alpha}-n{len(extras)}-d05'
    path = qh.OUT / 'preds' / f'scores-{tag}.pkl'
    if path.exists():
        sc = pickle.load(open(path, 'rb'))
    else:
        sc = {}
        for H in qh.PROTOS:
            train = [p for p in qh.PROTOS if p != H]
            if STAGE == 's1':
                m = gm.hgb().fit(*fit_rows(train, alpha=alpha))
                sc[H] = [m.predict_proba(g['X'])[:, 1] for g in data[H]]
                continue
            oof = {}
            for f in [train[k::4] for k in range(4)]:
                m = gm.hgb().fit(*fit_rows([p for p in train if p not in f], alpha=alpha))
                for p in f:
                    oof[p] = [m.predict_proba(g['X'])[:, 1] for g in data[p]]
            s1 = gm.hgb().fit(*fit_rows(train, alpha=alpha))
            oof[H] = [s1.predict_proba(g['X'])[:, 1] for g in data[H]]
            for p in train + [H]:
                for g, q in zip(data[p], oof[p]):
                    g['X2'] = pred.v2.neighbour_features(g['X'], q)
            # stage 2 sees only real protocols with out-of-fold stage-1 scores (extras feed stage 1 only)
            s2 = gm.hgb().fit(*fit_rows(train, feat=lambda g: g['X2'], alpha=0))
            sc[H] = [s2.predict_proba(g['X2'])[:, 1] for g in data[H]]
            print(H, 'done', flush=True)
        pickle.dump(sc, open(path, 'wb'))
    gm.evaluate(sc, 'open', label=f'{tag} open +strings', verbose=True)
