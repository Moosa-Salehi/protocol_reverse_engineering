"""Build a truth file (truth_files/<protocol>.json format) from the tshark dissection.

The truth is derived from the Wireshark dissector output of the benchmark capture
(fields.jsonl from dissect_fields.py), with a small hand-written config per protocol
(configs.py) that fixes what the dissector does not say directly:
  * header_len   length of the shared framing header (absolute offsets 0..header_len)
  * key          function(row, payload) -> (message_type_id, role) or None; one message
                 type per protocol opcode/service (and direction where it matters)
  * disc         True when the byte at header_len is the per-type opcode; it then becomes
                 the PDU field at offset 0 with a constant_value (the evaluator's gate)
  * endian, names, roles, relations

Field derivation, per message type (same rules for the header over all messages):
  1. dissector leaves sharing one byte span (bitfields) are merged into one field;
  2. a field (offset, width) is kept when it occurs in >= SUPPORT of the type's messages;
  3. runs of >= 3 adjacent fields with the same base name and width (arrays such as
     register blocks, offset tables, repeated items) become one `bytes` field - the
     convention of truth_files/modbus.json, where a register array is one field;
  4. bytes not covered by a kept field become `bytes` fields: an interior gap with a
     fixed width, the variable tail (from the last kept field to the message end) with
     no length, as modbus.json does for register_values.
Types with fewer than MIN_TYPE_MESSAGES messages are left out (the pipeline's smallest
family is 5 messages).

Usage: build_truth.py <protocol> [--write]   (prints a summary; --write writes truth_files/<protocol>.json)
"""
import importlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
DER = ROOT / 'dol/truth-file-derivation'
SUPPORT = 0.6
MIN_TYPE_MESSAGES = 5

# dissector-name patterns -> semantic_role tokens of the evaluator's ROLE_CLASSES
ROLE_PATTERNS = [
    (r'checksum|crc|fcs', 'checksum'),
    (r'trans(action)?_?id|invoke|xid|context|pduref|request_?id|rqid|correlation', 'transaction_id'),
    (r'(^|_)(len|length|size|apdulen|msg_length|datlg|parlg|byte_?count)(_|$)|length', 'length'),
    (r'function|func|service|command|cmd|opcode|message_?type|msg_?type|rosctr|typeid|svid|choice|pdu_?type|(^|_)type$', 'opcode'),
    (r'seq(uence)?(_?num|no)?($|_)|(^|_)seq|sqnum|stnum|(^|_)tx$|(^|_)rx$|counter|(^|_)cnt$', 'sequence_number'),
    (r'status|result|error|return_?code|errcod|abort|iin|response_code', 'status'),
    (r'time|timestamp', 'timestamp'),
    (r'(^|_)(addr|address|adp|ado|ioa|dst|src|dest|source|node|device_id|db|area|reference|instance|class|attribute)', 'address'),
    (r'unit|slave|station|(^|_)oa$|session|channel|handle|iface|scid|connid|tokenid', 'unit_id'),
    (r'count|quantity|numix|itemcount|num_', 'quantity'),
    (r'flag|options|control|ctrl|delimiter|(^|_)fc$|bits|sq$|mode', 'flags'),
    (r'reserved|padding|pad|protid|version|start$|magic|protocol_id', 'constant'),
    (r'data|value|payload|float|object|string|symbol|item', 'payload'),
]


def role_for(name, overrides):
    if name in overrides:
        return overrides[name]
    for pat, role in ROLE_PATTERNS:
        if re.search(pat, name):
            return role
    return None


def clean(name, strip):
    """Dissector field name -> truth field name (drop protocol prefixes and subtree indices)."""
    for s in strip:
        if name.startswith(s):
            name = name[len(s):]
            break
    name = re.sub(r'sub\d+\.', '', name)
    return re.sub(r'[^0-9a-zA-Z]+', '_', name).strip('_').lower()


def leaves_of(fields):
    """Fields that contain no other field with a different span."""
    spans = {(o, w) for _, o, w in fields}
    return [(n, o, w) for n, o, w in fields
            if not any((o2, w2) != (o, w) and o <= o2 and o2 + w2 <= o + w for o2, w2 in spans)]


