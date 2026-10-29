"""How length-determined is each protocol's bootstrap? H(Y|L)/H(Y) over non-noise messages, plus the
discriminator the current detector picks and the truth NMI of that byte (diagnosis only)."""
import json, pickle, sys, math, collections
sys.path.insert(0, '/mnt/d/tez/practical/protocol_re/src')
from protocol_re.inference.discriminator_fields import entropy, detect_global_discriminator, normalized_mi
ROOT = '/mnt/d/tez/practical/protocol_re'
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
for p in P:
    records, assignments = pickle.load(open(f'{ROOT}/dol/iec104-discriminator/bootstrap/{p}.pkl', 'rb'))
    fam = {a.msg_id: a.family_id for a in assignments}
    rows = [(r, fam[r.msg_id]) for r in records if fam.get(r.msg_id) not in (None, 'noise')]
    Y = [f for _, f in rows]; L = [r.payload_len for r, _ in rows]
    hy = entropy(Y)
    groups = collections.defaultdict(list)
    for y, l in zip(Y, L): groups[l].append(y)
    hyl = sum(len(g) / len(Y) * entropy(g) for g in groups.values())
    d = detect_global_discriminator(records, fam)
    truth = {}
    for line in open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl'):
        a = json.loads(line); truth[a['msg_id']] = a.get('type')
    tn = ''
    if d:
        pairs = [(bytes.fromhex(r.payload_hex), truth.get(r.msg_id)) for r, _ in rows if truth.get(r.msg_id)]
        v = [int.from_bytes(m[d['offset']:d['offset'] + d['width']], 'big') if len(m) >= d['offset'] + d['width'] else -1 for m, _ in pairs]
        tn = f"truthNMI={normalized_mi(v, [t for _, t in pairs]):.2f}"
    print(f"{p:10s} fams={len(set(Y)):3d} H(Y)={hy:.2f} H(Y|L)={hyl:.3f} ratio={hyl / hy if hy else 0:.3f}  chosen={(d or {}).get('offset')} {tn}")
