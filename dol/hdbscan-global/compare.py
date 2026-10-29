"""Compare rule-based runs: overall / message-type F1 / boundary F1 per protocol, full corpus and 500-sample,
plus noise share. usage: compare.py <before-full> <before-sample> <after-dir>   (after-dir has full/, sample/)"""
import json, sys
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
bf, bs, after = sys.argv[1:4]
def get(root, p):
    try:
        r = json.load(open(f'{root}/{p}/data/15_evaluation_result.json')); m = r['metrics']
        a = json.load(open(f'{root}/{p}/data/02_family_assignments.json'))['assignments']
        return r['summary']['overall_score'], m['message_type_matching']['f1_score'], m['field_boundary']['f1_score'], sum(x['family_id'] == 'noise' for x in a) / len(a)
    except FileNotFoundError:
        return None
for label, before, now in (('FULL', bf, f'{after}/full'), ('SAMPLE', bs, f'{after}/sample')):
    print(f'== {label}: overall / message-type F1 / boundary F1 / noise   before -> after')
    sums = [[0, 0], [0, 0], [0, 0]]
    for p in P:
        a, b = get(before, p), get(now, p)
        if not a or not b: print(f'  {p:10s} missing'); continue
        for k in range(3): sums[k][0] += a[k]; sums[k][1] += b[k]
        flag = '  <-- down' if b[0] < a[0] - 0.005 else ('  up' if b[0] > a[0] + 0.005 else '')
        print(f'  {p:10s} {a[0]:.3f}->{b[0]:.3f}  mt {a[1]:.3f}->{b[1]:.3f}  bnd {a[2]:.3f}->{b[2]:.3f}  noise {a[3]:.0%}->{b[3]:.0%}{flag}')
    print('  macro      ' + '  '.join(f'{n} {s[0]/14:.3f}->{s[1]/14:.3f}' for n, s in zip(('overall', 'mt', 'bnd'), sums)))
