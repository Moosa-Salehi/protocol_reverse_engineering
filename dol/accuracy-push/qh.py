"""Quick harness: per-message boundary scoring for the 14 benchmark protocols in seconds.

Loads (and caches) every protocol's messages, family assignments and non-coarse annotations.
A predictor returns edges per message; score() reproduces the official per-message scorer
(scripts/diagnostics/31_benchmark_message_boundaries.py): interior edges 0 < e < len, tp/fp/fn
summed over a protocol's annotated messages.

Reference predictor `family_file(p, path)`: a 05_families-style file (fixed edges per family,
TLV message_layout applied per message), as the official scorer does.
"""
import json
import pickle
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re')
sys.path.insert(0, str(ROOT / 'src'))
from protocol_re.inference.tlv import message_layout_edges  # noqa: E402

B = ROOT / 'dol/benchmark-14-protocols'
ANN = ROOT / 'finetuning/cluster-free-dataset/annotations'
GS = ROOT / 'dol/global-segmentation'
OUT = ROOT / 'dol/accuracy-push'
CACHE = OUT / 'cache'
PROTOS = 'modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')
COARSE = {'tshark-cache'}
import os
ANNSET = os.environ.get('ANNSET', '')            # '' = original tshark annotations; 'truthconv' = truth-file conventions
if ANNSET:
    ANN = OUT / f'annotations-{ANNSET}'
SUFFIX = f'-{ANNSET}' if ANNSET else ''


class Proto:
    """msgs: msg_id -> dict(payload, family, session, direction, ts); ann: msg_id -> sorted truth edges (interior)."""

    def __init__(self, p, data_dir=None, ann_path=None):
        self.name = p
        self.data_dir = str(data_dir or (B / p / 'data'))
        d = Path(self.data_dir)
        assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
        self.msgs = {}
        self.order = []
        for line in open(d / '01_messages.jsonl'):
            if not line.strip():
                continue
            m = json.loads(line)
            mid = int(m['msg_id'])
            self.msgs[mid] = dict(payload=bytes.fromhex(m['payload_hex']), family=assign.get(mid), session=m.get('session_id'),
                                  direction=m.get('direction'), ts=m.get('timestamp') or 0.0)
            self.order.append(mid)
        self.ann = {}
        for line in open(ann_path or (ANN / f'{p}.jsonl')):
            if not line.strip():
                continue
            a = json.loads(line)
            mid = int(a['msg_id'])
            if a.get('reviewer') in COARSE or mid not in self.msgs or not a.get('boundaries'):
                continue
            n = len(self.msgs[mid]['payload'])
            self.ann[mid] = sorted({int(e) for e in a['boundaries'] if 0 < int(e) < n})
        self.families = defaultdict(list)
        for mid in self.order:
            f = self.msgs[mid]['family']
            if f is not None and f != 'noise':
                self.families[f].append(mid)


EXTRA = OUT / 'extra'


def load(p):
    """Benchmark protocol, or an extra training protocol 'x:<name>' from dol/accuracy-push/extra/<name>."""
    path = CACHE / f"{p.replace(':', '_')}{SUFFIX}.pkl"
    if path.exists():
        pr = Proto.__new__(Proto)
        pr.__dict__.update(pickle.load(open(path, 'rb')))
        pr.__dict__.setdefault('data_dir', str(B / p / 'data'))
        return pr
    if p.startswith('x:'):
        d = EXTRA / p[2:]
        pr = Proto(p, d / 'data', d / 'annotations.jsonl')
    else:
        pr = Proto(p)
    CACHE.mkdir(parents=True, exist_ok=True)
    state = dict(pr.__dict__, families=dict(pr.families))
    pickle.dump(state, open(path, 'wb'))      # plain dicts: loadable from any script
    return pr


def load_all(protos=PROTOS):
    return {p: load(p) for p in protos}


def score(pr, pred):
    """pred: msg_id -> iterable of edges. Returns dict(precision, recall, f1, tp, fp, fn)."""
    tp = fp = fn = 0
    for mid, truth in pr.ann.items():
        n = len(pr.msgs[mid]['payload'])
        t = set(truth)
        e = {x for x in pred.get(mid, ()) if 0 < x < n}
        tp += len(e & t); fp += len(e - t); fn += len(t - e)
    P = tp / (tp + fp) if tp + fp else 0.0
    R = tp / (tp + fn) if tp + fn else 0.0
    return dict(precision=P, recall=R, f1=2 * P * R / (P + R) if P + R else 0.0, tp=tp, fp=fp, fn=fn)


def family_file(pr, path):
    """Per-message edges from a families file, as the official scorer computes them."""
    fams = json.load(open(path))
    out = {}
    for mid in pr.ann:
        m = pr.msgs[mid]
        det = fams.get(m['family'] or '', {}) if isinstance(fams.get(m['family'] or ''), dict) else {}
        edges = set()
        for h in det.get('field_hypotheses', []) or []:
            s = int(h.get('start', 0) or 0)
            edges.update((s, s + int(h.get('length', 0) or 0)))
        if det.get('message_layout'):
            edges = set(message_layout_edges(m['payload'], sorted(edges), det['message_layout']))
        out[mid] = edges
    return out


def report(results, label=''):
    """results: protocol -> score dict. Prints one compact line per protocol plus macro."""
    lines = []
    for p, r in results.items():
        lines.append(f"{p:10s} {r['precision']:.2f}/{r['recall']:.2f}/{r['f1']:.3f}")
    f1 = [r['f1'] for r in results.values()]
    lines.append(f"{'macro':10s} F1 {np.mean(f1):.3f}  min {min(f1):.3f}  >=0.70: {sum(x >= 0.7 for x in f1)}/{len(f1)}  {label}")
    return '\n'.join(lines)


if __name__ == '__main__':
    # sanity: reproduce the official scores of the gated families files
    data = load_all()
    res = {}
    for p, pr in data.items():
        res[p] = score(pr, family_file(pr, GS / 'families' / p / '05_families.exp-gated-stage1-msgsel.json'))
    print(report(res, 'gated-stage1-msgsel (official 0.594)'))
