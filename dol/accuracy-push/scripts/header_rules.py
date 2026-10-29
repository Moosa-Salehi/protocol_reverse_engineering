"""Compare label-free protocol-level header-length rules with the truth files' header lengths.

  current     message-weighted mode of stage 05's per-family body_start (today's behaviour)
  earliest    message-weighted mode of the smallest body_start among each family's top-3 hypotheses
  discrim     first offset whose byte is constant inside (>= 90% of) every large family but takes >= 2 values
              across families
  lenfield    end of the earliest length field: 1/2/4 bytes, either byte order, value + c = message length for
              >= 80% of messages (c constant, >= 2 distinct lengths)
Usage: header_rules.py"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
BASE = ROOT / 'dol/global-segmentation/truth-eval-14/baseline'
PROTOS = 'modbus,bacnet,cip,dnp3,enip,ethercat,goose,hart_ip,iec104,mms,opcua,powerlink,s7comm,zigbee'.split(',')


def truth_header(p):
    t = json.load(open(ROOT / 'truth_files' / f'{p}.json'))['ground_truth_protocol']
    hdr = [m for m in t['message_types'] if m['role'] == 'header' or 'header' in m['message_type_id']]
    return max((f['start'] + (f.get('length') or 0) for m in hdr for f in m['fields'] if f.get('start') is not None), default=0)


def load(p):
    d = BASE / p / 'data'
    fams = Counter(); by = {}
    for a in json.load(open(d / '02_family_assignments.json'))['assignments']:
        fams[a['family_id']] += 1; by[int(a['msg_id'])] = a['family_id']
    msgs = {}
    for line in open(d / '01_messages.jsonl'):
        if line.strip():
            m = json.loads(line); msgs[int(m['msg_id'])] = bytes.fromhex(m['payload_hex'])
    fr = json.load(open(d / '04_framing.json'))['families']
    return fams, by, msgs, fr


def rule_current(fams, fr):
    c = Counter()
    for f, v in fr.items():
        c[((v.get('layout_hypotheses') or [{}])[0]).get('body_start')] += fams.get(f, 0)
    return c.most_common(1)[0][0]


def rule_earliest(fams, fr):
    c = Counter()
    for f, v in fr.items():
        hs = [h.get('body_start') for h in (v.get('layout_hypotheses') or [])[:3] if h.get('body_start') is not None]
        if hs:
            c[min(hs)] += fams.get(f, 0)
    return c.most_common(1)[0][0]


def rule_discrim(fams, by, msgs, max_off=40):
    big = [f for f, n in fams.items() if f != 'noise' and n >= 20]
    per = {f: [msgs[m] for m, g in by.items() if g == f][:500] for f in big}
    for o in range(1, max_off):
        vals, ok = set(), True
        for f, ms in per.items():
            col = [b[o] for b in ms if len(b) > o]
            if len(col) < 0.9 * len(ms):
                ok = False; break
            v, n = Counter(col).most_common(1)[0]
            if n < 0.9 * len(col):
                ok = False; break
            vals.add(v)
        if ok and len(vals) >= 2:
            return o
    return None


def rule_lenfield(msgs, max_off=16):
    sample = list(msgs.values())[:3000]
    for o in range(0, max_off):
        for w in (1, 2, 4):
            for order in ('big', 'little'):
                c = Counter(len(b) - int.from_bytes(b[o:o + w], order) for b in sample if len(b) >= o + w)
                if not c:
                    continue
                k, n = c.most_common(1)[0]
                if n >= 0.8 * len(sample) and len({len(b) for b in sample}) >= 2 and -8 <= k <= 64:
                    return o + w
    return None


rows = []
for p in PROTOS:
    fams, by, msgs, fr = load(p)
    rows.append((p, truth_header(p), rule_current(fams, fr), rule_earliest(fams, fr), rule_discrim(fams, by, msgs), rule_lenfield(msgs)))
print(f"{'protocol':10s} {'truth':>5s} {'current':>8s} {'earliest':>9s} {'discrim':>8s} {'lenfield':>9s}")
for r in rows:
    print(f'{r[0]:10s} {r[1]:5d} ' + ' '.join(f'{str(x):>8s}' for x in r[2:]))
for k, name in enumerate(('current', 'earliest', 'discrim', 'lenfield')):
    exact = sum(r[2 + k] == r[1] for r in rows)
    err = sum(abs((r[2 + k] if r[2 + k] is not None else 0) - r[1]) for r in rows) / len(rows)
    print(f'{name:9s} exact {exact}/14  mean abs error {err:.1f}')
