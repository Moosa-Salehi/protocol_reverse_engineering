"""Most common dissector leaf layouts of a protocol (from fields.jsonl).
Usage: layouts.py <protocol> [top] [maxoff]"""
import json, sys
from collections import Counter
from pathlib import Path
p = sys.argv[1]; top = int(sys.argv[2]) if len(sys.argv) > 2 else 6; maxoff = int(sys.argv[3]) if len(sys.argv) > 3 else 64
rows = [json.loads(l) for l in open(Path('/mnt/d/tez/practical/protocol_re/dol/truth-file-derivation') / p / 'fields.jsonl')]
c = Counter(); ex = {}
for r in rows:
    key = tuple((n, o, w) for n, o, w in r['leaves'] if o < maxoff)
    c[key] += 1; ex.setdefault(key, r)
print(f'== {p}: {len(rows)} messages, {len(c)} distinct layouts (first {maxoff} bytes)')
for key, n in c.most_common(top):
    r = ex[key]
    print(f'-- {n} msgs, e.g. len {r["len"]} {r["dir"]} {r["payload_hex"][:64]}')
    print('   ' + '  '.join(f'{nm}@{o}:{w}' for nm, o, w in key))
