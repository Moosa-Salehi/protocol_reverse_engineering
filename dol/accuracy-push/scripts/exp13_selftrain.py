"""Exp 13: transductive self-training. For held-out H: model on the 13 others -> scores on H; H rows with
score >= HI become pseudo-positives, <= LO pseudo-negatives; retrain with them (total weight BETA x one real
protocol) and rescore H. No labels of H are used. Base: stage-1 group model (exp02).
Usage: exp13_selftrain.py [hi,lo,beta ...]"""
import pickle, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm
data, prs, ctxs = gm.setup()
base = gm.lopo_scores('exp02', data)
gm.evaluate(base, label='exp02 base +strings')
for spec in (sys.argv[1:] or ['0.6,0.05,1', '0.5,0.1,2']):
    hi, lo, beta = map(float, spec.split(','))
    tag = f'exp13-{hi}-{lo}-{beta}'
    path = qh.OUT / 'preds' / f'scores-{tag}.pkl'
    if path.exists():
        sc = pickle.load(open(path, 'rb'))
    else:
        sc = {}
        for H in qh.PROTOS:
            train = [p for p in qh.PROTOS if p != H]
            X, y, w = gm.stack(data, train)
            px, py = [], []
            for g, q in zip(data[H], base[H]):
                keep = (q >= hi) | (q <= lo)
                px.append(g['X'][keep]); py.append(q[keep] >= hi)
            px, py = np.vstack(px), np.concatenate(py)
            pw = np.full(len(py), beta * w.sum() / len(train) / max(1, len(py)))
            m = gm.hgb().fit(np.vstack([X, px]), np.concatenate([y, py]), sample_weight=np.concatenate([w, pw]))
            sc[H] = [m.predict_proba(g['X'])[:, 1] for g in data[H]]
        pickle.dump(sc, open(path, 'wb'))
    gm.evaluate(sc, label=f'{tag} +strings')
