"""Offset-level evaluation of the zero-shot boundary model on the 14 real protocols' labelled rows (no pipeline):
  A  real-LOPO   trained on the other 13 real protocols, threshold = shipped LOPO threshold (current default)
  B  syn         trained on synthetic protocols only, threshold chosen on held-out synthetic protocols
  C  syn+real    synthetic + the other 13 real protocols (synthetic total weight = real total weight),
                 threshold chosen on held-out synthetic protocols
Metrics per protocol: F1 at the chosen threshold, oracle F1 (best threshold, an upper bound), average precision.
Rows are weighted as in fewshot_boundaries.zeroshot_thresholds (labelled messages per group).

usage: eval_offline.py <syn.npz>[,<syn2.npz>...] [out.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
from sklearn.metrics import average_precision_score  # noqa: E402

from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402

GRID = fsb.TH_GRID


def load(paths):
    Xs, ys, ws, ps = [], [], [], []
    off = 0
    for p in paths:
        d = np.load(p)
        Xs.append(d["X"]); ys.append(d["y"]); ws.append(d["weight"]); ps.append(d["proto"].astype(np.int32) + off)
        off += len(d["protocols"])
    return np.vstack(Xs), np.concatenate(ys), np.concatenate(ws), np.concatenate(ps), off


def f1_curve(s, y, w):
    out = []
    for t in GRID:
        pr = s >= t
        tp = w[pr & y].sum(); fp = w[pr & ~y].sum(); fn = w[~pr & y].sum()
        out.append(2 * tp / max(1e-12, 2 * tp + fp + fn))
    return np.array(out)


def heldout_threshold(model, Xh, yh, wh, ph):
    # mean over held-out synthetic protocols of their F1 curve
    s = model.predict_proba(Xh)[:, 1]
    curves = [f1_curve(s[ph == k], yh[ph == k], wh[ph == k]) for k in np.unique(ph)]
    return float(GRID[int(np.argmax(np.mean(curves, axis=0)))])


def main():
    syn_paths = sys.argv[1].split(",")
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "offline.json"
    real = np.load(ROOT / "assets/pre_trained/fewshot_boundary_training.npz")
    names = [str(x) for x in real["protocols"]]
    thr_real = dict(zip([str(x) for x in real["zs_threshold_protocols"]], [float(x) for x in real["zs_thresholds"]]))
    Xr, yr, wr, pr = real["X"], real["y"], real["weight"].astype(float), real["proto"]
    Xs, ys, ws, ps, nsyn = load(syn_paths)
    hold = ps % 10 == 0                                  # 10% of synthetic protocols for the threshold
    Xh, yh, wh, ph = Xs[hold], ys[hold], ws[hold], ps[hold]
    Xt, yt, wt = Xs[~hold], ys[~hold], ws[~hold].astype(float)
    ntrain = len(np.unique(ps[~hold]))
    print(f"real rows {len(yr)}  synthetic train rows {len(yt)} ({ntrain} protocols)  held-out {len(yh)}", flush=True)

    mB = fsb.hgb().fit(Xt, yt, sample_weight=wt * len(wt) / wt.sum())
    tB = heldout_threshold(mB, Xh, yh, wh, ph)
    print(f"B threshold {tB}", flush=True)
    res = {}
    for k, q in enumerate(names):
        te = pr == k
        Xq, yq, wq = Xr[te], yr[te], wr[te]
        tr = ~te
        # A
        wa = wr[tr]; mA = fsb.hgb().fit(Xr[tr], yr[tr], sample_weight=wa * len(wa) / wa.sum())
        # C: per-protocol unit weights; synthetic rows scaled so their total equals the 13 real units
        wc_real = wr[tr]                                  # each real protocol sums to 1
        wc_syn = wt * (13.0 / ntrain)                     # each synthetic protocol sums to 13/ntrain
        Xc = np.vstack([Xr[tr], Xt]); yc = np.concatenate([yr[tr], yt]); wc = np.concatenate([wc_real, wc_syn])
        mC = fsb.hgb().fit(Xc, yc, sample_weight=wc * len(wc) / wc.sum())
        tC = heldout_threshold(mC, Xh, yh, wh, ph)
        row = {}
        for tag, m, t in (("A", mA, thr_real[q]), ("B", mB, tB), ("C", mC, tC)):
            s = m.predict_proba(Xq)[:, 1]
            c = f1_curve(s, yq, wq)
            row[tag] = dict(f1=float(c[list(GRID).index(t)]), oracle=float(c.max()), t=t,
                            ap=float(average_precision_score(yq, s, sample_weight=wq)))
        res[q] = row
        print(f"{q:10s} " + "  ".join(f"{t}: f1 {row[t]['f1']:.3f} or {row[t]['oracle']:.3f} ap {row[t]['ap']:.3f}" for t in "ABC"), flush=True)
    for t in "ABC":
        print(f"mean {t}: f1 {np.mean([res[q][t]['f1'] for q in names]):.3f}  oracle {np.mean([res[q][t]['oracle'] for q in names]):.3f}"
              f"  ap {np.mean([res[q][t]['ap'] for q in names]):.3f}")
    out.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
