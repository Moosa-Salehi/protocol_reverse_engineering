"""Label-guided pick (with the dumped bootstrap) vs label-free pick (bootstrap ignored: one family) per protocol;
truth NMI of each picked byte is diagnosis only."""
import json, pickle, sys
sys.path.insert(0, '/mnt/d/tez/practical/protocol_re/src')
from protocol_re.inference.discriminator_fields import detect_global_discriminator, normalized_mi
ROOT = '/mnt/d/tez/practical/protocol_re'
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
def tnmi(records, fam, d, truth):
    if not d: return None
    rows = [(bytes.fromhex(r.payload_hex), truth.get(r.msg_id)) for r in records if fam.get(r.msg_id) not in (None, 'noise') and truth.get(r.msg_id)]
    o, w = d['offset'], d['width']
    return normalized_mi([int.from_bytes(m[o:o + w], 'big') if len(m) >= o + w else -1 for m, _ in rows], [t for _, t in rows])
for p in P:
    records, assignments = pickle.load(open(f'{ROOT}/dol/iec104-discriminator/bootstrap/{p}.pkl', 'rb'))
    fam = {a.msg_id: a.family_id for a in assignments}
    truth = {json.loads(l)['msg_id']: json.loads(l).get('type') for l in open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl')}
    guided = detect_global_discriminator(records, fam)
    one = {m: ('noise' if f == 'noise' else 'one') for m, f in fam.items()}
    free = detect_global_discriminator(records, one)
    g, f = tnmi(records, fam, guided, truth), tnmi(records, one, free, truth)
    print(f"{p:10s} guided off={guided and guided['offset']} truth={g if g is None else round(g, 2)}   label-free off={free and free['offset']} "
          f"truth={f if f is None else round(f, 2)} structMI={free and free.get('structure_mi')}")
