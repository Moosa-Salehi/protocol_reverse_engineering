"""How many of the var|var 2|2 and 1|1 misses does the periodic post-process recover?

Reuses dol/boundary-recall-experiments/scripts/error_analysis.py (family-level labels,
messages-weighted) with the periodic family files read from bench/<protocol>/data.
Usage: error_periodic.py <base>:<periodic-variant> [...]
       e.g. learned-v2:loose-learned-v2 base:loose-base
"""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
EA = Path('/mnt/d/tez/practical/protocol_re/dol/boundary-recall-experiments/scripts/error_analysis.py')
spec = importlib.util.spec_from_file_location('ea', EA)
ea = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ea)
_orig = ea.predicted_edges


def predicted_edges(p, suffix):
    if not suffix.startswith('periodic-'):
        return _orig(p, suffix)
    fams = json.load(open(HERE.parent / 'bench' / p / 'data' / f'05_families.exp-{suffix}.json'))
    out = {}
    for fam, d in fams.items():
        e = set()
        for h in d.get('field_hypotheses', []):
            s = int(h.get('start', 0) or 0)
            e.update((s, s + int(h.get('length', 0) or 0)))
        out[fam] = e
    return out


ea.predicted_edges = predicted_edges
KINDS = [('var|var', '2|2'), ('var|var', '1|1')]


def main():
    pairs = [a.split(':') for a in sys.argv[1:]] or [['learned-v2', 'loose-learned-v2'], ['base', 'loose-base']]
    data = {p: ea.v2.load_protocol(p) for p in ea.PROTOS}
    report = {}
    for base, var in pairs:
        print(f'\n===== {base} -> {var}')
        print(f"{'protocol':10s} " + ' '.join(f'{"/".join(k[1:]):>20s}' for k in KINDS) + f"{'all FN':>20s} {'extra FP':>9s}")
        tot = Counter()
        rows = {}
        for p in ea.PROTOS:
            tp0, fn0, fp0 = ea.analyse(p, base, data[p])
            tp1, fn1, fp1 = ea.analyse(p, 'periodic-' + var, data[p])
            truth = tp0 + sum(fn0.values())
            row = {}
            for k in KINDS:
                row[k[1]] = (fn0[k], fn1[k])
                tot[(k[1], 0)] += fn0[k] / truth
                tot[(k[1], 1)] += fn1[k] / truth
            row['all'] = (sum(fn0.values()), sum(fn1.values()))
            row['fp'] = (sum(fp0.values()), sum(fp1.values()))
            tot[('all', 0)] += row['all'][0] / truth
            tot[('all', 1)] += row['all'][1] / truth
            tot[('fp', 0)] += row['fp'][0] / truth
            tot[('fp', 1)] += row['fp'][1] / truth
            rows[p] = {k: list(v) for k, v in row.items()}
            fmt = lambda a, b: f'{a:7.0f}->{b:7.0f} ({(a - b) / a:4.0%})' if a else f'{"-":>20s}'
            print(f'{p:10s} ' + ' '.join(fmt(*row[k[1]]) for k in KINDS) + ' ' + fmt(*row['all']) + f"  {row['fp'][1] - row['fp'][0]:+8.0f}")
        n = len(ea.PROTOS)
        print('protocol-weighted, as share of truth edges: ' + '  '.join(
            f"{k}: {tot[(k, 0)] / n:.3f} -> {tot[(k, 1)] / n:.3f} (recovered {1 - tot[(k, 1)] / max(tot[(k, 0)], 1e-9):.0%})"
            for k in ('2|2', '1|1', 'all')) + f"  FP/truth {tot[('fp', 0)] / n:.3f} -> {tot[('fp', 1)] / n:.3f}")
        report[f'{base}->{var}'] = rows
    json.dump(report, open(HERE.parent / 'error-periodic.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
