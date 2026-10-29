"""Truth-file scores for the 14-protocol runs: per protocol, macro, paired bootstrap vs baseline.

Usage: summarize_truth14.py   -> dol/global-segmentation/truth-eval-14-summary.{json,txt}
"""
import json
from pathlib import Path

import numpy as np

OUT = Path('/mnt/d/tez/practical/protocol_re/dol/global-segmentation')
PROTOS = 'modbus,bacnet,cip,dnp3,enip,ethercat,goose,hart_ip,iec104,mms,opcua,powerlink,s7comm,zigbee'.split(',')
VARIANTS = ('baseline', 'learned-gated', 'learned-gated8')
METRICS = (('overall', None), ('bnd', 'field_boundary'), ('sem', 'field_semantics'), ('role', 'field_roles'))


def load(v, p):
    path = OUT / 'truth-eval-14' / v / p / 'data' / '15_evaluation_result.json'
    if not path.exists():
        return None
    r = json.load(open(path))
    return {k: (r['summary']['overall_score'] if m is None else r['metrics'][m]['f1_score']) for k, m in METRICS}


def main():
    table = {v: {p: load(v, p) for p in PROTOS} for v in VARIANTS}
    lines = [f"{'protocol':10s} " + ' '.join(f'{v + " overall/bnd/sem":>34s}' for v in VARIANTS)]
    for p in PROTOS:
        cells = []
        for v in VARIANTS:
            r = table[v][p]
            cells.append((f"{r['overall']:.3f} / {r['bnd']:.3f} / {r['sem']:.3f}" if r else 'missing').rjust(34))
        lines.append(f'{p:10s} ' + ' '.join(cells))
    done = [p for p in PROTOS if all(table[v][p] for v in VARIANTS)]
    lines.append(f"{'macro (' + str(len(done)) + ')':10s} " + ' '.join(
        f"{np.mean([table[v][p]['overall'] for p in done]):.3f} / {np.mean([table[v][p]['bnd'] for p in done]):.3f} / {np.mean([table[v][p]['sem'] for p in done]):.3f}".rjust(34)
        for v in VARIANTS))
    rng = np.random.default_rng(20261016)
    idx = rng.integers(0, len(done), size=(10000, len(done)))
    lines.append('')
    for v in VARIANTS[1:]:
        for k, _ in METRICS:
            d = np.array([table[v][p][k] - table['baseline'][p][k] for p in done])
            lo, hi = np.percentile(d[idx].mean(1), [2.5, 97.5])
            lines.append(f'{v:16s} {k:8s} diff {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]  up {(d > 0.005).sum()} / down {(d < -0.005).sum()}')
    text = '\n'.join(lines)
    print(text)
    (OUT / 'truth-eval-14-summary.txt').write_text(text + '\n', encoding='utf-8')
    json.dump(table, open(OUT / 'truth-eval-14-summary.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
