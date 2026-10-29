"""Which label-free signal finds the byte that separates merged message types? (design analysis, 2026-10-29)

For every family of the saved zero-shot runs that holds >= 2 truth types with >= MIN messages each, the oracle key
is the (offset, width) whose values best separate the truth types (homogeneity gain). For every candidate key
(offset < 48, width 1/2, 2..32 frequent values) label-free signals are computed and the oracle key's rank under each
is reported:
  echo     share of request/response pairs in which the partner carries the same value at the same offset
  determ   I(key; partner family) / H(partner family)  (request/response determinism)
  length   share of length variance explained by the key (eta^2)  (the signal of the earlier split)
  card     cardinality prior: 1 - |log2(#values) - 2| / 4 (prefers ~4 values, few and none dominant)
  combo    echo + determ + card (unweighted)
usage: signals.py [protocols]
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "dol/llm-parser-synthesis"))
import common  # noqa: E402

MIN = 20
SIGNALS = ("echo", "determ", "length", "card", "combo")


def H(c: Counter) -> float:
    n = sum(c.values())
    return -sum(v / n * math.log2(v / n) for v in c.values() if v) if n else 0.0


def load_pairs(p):
    partner = {}
    f = common.run_data(p) / "06_pairs.json"
    if f.exists():
        for x in json.loads(f.read_text()):
            a, b = int(x["request_msg_id"]), int(x["response_msg_id"])
            partner[a] = b; partner[b] = a
    return partner


def candidates(mids, payload):
    med = int(np.median([len(payload[m]) for m in mids]))
    for o in range(0, min(48, med)):
        for w in (1, 2):
            vals = [payload[m][o:o + w] for m in mids if len(payload[m]) >= o + w]
            if len(vals) < 0.9 * len(mids):
                continue
            c = Counter(vals)
            big = [v for v, k in c.items() if k >= max(MIN, 0.05 * len(mids))]
            if 2 <= len(big) <= 32 and c.most_common(1)[0][1] < 0.95 * len(vals):
                yield o, w


def key_of(b, o, w):
    return b[o:o + w] if len(b) >= o + w else None


def main():
    protos = sys.argv[1].split(",") if len(sys.argv) > 1 else common.PROTOS
    ranks = defaultdict(list); n_fam = 0
    for p in protos:
        d = common.load(p)
        types = {}
        for line in common.ann_path(p).open():
            a = json.loads(line)
            if a.get("type"):
                types[int(a["msg_id"])] = a["type"]
        partner = load_pairs(p)
        for f, mids in d["fams"].items():
            tc = Counter(types[m] for m in mids if m in types)
            if sum(1 for v in tc.values() if v >= MIN) < 2:
                continue
            typed = [m for m in mids if m in types]
            base_h = H(tc)
            cands = list(candidates(mids, d["payload"]))
            if not cands:
                continue
            gain, sig = {}, {s: {} for s in SIGNALS}
            for o, w in cands:
                # oracle: conditional entropy of truth type given the key
                g = defaultdict(Counter)
                for m in typed:
                    g[key_of(d["payload"][m], o, w)][types[m]] += 1
                cond = sum(sum(c.values()) * H(c) for c in g.values()) / len(typed)
                gain[(o, w)] = base_h - cond
                keys = [key_of(d["payload"][m], o, w) for m in mids]
                kc = Counter(keys)
                # echo
                pairs = [(m, partner[m]) for m in mids if m in partner]
                echo = np.mean([key_of(d["payload"][a], o, w) == key_of(d["payload"][b], o, w) for a, b in pairs]) if pairs else 0.0
                # determinism: I(key; partner family)/H(partner family)
                pf = [(key_of(d["payload"][a], o, w), d["assign"].get(b)) for a, b in pairs]
                hp = H(Counter(x[1] for x in pf))
                det = 0.0
                if hp > 0:
                    gg = defaultdict(Counter)
                    for k, fam in pf:
                        gg[k][fam] += 1
                    det = (hp - sum(sum(c.values()) * H(c) for c in gg.values()) / len(pf)) / hp
                # length eta^2
                L = np.array([len(d["payload"][m]) for m in mids], float)
                if L.var() > 0:
                    gm = defaultdict(list)
                    for k, l in zip(keys, L):
                        gm[k].append(l)
                    eta = sum(len(v) * (np.mean(v) - L.mean()) ** 2 for v in gm.values()) / (len(L) * L.var())
                else:
                    eta = 0.0
                nbig = sum(1 for v in kc.values() if v >= max(MIN, 0.05 * len(mids)))
                card = 1 - abs(math.log2(nbig) - 2) / 4
                for s, v in (("echo", echo), ("determ", det), ("length", eta), ("card", card), ("combo", echo + det + card)):
                    sig[s][(o, w)] = v
            best = max(gain, key=gain.get)
            if gain[best] < 0.5 * base_h:          # no single byte separates these types well
                continue
            n_fam += 1
            for s in SIGNALS:
                order = sorted(sig[s], key=lambda k: -sig[s][k])
                # rank of the best key among keys that separate as well as the oracle (within 90% of its gain)
                good = {k for k in gain if gain[k] >= 0.9 * gain[best]}
                ranks[s].append(min(order.index(k) for k in good) + 1)
        print(f"{p} done ({n_fam} families so far)", flush=True)
    print(f"\n{n_fam} merged families with a separating byte")
    for s in SIGNALS:
        r = np.array(ranks[s])
        print(f"{s:7s} top-1 {np.mean(r == 1):.2f}  top-3 {np.mean(r <= 3):.2f}  median rank {np.median(r):.0f}  (candidates per family ~{np.mean([1]):.0f})")


if __name__ == "__main__":
    main()
