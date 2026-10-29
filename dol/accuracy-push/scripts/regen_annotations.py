"""Regenerate per-message boundary annotations with the truth-file conventions (truth_files/<protocol>.json).

For each message of the benchmark run, the message type is assigned exactly as the truth files were built
(dol/truth-file-derivation/scripts/configs.py `key`, header_len, pdu_lo; Modbus and GOOSE have hand-written
truth files and get the small assignments below). The message's edges are the starts and ends of every field
of its header type (wire-absolute) and of its message type (relative to the PDU start), including `bytes`
fields; a field without a length (variable tail) contributes its start only. GOOSE (variable-position BER
fields): header fields, the GoosePdu tag, and the start/end of every top-level GoosePdu element.
Messages without an assigned truth type get no annotation (they are not scored).

Output: dol/accuracy-push/annotations-truthconv/<protocol>.jsonl  {msg_id, boundaries, reviewer: 'truth-file', type}
Usage: regen_annotations.py [protocols]
"""
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
DER = ROOT / 'dol/truth-file-derivation'
B = ROOT / 'dol/benchmark-14-protocols'
OUT = ROOT / 'dol/accuracy-push/annotations-truthconv'
sys.path.insert(0, str(ROOT / 'src'))
from protocol_re.inference.tlv import parse_ber_elements  # noqa: E402

spec = importlib.util.spec_from_file_location('configs', DER / 'scripts/configs.py')
configs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(configs)
PROTOS = 'modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')


def type_edges(mt, base, n):
    out = set()
    for f in mt['fields']:
        s = f.get('start')
        if s is None:
            continue
        a = base + s
        out.add(a)
        if f.get('length') is not None:
            out.add(a + f['length'])
    return {e for e in out if 0 < e < n}


def modbus_rows():
    for line in open(B / 'modbus/data/01_messages.jsonl'):
        if line.strip():
            m = json.loads(line)
            yield {'msg_id': int(m['msg_id']), 'len': int(m['payload_len']), 'dir': m.get('direction'), 'payload_hex': m['payload_hex']}


def modbus_key(types):
    by_fc = {}
    for t in types:
        if t.startswith('modbus_fc'):
            by_fc.setdefault(t[9:11], []).append(t)

    def key(r, p):
        if len(p) < 8:
            return None
        fc = p[7]
        if fc & 0x80:
            c = [t for t in by_fc.get(f'{fc & 0x7f:02x}', []) if t.endswith('_exception')]
            return (c[0], 'response') if c else None
        cands = [t for t in by_fc.get(f'{fc:02x}', []) if not t.endswith('_exception')]
        if not cands:
            return None
        want_req = r.get('dir') == 'client_to_server'
        req = [t for t in cands if t.endswith('_request') or not t.endswith('_response')]
        resp = [t for t in cands if t.endswith('_response')]
        pick = req if want_req else resp
        return (pick[0], 'request' if want_req else 'response') if pick else None
    return key


def _tlv(p, pos):
    """(header_len, value_len) of the BER element at pos, or None."""
    if pos + 2 > len(p):
        return None
    lb = p[pos + 1]
    if lb < 0x80:
        return 2, lb
    if 0x81 <= lb <= 0x84 and pos + 2 + (lb - 0x80) <= len(p):
        k = lb - 0x80
        return 2 + k, int.from_bytes(p[pos + 2:pos + 2 + k], 'big')
    return None


def goose_edges(p, truth_types):
    """Header fields, the GoosePdu tag, and the start/end of every top-level GoosePdu element that fits in
    the payload (captures can be truncated, so the walk stops at the payload end)."""
    if len(p) < 12 or p[8] != 0x61:
        return None
    root = _tlv(p, 8)
    if root is None:
        return None
    edges = type_edges(truth_types['goose_header'], 0, len(p)) | {8, 9}
    pos = 8 + root[0]
    edges.add(pos)
    end = min(len(p), 8 + root[0] + root[1])
    children = 0
    while pos < end:
        h = _tlv(p, pos)
        if h is None or pos + h[0] + h[1] > len(p):
            break
        pos += h[0] + h[1]
        edges.add(pos)
        children += 1
    if children < 3:
        return None
    return {e for e in edges if 0 < e < len(p)}


def regen(proto):
    truth = json.load(open(ROOT / 'truth_files' / f'{proto}.json'))['ground_truth_protocol']
    types = {t['message_type_id']: t for t in truth['message_types']}
    out, kinds = [], Counter()
    if proto == 'goose':
        for r in _rows(proto):
            p = bytes.fromhex(r['payload_hex'])
            e = goose_edges(p, types)
            if e is None:
                kinds['unassigned'] += 1
                continue
            kinds['goose_pdu'] += 1
            out.append({'msg_id': r['msg_id'], 'boundaries': sorted({0, len(p)} | e), 'reviewer': 'truth-file', 'type': 'goose_pdu'})
        return out, kinds
    if proto == 'modbus':
        cfg = {'header_len': 7, 'key': modbus_key(types)}
        rows = modbus_rows()
        header_id = 'modbus_tcp_mbap'
    else:
        cfg = configs.CONFIGS[proto]
        rows = (json.loads(line) for line in open(DER / proto / 'fields.jsonl') if line.strip())
        header_id = f'{proto}_header'
    H = cfg['header_len']
    lo_of = cfg.get('pdu_lo', lambda r: H)
    for r in rows:
        p = bytes.fromhex(r['payload_hex'])
        k = cfg['key'](r, p)
        if not k or k[0] not in types:
            kinds['unassigned'] += 1
            continue
        lo = lo_of(r)
        n = len(p)
        e = set()
        if header_id in types and lo == H:
            e |= type_edges(types[header_id], 0, n)
        if types[k[0]]['role'] == 'header':
            e |= type_edges(types[k[0]], 0, n)
        else:
            e |= type_edges(types[k[0]], lo, n)
            if lo > 0:
                e.add(lo)
        kinds[k[0]] += 1
        out.append({'msg_id': int(r['msg_id']), 'boundaries': sorted({0, n} | e), 'reviewer': 'truth-file', 'type': k[0]})
    return out, kinds


def _rows(proto):
    for line in open(B / proto / 'data/01_messages.jsonl'):
        if line.strip():
            m = json.loads(line)
            yield {'msg_id': int(m['msg_id']), 'len': int(m['payload_len']), 'dir': m.get('direction'), 'payload_hex': m['payload_hex']}


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for proto in (sys.argv[1].split(',') if len(sys.argv) > 1 else PROTOS):
        rows, kinds = regen(proto)
        with open(OUT / f'{proto}.jsonl', 'w') as fh:
            for r in rows:
                fh.write(json.dumps(r) + '\n')
        total = sum(kinds.values())
        print(f"{proto:10s} annotated {len(rows):6d} / {total:6d} messages ({len(rows) / max(1, total):.0%}), types {len(kinds) - ('unassigned' in kinds)}", flush=True)
