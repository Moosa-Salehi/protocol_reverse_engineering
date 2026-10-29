"""Supervised reference baselines for the few-shot comparison: they see the same 50 labelled messages as few-shot
(truth-file convention on the benchmark, parser annotations on the held-out protocols) and nothing else.

  sup-copy-offsets  nearest labelled message (8 closest lengths, best quick ratio; the few-shot neighbour rule,
                    without the family restriction), its edges copied at the same absolute offsets
  sup-copy-align    same neighbour, edges carried over through difflib matching blocks (the few-shot transfer
                    step) and nothing where no block matches: few-shot without the boundary model,
                    the post-processors, family splitting and family-level field reconstruction

Writes dol/baseline-comparison/preds/<name>/<protocol>.jsonl like the tools. Labelled messages get their own
labels (they are excluded from scoring). Run with ~/.venvs/protocol_re."""
import json, os, sys, time
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'dol/baseline-comparison/scripts'))
from protocol_re.inference.fewshot_boundaries import neighbour, transfer
from common import PROTOCOLS, HELDOUT_PROTOCOLS, load_sample, write_preds, iter_jsonl


def labels_of(protocol):
    path = (f'{ROOT}/dol/heldout/{protocol}/labels.jsonl' if protocol in HELDOUT_PROTOCOLS
            else f'{ROOT}/dol/accuracy-push/integrated-labels/{protocol}.jsonl')
    return {r['msg_id']: (bytes.fromhex(r['payload_hex']), sorted(int(e) for e in r['boundaries'])) for r in iter_jsonl(path)}


def run(protocol):
    labels = labels_of(protocol)
    payload = {m: b for m, (b, _) in labels.items()}
    rows = {'sup-copy-offsets': [], 'sup-copy-align': []}
    t0 = time.time()
    for r in load_sample(protocol):
        mid, b = r['msg_id'], bytes.fromhex(r['payload_hex'])
        if mid in labels:
            own = labels[mid][1]
            for name in rows:
                rows[name].append({'msg_id': mid, 'boundaries': own, 'cluster': None})
            continue
        a = neighbour(b, list(labels), payload)
        ea = labels[a][1]
        rows['sup-copy-offsets'].append({'msg_id': mid, 'boundaries': [e for e in ea if 0 < e < len(b)], 'cluster': None})
        moved, _cov = transfer(labels[a][0], ea, b)
        rows['sup-copy-align'].append({'msg_id': mid, 'boundaries': sorted(e for e in moved if 0 < e < len(b)), 'cluster': None})
    for name, out in rows.items():
        write_preds(name, protocol, out, {'labels': len(labels), 'seconds': round(time.time() - t0, 2)})
    print(f'{protocol:10s} labels={len(labels)} messages={len(rows["sup-copy-align"])}')


if __name__ == '__main__':
    for p in (sys.argv[1:] or PROTOCOLS + HELDOUT_PROTOCOLS):
        run(p)
