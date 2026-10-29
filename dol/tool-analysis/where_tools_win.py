"""Where do the tools beat our configurations? Per protocol (14 benchmark on truth-file reference + 2 held-out on
parser annotations): F1 of each system, an 'every byte is a boundary' baseline, and for the winning tool the
edges it gets right that ours misses, by width of the truth field that starts/ends there."""
import json, os, sys
from collections import Counter, defaultdict
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, f'{ROOT}/src'); sys.path.insert(0, f'{ROOT}/dol/baseline-comparison/scripts')
from protocol_re.inference.tlv import message_layout_edges
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
def ours(run_dir, ids):
    d = run_dir
    fams = json.load(open(f'{d}/05_families.json'))
    assign = {a['msg_id']: str(a['family_id']) for a in json.load(open(f'{d}/02_family_assignments.json'))['assignments']}
    edges = {f: sorted({int(x['start']) for x in v.get('field_hypotheses', [])} | {int(x['start']) + int(x['length']) for x in v.get('field_hypotheses', [])}) for f, v in fams.items()}
    out = {}
    for l in open(f'{d}/01_messages.jsonl'):
        r = json.loads(l)
        if r['msg_id'] not in ids: continue
        f = assign.get(r['msg_id']); e = edges.get(f, []); lay = fams.get(f, {}).get('message_layout') if f else None
        if lay: e = message_layout_edges(bytes.fromhex(r['payload_hex']), e, lay)
        out[r['msg_id']] = set(e)
    return out
def f1(pred, ann, L):
    tp = fp = fn = 0
    for m, t in ann.items():
        tt = {x for x in t if 0 < x < L[m]}; e = {x for x in pred.get(m, ()) if 0 < x < L[m]}
        tp += len(tt & e); fp += len(e - tt); fn += len(tt - e)
    p = tp / max(1, tp + fp); r = tp / max(1, tp + fn)
    return round(2 * p * r / max(1e-9, p + r), 3), round(p, 2), round(r, 2)
rows = []
cases = [(p, f'{ROOT}/dol/benchmark-14-protocols/{p}/data/01_messages.jsonl', f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl',
          f'{ROOT}/dol/baseline-comparison/samples/{p}.json', {c: f'{ROOT}/dol/final-v4/{c}/{p}/data' for c in ('full', 'zs')}) for p in P]
cases += [(p, f'{ROOT}/dol/heldout/{p}/data/01_messages.jsonl', f'{ROOT}/dol/heldout/{p}/annotations_typed.jsonl', f'{ROOT}/dol/heldout/{p}/sample.json',
           {'full': f'{ROOT}/dol/heldout/{p}/runs/rules-full/data', 'zs': f'{ROOT}/dol/heldout/{p}/runs/zs-full/data'}) for p in ('synphasor', 'ams')]
width_gain = defaultdict(Counter)
for p, msgs, annp, sp, runs in cases:
    ids = set(json.load(open(sp)))
    L = {json.loads(l)['msg_id']: json.loads(l)['payload_len'] for l in open(msgs) if json.loads(l)['msg_id'] in ids}
    ann = {a['msg_id']: a['boundaries'] for a in map(json.loads, open(annp)) if a['msg_id'] in ids and a['msg_id'] in L}
    systems = {t: {r['msg_id']: set(r['boundaries']) for r in map(json.loads, open(f'{ROOT}/dol/baseline-comparison/preds/{t}/{p}.jsonl'))}
               for t in ('nemesys', 'netzob', 'netplier') if os.path.exists(f'{ROOT}/dol/baseline-comparison/preds/{t}/{p}.jsonl')}
    systems['rules'] = ours(runs['full'], ids); systems['zs'] = ours(runs['zs'], ids)
    systems['every-byte'] = {m: set(range(1, L[m])) for m in ann}
    sc = {n: f1(s, ann, L) for n, s in systems.items()}
    best_tool = max((n for n in sc if n in ('nemesys', 'netzob', 'netplier')), key=lambda n: sc[n][0])
    rows.append((p, sc, best_tool))
    # edges the best tool gets right that zero-shot misses, by width of the truth field on each side
    for m, t in ann.items():
        tt = sorted({x for x in t if 0 < x < L[m]}); tc = [0] + tt + [L[m]]
        for x in set(tt) & systems[best_tool].get(m, set()) - systems['zs'].get(m, set()):
            i = tc.index(x); w = lambda v: '1' if v == 1 else '2' if v == 2 else '3-4' if v <= 4 else '5+'
            width_gain[p][f'{w(x - tc[i - 1])}|{w(tc[i + 1] - x)}'] += 1
print(f"{'protocol':10s} {'rules':>16s} {'zero-shot':>16s} {'NEMESYS':>16s} {'Netzob':>16s} {'NetPlier':>16s} {'every-byte':>16s}   (F1, P, R)")
for p, sc, bt in rows:
    print(f'{p:10s} ' + ' '.join(f"{str(sc.get(n, '-')):>16s}" for n in ('rules', 'zs', 'nemesys', 'netzob', 'netplier', 'every-byte')) + f'  best tool={bt}')
print('\nedges the best tool finds and zero-shot misses, by (left|right truth-field width):')
for p, c in width_gain.items():
    if sum(c.values()) > 50: print(f'  {p:10s} n={sum(c.values()):5d}', dict(c.most_common(5)))
json.dump({p: {'scores': sc, 'best_tool': bt} for p, sc, bt in rows}, open(f'{ROOT}/dol/tool-analysis/where_tools_win.json', 'w'), indent=1)
