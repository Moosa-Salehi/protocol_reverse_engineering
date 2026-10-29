"""Why did synthetic pretraining not transfer? (1) synthetic->unseen synthetic, (2) real within-protocol (group 5-fold),
(3) cross-protocol real (LOPO, from offline_v2.json), (4) domain classifier synthetic vs real (AUC) + most different features."""
import json, sys
from pathlib import Path
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
sys.path.insert(0, str(Path(__file__).parent))
import eval_offline as eo

def f1_at_best(s, y, w):
    c = eo.f1_curve(s, y, w); return float(c.max())

real = np.load(eo.ROOT / "assets/pre_trained/fewshot_boundary_training.npz")
names = [str(x) for x in real["protocols"]]
Xr, yr, wr, pr = real["X"], real["y"], real["weight"].astype(float), real["proto"]
d = np.load("rows/v2a.npz"); keep = d["proto"] < 250
Xs, ys, ws, ps = d["X"][keep], d["y"][keep], d["weight"][keep].astype(float), d["proto"][keep]
fit = lambda X, y, w: eo.fsb.hgb().fit(X, y, sample_weight=w * len(w) / w.sum())

# (1) synthetic -> unseen synthetic protocols
tr, te = ps % 5 != 0, ps % 5 == 0
m = fit(Xs[tr], ys[tr], ws[tr]); s = m.predict_proba(Xs[te])[:, 1]
syn_scores = [f1_at_best(s[ps[te] == k], ys[te][ps[te] == k], ws[te][ps[te] == k]) for k in np.unique(ps[te])]
print(f"(1) synthetic -> unseen synthetic: mean best-threshold F1 {np.mean(syn_scores):.3f} over {len(syn_scores)} protocols")

# (2) real within protocol: 5 folds over row blocks (groups are contiguous rows)
within = {}
for k, q in enumerate(names):
    idx = np.where(pr == k)[0]
    if len(idx) < 200: continue
    fold = (np.arange(len(idx)) * 5 // len(idx))
    sc = np.zeros(len(idx))
    for f in range(5):
        a, b = idx[fold != f], idx[fold == f]
        if yr[a].sum() == 0: continue
        sc[fold == f] = fit(Xr[a], yr[a], wr[a]).predict_proba(Xr[b])[:, 1]
    within[q] = f1_at_best(sc, yr[idx], wr[idx])
off = json.loads(Path("rows/offline_v2.json").read_text())
print("(2) real within-protocol vs (3) real cross-protocol (LOPO) vs synthetic-only, best-threshold F1:")
for q in names:
    if q in within:
        print(f"    {q:10s} within {within[q]:.3f}   cross {off[q]['A']['oracle']:.3f}   syn-only {off[q]['B']['oracle']:.3f}")
print(f"    mean       within {np.mean(list(within.values())):.3f}   cross {np.mean([off[q]['A']['oracle'] for q in within]):.3f}"
      f"   syn-only {np.mean([off[q]['B']['oracle'] for q in within]):.3f}")

# (4) domain classifier
rng = np.random.default_rng(0)
n = min(len(Xr), len(Xs)); a = rng.choice(len(Xr), n, replace=False); b = rng.choice(len(Xs), n, replace=False)
X = np.vstack([Xr[a], Xs[b]]); y = np.r_[np.zeros(n), np.ones(n)]
grp = np.r_[pr[a], 1000 + ps[b]]; f = (grp % 4 == 0)
dc = HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(X[~f], y[~f])
auc = roc_auc_score(y[f], dc.predict_proba(X[f])[:, 1])
print(f"(4) domain classifier synthetic vs real rows (unseen protocols): AUC {auc:.3f}")
# per-feature shift: standardized mean difference
smd = np.abs(Xr.mean(0) - Xs.mean(0)) / (np.sqrt((Xr.var(0) + Xs.var(0)) / 2) + 1e-9)
print("    largest standardized differences (feature index: SMD, real mean, synthetic mean):",
      [(int(i), round(float(smd[i]), 2), round(float(Xr[:, i].mean()), 2), round(float(Xs[:, i].mean()), 2)) for i in np.argsort(-smd)[:8]])
print(f"    boundary rate real {np.average(yr, weights=wr):.3f}  synthetic {np.average(ys, weights=ws):.3f}")
