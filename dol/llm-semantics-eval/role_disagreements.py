"""Where stage 11b (local fine-tuned model) changed a field's role, who is right: the heuristic role (run without 11b)
or the model's role? Judged against the truth-file field that covers the predicted field's first byte in the truth type
the evaluator matched to the family (header fields: the protocol's header types, absolute offsets). Uses only the saved
runs in runs/<p>/{check,llm} (no new LLM requests). -> role_disagreements.json, printed summary."""
import importlib.util, json, os, random
ROOT = '/mnt/d/tez/practical/protocol_re'; H = f'{ROOT}/dol/llm-semantics-eval/runs'
spec = importlib.util.spec_from_file_location('ev17', f'{ROOT}/scripts/17_evaluate_protocol_spec.py')
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']

def fields(path):
    out, fam = {}, {}
    for f in json.load(open(path))['predicted_protocol']['families']:
        fam[str(f['family_id'])] = f
        for fl in f.get('field_hypotheses', []) or []:
            out[(str(f['family_id']), int(fl.get('start', 0) or 0), int(fl.get('length', 0) or 0))] = ev._predicted_role_class(fl)
    return out, fam

def covering(tfields, off, ln):
    for t in tfields:
        s, l = int(t.get('start', 0) or 0), int(t.get('length', 0) or 0)
        if s <= off < s + max(l, 1):
            return t, (s == off and l == ln)
    return None, False

res, rows = {}, []
for p in P:
    A, _ = fields(f'{H}/{p}/check/data/14_evaluation_model_data.json')
    B, fam = fields(f'{H}/{p}/llm/data/14_evaluation_model_data.json')
    truth = json.load(open(f'{ROOT}/truth_files/{p}.json')); tp = truth.get('ground_truth_protocol') or truth
    types = {m['message_type_id']: m for m in tp['message_types']}
    headers = [m for m in tp['message_types'] if ev._truth_uses_absolute_offsets(m)]
    match = {m['predicted_family_id']: m['ground_truth_message_type_id']
             for m in json.load(open(f'{H}/{p}/llm/data/15_evaluation_result.json'))['matches']['message_types']}
    c = dict(changed=0, judged=0, heuristic_right=0, llm_right=0, both_wrong=0, exact=0, unmatched_family=0, no_truth_role=0)
    for k, rb in B.items():
        ra = A.get(k)
        if ra == rb or rb is None:
            continue
        c['changed'] += 1
        fid, start, ln = k
        if fid not in match:
            c['unmatched_family'] += 1; continue
        body = ev._family_body_offset(fam[fid])
        if start < body and headers:
            t, exact = None, False
            for h in headers:
                t, exact = covering(h.get('fields', []), start, ln)
                if t: break
        else:
            t, exact = covering(types[match[fid]].get('fields', []), start - body, ln)
        tr = ev._truth_role_class(t) if t else None
        if tr is None:
            c['no_truth_role'] += 1; continue
        c['judged'] += 1; c['exact'] += exact
        c['heuristic_right'] += ra == tr; c['llm_right'] += rb == tr; c['both_wrong'] += ra != tr and rb != tr
        rows.append(dict(protocol=p, family=fid, start=start, length=ln, truth=tr, heuristic=ra, llm=rb, exact=exact))
    res[p] = c
tot = {k: sum(r[k] for r in res.values()) for k in next(iter(res.values()))}
json.dump(dict(per_protocol=res, total=tot, rows=rows), open(f'{os.path.dirname(H)}/role_disagreements.json', 'w'), indent=1)
for p, c in res.items():
    print(f"{p:10s} {c}")
print('TOTAL', tot)
# per-protocol paired difference in "share right" (llm - heuristic) over protocols with judged fields
d = [(c['llm_right'] - c['heuristic_right']) / c['judged'] for c in res.values() if c['judged']]
rng = random.Random(0); bs = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(10000))
print(f'protocols judged {len(d)}: mean share (llm - heuristic) {sum(d)/len(d):+.3f} [{bs[250]:+.3f}, {bs[9750]:+.3f}]')
