"""Exp 08: feature window MAXLEN (env) for the stage-1 group model. Compare exp02 (256): 0.632 pure / 0.641 open.
Usage: MAXLEN=1024 exp08_maxlen.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm, pred
data, prs, ctxs = gm.setup()
sc = gm.lopo_scores('exp02', data)
for mode in ('pure', 'open'):
    res, thr, _ = gm.shared_threshold(sc, mode)
    print(qh.report(res, f'exp08 MAXLEN={pred.MAXLEN} {mode} thr {sorted(set(thr.values()))}'))
