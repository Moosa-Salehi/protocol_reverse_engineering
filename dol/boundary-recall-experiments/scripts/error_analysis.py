"""Where do the boundary scorers go wrong?

Works in the family-level label space used for training: an offset is a true
edge when it is a field edge in at least half of the family's messages that
reach it. Every offset of every family is one row, weighted by the family's
message count so large families count as they do in the per-message benchmark.

Missed edges (FN) and extra edges (FP) are classified by the bytes around them:
  const|const   both neighbouring bytes constant inside the family
  const|var     one side constant, the other varying
  var|var       both sides varying
and by the true fields around them (width of the field the edge splits or the
two fields an FN would separate). The per-message share of edges that fall
outside the family-level labels (variable layouts) is reported separately as
the gap between the family-level labels and the per-message truth.

Usage: error_analysis.py <families-file-suffix> [...]   e.g. learned-v2 base
"""
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location('v2', HERE / 'learned_boundaries_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
B, PROTOS = v2.B, v2.PROTOS
H_PREV, H_CUR = 2, 3                      # family entropy of bytes i-1 and i (window i-3 .. i+2)
CH_PREV, CH_CUR = 54 + 1, 54 + 2          # corpus entropy of bytes i-1 and i (window i-2 .. i+1)


def family_sizes(p):
    assign = json.load(open(B / p / 'data' / '02_family_assignments.json'))['assignments']
    return Counter(a['family_id'] for a in assign)


def predicted_edges(p, suffix):
    fams = json.load(open(B / p / 'data' / f'05_families.exp-{suffix}.json'))
    out = {}
    for fam, details in fams.items():
        edges = set()
        for h in details.get('field_hypotheses', []):
            start = int(h.get('start', 0) or 0)
            edges.update((start, start + int(h.get('length', 0) or 0)))
        out[fam] = edges
    return out


def width_class(width):
    return '1' if width == 1 else '2' if width == 2 else '3-4' if width <= 4 else '5+'


def analyse(p, suffix, data):
    sizes = family_sizes(p)
    pred = predicted_edges(p, suffix)
    fn, fp, tp = Counter(), Counter(), 0.0
    for fam, (X, offs, y) in data.items():
        w = sizes.get(fam, 1)
        true_edges = [0] + [o for o, t in zip(offs, y) if t] + [offs[-1] + 1]
        edges_pred = pred.get(fam, set())
        for k, (o, t) in enumerate(zip(offs, y)):
            const_prev = X[k, H_PREV] < 1e-9
            const_cur = X[k, H_CUR] < 1e-9
            local = 'const|const' if const_prev and const_cur else 'var|var' if not (const_prev or const_cur) else 'const|var'
            if const_prev and const_cur and not (X[k, CH_PREV] < 1e-9 and X[k, CH_CUR] < 1e-9):
                local = 'const|const (varies in corpus)'
            hit = o in edges_pred
            if t and hit:
                tp += w
            elif t:
                left = o - max(e for e in true_edges if e < o)
                right = min(e for e in true_edges if e > o) - o
                fn[(local, f'{width_class(left)}|{width_class(right)}')] += w
            elif hit:
                start = max(e for e in true_edges if e < o)
                end = min(e for e in true_edges if e > o)
                fp[(local, f'inside {width_class(end - start)}-byte field')] += w
    return tp, fn, fp


def main():
    suffixes = sys.argv[1:] or ['learned-v2', 'base']
    data = {p: v2.load_protocol(p) for p in PROTOS}
    report = {}
    for suffix in suffixes:
        total_fn, total_fp, total_tp = Counter(), Counter(), 0.0
        per_protocol = {}
        for p in PROTOS:
            tp, fn, fp = analyse(p, suffix, data[p])
            n_fn, n_fp = sum(fn.values()), sum(fp.values())
            per_protocol[p] = {'tp': tp, 'fn': n_fn, 'fp': n_fp,
                               'recall': tp / max(tp + n_fn, 1), 'precision': tp / max(tp + n_fp, 1),
                               'fn_by_kind': {' / '.join(k): v for k, v in fn.most_common()},
                               'fp_by_kind': {' / '.join(k): v for k, v in fp.most_common()}}
            # normalise per protocol so each protocol counts equally in the totals
            scale = 1.0 / max(tp + n_fn + n_fp, 1)
            total_tp += tp * scale
            for k, v in fn.items():
                total_fn[k] += v * scale
            for k, v in fp.items():
                total_fp[k] += v * scale
        report[suffix] = per_protocol
        nf, np_ = sum(total_fn.values()), sum(total_fp.values())
        print(f'\n===== {suffix}: family-level recall {total_tp / (total_tp + nf):.2f}, precision {total_tp / (total_tp + np_):.2f} (protocols weighted equally)')
        print('  missed edges (FN), share of all FN:')
        for (local, ctx), v in sorted(total_fn.items(), key=lambda kv: -kv[1])[:10]:
            print(f'    {v / nf:5.0%}  {local:32s} between fields of width {ctx}')
        by_local = Counter()
        for (local, _), v in total_fn.items():
            by_local[local] += v
        print('    by neighbourhood: ' + ', '.join(f'{k} {v / nf:.0%}' for k, v in by_local.most_common()))
        print('  extra edges (FP), share of all FP:')
        for (local, ctx), v in sorted(total_fp.items(), key=lambda kv: -kv[1])[:8]:
            print(f'    {v / np_:5.0%}  {local:32s} {ctx}')
        print('  per protocol (family-level):  ' + '  '.join(f"{p} R{r['recall']:.2f}/P{r['precision']:.2f}" for p, r in per_protocol.items()))
    json.dump(report, open(v2.OUT / 'error-analysis.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