def merged_fields(r, lo, hi, cfg):
    """Non-overlapping fields of one message inside [lo, hi), sorted by offset.

    Dissector fields matching cfg['drop'] (interpretations of opaque data, bit
    subfields) are removed before leaves are taken, so their parent span becomes the
    field. Leaves sharing a span are one field, named by cfg['prefer'], then shortest.
    """
    strip, prefer, rename = cfg['strip'], cfg.get('prefer', []), cfg.get('rename', {})
    drop = [re.compile(p) for p in cfg.get('drop', [])]
    keep = [(n, o, w) for n, o, w in r['fields'] if lo <= o and o + w <= hi and not any(d.search(n) for d in drop)
            and not (o == lo and w == hi - lo and cfg.get('skip_whole', True))]
    spans = defaultdict(list)
    for n, o, w in leaves_of(keep):
        c = clean(n, strip)
        spans[(o, w)].append(rename.get(c, c))
    out, end = [], lo
    for (o, w), names in sorted(spans.items(), key=lambda kv: (kv[0][0], -kv[0][1])):
        if o < end:
            continue
        names = sorted(set(names), key=lambda x: (next((i for i, p in enumerate(prefer) if re.search(p, x)), len(prefer)), len(x), x))
        out.append((o - lo, w, names[0]))
        end = o + w
    return out


def stable_layout(rows, lo_of, hi_of, cfg):
    """Majority field sequence: walk the fields in offset order, at each step taking the
    most common next field among the messages that agreed so far, while at least SUPPORT
    of all messages agree. Every kept field therefore co-occurs in that majority."""
    seqs = [merged_fields(r, lo_of(r), hi_of(r), cfg) for r in rows]
    agree = list(range(len(seqs)))
    pos_idx = [0] * len(seqs)
    out, pos = [], 0
    while True:
        nxt = Counter()
        for i in agree:
            s = seqs[i]
            while pos_idx[i] < len(s) and s[pos_idx[i]][0] < pos:
                pos_idx[i] += 1
            if pos_idx[i] < len(s):
                nxt[s[pos_idx[i]]] += 1
        if not nxt:
            break
        (o, w, n), c = max(nxt.items(), key=lambda kv: (kv[1], -kv[0][0]))
        if c < SUPPORT * len(rows):
            break
        agree = [i for i in agree if pos_idx[i] < len(seqs[i]) and seqs[i][pos_idx[i]] == (o, w, n)]
        out.append((o, w, n))
        pos = o + w
    return out, len(agree)


def collapse_arrays(fields):
    """Runs of >= 3 adjacent fields with the same base name and width -> one bytes field."""
    base = lambda n: re.sub(r'\d+', '', n)
    out, i = [], 0
    while i < len(fields):
        j = i
        while (j + 1 < len(fields) and fields[j + 1][0] == fields[j][0] + fields[j][1]
               and base(fields[j + 1][2]) == base(fields[i][2]) and fields[j + 1][1] == fields[i][1]):
            j += 1
        if j - i + 1 >= 3:
            o = fields[i][0]
            out.append((o, fields[j][0] + fields[j][1] - o, base(fields[i][2]).strip('_') + '_array', 'array'))
        else:
            out.extend((o, w, n, None) for o, w, n in fields[i:j + 1])
        i = j + 1
    return out


def type_for_width(w):
    return {1: 'uint8', 2: 'uint16', 4: 'uint32', 8: 'uint64'}.get(w, 'bytes')


