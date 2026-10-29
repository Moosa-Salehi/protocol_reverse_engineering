"""Item 1 offline: family-level gating (current apply_gated) vs per-(family, exact length) gating stored as a by-length
message layout, on the zero-shot predictions of dol/final-v2/zs (04b_fewshot_edges.json + 05_families.pre-fewshot.json).
Per-message boundary F1 against the truth-file convention annotations, all annotated messages, 14 protocols."""
import copy, json, sys
from collections import Counter, defaultdict
import numpy as np
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, f'{ROOT}/src')
from protocol_re.inference import fewshot_boundaries as fsb
from protocol_re.inference.tlv import message_layout_edges
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
MIN_GROUP = int(sys.argv[1]) if len(sys.argv) > 1 else 20

def gate(hyps, edges, median, min_width=3):
    """apply_gated's rule for one edge set: stage-07 fields kept; predicted edges split fields >= min_width bytes and
    fill the tail past the last stage-07 field."""
    hyps = sorted(hyps, key=lambda h: int(h['start']))
    out = set()
    for h in hyps:
        a, b = int(h['start']), int(h['start']) + int(h['length']); out.update((a, b))
        if b - a >= min_width: out.update(e for e in edges if a < e < b)
    end07 = max(int(h['start']) + int(h['length']) for h in hyps)
    if median > end07: out.update([end07, median] + [e for e in edges if end07 < e < median])
    return out

def score(pred_edges, ann, payload):
    tp = fp = fn = 0
    for m, t in ann.items():
        L = len(payload[m]); tt = {x for x in t if 0 < x < L}; e = {x for x in pred_edges(m) if 0 < x < L}
        tp += len(tt & e); fp += len(e - tt); fn += len(tt - e)
    p = tp / max(1, tp + fp); r = tp / max(1, tp + fn)
    return 2 * p * r / max(1e-9, p + r), p, r

res = {}
for p in P:
    d = f'{ROOT}/dol/final-v2/zs/{p}/data'
    payload = {json.loads(l)['msg_id']: bytes.fromhex(json.loads(l)['payload_hex']) for l in open(f'{d}/01_messages.jsonl')}
    fam_of = {a['msg_id']: str(a['family_id']) for a in json.load(open(f'{d}/02_family_assignments.json'))['assignments']}
    pre = json.load(open(f'{d}/05_families.pre-fewshot.json')); final = json.load(open(f'{d}/05_families.json'))
    pred = {int(k): set(v) for k, v in json.load(open(f'{d}/04b_fewshot_edges.json'))['edges'].items()}
    ann = {a['msg_id']: a['boundaries'] for a in map(json.loads, open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl')) if a['msg_id'] in payload}
    def fam_edges(fams, f):
        det = fams.get(f) or {}
        return {int(h['start']) for h in det.get('field_hypotheses', [])} | {int(h['start']) + int(h['length']) for h in det.get('field_hypotheses', [])}
    def current(m):
        f = fam_of.get(m); e = fam_edges(final, f); lay = (final.get(f) or {}).get('message_layout')
        return message_layout_edges(payload[m], e, lay) if lay else e
    # per (family, length) majority of the predicted edges, gated like apply_gated
    votes, reach, count = defaultdict(Counter), defaultdict(Counter), Counter()
    for m, e in pred.items():
        f = fam_of.get(m)
        if f in (None, 'noise'): continue
        k = (f, len(payload[m])); n = len(payload[m])
        votes[k].update(x for x in e if 0 < x < n); reach[k].update(range(1, n)); count[k] += 1
    by_len = {}
    for (f, n), c in count.items():
        hyps = (pre.get(f) or {}).get('field_hypotheses') or []
        if c < MIN_GROUP or not hyps or any((h.get('attributes') or {}).get('tlv_tag') is not None for h in hyps): continue
        edges = {e for e, v in votes[(f, n)].items() if v >= 0.5 * reach[(f, n)][e]}
        by_len[(f, n)] = gate(hyps, edges, n)
    def per_length(m):
        k = (fam_of.get(m), len(payload[m]))
        return by_len[k] if k in by_len else current(m)
    res[p] = (score(current, ann, payload), score(per_length, ann, payload), sum(1 for k in by_len))
    print(f'{p:10s} family-gated F1 {res[p][0][0]:.3f} (P {res[p][0][1]:.2f} R {res[p][0][2]:.2f})  per-length {res[p][1][0]:.3f} (P {res[p][1][1]:.2f} R {res[p][1][2]:.2f})  groups {res[p][2]}', flush=True)
a = np.mean([r[0][0] for r in res.values()]); b = np.mean([r[1][0] for r in res.values()])
print(f'MACRO family-gated {a:.3f} -> per-length {b:.3f}   up/down {sum(r[1][0] > r[0][0] + 0.005 for r in res.values())}/{sum(r[1][0] < r[0][0] - 0.005 for r in res.values())}')
