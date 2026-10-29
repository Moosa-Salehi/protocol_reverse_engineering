"""Ceilings: majority-truth edges per family vs per sub-family (refine), per-message scored.
Usage: oracle.py [protocols]"""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, pred
protos = sys.argv[1].split(',') if len(sys.argv) > 1 else qh.PROTOS
res = {k: {} for k in ('family', 'sub2', 'sub3', 'sub-len')}
def majority(pr, g):
    a = [m for m in g if m in pr.ann]
    if not a: return set()
    c = Counter(e for m in a for e in pr.ann[m])
    reach = Counter(o for m in a for o in range(1, len(pr.msgs[m]['payload'])))
    return {e for e, k in c.items() if k >= 0.5 * reach[e]}
for p in protos:
    pr = qh.load(p)
    for name, groups_of in (('family', lambda mids: [mids]),
                            ('sub2', lambda mids: pred.refine(pr, mids, depth=2)),
                            ('sub3', lambda mids: pred.refine(pr, mids, depth=4, min_size=10, min_gain=0.05)),
                            ('sub-len', None)):
        out = {}
        for fam, mids in pr.families.items():
            if groups_of is None:
                by = {}
                for m in mids: by.setdefault(len(pr.msgs[m]['payload']), []).append(m)
                groups = list(by.values())
            else:
                groups = groups_of(mids)
            for g in groups:
                e = majority(pr, g)
                for m in g:
                    if m in pr.ann: out[m] = e
        res[name][p] = qh.score(pr, out)
    print(p, ' '.join(f"{k} {res[k][p]['f1']:.3f}" for k in res), flush=True)
for k, r in res.items():
    print(qh.report(r, 'oracle ' + k).splitlines()[-1])
