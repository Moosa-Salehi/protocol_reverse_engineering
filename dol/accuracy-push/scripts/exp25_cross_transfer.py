"""Exp 25 (ZERO-SHOT): cross-protocol alignment transfer. Shared lower layers (TPKT/COTP, ENIP encapsulation,
BER) carry the same field layout across protocols. For each (family, length) group of the held-out protocol,
a representative message is aligned to the most similar labelled message of the OTHER 13 protocols
(pool: up to POOL annotated messages per protocol, one per (family, length) group first); edges inside
matching blocks of >= MINB bytes are transferred to the group's fixed edges when the ratio >= MINR.
Positions not covered keep the model edges (best zero-shot: exp05-s2, open, strings+BER+CRC).
Usage: exp25_cross_transfer.py [MINB] [MINR]"""
import difflib
import pickle
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import plans as PL  # noqa: E402

MINB = int(sys.argv[1]) if len(sys.argv) > 1 else 6
MINR = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
POOL = 400
data, prs, ctxs = gm.setup()
sc = pickle.load(open(qh.OUT / 'preds' / 'scores-exp05-s2.pkl', 'rb'))
P = {p: PL.plans(p) for p in qh.PROTOS}
POSTS = [gm.post_strings, gm.post_ber, gm.post_crc(False)]

pool = {}
for p in qh.PROTOS:
    rnd = random.Random(1)
    reps = []
    for g in data[p]:
        a = [m for m in g['mids'] if m in prs[p].ann]
        if a:
            reps.append(a[0])
    rest = [m for m in prs[p].ann if m not in set(reps)]
    pool[p] = (reps + rnd.sample(rest, max(0, min(len(rest), POOL - len(reps)))))[:POOL]


def best_other(H, b):
    best = (0.0, None, None)
    sm = difflib.SequenceMatcher(None, autojunk=False)
    sm.set_seq2(b[:128])
    for p in qh.PROTOS:
        if p == H:
            continue
        for m in pool[p]:
            sm.set_seq1(prs[p].msgs[m]['payload'][:128])
            if sm.real_quick_ratio() <= best[0] or sm.quick_ratio() <= best[0]:
                continue
            r = sm.ratio()
            if r > best[0]:
                best = (r, p, m)
    return best


def cross_edges(H, b):
    r, p, m = best_other(H, b)
    if p is None or r < MINR:
        return set(), np.zeros(len(b) + 1, dtype=bool), (r, p)
    a = prs[p].msgs[m]['payload']
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out, cov = set(), np.zeros(len(b) + 1, dtype=bool)
    for i, j, n in sm.get_matching_blocks():
        if n >= MINB:
            cov[j + 1:j + n] = True        # interior of the block: transferred edges decide
            out.update(j + (e - i) for e in prs[p].ann[m] if i < e < i + n)
    return out, cov, (r, p)


thr = {p: r['thr'] for p, r in gm.evaluate_post(sc, POSTS, 'open', label='base exp05-s2 open +posts').items()}
res = {}
for H in qh.PROTOS:
    pr = prs[H]
    out, used = {}, {}
    for g, q in zip(data[H], sc[H]):
        rep = next((m for m in g['mids'] if m in pr.ann), g['mids'][0])
        ce, cov, info = cross_edges(H, pr.msgs[rep]['payload'])
        used[info[1]] = used.get(info[1], 0) + 1
        model = gm.pred_msgs(H, [q], thr[H], 'open') if False else None
        e_model = {o for o, s in zip(g['offs'], q) if s >= thr[H]}
        for m in g['mids']:
            if m not in pr.ann:
                continue
            b = pr.msgs[m]['payload']
            import pred as PR
            base = PR.apply_layout(ctxs[H], m, PR.gated_open(ctxs[H].fields07[g['fam']], e_model, len(b))) if g['fam'] in ctxs[H].fields07 else PR.apply_layout(ctxs[H], m, set(e_model))
            if len(b) == len(pr.msgs[rep]['payload']) and cov.any():
                base = {x for x in base if not (x < len(cov) and cov[x])} | {x for x in ce if x < len(b)}
            for f in POSTS:
                base = f(H, m, b, base, P)
            out[m] = base
    res[H] = qh.score(pr, out)
    print(f"{H:10s} {res[H]['f1']:.3f}  donors {dict(sorted(used.items(), key=lambda kv: -kv[1])[:3])}", flush=True)
print(qh.report(res, f'exp25 ZERO-SHOT cross-protocol transfer MINB={MINB} MINR={MINR} (+exp05-s2 open +posts)'))
