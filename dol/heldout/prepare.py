"""Held-out protocols (never used in any design decision): add a spec-derived message type to the parser annotations
(evaluation only) and draw the <= 500-message session-based evaluation sample (seed 0), as for the benchmark.
  synphasor (IEEE C37.118): frame type = bits 4-6 of the second sync byte; non-0xAA payloads -> 'other'
  ams (Beckhoff ADS/AMS over TCP): command id (LE, AMS header offset 16) + response bit of the state flags"""
import json, random
ROOT = '/mnt/d/tez/practical/protocol_re/dol/heldout'
FT = {0: 'data', 1: 'header', 2: 'cfg1', 3: 'cfg2', 4: 'command', 5: 'cfg3'}
def mtype(p, b):
    if p == 'synphasor':
        return f'c37_{FT.get((b[1] >> 4) & 7, "unknown")}' if len(b) >= 2 and b[0] == 0xAA else 'other'
    if len(b) < 6 + 32:
        return 'other'
    cmd = int.from_bytes(b[6 + 16:6 + 18], 'little'); state = int.from_bytes(b[6 + 18:6 + 20], 'little')
    return f'ams_cmd{cmd}_{"response" if state & 1 else "request"}'
for p in ('synphasor', 'ams'):
    rows = {json.loads(l)['msg_id']: json.loads(l) for l in open(f'{ROOT}/{p}/data/01_messages.jsonl')}
    with open(f'{ROOT}/{p}/annotations_typed.jsonl', 'w') as out:
        for l in open(f'{ROOT}/{p}/annotations.jsonl'):
            a = json.loads(l)
            if a['msg_id'] in rows and a.get('boundaries'):
                a['type'] = mtype(p, bytes.fromhex(rows[a['msg_id']]['payload_hex'])); out.write(json.dumps(a) + '\n')
    ann = {json.loads(l)['msg_id'] for l in open(f'{ROOT}/{p}/annotations_typed.jsonl')}
    sessions = {}
    for mid, r in rows.items():
        if mid in ann: sessions.setdefault(r['session_id'], []).append(mid)
    order = sorted(sessions); random.Random(0).shuffle(order); pick = []
    for key in order:
        ids = sorted(sessions[key]); room = 500 - len(pick)
        if room <= 0: break
        if len(ids) > room:
            st = random.Random(key).randrange(len(ids) - room + 1); ids = ids[st:st + room]
        pick.extend(ids)
    json.dump(sorted(pick), open(f'{ROOT}/{p}/sample.json', 'w'))
    from collections import Counter
    types = Counter(json.loads(l)['type'] for l in open(f'{ROOT}/{p}/annotations_typed.jsonl'))
    print(p, 'annotated', len(ann), 'sample', len(pick), 'types', dict(types.most_common(8)))
