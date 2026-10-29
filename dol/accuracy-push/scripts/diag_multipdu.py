"""Diagnostic: in payloads where the protocol's leading magic recurs (several PDUs), which PDU carries the
truth edges? Magic = longest prefix (1-4 bytes) shared by >= 90% of the protocol's messages."""
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh

def magic(pr):
    pays = [pr.msgs[m]['payload'] for m in pr.order]
    best = b''
    for k in (1, 2, 3, 4):
        c = Counter(b[:k] for b in pays if len(b) >= k).most_common(1)
        if c and c[0][1] >= 0.9 * len(pays):
            best = c[0][0]
    return best

for p in qh.PROTOS:
    pr = qh.load(p); mg = magic(pr)
    if not mg:
        print(f'{p:10s} no magic'); continue
    where = Counter(); n = 0
    for m, t in pr.ann.items():
        b = pr.msgs[m]['payload']
        starts = [i for i in range(len(b) - len(mg) + 1) if b[i:i + len(mg)] == mg]
        if len(starts) < 2 or len(mg) < 2 and len(starts) > 6:
            continue
        n += 1
        if not t:
            where['no edges'] += 1; continue
        first = t[0]
        # which PDU start is the closest at/before the first truth edge
        k = max([i for i, s in enumerate(starts) if s <= first], default=-1)
        where['first' if k == 0 else ('last' if k == len(starts) - 1 else ('middle' if k > 0 else 'before first magic'))] += 1
    print(f'{p:10s} magic {mg.hex():8s} multi-magic msgs {n:6d}  annotated PDU: ' + ', '.join(f'{k} {v}' for k, v in where.most_common()))
