"""Offline check of refine.py on the saved zero-shot runs: V-measure / homogeneity / completeness against the
truth message types for a small grid of (D, min_share). Parameters are chosen on the 14 benchmark protocols only;
the 4 held-out protocols are reported separately. Edge probabilities are cached in probs/<p>.npz.
usage: grid.py [protocols]"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from sklearn import metrics

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[0] / "llm-parser-synthesis"))
import common  # noqa: E402
import refine  # noqa: E402

GRID = [(1, 0.1), (2, 0.05), (2, 0.1), (2, 0.2), (3, 0.1), (4, 0.1)]


def probs_for(p, d):
    f = HERE / "probs" / f"{p}.npz"
    if f.exists():
        z = np.load(f)
        ids, P = z["ids"], z["P"]
        # messages of one length group share one vector object (refine relies on identity)
        cache, out = {}, {}
        for i, row in zip(ids, P):
            key = row.tobytes()
            out[int(i)] = cache.setdefault(key, row)
        return out
    pr = refine.edge_probabilities(d["order"], d["payload"], exclude=[p] if p in common.PROTOS else [])
    f.parent.mkdir(exist_ok=True)
    ids = np.array(list(pr)); np.savez_compressed(f, ids=ids, P=np.array([pr[i] for i in ids]))
    return probs_for(p, d)


def main():
    protos = sys.argv[1].split(",") if len(sys.argv) > 1 else common.PROTOS + common.HELDOUT
    res = {}
    for p in protos:
        d = common.load(p)
        types = {}
        for line in common.ann_path(p).open():
            a = json.loads(line)
            if a.get("type") and int(a["msg_id"]) in d["payload"]:
                types[int(a["msg_id"])] = a["type"]
        ids = [i for i in d["order"] if i in types]
        y = [types[i] for i in ids]
        pr = probs_for(p, d)
        row = {}
        base = [str(d["assign"].get(i)) for i in ids]
        row["pipe"] = metrics.homogeneity_completeness_v_measure(y, base) + (len(set(base)),)
        for D, ms in GRID:
            new = refine.refine(d["order"], d["assign"], pr, D=D, min_share=ms)
            lab = [str(new.get(i)) for i in ids]
            row[f"D{D}/{ms}"] = metrics.homogeneity_completeness_v_measure(y, lab) + (len(set(lab)),)
        res[p] = row
        print(f"{p:10s} " + "  ".join(f"{k} V {v[2]:.2f} ({v[3]})" for k, v in row.items()), flush=True)
    for name, S in (("benchmark", common.PROTOS), ("held-out", common.HELDOUT)):
        S = [p for p in S if p in res]
        if S:
            print(name + ": " + "  ".join(f"{k} V {np.mean([res[p][k][2] for p in S]):.3f} h {np.mean([res[p][k][0] for p in S]):.3f} "
                                          f"c {np.mean([res[p][k][1] for p in S]):.3f}" for k in res[S[0]]))
    (HERE / "grid.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
