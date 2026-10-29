"""Second held-out pair (added after the design was frozen; run once): type annotations from tshark fields, then the
<= 500-message session-based evaluation sample (seed 0), exactly as prepare.py does for synphasor / ams.
  doip (ISO 13400 DoIP over TCP): DoIP payload type + UDS service id of diagnostic messages
  cnip (CN/IP, LonWorks over IP): LonTalk PDU format + TPDU / SPDU type"""
import json, random, subprocess, sys
from collections import Counter
ROOT = '/mnt/d/tez/practical/protocol_re/dol/heldout'
FIELDS = {'doip': ('doip', ['doip.type', 'uds.sid']), 'cnip': ('cnip', ['lon.pdufmt', 'lon.tpdu_type', 'lon.spdu_type'])}
for p in sys.argv[1:]:
    flt, fields = FIELDS[p]
    pcap = f'{ROOT}/{p}/pcaps/000_' + {'doip': 'hohohouds.pcap', 'cnip': 'lon.pcap'}[p]
    cmd = ['tshark', '-r', pcap, '-Y', flt, '-T', 'fields', '-e', 'frame.number'] + sum((['-e', f] for f in fields), [])
    by_frame = {}
    for line in subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines():
        cols = line.split('\t'); by_frame[cols[0]] = '_'.join(c.split(',')[0] or '-' for c in cols[1:])
    rows = {json.loads(l)['msg_id']: json.loads(l) for l in open(f'{ROOT}/{p}/data/01_messages.jsonl')}
    with open(f'{ROOT}/{p}/annotations_typed.jsonl', 'w') as out:
        for l in open(f'{ROOT}/{p}/annotations.jsonl'):
            a = json.loads(l); r = rows.get(a['msg_id'])
            if r and a.get('boundaries'):
                a['type'] = f"{p}_{by_frame.get(r['metadata']['frame_number'], 'other')}"; out.write(json.dumps(a) + '\n')
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
    types = Counter(json.loads(l)['type'] for l in open(f'{ROOT}/{p}/annotations_typed.jsonl'))
    st = Counter(json.loads(l)['type'] for l in open(f'{ROOT}/{p}/annotations_typed.jsonl') if json.loads(l)['msg_id'] in set(pick))
    print(p, 'annotated', len(ann), 'types', len(types), dict(types.most_common(6)), '| sample', len(pick), 'types', len(st))
