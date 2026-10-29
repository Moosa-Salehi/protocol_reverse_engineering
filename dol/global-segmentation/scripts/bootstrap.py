"""Paired bootstrap over protocols: macro-F1 difference of each variant to a reference.

Usage: bootstrap.py <results.json> [<results.json> ...]   (variants are prefixed by the file tag)
"""
import json
import sys
from pathlib import Path

import numpy as np

rng = np.random.default_rng(20261016)
table = {}
for path in sys.argv[1:]:
    tag = Path(path).stem.replace('results', '') or '-base'
    for p, res in json.load(open(path)).items():
        for v, r in res.items():
            table.setdefault(f'{v}{tag}', {})[p] = r['f1']
protos = sorted(next(iter(table.values())))
ref = 'v2-base' if 'v2-base' in table else next(iter(table))
idx = rng.integers(0, len(protos), size=(10000, len(protos)))
print(f"reference {ref}: macro {np.mean([table[ref][p] for p in protos]):.3f}")
for v in table:
    if v == ref or set(table[v]) != set(protos):
        continue
    d = np.array([table[v][p] - table[ref][p] for p in protos])
    boot = d[idx].mean(1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    wins = int((d > 0.005).sum()); losses = int((d < -0.005).sum())
    print(f'{v:28s} macro {np.mean([table[v][p] for p in protos]):.3f}  diff {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]  up {wins} / down {losses}')