def build_fields(rows, lo_of, cfg, absolute):
    fields, count = stable_layout(rows, lo_of, lambda r: r['len'], cfg)
    fields = collapse_arrays(fields)
    lens = sorted(r['len'] - lo_of(r) for r in rows)
    median = lens[len(lens) // 2]
    max_hi = cfg['header_len'] if absolute else None
    out, pos = [], 0
    for o, w, n, kind in fields:
        if max_hi is not None and o + w > max_hi:
            continue
        if o > pos:
            out.append(dict(name=f'data_{pos}' if not absolute else f'bytes_{pos}', start=pos, length=o - pos, field_type='bytes', semantic_role=None if absolute else 'payload', gap=True))
        role = 'payload' if kind == 'array' else role_for(n, cfg.get('roles', {}))
        f = dict(name=n, start=o, length=w, field_type=type_for_width(w) if kind != 'array' else 'bytes', semantic_role=role)
        if w > 1 and f['field_type'] != 'bytes':
            f['endian'] = cfg.get('endian', 'big')
        out.append(f)
        pos = o + w
    end = cfg['header_len'] if absolute else median
    if pos < end:
        variable = absolute is False and len(set(lens)) > 1
        out.append(dict(name='data' if not absolute else f'bytes_{pos}', start=pos, length=None if variable else end - pos,
                        field_type='bytes', semantic_role='payload' if not absolute else None, gap=True))
    for f in out:
        f.pop('gap', None)
        if f.get('semantic_role') is None:
            f.pop('semantic_role')
        if f.get('length') is None:
            f.pop('length')
    return out


def main():
    proto = sys.argv[1]
    sys.path.insert(0, str(Path(__file__).parent))
    cfg = importlib.import_module('configs').CONFIGS[proto]
    rows = [json.loads(l) for l in open(DER / proto / 'fields.jsonl')]
    if cfg.get('fields_fn'):  # protocol-specific parse replaces dissector offsets that are not wire offsets
        for r in rows:
            r['fields'] = cfg['fields_fn'](bytes.fromhex(r['payload_hex']), r)
    H = cfg['header_len']
    by_type = defaultdict(list)
    for r in rows:
        payload = bytes.fromhex(r['payload_hex'])
        k = cfg['key'](r, payload)
        if k:
            by_type[k].append(r)
    lo = cfg.get('pdu_lo', lambda r: H)
    header_rows = [r for r in rows if lo(r) == H]  # messages that carry the shared header
    header_fields = build_fields(header_rows, lambda r: 0, cfg, absolute=True) if H else []
    for f in header_fields:
        f.update(cfg.get('header_overrides', {}).get(f['name'], {}))
    types = []
    if header_fields:
        types.append(dict(message_type_id=f'{proto}_header', name=cfg['header_name'], role='header',
                          description=cfg['header_description'] + ' Offsets are wire-absolute.', fields=header_fields,
                          examples=[' '.join(f'{b:02X}' for b in bytes.fromhex(rows[0]['payload_hex'])[:H])]))
    skipped = {}
    for (tid, role), rs in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        if len(rs) < MIN_TYPE_MESSAGES:
            skipped[tid] = len(rs)
            continue
        fields = build_fields(rs, lo, cfg, absolute=False)
        disc = cfg.get('disc')
        if disc if not callable(disc) else disc(tid):
            value = bytes.fromhex(rs[0]['payload_hex'])[H]
            fields = [f for f in fields if f['start'] != 0]
            fields.insert(0, dict(name=cfg.get('disc_name', 'function_code'), start=0, length=1, field_type='uint8',
                                  semantic_role='function_code', constant_value=value))
            if len(fields) > 1 and fields[1]['start'] == 0:
                fields.pop(1)
            # a field overlapping the discriminator byte is shifted past it
            for f in fields[1:]:
                if f['start'] < 1:
                    if f.get('length'):
                        f['length'] -= 1 - f['start']
                    f['start'] = 1
        mt = dict(message_type_id=tid, name=tid.replace('_', ' '), role=role,
                  description=f'{len(rs)} messages in the benchmark capture.', fields=fields,
                  examples=[' '.join(f'{b:02X}' for b in bytes.fromhex(r['payload_hex'])[H:H + 24]) for r in rs[:2]])
        if cfg.get('type_extra'):
            mt.update(cfg['type_extra'](tid, role, rs))
        types.append(mt)
    ids = {t['message_type_id'] for t in types}
    relations = [dict(request_message_type_id=a, response_message_type_id=b, relation_type='request_response',
                      description=d) for a, b, d in cfg['relations'](ids)]
    truth = dict(predicted_protocol=dict(protocol_name=proto, version='unknown', families=[], relations=[], llm_analysis=None),
                 ground_truth_protocol=dict(protocol_name=cfg['protocol_name'], version=cfg.get('version', 'unknown'),
                                            description=cfg['description'] + DERIVATION, offset_convention=cfg['offset_convention'],
                                            message_types=types, relations=relations))
    print(f'== {proto}: {len(rows)} messages, {len(types)} types ({sum(len(v) for v in by_type.values())} keyed), '
          f'{len(relations)} relations; skipped rare types {skipped}')
    for t in types:
        print(f"  {t['message_type_id']:42s} {t['role']:12s} " + ' '.join(
            f"{f['name']}@{f['start']}:{f.get('length', '*')}" + (f"={f['constant_value']}" if 'constant_value' in f else '') for f in t['fields']))
    for r in relations:
        print(f"  rel {r['request_message_type_id']} -> {r['response_message_type_id']}")
    if '--write' in sys.argv:
        # held-out protocols (dol/heldout) go to truth_files/heldout/ so nothing that globs truth_files/ picks them up
        out = ROOT / 'truth_files' / ('heldout' if cfg.get('heldout') else '') / f'{proto}.json'
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(truth, indent=2) + '\n', encoding='utf-8')
        print(f'[+] wrote {out}')


DERIVATION = (' Derived from the Wireshark/tshark dissection of the benchmark capture '
              '(dol/truth-file-derivation/scripts/build_truth.py): fields at a fixed offset in at least 60% of a '
              "type's messages, bitfields sharing a byte merged, arrays of 3+ equal fields and variable-position "
              'content kept as one bytes field (the modbus.json convention for register arrays); types with fewer '
              'than 5 messages are omitted.')

if __name__ == '__main__':
    main()
