"""Exp 20 (FEW-SHOT setting): stratified k labelled messages of the target protocol + structural post-processing.
Model: stage-1 group model trained on the other 13 protocols + the target's labelled groups (weight BETA).
Prediction: pure learned edges per group, TLV layouts (stage 07 + fallback) unless NOLAYOUT, then strings,
embedded BER, CRC blocks. Threshold: 'shared' (zero-shot choice on the other 13) or 'seen' (best F1 on the
k labelled messages themselves). Scoring on the target's UNSEEN annotated messages only.
Usage: [NOLAYOUT=1] exp20_fewshot_post.py [k,...] [beta]"""
import os
import pickle
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import pred  # noqa: E402
import plans as PL  # noqa: E402

KS = [int(k) for k in (sys.argv[1].split(',') if len(sys.argv) > 1 else ['5', '20', '50'])]
BETA = float(sys.argv[2]) if len(sys.argv) > 2 else 3.0
NOLAYOUT = bool(os.environ.get('NOLAYOUT'))
data, prs, ctxs = gm.setup()
P = {p: PL.plans(p) for p in qh.PROTOS}
zero = gm.lopo_scores('exp02', data)
shared_thr = {p: r['thr'] for p, r in gm.evaluate(zero, 'pure', strings=True, label='exp02 zero-shot pure +strings').items()}
POSTS = [gm.post_strings, gm.post_ber, gm.post_crc(False)]


def stratified(pr, H, k, rnd):
    pools = [sorted(m for m in g['mids'] if m in pr.ann) for g in sorted(data[H], key=lambda g: -g['nann'])]
    pools = [rnd.sample(x, len(x)) for x in pools if x]
    seen, r = set(), 0
    while len(seen) < min(k, len(pr.ann)) and any(len(x) > r for x in pools):
        for x in pools:
            if len(x) > r and len(seen) < k:
                seen.add(x[r])
        r += 1
    return seen


def predict(H, sc, t, mids):
    pr, ctx = prs[H], ctxs[H]
    out = {}
    for g, q in zip(data[H], sc):
        e = {o for o, s in zip(g['offs'], q) if s >= t}
        for m in g['mids']:
            if m not in mids:
                continue
            b = pr.msgs[m]['payload']
            em = set(e) if NOLAYOUT else pred.apply_layout(ctx, m, set(e))
            for f in POSTS:
                em = f(H, m, b, em, P)
            out[m] = em
    return out


def sub(pr, keep):
    s = qh.Proto.__new__(qh.Proto)
    s.__dict__.update(pr.__dict__)
    s.ann = {m: t for m, t in pr.ann.items() if m in keep}
    return s


for k in KS:
    res = {'shared': {}, 'seen': {}}
    for H in qh.PROTOS:
        pr = prs[H]
        seen = stratified(pr, H, k, random.Random(20261017))
        X, y, w = gm.stack(data, [p for p in qh.PROTOS if p != H])
        hx, hy = [], []
        for g in data[H]:
            a = [m for m in g['mids'] if m in seen]
            if not a:
                continue
            c = Counter(e for m in a for e in pr.ann[m])
            reach = Counter(o for m in a for o in range(1, len(pr.msgs[m]['payload'])))
            ok = np.array([reach[o] > 0 for o in g['offs']])
            yy = np.array([c[o] >= 0.5 * max(1, reach[o]) for o in g['offs']])
            hx.append(g['X'][ok]); hy.append(yy[ok])
        hx, hy = np.vstack(hx), np.concatenate(hy)
        hw = np.full(len(hy), BETA * w.sum() / 13 / len(hy))
        m = gm.hgb().fit(np.vstack([X, hx]), np.concatenate([y, hy]), sample_weight=np.concatenate([w, hw]))
        sc = [m.predict_proba(g['X'])[:, 1] for g in data[H]]
        unseen = set(pr.ann) - seen
        res['shared'][H] = qh.score(sub(pr, unseen), predict(H, sc, shared_thr[H], unseen))
        t_seen = max(gm.TH, key=lambda t: qh.score(sub(pr, seen), predict(H, sc, t, seen))['f1'])
        pm_seen = predict(H, sc, t_seen, unseen)
        res['seen'][H] = qh.score(sub(pr, unseen), pm_seen)
        if os.environ.get('SAVE'):
            pickle.dump(pm_seen, open(qh.OUT / 'preds' / f'fewshot{k}-{H}.pkl', 'wb'))
        print(H, k, f"shared {res['shared'][H]['f1']:.3f} seen-thr {t_seen} {res['seen'][H]['f1']:.3f}", flush=True)
    for v, r in res.items():
        print(qh.report(r, f'exp20 FEW-SHOT k={k} beta={BETA} pure layout={not NOLAYOUT} +strings+BER+CRC thr={v}'), flush=True)
