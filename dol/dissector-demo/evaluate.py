"""Use the generated dissector like an analyst would and compare it with Wireshark's own Modbus/TCP dissector on
the same capture (joined by frame number, first PDU of each TCP segment):
  coverage       packets with a Modbus PDU that the inferred dissector assigns to a family
  family purity  share of assigned packets whose family's majority (function code, direction) is their own
  rule agreement for every function code v: Jaccard of {inferred.opcode == v} and {modbus.func_code == v}
                 (an IDS rule written on the inferred field vs the same rule on the real dissector)
  field values   per role, share of packets where the inferred field's value equals the real field's value
usage: evaluate.py <pcap> <dissector.lua> <server-port> <out.json>"""
import json, subprocess, sys
from collections import Counter, defaultdict
pcap, lua, port, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]

def fields(extra, names):
    cmd = ['tshark', '-n', '-r', pcap] + extra + ['-T', 'fields', '-E', 'occurrence=f'] + sum((['-e', x] for x in names), [])
    rows = {}
    for line in subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines():
        c = line.split('\t'); rows[int(c[0])] = dict(zip(names[1:], c[1:]))
    return rows

REAL = ['frame.number', 'tcp.dstport', 'modbus.func_code', 'mbtcp.trans_id', 'mbtcp.len', 'mbtcp.unit_id']
INF = ['frame.number', 'inferred.family', 'inferred.role', 'inferred.opcode', 'inferred.transaction_id', 'inferred.length']
real = fields(['-Y', 'modbus'], REAL)
inf = fields(['-X', f'lua_script:{lua}', '-Y', 'inferred'], INF)
pk = [f for f in real if real[f]['modbus.func_code']]
cov = [f for f in pk if f in inf and inf[f]['inferred.family'] not in ('', 'unmatched')]
key = lambda f: (int(real[f]['modbus.func_code']), 'request' if real[f]['tcp.dstport'] == str(port) else 'response')
by_fam = defaultdict(Counter)
for f in cov:
    by_fam[inf[f]['inferred.family']][key(f)] += 1
pure = sum(c.most_common(1)[0][1] for c in by_fam.values())
rules = {}
for v in sorted({int(real[f]['modbus.func_code']) for f in pk}):
    A = {f for f in pk if int(real[f]['modbus.func_code']) == v}
    B = {f for f in inf if inf[f]['inferred.opcode'] == str(v)}
    rules[v] = dict(real=len(A), inferred=len(B), jaccard=len(A & B) / max(1, len(A | B)))
def agree(i, r):
    both = [f for f in cov if inf[f][i] != '' and real[f][r] != '']
    return dict(n=len(both), equal=sum(int(inf[f][i]) == int(real[f][r]) for f in both) / max(1, len(both)))
res = dict(pcap=pcap, modbus_packets=len(pk), coverage=len(cov) / max(1, len(pk)), families=len(by_fam),
           family_purity=pure / max(1, len(cov)), family_majority={k: dict(v.most_common(3)).__repr__() for k, v in by_fam.items()},
           rules=rules, values={'opcode': agree('inferred.opcode', 'modbus.func_code'),
                                'transaction_id': agree('inferred.transaction_id', 'mbtcp.trans_id'),
                                'length': agree('inferred.length', 'mbtcp.len')})
json.dump(res, open(out, 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != 'family_majority'}, indent=1))
