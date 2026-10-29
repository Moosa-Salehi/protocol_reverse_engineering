"""Exp 01: gated learned edges per sub-family (families split by their most informative byte / length).

Variants: gated (per family, = the 0.594 reference recomputed), sub-gated (per sub-family), with thresholds.
Usage: exp01_subfamilies.py [protocols]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import pred  # noqa: E402

protos = sys.argv[1].split(',') if len(sys.argv) > 1 else qh.PROTOS
variants = {}
for p in protos:
    pr = qh.load(p)
    ctx = pred.Ctx(pr)
    thr = pred.model(p)[1]
    out = {k: {} for k in ('gated', 'sub-gated', 'sub-gated-depth3')}
    for fam, mids in pr.families.items():
        fields = ctx.fields07.get(fam, [])
        offs, q = ctx.scores(mids, fam)
        e_fam = {o for o, s in zip(offs, q) if s >= thr}
        for m in mids:
            if m in pr.ann:
                out['gated'][m] = pred.apply_layout(ctx, m, pred.gated_edges(fields, e_fam))
        for name, depth in (('sub-gated', 2), ('sub-gated-depth3', 3)):
            for g in pred.refine(pr, mids, depth=depth):
                offs, q = ctx.scores(g, fam)
                e = {o for o, s in zip(offs, q) if s >= thr}
                for m in g:
                    if m in pr.ann:
                        out[name][m] = pred.apply_layout(ctx, m, pred.gated_edges(fields, e))
    for k, v in out.items():
        variants.setdefault(k, {})[p] = qh.score(pr, v)
    print(p, ' '.join(f"{k} {variants[k][p]['f1']:.3f}" for k in out), flush=True)
for k, res in variants.items():
    print(qh.report(res, k).splitlines()[-1])
