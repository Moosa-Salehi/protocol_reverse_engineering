"""Exp 04: calibration. Group model scores (exp02 features), mode open/pure.

  shared   threshold chosen on the other protocols (as exp02)
  oracle   best threshold per protocol (uses the protocol's labels: an upper bound, not a result)
  density  label-free: per protocol, the threshold whose predicted edge density (edges per byte of
           annotated messages) is closest to the median truth density of the training protocols
Usage: exp04_threshold.py [mode]
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402

mode = sys.argv[1] if len(sys.argv) > 1 else 'open'
data, prs, ctxs = gm.setup()
scores = gm.lopo_scores('exp02', data)
shared, thr, f1 = gm.shared_threshold(scores, mode)
print(qh.report(shared, f'shared {mode}').splitlines()[-1])
oracle = {p: max(f1[p]) for p in qh.PROTOS}
print(f"oracle threshold per protocol: macro {np.mean(list(oracle.values())):.3f}  >=0.70: {sum(v >= 0.7 for v in oracle.values())}/14  "
      + ' '.join(f'{p} {v:.2f}@{gm.TH[int(np.argmax(f1[p]))]}' for p, v in oracle.items()))


def density(p, t):
    pm = gm.pred_msgs(p, scores[p], t, mode)
    return sum(len([e for e in pm[m] if 0 < e < len(prs[p].msgs[m]['payload'])]) for m in pm) / sum(len(prs[p].msgs[m]['payload']) for m in pm)


truth_den = {p: sum(len(v) for v in prs[p].ann.values()) / sum(len(prs[p].msgs[m]['payload']) for m in prs[p].ann) for p in qh.PROTOS}
print('truth edge density per byte:', ' '.join(f'{p} {v:.2f}' for p, v in truth_den.items()))
res = {}
for H in qh.PROTOS:
    target = float(np.median([truth_den[p] for p in qh.PROTOS if p != H]))
    k = int(np.argmin([abs(density(H, t) - target) for t in gm.TH]))
    res[H] = qh.score(prs[H], gm.pred_msgs(H, scores[H], gm.TH[k], mode))
print(qh.report(res, f'density-matched {mode}').splitlines()[-1])
