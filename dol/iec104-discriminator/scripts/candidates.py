"""Per-offset discriminator statistics on a dumped bootstrap, with messages too short for the byte folded in as
an 'absent' value. Truth-type NMI is shown for diagnosis only (never used by the method).
usage: candidates.py <protocol>"""
import json, pickle, sys, collections
sys.path.insert(0, '/mnt/d/tez/practical/protocol_re/src')
from protocol_re.inference.discriminator_fields import normalized_mi, conditional_normalized_mi, _effective_cardinality
p = sys.argv[1]
ROOT = '/mnt/d/tez/practical/protocol_re'
records, assignments = pickle.load(open(f'{ROOT}/dol/iec104-discriminator/bootstrap/{p}.pkl', 'rb'))
fam = {a.msg_id: a.family_id for a in assignments}
truth = {}
for line in open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl'):
    a = json.loads(line); truth[a['msg_id']] = a.get('type')
rows = [(bytes.fromhex(r.payload_hex), fam[r.msg_id], truth.get(r.msg_id), r.msg_id) for r in records if fam.get(r.msg_id) not in (None, 'noise')]
msgs = [m for m, *_ in rows]; labels = [l for _, l, *_ in rows]; L = [len(m) for m in msgs]
tl = [(i, t) for i, (_, _, t, _) in enumerate(rows) if t]
print(p, 'messages', len(msgs), 'bootstrap families', len(set(labels)))
for o in range(16):
    present = [i for i, m in enumerate(msgs) if len(m) > o]
    cov = len(present) / len(msgs)
    if not present: break
    vc = collections.Counter(msgs[i][o] for i in present)
    eff = _effective_cardinality(vc, len(present), 0.01); stab = vc.most_common(1)[0][1] / len(present)
    full = [m[o] if len(m) > o else -1 for m in msgs]
    mi = normalized_mi(full, labels); tmi = conditional_normalized_mi(full, labels, L)
    tnmi = normalized_mi([full[i] for i, _ in tl], [t for _, t in tl])
    print(f'  off{o:2d} cov={cov:.2f} eff={eff:3d} stab={stab:.2f} NMI(V;Y)={mi:.3f} typeMI={tmi:.3f}  [truth NMI {tnmi:.3f}]')
