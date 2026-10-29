"""Exp 26 (ZERO-SHOT, user idea): detect the closest known protocol and use its labels.

For each held-out protocol H (truth-convention annotations, ANNSET=truthconv):
  all13      stage-1 group model trained on all 13 other protocols (reference)
  closest-k  model trained only on the k protocols nearest to H (k = 1, 3); nearness is label-free: distance
             between protocols' mean and std of their (message-weighted) group feature rows, z-scored over protocols
  oracle-1   the single source protocol that gives H the best F1 (uses H's labels: the ceiling of the idea)
Per-message F1, pure learned edges (no post-processing), threshold chosen on the other protocols with the same scheme.
Usage: ANNSET=truthconv exp26_closest_protocol.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402

data, prs, ctxs = gm.setup()
P = qh.PROTOS


def signature(p):
    gs = [g for g in data[p]]
    w = np.concatenate([np.full(len(g['offs']), len(g['mids'])) for g in gs]).astype(float)
    X = np.vstack([g['X'] for g in gs])
    mu = (X * w[:, None]).sum(0) / w.sum()
    sd = np.sqrt((((X - mu) ** 2) * w[:, None]).sum(0) / w.sum())
    return np.concatenate([mu, sd])


S = np.array([signature(p) for p in P])
Z = (S - S.mean(0)) / (S.std(0) + 1e-9)
D = np.linalg.norm(Z[:, None, :] - Z[None, :, :], axis=2)
nearest = {p: [P[j] for j in np.argsort(D[i]) if P[j] != p] for i, p in enumerate(P)}
print('nearest known protocol (label-free):', {p: nearest[p][:3] for p in P}, flush=True)

# single-source models: scores of every target under a model trained on one protocol
single = {}
for src in P:
    m = gm.hgb().fit(*gm.stack(data, [src]))
    for tgt in P:
        if tgt != src:
            single[(src, tgt)] = [m.predict_proba(g['X'])[:, 1] for g in data[tgt]]
    print('trained on', src, flush=True)
all13 = gm.lopo_scores('exp02', data)


def scheme(k):
    return {H: [np.mean([single[(s, H)][i] for s in nearest[H][:k]], axis=0) for i in range(len(data[H]))] for H in P}


results = {'all13': gm.evaluate_post(all13, [], 'pure', label='all13 (train on the 13 others)', verbose=True)}
for k in (1, 3):
    results[f'closest-{k}'] = gm.evaluate_post(scheme(k), [], 'pure', label=f'closest-{k} (label-free nearest protocols)', verbose=True)

# oracle: best single source per target, at that pair's best threshold (optimistic ceiling)
oracle = {}
for H in P:
    best = (0.0, None)
    for s in P:
        if s == H:
            continue
        for t in gm.TH:
            f = qh.score(prs[H], gm.pred_msgs(H, single[(s, H)], t, 'pure'))['f1']
            if f > best[0]:
                best = (f, s)
    oracle[H] = best
print('oracle best single source per protocol:', {H: (round(f, 3), s) for H, (f, s) in oracle.items()})
print(f"oracle-1 macro {np.mean([f for f, _ in oracle.values()]):.3f}  >=0.70: {sum(f >= 0.7 for f, _ in oracle.values())}/14")
print('label-free nearest == oracle source:', sum(nearest[H][0] == oracle[H][1] for H in P), 'of 14')
