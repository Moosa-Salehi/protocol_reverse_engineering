"""Error categories for a saved prediction set: errors.py <pred-name>
FP: predicted edge strictly inside a truth field (width w, byte pattern); FN: truth edge strictly inside a
predicted piece (width w). Shares are protocol-weighted (each protocol 1/14)."""
import pickle, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh
name = sys.argv[1]
tot = defaultdict(float); perp = {}
def wcat(w): return str(w) if w <= 4 else ('5-8' if w <= 8 else '9+')
for p in qh.PROTOS:
    pr = qh.load(p); pred = pickle.load(open(qh.OUT / 'preds' / f'{name}-{p}.pkl', 'rb'))
    c = Counter(); n = 0
    for mid, truth in pr.ann.items():
        b = pr.msgs[mid]['payload']; L = len(b)
        t = sorted(set(truth)); e = sorted(x for x in pred.get(mid, ()) if 0 < x < L)
        tc = [0] + t + [L]; ec = [0] + e + [L]
        for x in set(e) - set(t):
            a = max(q for q in tc if q < x); z = min(q for q in tc if q > x)
            w = z - a
            zero_hi = all(v == 0 for v in b[x:z]) and any(v != 0 for v in b[a:x])
            c['FP in truth w=' + wcat(w) + (' (LE-int pattern)' if zero_hi else '')] += 1; n += 1
        for x in set(t) - set(e):
            a = max(q for q in ec if q < x); z = min(q for q in ec if q > x)
            c['FN in pred w=' + wcat(z - a)] += 1; n += 1
    perp[p] = {k: v / max(n, 1) for k, v in c.items()}
    for k, v in perp[p].items(): tot[k] += v / len(qh.PROTOS)
for k, v in sorted(tot.items(), key=lambda kv: -kv[1])[:16]:
    top = sorted(qh.PROTOS, key=lambda p: -perp[p].get(k, 0))[:4]
    print(f'{v:6.1%}  {k:36s}  most in: ' + ', '.join(f'{p} {perp[p].get(k,0):.0%}' for p in top))
