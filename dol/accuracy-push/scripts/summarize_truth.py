"""Truth-file scores: baseline (dol/global-segmentation/truth-eval-14/baseline) vs variants under
dol/accuracy-push/truth-eval/<tag>. Per protocol overall / boundary / semantics, macro, paired bootstrap.
Usage: summarize_truth.py <tag> [<tag> ...]"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re/dol')
PROTOS = 'modbus,bacnet,cip,dnp3,enip,ethercat,goose,hart_ip,iec104,mms,opcua,powerlink,s7comm,zigbee'.split(',')
KEYS = (('overall', None), ('bnd', 'field_boundary'), ('sem', 'field_semantics'))
runs = {'baseline': ROOT / 'global-segmentation/truth-eval-14/baseline'}
runs.update({t: ROOT / 'accuracy-push/truth-eval' / t for t in sys.argv[1:]})


def load(d, p):
    f = d / p / 'data' / '15_evaluation_result.json'
    if not f.exists():
        return None
    r = json.load(open(f))
    return {k: (r['summary']['overall_score'] if m is None else r['metrics'][m]['f1_score']) for k, m in KEYS}


T = {v: {p: load(d, p) for p in PROTOS} for v, d in runs.items()}
print(f"{'protocol':10s} " + ' '.join(f'{v[:22]:>24s}' for v in runs))
for p in PROTOS:
    print(f'{p:10s} ' + ' '.join((f"{T[v][p]['overall']:.3f}/{T[v][p]['bnd']:.3f}/{T[v][p]['sem']:.3f}" if T[v][p] else 'missing').rjust(24) for v in runs))
done = [p for p in PROTOS if all(T[v][p] for v in runs)]
print(f"{'macro(' + str(len(done)) + ')':10s} " + ' '.join(
    f"{np.mean([T[v][p]['overall'] for p in done]):.3f}/{np.mean([T[v][p]['bnd'] for p in done]):.3f}/{np.mean([T[v][p]['sem'] for p in done]):.3f}".rjust(24) for v in runs))
rng = np.random.default_rng(20261017)
idx = rng.integers(0, len(done), size=(10000, len(done)))
for v in list(runs)[1:]:
    for k, _ in KEYS:
        d = np.array([T[v][p][k] - T['baseline'][p][k] for p in done])
        lo, hi = np.percentile(d[idx].mean(1), [2.5, 97.5])
        print(f'{v:24s} {k:8s} diff {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]  up {(d > 0.005).sum()} / down {(d < -0.005).sum()}')
