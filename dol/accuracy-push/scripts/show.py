"""Show annotated messages with truth vs predicted edges: show.py <protocol> [n] [family]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh
p = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
fam = sys.argv[3] if len(sys.argv) > 3 else None
pr = qh.load(p)
import os, pickle
if os.environ.get('PRED'):
    pred = pickle.load(open(qh.OUT / 'preds' / f"{os.environ['PRED']}-{p}.pkl", 'rb'))
else:
    pred = qh.family_file(pr, qh.GS / 'families' / p / '05_families.exp-gated-stage1-msgsel.json')
def seg(b, edges):
    cuts = [0] + sorted(e for e in edges if 0 < e < len(b)) + [len(b)]
    return ' '.join(b[a:c].hex() for a, c in zip(cuts, cuts[1:]))
shown = 0; seen = set()
for mid in pr.order:
    if mid not in pr.ann: continue
    m = pr.msgs[mid]
    if fam and m['family'] != fam: continue
    key = (m['family'], len(m['payload']))
    if key in seen: continue
    seen.add(key)
    b = m['payload'][:80]
    print(f"{m['family']} len {len(m['payload'])} dir {m['direction']}")
    print('  truth', seg(b, pr.ann[mid]))
    print('  pred ', seg(b, pred[mid]))
    shown += 1
    if shown >= n: break
