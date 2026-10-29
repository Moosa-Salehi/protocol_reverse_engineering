"""Test-time self-training of the zero-shot boundary model, offline on the 14 real protocols' rows (target excluded
from training as in the pipeline). The target's own rows are pseudo-labelled from confident predictions
(p >= HI -> edge, p <= LO -> no edge) and added to the training rows with total weight BETA x one protocol unit;
repeated ROUNDS times. Labels of the target are used only for scoring. usage: offline.py"""
import json, sys
from pathlib import Path
import numpy as np
from sklearn.metrics import average_precision_score
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dol/synthetic-pretrain"))
import eval_offline as eo

real = np.load(ROOT / "assets/pre_trained/fewshot_boundary_training.npz")
names = [str(x) for x in real["protocols"]]
thr = dict(zip([str(x) for x in real["zs_threshold_protocols"]], [float(x) for x in real["zs_thresholds"]]))
X, y, w, pr = real["X"], real["y"], real["weight"].astype(float), real["proto"]
CONFIGS = [(0.8, 0.1, 1.0, 1), (0.8, 0.1, 1.0, 2), (0.9, 0.05, 1.0, 2), (0.8, 0.1, 3.0, 2), (0.7, 0.2, 1.0, 2)]
res = {}
for k, q in enumerate(names):
    te = pr == k; tr = ~te
    Xq, yq, wq = X[te], y[te], w[te]
    base = eo.fsb.hgb().fit(X[tr], y[tr], sample_weight=w[tr] * tr.sum() / w[tr].sum())
    s0 = base.predict_proba(Xq)[:, 1]
    def score(s):
        c = eo.f1_curve(s, yq, wq)
        return dict(f1=float(c[list(eo.GRID).index(thr[q])]), oracle=float(c.max()), ap=float(average_precision_score(yq, s, sample_weight=wq)))
    row = {"base": score(s0)}
    for hi, lo, beta, rounds in CONFIGS:
        s = s0
        for _ in range(rounds):
            conf = (s >= hi) | (s <= lo)
            Xa = np.vstack([X[tr], Xq[conf]]); ya = np.r_[y[tr], s[conf] >= hi]
            wt = w[tr]; wpl = wq[conf] / max(1e-12, wq[conf].sum()) * beta     # target pseudo rows = beta protocol units
            wa = np.r_[wt, wpl]; m = eo.fsb.hgb().fit(Xa, ya, sample_weight=wa * len(wa) / wa.sum())
            s = m.predict_proba(Xq)[:, 1]
        row[f"hi{hi}/lo{lo}/b{beta}/r{rounds}"] = score(s)
    res[q] = row
    print(f"{q:10s} " + "  ".join(f"{t}: {v['f1']:.3f}/{v['ap']:.3f}" for t, v in row.items()), flush=True)
for t in res[names[0]]:
    print(f"mean {t:22s} f1 {np.mean([res[q][t]['f1'] for q in names]):.3f}  oracle {np.mean([res[q][t]['oracle'] for q in names]):.3f}  ap {np.mean([res[q][t]['ap'] for q in names]):.3f}")
(Path(__file__).parent / "offline.json").write_text(json.dumps(res, indent=1))
