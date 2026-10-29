"""Exp 14: stage-07 (rules) evidence as features of the group model (learned combination instead of the
hand-made 'open' gate). Features per offset i of a group (family's stage-07 fields):
  is_edge(i), covered(i), width of the stage-07 field containing byte i (and byte i-1), field type one-hot
  of both, is i the start of a field of width >= 3, distance to the previous / next stage-07 edge.
Stage 1 (compare exp02 + strings 0.647 open) and stage 2 (compare exp05-s2 + strings 0.657 open).
Usage: exp14_stack_rules.py [s1|s2]"""
import pickle
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import pred  # noqa: E402

TYPES = ['constant', 'counter_or_transaction_id', 'length', 'keyword', 'flags_or_status', 'blob']
data, prs, ctxs = gm.setup()


def rule_feats(ctx, fam, offs):
    det = ctx.fams07.get(fam) if fam != '__noise__' else None
    hyps = (det or {}).get('field_hypotheses', []) or []
    spans = sorted((int(h['start']), int(h['start']) + int(h['length']), h.get('field_type') or '') for h in hyps)
    edges = sorted({x for a, b, _ in spans for x in (a, b)})
    end = max((b for _, b, _ in spans), default=0)

    def field_at(j):
        for a, b, t in spans:
            if a <= j < b:
                return b - a, t
        return 0, ''
    rows = []
    for i in offs:
        w0, t0 = field_at(i - 1)
        w1, t1 = field_at(i)
        prev = max((e for e in edges if e <= i), default=0)
        nxt = min((e for e in edges if e >= i), default=end)
        rows.append([float(i in edges), float(i < end), min(w0, 32) / 32, min(w1, 32) / 32,
                     *[float(t0 == t) for t in TYPES], *[float(t1 == t) for t in TYPES],
                     float(i in edges and w1 >= 3), min(i - prev, 16) / 16, min(nxt - i, 16) / 16, float(bool(spans))])
    return np.array(rows, dtype=float)


for p in qh.PROTOS:
    for g in data[p]:
        g['XR'] = np.hstack([g['X'], rule_feats(ctxs[p], g['fam'], g['offs'])])

which = sys.argv[1] if len(sys.argv) > 1 else 's1'
if which == 's1':
    sc = gm.lopo_scores('exp14-s1', data, feat=lambda g: g['XR'])
else:
    path = qh.OUT / 'preds' / 'scores-exp14-s2.pkl'
    if path.exists():
        sc = pickle.load(open(path, 'rb'))
    else:
        sc = {}
        for H in qh.PROTOS:
            train = [p for p in qh.PROTOS if p != H]
            oof = {}
            for f in [train[k::4] for k in range(4)]:
                m = gm.hgb().fit(*gm.stack(data, [p for p in train if p not in f], feat=lambda g: g['XR']))
                for p in f:
                    oof[p] = [m.predict_proba(g['XR'])[:, 1] for g in data[p]]
            s1 = gm.hgb().fit(*gm.stack(data, train, feat=lambda g: g['XR']))
            oof[H] = [s1.predict_proba(g['XR'])[:, 1] for g in data[H]]
            for p in train + [H]:
                for g, q in zip(data[p], oof[p]):
                    g['XR2'] = pred.v2.neighbour_features(g['XR'], q)
            s2 = gm.hgb().fit(*gm.stack(data, train, feat=lambda g: g['XR2']))
            sc[H] = [s2.predict_proba(g['XR2'])[:, 1] for g in data[H]]
            print(H, 'done', flush=True)
        pickle.dump(sc, open(path, 'wb'))
for mode in ('pure', 'open'):
    gm.evaluate(sc, mode, label=f'exp14-{which} {mode} +strings', verbose=True)
