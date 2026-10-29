"""Realism check of synthetic rows against the real training rows: domain-classifier AUC on unseen protocols and the
mean of the most shifted features (distinct ratio, top-value share). usage: realism.py <syn.npz> [...]"""
import sys
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
real = np.load(ROOT / "assets/pre_trained/fewshot_boundary_training.npz")
Xr, pr = real["X"], real["proto"]
for path in sys.argv[1:]:
    d = np.load(path); Xs, ps = d["X"], d["proto"]
    rng = np.random.default_rng(0); n = min(len(Xr), len(Xs), 40000)
    a = rng.choice(len(Xr), n, replace=False); b = rng.choice(len(Xs), n, replace=False)
    X = np.vstack([Xr[a], Xs[b]]); y = np.r_[np.zeros(n), np.ones(n)]; grp = np.r_[pr[a], 1000 + ps[b]]; f = grp % 4 == 0
    auc = roc_auc_score(y[f], HistGradientBoostingClassifier(max_iter=200, random_state=0).fit(X[~f], y[~f]).predict_proba(X[f])[:, 1])
    print(f"{Path(path).name:14s} AUC {auc:.3f}  distinct@i real {Xr[:, 9].mean():.2f} syn {Xs[:, 9].mean():.2f}"
          f"  top@i real {Xr[:, 15].mean():.2f} syn {Xs[:, 15].mean():.2f}  entropy@i real {Xr[:, 3].mean():.2f} syn {Xs[:, 3].mean():.2f}")
