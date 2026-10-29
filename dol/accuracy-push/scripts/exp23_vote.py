"""Exp 23 (FEW-SHOT): multi-neighbour alignment voting. For each unseen message, the NB most similar labelled
messages (same family first; similarity = difflib ratio on the first 512 bytes) each transfer their edges;
an edge is kept when its similarity-weighted vote >= VOTE of the weight of the neighbours that cover that
position; positions no neighbour covers take the saved few-shot model edges (preds/fewshot<k>-<p>.pkl).
Post-processors are chosen per protocol by leave-one-out on the labelled messages (as exp22).
Usage: exp23_vote.py [k] [NB] [VOTE] [protocols]"""
import difflib, itertools, pickle, random, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm, plans as PL

K = int(sys.argv[1]) if len(sys.argv) > 1 else 20
NB = int(sys.argv[2]) if len(sys.argv) > 2 else 3
VOTE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
protos = sys.argv[4].split(',') if len(sys.argv) > 4 else qh.PROTOS
data, prs, ctxs = gm.setup()
POSTS = [gm.post_strings, gm.post_ber, gm.post_crc(False)]
NAMES = ('strings', 'ber', 'crc')


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


def transfer(a, ea, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    out, cov = set(), np.zeros(len(b) + 1, dtype=bool)
    for i, j, n in sm.get_matching_blocks():
        if n:
            cov[j:j + n + 1] = True
            out.update(j + (e - i) for e in ea if i <= e <= i + n)
    return out, cov


def vote(pr, b, fam, pool, byfam, exclude=None):
    cands = [m for m in (byfam.get(fam) or []) if m != exclude] or [m for m in pool if m != exclude]
    sims = sorted(((difflib.SequenceMatcher(None, pr.msgs[m]['payload'][:512], b[:512], autojunk=False).ratio(), m) for m in cands), reverse=True)[:NB]
    score = defaultdict(float); covw = np.zeros(len(b) + 1)
    for s, m in sims:
        e, cov = transfer(pr.msgs[m]['payload'], pr.ann[m], b)
        covw += s * cov
        for x in e:
            score[x] += s
    edges = {x for x, v in score.items() if v >= VOTE * covw[x] and covw[x] > 0}
    return edges, covw > 0


def sub(pr, keep):
    s = qh.Proto.__new__(qh.Proto); s.__dict__.update(pr.__dict__)
    s.ann = {m: t for m, t in pr.ann.items() if m in keep}
    return s


res = {}
for H in protos:
    pr = prs[H]; PP = {H: PL.plans(H)}
    seen = stratified(pr, H, K, random.Random(20261017)); unseen = set(pr.ann) - seen
    model = pickle.load(open(qh.OUT / 'preds' / f'fewshot{K}-{H}.pkl', 'rb'))
    byfam = defaultdict(list)
    for m in seen:
        byfam[pr.msgs[m]['family']].append(m)
    loo = {s_: vote(pr, pr.msgs[s_]['payload'], pr.msgs[s_]['family'], seen, byfam, exclude=s_)[0] for s_ in seen}
    def cfg(c, preds):
        out = {}
        for m_, e_ in preds.items():
            z = set(e_)
            for i in c:
                z = POSTS[i](H, m_, pr.msgs[m_]['payload'], z, PP)
            out[m_] = z
        return out
    subsets = [c for r in range(4) for c in itertools.combinations(range(3), r)]
    chosen = max(subsets, key=lambda c: qh.score(sub(pr, seen), cfg(c, loo))['f1'])
    out = {}
    for u in unseen:
        b = pr.msgs[u]['payload']
        e, cov = vote(pr, b, pr.msgs[u]['family'], seen, byfam)
        out[u] = e | {x for x in model.get(u, ()) if 0 < x < len(b) and not cov[x]}
    out = cfg(chosen, out)
    pickle.dump(out, open(qh.OUT / 'preds' / f'vote{K}-{H}.pkl', 'wb'))
    res[H] = qh.score(sub(pr, unseen), out)
    print(H, f"{res[H]['f1']:.3f}", [NAMES[i] for i in chosen], flush=True)
print(qh.report(res, f'exp23 FEW-SHOT k={K} vote NB={NB} VOTE={VOTE} +selected posts'))
