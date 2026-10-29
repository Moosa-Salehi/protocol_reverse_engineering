"""Leave-one-protocol-out evaluation of the zero-shot boundary step with the final clustering (dol/final-v2/full).
For each protocol p: model trained on the other 13 protocols' rows (labels: truth-file convention annotations),
threshold chosen leave-one-protocol-out (nested, fsb.zeroshot_thresholds), predictions + structural post-processors
+ apply_gated on the stage-07 families, per-message boundary F1 against the annotations.
usage: lopo_boundaries.py <variant-name> [CHANGE_FEATURES=0|1]   -> dol/improve/lopo-<variant>.json"""
import copy, json, os, pickle, sys
from collections import defaultdict
import numpy as np
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, f'{ROOT}/src')
from protocol_re.config.thresholds import FewShotBoundaries as _FS
name = sys.argv[1]; _FS.CHANGE_FEATURES = len(sys.argv) > 2 and sys.argv[2] == '1'
VETO = float(sys.argv[3]) if len(sys.argv) > 3 else None   # drop stage-07 edges whose family-mean model probability < VETO
ROWS = sys.argv[4] if len(sys.argv) > 4 else name
from protocol_re.inference import fewshot_boundaries as fsb
from protocol_re.inference.framing import infer_framing_hypotheses
from protocol_re.inference.tlv import message_layout_edges
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
RUNS = os.environ.get('LOPO_RUNS', 'final-v2/full')
cache = f'{ROOT}/dol/improve/rows-{ROWS}.pkl'
data = {}
for p in P:
    d = f'{ROOT}/dol/{RUNS}/{p}/data'
    order, payload = [], {}
    for l in open(f'{d}/01_messages.jsonl'):
        r = json.loads(l); order.append(r['msg_id']); payload[r['msg_id']] = bytes.fromhex(r['payload_hex'])
    fam_of = {a['msg_id']: a['family_id'] for a in json.load(open(f'{d}/02_family_assignments.json'))['assignments']}
    ann = {a['msg_id']: [int(x) for x in a['boundaries']] for a in map(json.loads, open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl')) if a['msg_id'] in payload}
    data[p] = (order, payload, fam_of, ann, json.load(open(f'{d}/05_families.json')))
if os.path.exists(cache):
    per_protocol, body = pickle.load(open(cache, 'rb'))
else:
    per_protocol, body = {}, {}
    for p, (order, payload, fam_of, ann, _) in data.items():
        grouped = defaultdict(list)
        for m in order:
            f = fam_of.get(m)
            if f not in (None, 'noise'): grouped[str(f)].append(payload[m].hex())
        bs = {}
        for fam, res in infer_framing_hypotheses(grouped)['families'].items():
            best = (res.get('layout_hypotheses') or [{}])[0]
            if best.get('body_start'): bs[fam] = int(best['body_start'])
        body[p] = bs
        per_protocol[p] = fsb.build_rows(order, fam_of, payload, bs, ann)
        print('rows', p, sum(len(g['offs']) for g in per_protocol[p]), flush=True)
    pickle.dump((per_protocol, body), open(cache, 'wb'))
thr = fsb.zeroshot_thresholds(per_protocol)
print('thresholds', thr, flush=True)
out = {}
for p in P:
    order, payload, fam_of, ann, families = data[p]
    X, y, w = fsb._stack_rows({q: per_protocol[q] for q in P if q != p})
    model = fsb.hgb().fit(X, y, sample_weight=w)
    pred = {}
    prob = defaultdict(lambda: defaultdict(list))
    for g in per_protocol[p]:
        s = model.predict_proba(g['X'])[:, 1]
        e = {o for o, v in zip(g['offs'], s) if v >= thr[p]}
        for o, v in zip(g['offs'], s):
            prob[g['fam']][o].append(v)
        for m in g['mids']:
            pred[m] = set(e)
    funcs = dict(fsb.POSTS)
    for m in pred:
        for nm in ('strings', 'ber', 'crc'):
            pred[m] = funcs[nm](payload[m], pred[m])
    fams = copy.deepcopy(families)
    if VETO is not None:
        for fam, det in fams.items():
            hyps = sorted(det.get('field_hypotheses', []) or [], key=lambda h: int(h['start']))
            if not hyps or any((h.get('attributes') or {}).get('tlv_tag') is not None for h in hyps) or fam not in prob:
                continue
            keep_edge = set()
            for h in hyps:
                if h.get('field_type') in ('length', 'keyword', 'opcode') and float(h.get('confidence', 0)) >= 0.9:
                    keep_edge.update((int(h['start']), int(h['start']) + int(h['length'])))
            merged = [dict(hyps[0])]
            for h in hyps[1:]:
                e = int(h['start']); pv = prob[fam].get(e)
                if e not in keep_edge and pv and float(np.mean(pv)) < VETO:
                    last = merged[-1]; last['length'] = int(h['start']) + int(h['length']) - int(last['start'])
                    last['field_type'] = 'blob'
                else:
                    merged.append(dict(h))
            fams[fam] = dict(det, field_hypotheses=merged)
    fsb.apply_gated(fams, {m: (None if f in (None, 'noise') else str(f)) for m, f in fam_of.items()}, pred, {m: len(b) for m, b in payload.items()})
    tp = fp = fn = 0
    for m, t in ann.items():
        f = fam_of.get(m); det = fams.get(str(f)) or {}
        e = {int(h['start']) for h in det.get('field_hypotheses', [])} | {int(h['start']) + int(h['length']) for h in det.get('field_hypotheses', [])}
        if det.get('message_layout'): e = set(message_layout_edges(payload[m], e, det['message_layout']))
        L = len(payload[m]); tt = {x for x in t if 0 < x < L}; ee = {x for x in e if 0 < x < L}
        tp += len(tt & ee); fp += len(ee - tt); fn += len(tt - ee)
    P_, R_ = tp / max(1, tp + fp), tp / max(1, tp + fn)
    out[p] = dict(f1=2 * P_ * R_ / max(1e-9, P_ + R_), p=P_, r=R_, thr=thr[p])
    print(f"{p:10s} F1 {out[p]['f1']:.3f} P {P_:.2f} R {R_:.2f} thr {thr[p]}", flush=True)
print(f"MACRO {name}: F1 {np.mean([v['f1'] for v in out.values()]):.3f} P {np.mean([v['p'] for v in out.values()]):.3f} R {np.mean([v['r'] for v in out.values()]):.3f}")
json.dump(out, open(f'{ROOT}/dol/improve/lopo-{name}.json', 'w'), indent=1)
