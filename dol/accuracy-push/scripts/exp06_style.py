"""Exp 06: family-level style descriptors (label-free) appended to every row of the family's groups.
Stage-1 group model (compare with exp02: 0.632 pure / 0.641 open).
Usage: exp06_style.py"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm, pred

data, prs, ctxs = gm.setup()


def style(payloads):
    M, lens, full = pred.v2.to_matrix(payloads[:3000])
    valid, st = pred.v2.column_stats(M, lens, full)
    L = int(min(np.median(lens), pred.MAXLEN))
    H, zero = st['H'][:L], st['zero'][:L]
    var = H > 0.05
    zc = (zero > 0.98)
    le = [i for i in range(L - 1) if var[i] and zc[i + 1]]
    be = [i for i in range(1, L) if var[i] and zc[i - 1]]
    n = max(1, L)
    le4 = sum(1 for i in le if i + 3 < L and zc[i + 1:i + 4].all()) / max(1, len(le))
    return [len(le) / n, len(be) / n, le4, np.mean([i % 4 == 0 for i in le]) if le else 0.0,
            np.mean([i % 2 == 0 for i in le]) if le else 0.0, float(st['ascii'][:L].mean()), float(H.mean()),
            float(zc.mean()), np.log2(1 + np.median(lens)) / 12, float(np.std(lens) / max(1, np.mean(lens)))]


for p in qh.PROTOS:
    pr = prs[p]
    desc = {}
    for g in data[p]:
        fam = g['fam']
        if fam not in desc:
            fm = pr.families.get(fam) or [m for m in pr.order if pr.msgs[m]['family'] in (None, 'noise')]
            desc[fam] = style([pr.msgs[m]['payload'] for m in fm])
        g['XS'] = np.hstack([g['X'], np.tile(desc[fam], (len(g['offs']), 1))])
sc = gm.lopo_scores('exp06-style', data, feat=lambda g: g['XS'])
for mode in ('pure', 'open'):
    res, thr, _ = gm.shared_threshold(sc, mode)
    print(qh.report(res, f'exp06 style {mode} thr {sorted(set(thr.values()))}'))
