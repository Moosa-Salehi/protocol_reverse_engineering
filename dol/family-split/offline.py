"""Offline proxy for split.py on the saved zero-shot runs: message-type F1 with content pairing (greedy Jaccard >= 0.1,
as stage 17), number of families, for a grid of (T_DET, T_LEN). Choose on the 14 benchmark protocols; held-out
reported separately. usage: offline.py"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[0] / "llm-parser-synthesis"))
import common, split
from signals import load_pairs

GRID = [(9, 9), (0.3, 9), (0.5, 9), (0.7, 9), (9, 0.5), (9, 0.7), (0.5, 0.5), (0.5, 0.7), (0.7, 0.7)]


def mt_f1(family_of, types):
    fm, tm = defaultdict(set), defaultdict(set)
    for m, f in family_of.items():
        if f not in (None, "noise"):
            fm[str(f)].add(m)
    for m, t in types.items():
        tm[t].add(m)
    cand = sorted(((len(a & b) / len(a | b), f, t) for f, a in fm.items() for t, b in tm.items() if a & b), reverse=True)
    uf, ut, k = set(), set(), 0
    for j, f, t in cand:
        if j >= 0.1 and f not in uf and t not in ut:
            uf.add(f); ut.add(t); k += 1
    P, R = k / max(1, len(fm)), k / max(1, len(tm))
    return 2 * P * R / (P + R) if P + R else 0.0, len(fm)


res = {}
for p in common.PROTOS + common.HELDOUT:
    d = common.load(p)
    types = {}
    for line in common.ann_path(p).open():
        a = json.loads(line)
        if a.get("type"):
            types[int(a["msg_id"])] = a["type"]
    partner = load_pairs(p)
    row = {}
    for td, tl in GRID:
        new, log = (d["assign"], []) if (td, tl) == (9, 9) else split.split_families(d["order"], d["payload"], d["assign"], partner, td, tl)
        row[f"{td}/{tl}"] = mt_f1(new, types) + (len(log),)
    res[p] = row
    print(f"{p:10s} " + "  ".join(f"{k}: {v[0]:.2f} ({v[1]}f,{v[2]}s)" for k, v in row.items()), flush=True)
for name, S in (("benchmark", common.PROTOS), ("held-out", common.HELDOUT)):
    print(name + ": " + "  ".join(f"{k} {np.mean([res[p][k][0] for p in S]):.3f}" for k in res[S[0]]))
(HERE / "offline.json").write_text(json.dumps(res, indent=1))
