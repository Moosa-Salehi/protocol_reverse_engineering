"""Exp 10: regularisation sweep for the stage-1 group model (cross-protocol generalisation).
Usage: exp10_regularize.py name=k:v,k:v ...   e.g. d3=max_depth:3,max_iter:150"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm
data, prs, ctxs = gm.setup()
for spec in sys.argv[1:]:
    name, kv = spec.split('=')
    kw = {}
    for item in kv.split(','):
        k, v = item.split(':')
        kw[k] = float(v) if '.' in v else int(v)
    sc = gm.lopo_scores(f'exp10-{name}', data, **kw)
    for mode in ('pure', 'open'):
        res, thr, _ = gm.shared_threshold(sc, mode)
        print(qh.report(res, f'exp10 {name} {kw} {mode}').splitlines()[-1], flush=True)
