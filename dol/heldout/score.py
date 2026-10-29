"""Score the held-out protocols: per-message boundary P/R/F1 against the parser annotations and message-type
clustering (V-measure, ARI) against the spec-derived types, for the three tools and our three configurations
(full corpus and sample only). Few-shot is scored without its 50 labelled messages. -> dol/heldout/scores.json"""
import json, os, sys
from sklearn import metrics
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, os.path.join(ROOT, 'src'))
from protocol_re.inference.tlv import message_layout_edges
H = f'{ROOT}/dol/heldout'; T = f'{ROOT}/dol/baseline-comparison/preds'
def ours(p, run, ids):
    d = f'{H}/{p}/runs/{run}/data'
    fams = json.load(open(f'{d}/05_families.json'))
    assign = {a['msg_id']: str(a['family_id']) for a in json.load(open(f'{d}/02_family_assignments.json'))['assignments']}
    edges = {}
    for fid, det in fams.items():
        v = set()
        for f in det.get('field_hypotheses', []) or []:
            v.update((int(f.get('start', 0) or 0), int(f.get('start', 0) or 0) + int(f.get('length', 0) or 0)))
        edges[fid] = sorted(v)
    out = {}
    for l in open(f'{d}/01_messages.jsonl'):
        r = json.loads(l)
        if r['msg_id'] not in ids: continue
        fid = assign.get(r['msg_id']); e = edges.get(fid, [])
        lay = fams.get(fid, {}).get('message_layout') if fid else None
        if lay: e = message_layout_edges(bytes.fromhex(r['payload_hex']), e, lay)
        out[r['msg_id']] = {'boundaries': list(e), 'cluster': fid or 'noise'}
    return out
res = {}
for p in ('synphasor', 'ams', 'doip', 'cnip'):
    ids = set(json.load(open(f'{H}/{p}/sample.json')))
    ann = {a['msg_id']: a for a in map(json.loads, open(f'{H}/{p}/annotations_typed.jsonl')) if a['msg_id'] in ids}
    L = {json.loads(l)['msg_id']: json.loads(l)['payload_len'] for l in open(f'{H}/{p}/data/01_messages.jsonl')}
    labelled = {json.loads(l)['msg_id'] for l in open(f'{H}/{p}/labels.jsonl')}
    systems = {t: {r['msg_id']: r for r in map(json.loads, open(f'{T}/{t}/{p}.jsonl'))} for t in ('nemesys', 'netzob', 'netplier', 'sup-copy-offsets', 'sup-copy-align')}
    for c in ('rules', 'zs', 'fs50'):
        systems[f'ours-{c}'] = ours(p, f'{c}-full', ids); systems[f'ours-{c}-s'] = ours(p, f'{c}-sample', ids)
    for c in ('zs', 'fs50'):   # per-message edges of stage 04b, before the family field lists
        f = f'{H}/{p}/runs/{c}-full/data/04b_fewshot_edges.json'
        if os.path.exists(f):
            systems[f'ours-{c}-msg'] = {int(m): {'boundaries': e, 'cluster': None} for m, e in json.load(open(f))['edges'].items()}
    systems['every-byte'] = {m: {'boundaries': list(range(1, L[m]))} for m in ids if m in L}   # no clusters
    res[p] = {}
    for n, pred in systems.items():
        skip = labelled if 'fs50' in n or n.startswith('sup-') else set()
        tp = fp = fn = 0
        for mid, a in ann.items():
            if mid in skip: continue
            t = {e for e in a['boundaries'] if 0 < e < L[mid]}; e = {x for x in (pred.get(mid, {}).get('boundaries') or []) if 0 < x < L[mid]}
            tp += len(t & e); fp += len(e - t); fn += len(t - e)
        P = tp / max(1, tp + fp); R = tp / max(1, tp + fn); F = 2 * P * R / max(1e-9, P + R)
        row = {'p': round(P, 3), 'r': round(R, 3), 'f1': round(F, 3)}
        cl = [m for m in ann if m not in skip and pred.get(m, {}).get('cluster') not in (None, 'fail')]
        if n == 'every-byte': cl = []
        if cl and n not in ('nemesys', 'every-byte') and not n.startswith('sup-') and not n.endswith('-msg'):
            y = [ann[m]['type'] for m in cl]; z = [str(pred[m]['cluster']) for m in cl]
            row.update(v=round(metrics.v_measure_score(y, z), 3), ari=round(metrics.adjusted_rand_score(y, z), 3), clusters=len(set(z)))
        res[p][n] = row
json.dump(res, open(f'{H}/scores.json', 'w'), indent=1)
for p, r in res.items():
    print('==', p)
    for n, row in r.items(): print(f'  {n:14s} {row}')
