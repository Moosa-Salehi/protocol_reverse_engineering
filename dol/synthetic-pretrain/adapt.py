"""Improving synthetic-only training (idea 1, v3 rows), offline on the 14 real protocols' labelled rows:
  B      synthetic only, shipped model size (current v3 result)
  B-big  synthetic only, larger model (600 iterations, depth 8)
  B-iw   synthetic only, importance-weighted toward the TARGET capture: a domain classifier separates synthetic rows
         from the target's unlabelled rows; synthetic row weight = exp(0.5 * logit) (tempered density ratio, clipped at the
         99th percentile). Only the
         target's features are used, never its labels (test-time adaptation, available in zero-shot use).
  B-iw-big   both.
Threshold: chosen on held-out synthetic protocols (unweighted; same rule as eval_offline.py).
usage: adapt.py <syn.npz>[,...] [out.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eval_offline as eo  # noqa: E402


def big():
    return HistGradientBoostingClassifier(max_iter=600, learning_rate=0.06, max_depth=8, l2_regularization=1.0, random_state=0)


def main():
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "rows/adapt_v3.json"
    real = np.load(eo.ROOT / "assets/pre_trained/fewshot_boundary_training.npz")
    names = [str(x) for x in real["protocols"]]
    Xr, yr, wr, pr = real["X"], real["y"], real["weight"].astype(float), real["proto"]
    Xs, ys, ws, ps, _ = eo.load(sys.argv[1].split(","))
    keep = ps % 5 < 2                                     # memory: 40% of the synthetic protocols
    Xs, ys, ws, ps = Xs[keep], ys[keep], ws[keep].astype(float), ps[keep]
    hold = ps % 10 == 0
    Xt, yt, wt = Xs[~hold], ys[~hold], ws[~hold]
    norm = lambda w: w * len(w) / w.sum()  # noqa: E731
    models = {"B": eo.fsb.hgb().fit(Xt, yt, sample_weight=norm(wt)), "B-big": big().fit(Xt, yt, sample_weight=norm(wt))}
    thr = {k: eo.heldout_threshold(m, Xs[hold], ys[hold], ws[hold], ps[hold]) for k, m in models.items()}
    print("thresholds", thr, flush=True)
    rng = np.random.default_rng(0)
    res = {}
    for k, q in enumerate(names):
        te = pr == k
        Xq, yq, wq = Xr[te], yr[te], wr[te]
        # domain classifier: synthetic (0) vs target rows (1), balanced subsample of synthetic
        sub = rng.choice(len(Xt), min(len(Xt), 20 * len(Xq) + 20000), replace=False)
        Xd = np.vstack([Xt[sub], Xq]); yd = np.r_[np.zeros(len(sub)), np.ones(len(Xq))]
        wd = np.r_[np.full(len(sub), len(Xq) / len(sub)), np.ones(len(Xq))]
        dc = HistGradientBoostingClassifier(max_iter=100, max_depth=3, random_state=0).fit(Xd, yd, sample_weight=wd)
        logit = dc.decision_function(Xt)
        iw = np.exp(0.5 * (logit - logit.max()))           # tempered density ratio (alpha = 0.5), max weight 1
        iw = np.minimum(iw, np.quantile(iw, 0.99)); iw = iw / iw.mean()
        ess = iw.sum() ** 2 / (iw ** 2).sum() / len(iw)
        row = {"ess": float(ess)}
        fitted = dict(models)
        fitted["B-iw"] = eo.fsb.hgb().fit(Xt, yt, sample_weight=norm(wt * iw))
        fitted["B-iw-big"] = big().fit(Xt, yt, sample_weight=norm(wt * iw))
        for tag, m in fitted.items():
            t = thr.get(tag, thr["B-big" if "big" in tag else "B"])
            s = m.predict_proba(Xq)[:, 1]
            c = eo.f1_curve(s, yq, wq)
            row[tag] = dict(f1=float(c[list(eo.GRID).index(t)]), oracle=float(c.max()),
                            ap=float(average_precision_score(yq, s, sample_weight=wq)))
        res[q] = row
        print(f"{q:10s} ess {ess:.2f}  " + "  ".join(f"{t}: f1 {row[t]['f1']:.3f} or {row[t]['oracle']:.3f} ap {row[t]['ap']:.3f}"
                                                for t in ("B", "B-big", "B-iw", "B-iw-big")), flush=True)
    for t in ("B", "B-big", "B-iw", "B-iw-big"):
        print(f"mean {t:9s} f1 {np.mean([res[q][t]['f1'] for q in names]):.3f}  oracle {np.mean([res[q][t]['oracle'] for q in names]):.3f}"
              f"  ap {np.mean([res[q][t]['ap'] for q in names]):.3f}")
    off = json.loads((HERE / "rows/offline_v3.json").read_text())
    print(f"reference A (real LOPO) f1 {np.mean([off[q]['A']['f1'] for q in names]):.3f}  ap {np.mean([off[q]['A']['ap'] for q in names]):.3f}")
    out.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
