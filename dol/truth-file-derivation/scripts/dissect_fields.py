"""Dump the tshark dissector's leaf fields for every message of a benchmark run.

For each message of dol/benchmark-14-protocols/<protocol>/data/01_messages.jsonl the
packet is dissected again (tshark -T json -x --no-duplicate-keys on its source pcap) and every field
whose byte span lies inside the payload is kept with its payload-relative offset.
A field is a leaf when no other field with a different span lies inside it.

Output: dol/truth-file-derivation/<protocol>/fields.jsonl
  {"msg_id", "len", "dir", "fields": [[name, offset, width], ...], "leaves": [...]}

Usage: dissect_fields.py <protocol> <display-filter>
       HELDOUT=1 dissect_fields.py ...   held-out protocol: messages and pcaps from dol/heldout/<protocol>/{data,pcaps}
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
B = ROOT / 'dol/benchmark-14-protocols'
PCAPS = ROOT / 'finetuning/windows_data/sampled_pcaps'
OUT = ROOT / 'dol/truth-file-derivation'


def raw_fields(x, path=()):
    if isinstance(x, dict):
        for k, v in x.items():
            if k.endswith('_raw'):
                for e in (v if isinstance(v, list) and v and isinstance(v[0], list) else [v]):
                    if isinstance(e, list) and len(e) >= 3:
                        try:
                            yield k[:-4], int(e[1]), int(e[2])
                        except (TypeError, ValueError):
                            pass
            else:
                yield from raw_fields(v, path + (k,))
    elif isinstance(x, list):
        for y in x:
            yield from raw_fields(y, path)


def frame_hex(layers):
    v = layers.get('frame_raw')
    if isinstance(v, list) and v:
        v = v[0] if not isinstance(v[0], list) else v[0][0]
        return re.sub(r'[^0-9a-f]', '', str(v).lower())
    return ''


def leaves(fields):
    spans = {(o, w) for _, o, w in fields}
    out = []
    for name, o, w in fields:
        inner = any((o2, w2) != (o, w) and o <= o2 and o2 + w2 <= o + w for o2, w2 in spans)
        if not inner:
            out.append((name, o, w))
    return sorted(set(out), key=lambda t: (t[1], -t[2], t[0]))


def main():
    proto, flt = sys.argv[1], sys.argv[2]
    heldout = bool(os.environ.get('HELDOUT'))
    base = ROOT / 'dol/heldout' if heldout else B
    msgs = [json.loads(l) for l in open(base / proto / 'data/01_messages.jsonl') if l.strip()]
    by_file = defaultdict(list)
    for m in msgs:
        by_file[m.get('source_file')].append(m)
    out_dir = OUT / proto
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, missing = [], 0
    for fname, ms in by_file.items():
        pcap = (base / proto / 'pcaps' / fname) if heldout else (PCAPS / proto / fname)
        if not pcap.exists():
            missing += len(ms)
            continue
        proc = subprocess.run(['tshark', '-n', '-r', str(pcap), '-Y', flt, '-T', 'json', '-x', '--no-duplicate-keys'], capture_output=True, text=True)
        try:
            packets = json.loads(proc.stdout or '[]')
        except json.JSONDecodeError:
            missing += len(ms)
            continue
        by_frame = {}
        for pk in packets:
            layers = pk.get('_source', {}).get('layers', {})
            fr = layers.get('frame', {})
            num = None
            for k in ('frame.number', 'frame_frame_number'):
                if k in fr:
                    num = fr[k]
            if isinstance(num, list):
                num = num[0]
            by_frame[str(num)] = layers
        for m in ms:
            num = str(m.get('metadata', {}).get('frame_number'))
            layers = by_frame.get(num)
            if layers is None:
                missing += 1
                continue
            fh = frame_hex(layers)
            ph = m['payload_hex'].lower()
            pos = fh.find(ph)
            if pos < 0 or pos % 2:
                missing += 1
                continue
            start, plen = pos // 2, int(m['payload_len'])
            fields = [(n, o - start, w) for n, o, w in raw_fields(layers) if w > 0 and o >= start and o + w <= start + plen]
            rows.append({'msg_id': m['msg_id'], 'len': plen, 'dir': m.get('direction'), 'payload_hex': ph[:512],
                         'fields': sorted(set(fields), key=lambda t: (t[1], -t[2])), 'leaves': leaves(fields)})
    with open(out_dir / 'fields.jsonl', 'w') as fh:
        for r in rows:
            fh.write(json.dumps(r) + '\n')
    print(f'{proto}: {len(rows)} messages dissected, {missing} not matched')


if __name__ == '__main__':
    main()
