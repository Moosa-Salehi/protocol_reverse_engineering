"""Item 3 analysis (benchmark protocols only): request->response consistency of each candidate offset. Pairs are
consecutive (request, response) messages of a session in capture order (known direction only). For offset o:
determinism D = 1 - H(V_resp | V_req) / H(V_resp) and echo rate E = share of pairs with equal values. Compared with
the truth NMI of families keyed by that byte (diagnosis only) and the offset our pipeline chose."""
import json, math, collections
ROOT = '/mnt/d/tez/practical/protocol_re'
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
def H(vals):
    c = collections.Counter(vals); n = len(vals)
    return -sum(v / n * math.log2(v / n) for v in c.values()) if n else 0.0
def nmi(a, b):
    ha, hb = H(a), H(b); hab = H(list(zip(a, b)))
    return (ha + hb - hab) / max(1e-9, (ha + hb) / 2)
for p in P:
    rows = [json.loads(l) for l in open(f'{ROOT}/dol/benchmark-14-protocols/{p}/data/01_messages.jsonl')]
    known = sum(r['direction'] != 'unknown' for r in rows) / len(rows)
    truth = {json.loads(l)['msg_id']: json.loads(l).get('type') for l in open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl')}
    ref = json.load(open(f'{ROOT}/dol/final-v2/full/{p}/data/02_family_assignments.json'))['metadata'].get('discriminator_refinement') or {}
    sess = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: (r['timestamp'], r['msg_id'])): sess[r['session_id']].append(r)
    pairs = []
    for s in sess.values():
        for a, b in zip(s, s[1:]):
            if a['direction'] == 'client_to_server' and b['direction'] == 'server_to_client':
                pairs.append((bytes.fromhex(a['payload_hex']), bytes.fromhex(b['payload_hex'])))
    if len(pairs) < 20:
        print(f'{p:10s} known-direction {known:.0%}: {len(pairs)} pairs -- not applicable'); continue
    res = []
    for o in range(16):
        pr = [(a[o], b[o]) for a, b in pairs if len(a) > o and len(b) > o]
        if len(pr) < 0.9 * len(pairs): continue
        req = [x for x, _ in pr]; resp = [y for _, y in pr]
        hr = H(resp)
        if hr < 0.05 or len(set(req)) < 2: continue
        D = 1 - (H(pr) - H(req)) / hr; E = sum(x == y for x, y in pr) / len(pr)
        msgs = [(bytes.fromhex(r['payload_hex']), truth.get(r['msg_id'])) for r in rows if truth.get(r['msg_id'])]
        fam = [(b[o] if len(b) > o else -1, ) for b, _ in msgs]
        res.append((o, round(D, 2), round(E, 2), round(nmi(fam, [t for _, t in msgs]), 2)))
    best = max(res, key=lambda x: (x[1] * x[2], -x[0])) if res else None
    print(f'{p:10s} pairs {len(pairs):5d} chosen offset {ref.get("offset")}  candidates (o, determinism, echo, truthNMI): {res[:8]}')
    print(f'{"":10s} max determinism*echo -> {best}')
