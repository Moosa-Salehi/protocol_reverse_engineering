"""Exp 11: string post-processing on top of the best scores (exp05-s2, shared threshold per held-out protocol).
Variants: none, R1 length-prefixed strings (+bounds), R2 ASCII runs (interior removal), R1+R2.
The threshold is re-chosen on the other protocols for each variant.
Usage: exp11_strings.py [scores-tag] [mode]"""
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import post  # noqa: E402

tag = sys.argv[1] if len(sys.argv) > 1 else 'exp05-s2'
mode = sys.argv[2] if len(sys.argv) > 2 else 'open'
data, prs, ctxs = gm.setup()
sc = pickle.load(open(qh.OUT / 'preds' / f'scores-{tag}.pkl', 'rb'))
VARIANTS = {'none': None, 'R1': dict(lv=True, runs=False), 'R2': dict(lv=False, runs=True), 'R1+R2': dict(lv=True, runs=True),
            'R1-nobounds': dict(lv=True, runs=False, add_bounds=False)}


def predict(p, t, v):
    pm = gm.pred_msgs(p, sc[p], t, mode)
    if VARIANTS[v] is None:
        return pm
    return {m: post.apply_strings(prs[p].msgs[m]['payload'], e, **VARIANTS[v]) for m, e in pm.items()}


for v in VARIANTS:
    f1 = {p: [qh.score(prs[p], predict(p, t, v))['f1'] for t in gm.TH] for p in qh.PROTOS}
    res = {}
    for H in qh.PROTOS:
        k = int(np.argmax([np.mean([f1[p][i] for p in qh.PROTOS if p != H]) for i in range(len(gm.TH))]))
        res[H] = qh.score(prs[H], predict(H, gm.TH[k], v))
    print(qh.report(res, f'exp11 {tag} {mode} strings={v}'), flush=True)
