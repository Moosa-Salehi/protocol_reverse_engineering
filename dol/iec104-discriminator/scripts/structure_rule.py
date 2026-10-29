"""Label-free rule on a dumped bootstrap: gated candidates (coverage >= min_cov, partial ones with an 'absent'
value), NMI(value; exact length), length-relation share; truth NMI for diagnosis only.
usage: structure_rule.py <protocol> [min_cov]"""
import json, pickle, sys, collections
sys.path.insert(0, '/mnt/d/tez/practical/protocol_re/src')
from protocol_re.inference.discriminator_fields import normalized_mi, _effective_cardinality
ROOT = '/mnt/d/tez/practical/protocol_re'
p = sys.argv[1]; min_cov = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
records, assignments = pickle.load(open(f'{ROOT}/dol/iec104-discriminator/bootstrap/{p}.pkl', 'rb'))
fam = {a.msg_id: a.family_id for a in assignments}
truth = {json.loads(l)['msg_id']: json.loads(l).get('type') for l in open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl')}
rows = [r for r in records if fam.get(r.msg_id) not in (None, 'noise')]
msgs = [bytes.fromhex(r.payload_hex) for r in rows]; L = [len(m) for m in msgs]
for o in range(16):
    present = [i for i, m in enumerate(msgs) if len(m) > o]
    cov = len(present) / len(msgs)
    if cov < min_cov: continue
    vc = collections.Counter(msgs[i][o] for i in present)
    eff = _effective_cardinality(vc, len(present), 0.01); stab = vc.most_common(1)[0][1] / len(present)
    if len(vc) == 1 or eff < 2 or eff > 64 or stab > 0.98: continue
    v = [m[o] if len(m) > o else -1 for m in msgs]
    rel = collections.Counter(L[i] - msgs[i][o] for i in present).most_common(1)[0][1] / len(present)
    tp = [(v[i], truth.get(rows[i].msg_id)) for i in range(len(rows)) if truth.get(rows[i].msg_id)]
    print(f'  off{o:2d} cov={cov:.2f} eff={eff:2d} stab={stab:.2f} lenrel={rel:.2f} NMI(V;L)={normalized_mi(v, L):.3f}  [truth {normalized_mi([a for a, _ in tp], [b for _, b in tp]):.2f}]')
