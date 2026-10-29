"""Exp 09: average cached LOPO group scores of several models (all on the same 256-byte groups).
Usage: exp09_ensemble.py tagA,tagB,...  (tags of preds/scores-<tag>.pkl)"""
import pickle, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm
data, prs, ctxs = gm.setup()
for combo in sys.argv[1:]:
    tags = combo.split(',')
    S = [pickle.load(open(qh.OUT / 'preds' / f'scores-{t}.pkl', 'rb')) for t in tags]
    sc = {p: [np.mean([s[p][k] for s in S], axis=0) for k in range(len(data[p]))] for p in qh.PROTOS}
    for mode in ('pure', 'open'):
        res, thr, _ = gm.shared_threshold(sc, mode)
        print(qh.report(res, f'ensemble {combo} {mode}').splitlines()[-1], flush=True)
