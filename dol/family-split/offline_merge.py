"""Offline proxy (message-type F1, content pairing) for merge.py, and merge followed by split.py (determinism)."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[0] / "llm-parser-synthesis"))
import common, merge, split
from signals import load_pairs
from offline import mt_f1
res = {}
for p in common.PROTOS + common.HELDOUT:
    d = common.load(p)
    types = {}
    for line in common.ann_path(p).open():
        a = json.loads(line)
        if a.get("type"): types[int(a["msg_id"])] = a["type"]
    direction = {}
    for line in open(common.run_data(p) / "01_messages.jsonl"):
        m = json.loads(line); direction[int(m["msg_id"])] = m.get("direction") or ""
    partner = load_pairs(p)
    m1, log = merge.merge_families(d["order"], d["payload"], d["assign"], direction)
    m2, log2 = split.split_families(d["order"], d["payload"], m1, partner, 0.5, 9)
    res[p] = {"base": mt_f1(d["assign"], types), "merge": mt_f1(m1, types) + (len(log),), "merge+split": mt_f1(m2, types) + (len(log2),)}
    print(f"{p:10s} " + "  ".join(f"{k} {v[0]:.2f} ({v[1]}f)" for k, v in res[p].items()), flush=True)
for name, S in (("benchmark", common.PROTOS), ("held-out", common.HELDOUT)):
    print(name + ": " + "  ".join(f"{k} {np.mean([res[p][k][0] for p in S]):.3f}" for k in ("base", "merge", "merge+split")))
