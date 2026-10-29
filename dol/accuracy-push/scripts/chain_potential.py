"""Diagnostic (uses labels): which families have an accepted length-prefixed chain, and how well do the
chain's edges match the truth inside the chain region (per convention)."""
import sys
from itertools import combinations
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, chains
CONV = [('tag', 'len', 'val'), ('tag', 'val'), ('tag', 'len'), ('len', 'val'), ('tag',), ('val',)]
for p in qh.PROTOS:
    pr = qh.load(p)
    hits = []; covered = 0; tot = sum(1 for m in pr.ann)
    for fam, mids in pr.families.items():
        pay = [pr.msgs[m]['payload'] for m in mids]
        f = chains.find_format(pay)
        if not f: continue
        fmt, start, sc = f
        a = [m for m in mids if m in pr.ann]
        best = None
        for conv in CONV:
            tp = fp = fn = 0; n = 0
            for m in a:
                b = pr.msgs[m]['payload']; e = chains.chain_edges(b, start, fmt, conv)
                if e is None: continue
                n += 1
                e = {x for x in e if start < x < len(b)}; t = {x for x in pr.ann[m] if x > start}
                tp += len(e & t); fp += len(e - t); fn += len(t - e)
            f1 = 2 * tp / max(1, 2 * tp + fp + fn)
            if best is None or f1 > best[0]: best = (f1, conv, n)
        covered += best[2]
        hits.append(f"{fam}:{fmt}@{start} n={best[2]} F1in={best[0]:.2f} {'/'.join(best[1])}")
    print(f"{p:10s} chain-parsed annotated msgs {covered}/{tot}  " + '; '.join(hits[:4]) + (' ...' if len(hits) > 4 else ''), flush=True)
