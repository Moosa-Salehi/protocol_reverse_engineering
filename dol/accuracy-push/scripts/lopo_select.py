"""Leave-one-protocol-out choice of a configuration on the truth-file metric: for each protocol H, the config with
the best mean overall score on the other 13 protocols is chosen, and H is scored with it.
Usage: lopo_select.py <run-name> [<run-name> ...]   (runs under dol/accuracy-push/truth-eval/)"""
import json, sys
from pathlib import Path
import numpy as np
ROOT = Path('/mnt/d/tez/practical/protocol_re/dol')
PROTOS = 'modbus,bacnet,cip,dnp3,enip,ethercat,goose,hart_ip,iec104,mms,opcua,powerlink,s7comm,zigbee'.split(',')
runs = sys.argv[1:]


def overall(run, p):
    r = json.load(open(ROOT / 'accuracy-push/truth-eval' / run / p / 'data/15_evaluation_result.json'))
    return r['summary']['overall_score'], r['metrics']['field_boundary']['f1_score'], r['metrics']['field_semantics']['f1_score']


T = {r: {p: overall(r, p) for p in PROTOS} for r in runs}
base = {p: json.load(open(ROOT / 'global-segmentation/truth-eval-14/baseline' / p / 'data/15_evaluation_result.json'))['summary']['overall_score'] for p in PROTOS}
chosen, scores = {}, {}
for H in PROTOS:
    best = max(runs, key=lambda r: np.mean([T[r][p][0] for p in PROTOS if p != H]))
    chosen[H] = best; scores[H] = T[best][H]
for p in PROTOS:
    print(f'{p:10s} chosen {chosen[p]:16s} overall/bnd/sem {scores[p][0]:.3f}/{scores[p][1]:.3f}/{scores[p][2]:.3f}   baseline {base[p]:.3f}')
m = [np.mean([scores[p][k] for p in PROTOS]) for k in range(3)]
d = np.array([scores[p][0] - base[p] for p in PROTOS])
rng = np.random.default_rng(20261018); idx = rng.integers(0, 14, (10000, 14))
lo, hi = np.percentile(d[idx].mean(1), [2.5, 97.5])
print(f'LOPO-selected macro overall/bnd/sem {m[0]:.3f}/{m[1]:.3f}/{m[2]:.3f}  vs baseline {np.mean(list(base.values())):.3f}: '
      f'diff {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]  up {(d > 0.005).sum()} / down {(d < -0.005).sum()}')
print('configs chosen:', {r: sum(1 for c in chosen.values() if c == r) for r in runs})
