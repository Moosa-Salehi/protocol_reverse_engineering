"""Does aligning families at their inferred body start separate same-type from different-type family pairs better
than raw offsets? Pairs of the saved zero-shot runs' families (>= MIN messages, same majority direction); label =
same majority truth type. Body start per family from the run's framing (04_framing.json, best layout hypothesis).

Rules (merge when true):
  raw       no conflicting constant at offsets 0..K-1 (raw)                  (the failed merge.py rule)
  body      no conflicting constant at body offsets 0..7, and >= 1 equal constant at body offsets 0..3
  body+hdr  'body' and the two header lengths are equal or the shorter header's bytes agree where both constant
Precision / recall of the merge decision over same-type pairs, per protocol and pooled.
usage: aligned_signal.py [protocols]"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "llm-parser-synthesis"))
import common  # noqa: E402

MIN, K, CONST = 20, 32, 0.95


def consts(mids, payload, start, n):
    out = {}
    for j in range(n):
        c = Counter(payload[m][start + j] for m in mids if len(payload[m]) > start + j)
        if c and sum(c.values()) >= 0.5 * len(mids):
            v, k = c.most_common(1)[0]
            if k >= CONST * sum(c.values()):
                out[j] = v
    return out


def body_start(p):
    f = json.loads((common.run_data(p) / "04_framing.json").read_text())["families"]
    out = {}
    for fam, r in f.items():
        h = (r.get("layout_hypotheses") or [{}])[0]
        out[fam] = int(h.get("body_start") or 0)
    return out


def main():
    protos = sys.argv[1].split(",") if len(sys.argv) > 1 else common.PROTOS + common.HELDOUT
    tot = defaultdict(lambda: Counter())
    for p in protos:
        d = common.load(p)
        types = {}
        for line in common.ann_path(p).open():
            a = json.loads(line)
            if a.get("type"):
                types[int(a["msg_id"])] = a["type"]
        direction = {}
        for line in open(common.run_data(p) / "01_messages.jsonl"):
            m = json.loads(line); direction[int(m["msg_id"])] = m.get("direction") or ""
        bs = body_start(p)
        fams = {f: ms for f, ms in d["fams"].items() if len(ms) >= MIN}
        info = {}
        for f, ms in fams.items():
            tc = Counter(types[m] for m in ms if m in types)
            b = bs.get(f, 0)
            info[f] = dict(type=tc.most_common(1)[0][0] if tc else None,
                           dir=Counter(direction.get(m, "") for m in ms).most_common(1)[0][0],
                           raw=consts(ms, d["payload"], 0, K), body=consts(ms, d["payload"], b, 8), bs=b,
                           hdr=consts(ms, d["payload"], 0, b))
        c = defaultdict(Counter)
        for a, b in combinations(sorted(fams), 2):
            A, B = info[a], info[b]
            if A["dir"] != B["dir"] or A["type"] is None or B["type"] is None:
                continue
            same = A["type"] == B["type"]
            raw = not any(o in B["raw"] and B["raw"][o] != v for o, v in A["raw"].items())
            bconf = any(j in B["body"] and B["body"][j] != v for j, v in A["body"].items())
            beq = any(j in B["body"] and B["body"][j] == v for j, v in A["body"].items() if j < 4)
            body = (not bconf) and beq
            hconf = any(o in B["hdr"] and B["hdr"][o] != v for o, v in A["hdr"].items() if o < min(A["bs"], B["bs"]))
            for rule, dec in (("raw", raw), ("body", body), ("body+hdr", body and not hconf)):
                c[rule][(dec, same)] += 1
        for rule in c:
            tot[rule] += c[rule]
        print(f"{p:10s} same-type pairs {c['raw'][(True, True)] + c['raw'][(False, True)]:3d}  " +
              "  ".join(f"{r}: merges {c[r][(True, True)]}ok/{c[r][(True, False)]}wrong" for r in ("raw", "body", "body+hdr")), flush=True)
    for r in ("raw", "body", "body+hdr"):
        t = tot[r]; tp, fp, fn = t[(True, True)], t[(True, False)], t[(False, True)]
        print(f"POOLED {r:9s} precision {tp / max(1, tp + fp):.2f}  recall {tp / max(1, tp + fn):.2f}  (correct merges {tp}, wrong merges {fp}, missed {fn})")


if __name__ == "__main__":
    main()
