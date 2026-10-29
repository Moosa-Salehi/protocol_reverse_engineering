"""Exp 17 (different setting: FEW-SHOT). For held-out H, k annotated messages of H (random, seed fixed) are
revealed; group labels are computed from those messages only and H's groups that contain them are added to
the training set (weight BETA x one benchmark protocol). Scoring uses ONLY H's other annotated messages.
Stage-1 group model, open + strings, threshold shared as usual (chosen on the other 13 zero-shot curves).
Usage: exp17_fewshot.py [k,...] [beta]"""
import pickle
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import plans as PL  # noqa: E402
import post  # noqa: E402

KS = [int(k) for k in (sys.argv[1].split(',') if len(sys.argv) > 1 else ['1', '5', '20'])]
BETA = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
import os
STRAT = bool(os.environ.get('STRAT'))          # spread the k messages over (family, length) groups
MODE = os.environ.get('MODE', 'open')
data, prs, ctxs = gm.setup()
P = {p: PL.plans(p) for p in qh.PROTOS}
base = gm.lopo_scores('exp02', data)
base_res = gm.evaluate(base, 'open', label='exp02 zero-shot open +strings')
thr = {p: base_res[p]['thr'] for p in qh.PROTOS}


def few_labels(pr, g, seen):
    a = [m for m in g['mids'] if m in seen]
    if not a:
        return None
    c = Counter(e for m in a for e in pr.ann[m])
    reach = Counter(o for m in a for o in range(1, len(pr.msgs[m]['payload'])))
    return np.array([c[o] >= 0.5 * max(1, reach[o]) and reach[o] > 0 for o in g['offs']]), np.array([reach[o] > 0 for o in g['offs']])


for k in KS:
    res = {}
    for H in qh.PROTOS:
        pr = prs[H]
        rnd = random.Random(20261017)
        if STRAT:
            # round-robin over groups (largest first), one random annotated message per group per round
            pools = [sorted(m for m in g['mids'] if m in pr.ann) for g in sorted(data[H], key=lambda g: -g['nann'])]
            pools = [rnd.sample(x, len(x)) for x in pools if x]
            seen, r = set(), 0
            while len(seen) < min(k, len(pr.ann)) and any(len(x) > r for x in pools):
                for x in pools:
                    if len(x) > r and len(seen) < k:
                        seen.add(x[r])
                r += 1
        else:
            seen = set(rnd.sample(sorted(pr.ann), min(k, len(pr.ann))))
        X, y, w = gm.stack(data, [p for p in qh.PROTOS if p != H])
        hx, hy = [], []
        for g in data[H]:
            lab = few_labels(pr, g, seen)
            if lab is None:
                continue
            yy, ok = lab
            hx.append(g['X'][ok]); hy.append(yy[ok])
        if hx:
            hx, hy = np.vstack(hx), np.concatenate(hy)
            hw = np.full(len(hy), BETA * w.sum() / 13 / len(hy))
            X, y, w = np.vstack([X, hx]), np.concatenate([y, hy]), np.concatenate([w, hw])
        m = gm.hgb().fit(X, y, sample_weight=w)
        sc = [m.predict_proba(g['X'])[:, 1] for g in data[H]]
        pm = gm.pred_msgs(H, sc, thr[H], MODE)
        pm = {mm: post.apply_plan(e, P[H][mm]) for mm, e in pm.items() if mm not in seen}
        # score on the unseen annotated messages only
        sub = qh.Proto.__new__(qh.Proto)
        sub.__dict__.update(pr.__dict__)
        sub.ann = {mm: t for mm, t in pr.ann.items() if mm not in seen}
        res[H] = qh.score(sub, pm)
        print(H, k, f"{res[H]['f1']:.3f}", flush=True)
    print(qh.report(res, f'exp17 FEW-SHOT k={k} beta={BETA} strat={STRAT} mode={MODE} (stage 1, +strings)'), flush=True)
