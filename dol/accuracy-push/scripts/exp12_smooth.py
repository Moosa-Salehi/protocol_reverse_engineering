"""Exp 12: label-free score smoothing inside the held-out protocol.
  fam:   s' = (1-lam) s + lam * (message-weighted mean score of the same offset over the family's groups)
  proto: additionally the same with the protocol-wide mean for offsets < HEAD (shared header region)
Applied to cached scores (default exp05-s2), then strings R1+R2 post-process, threshold shared as usual.
Usage: exp12_smooth.py [scores-tag]"""
import pickle
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import post  # noqa: E402

tag = sys.argv[1] if len(sys.argv) > 1 else 'exp05-s2'
data, prs, ctxs = gm.setup()
raw = pickle.load(open(qh.OUT / 'preds' / f'scores-{tag}.pkl', 'rb'))


def smooth(p, lam, lam_p=0.0, head=8):
    gs = data[p]
    fam_sum, fam_w = defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(float))
    pro_sum, pro_w = defaultdict(float), defaultdict(float)
    for g, q in zip(gs, raw[p]):
        w = len(g['mids'])
        for o, s in zip(g['offs'], q):
            fam_sum[g['fam']][o] += w * s; fam_w[g['fam']][o] += w
            if o < head:
                pro_sum[o] += w * s; pro_w[o] += w
    out = []
    for g, q in zip(gs, raw[p]):
        q2 = np.array([(1 - lam) * s + lam * fam_sum[g['fam']][o] / fam_w[g['fam']][o] for o, s in zip(g['offs'], q)])
        if lam_p:
            q2 = np.array([(1 - lam_p) * s + lam_p * pro_sum[o] / pro_w[o] if o < head else s for o, s in zip(g['offs'], q2)])
        out.append(q2)
    return out


def evaluate(sc, label, strings=True):
    def predict(p, t):
        pm = gm.pred_msgs(p, sc[p], t, 'open')
        return {m: post.apply_strings(prs[p].msgs[m]['payload'], e) for m, e in pm.items()} if strings else pm
    f1 = {p: [qh.score(prs[p], predict(p, t))['f1'] for t in gm.TH] for p in qh.PROTOS}
    res = {}
    for H in qh.PROTOS:
        k = int(np.argmax([np.mean([f1[p][i] for p in qh.PROTOS if p != H]) for i in range(len(gm.TH))]))
        res[H] = qh.score(prs[H], predict(H, gm.TH[k]))
    print(qh.report(res, label).splitlines()[-1], flush=True)
    return res


for lam, lam_p in ((0.0, 0.0), (0.3, 0.0), (0.5, 0.0), (0.5, 0.5), (0.0, 0.5)):
    sc = {p: smooth(p, lam, lam_p) for p in qh.PROTOS}
    evaluate(sc, f'exp12 {tag} fam-lam {lam} proto-lam {lam_p} +strings')
