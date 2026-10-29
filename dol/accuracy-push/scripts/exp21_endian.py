"""Exp 21: protocol byte order (label-free, from the length field) as features of the group model.
Byte order: a 2- or 4-byte field at offset < 16 whose value + c equals the message length for >= 60% of the
protocol's messages (c constant); LE / BE / unknown. Features per offset i: LE, BE, unknown, and the
interactions LE*zero(i), LE*zero(i+1), BE*zero(i-1), BE*zero(i) using the group's per-byte zero share.
Stage 1, compared with exp02 under the same post-processing (strings + BER + CRC), open and pure.
Usage: exp21_endian.py"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh  # noqa: E402
import gm  # noqa: E402
import pred  # noqa: E402


def byte_order(pr, sample=3000):
    pays = [pr.msgs[m]['payload'] for m in pr.order[:sample]]
    best = (0.0, None)
    for o in range(0, 16):
        for w in (2, 4):
            for order in ('little', 'big'):
                c = Counter(len(b) - int.from_bytes(b[o:o + w], order) for b in pays if len(b) >= o + w)
                if not c:
                    continue
                k, n = c.most_common(1)[0]
                share = n / len(pays)
                vals = {b[o:o + w] for b in pays if len(b) >= o + w}
                if share > best[0] and len(vals) >= 3 and -64 <= k <= 64:
                    best = (share, order)
    return best[1] if best[0] >= 0.6 else None


data, prs, ctxs = gm.setup()
orders = {p: byte_order(prs[p]) for p in qh.PROTOS}
print('detected byte order:', orders, flush=True)
for p in qh.PROTOS:
    le, be = float(orders[p] == 'little'), float(orders[p] == 'big')
    for g in data[p]:
        msgs = [prs[p].msgs[m]['payload'] for m in g['mids'][:1000]]
        M, lens, full = pred.v2.to_matrix(msgs)
        _, st = pred.v2.column_stats(M, lens, full)
        z = st['zero']
        get = lambda j: float(z[j]) if 0 <= j < pred.MAXLEN else 0.0
        F = np.array([[le, be, 1 - le - be, le * get(i), le * get(i + 1), be * get(i - 1), be * get(i)] for i in g['offs']])
        g['XE'] = np.hstack([g['X'], F])
sc = gm.lopo_scores('exp21-endian', data, feat=lambda g: g['XE'])
base = gm.lopo_scores('exp02', data)
posts = [gm.post_strings, gm.post_ber, gm.post_crc(False)]
for mode in ('open', 'pure'):
    gm.evaluate_post(base, posts, mode, label=f'exp02 base {mode} +posts')
    gm.evaluate_post(sc, posts, mode, label=f'exp21 endian {mode} +posts', verbose=True)
