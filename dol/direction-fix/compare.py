"""Previous final runs (dol/hdbscan-global/final) vs direction-fix runs, every configuration: macro overall /
boundary / semantics / message-type F1, paired bootstrap of the overall difference, per-protocol changes."""
import json, os, random
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
import sys
OLD, NEW = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ('hdbscan-global/final', 'direction-fix/final')
CONF = ['full', 'zs', 'zs-shared', 'fs10', 'fs20', 'fs50', 'sample', 'sample-runs/zs', 'sample-runs/fs50']
def load(root, p):
    path = f'{root}/{p}/data/15_evaluation_result.json'
    if not os.path.exists(path): return None
    r = json.load(open(path)); m = r['metrics']
    return dict(overall=r['summary']['overall_score'], bnd=m['field_boundary']['f1_score'], sem=m['field_semantics']['f1_score'], mt=m['message_type_matching']['f1_score'])
for c in CONF:
    o = {p: load(f'{OLD}/{c}', p) for p in P}; n = {p: load(f'{NEW}/{c}', p) for p in P}
    if any(v is None for v in list(o.values()) + list(n.values())):
        print(f'{c:16s} incomplete'); continue
    d = [n[p]['overall'] - o[p]['overall'] for p in P]
    rng = random.Random(0); b = sorted(sum(rng.choice(d) for _ in d) / 14 for _ in range(10000))
    mac = lambda s, k: sum(s[p][k] for p in P) / 14
    print(f"{c:16s} overall {mac(o,'overall'):.3f}->{mac(n,'overall'):.3f} ({sum(d)/14:+.3f} [{b[250]:+.3f},{b[9750]:+.3f}])"
          f"  bnd {mac(o,'bnd'):.3f}->{mac(n,'bnd'):.3f}  sem {mac(o,'sem'):.3f}->{mac(n,'sem'):.3f}  mt {mac(o,'mt'):.3f}->{mac(n,'mt'):.3f}")
    ch = [(p, round(o[p]['overall'], 3), round(n[p]['overall'], 3)) for p in P if abs(n[p]['overall'] - o[p]['overall']) > 0.005]
    if ch: print('     changed:', ch)
