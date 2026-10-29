"""Layout-first clustering, feasibility check (user idea 2026-10-29): would grouping messages by their field layout
fix family-discovery errors? V-measure / homogeneity / completeness against the truth message types (annotation
'type') of
  pipe        the saved zero-shot run's families
  truth-lay   groups = truth boundary layout (edges < 64)            upper bound of "layout as the only feature"
  inf-lay     groups = layout inferred WITHOUT families (zero-shot boundary model, one family, groups by length)
  pipe+inf    pipeline families split by inferred layout
  pipe+truth  pipeline families split by truth layout                upper bound of "layout added to the features"
usage: check.py [protocols]
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "dol/llm-parser-synthesis"))

from sklearn import metrics  # noqa: E402

import common  # noqa: E402
from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402

spec = importlib.util.spec_from_file_location("b32", ROOT / "scripts/diagnostics/32_build_fewshot_training_set.py")
b32 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b32)
TS = ROOT / "assets/pre_trained/fewshot_boundary_training.npz"
K = 64


def layout(edges, n):
    return tuple(e for e in edges if e < min(K, n)) + (min(n, K) if n < K else -1,)


def main():
    protos = sys.argv[1].split(",") if len(sys.argv) > 1 else common.PROTOS + common.HELDOUT
    out = {}
    for p in protos:
        d = common.load(p)
        types = {}
        for line in common.ann_path(p).open():
            a = json.loads(line)
            if a.get("type") and int(a["msg_id"]) in d["payload"]:
                types[int(a["msg_id"])] = a["type"]
        ids = [i for i in d["order"] if i in types and i in d["truth"]]
        one = {i: "all" for i in d["order"]}
        body = b32.body_starts(d["order"], d["payload"], one)
        inf, _ = fsb.predict_edges_zeroshot(d["order"], one, d["payload"], body, str(TS),
                                            exclude=[p] if p in common.PROTOS else [])
        y = [types[i] for i in ids]
        n = {i: len(d["payload"][i]) for i in ids}
        groups = {
            "pipe": [d["assign"].get(i, "?") for i in ids],
            "truth-lay": [layout(d["truth"][i], n[i]) for i in ids],
            "inf-lay": [layout(sorted(inf.get(i, ())), n[i]) for i in ids],
            "pipe+inf": [(d["assign"].get(i, "?"), layout(sorted(inf.get(i, ())), n[i])) for i in ids],
            "pipe+truth": [(d["assign"].get(i, "?"), layout(d["truth"][i], n[i])) for i in ids],
        }
        row = {}
        for k, g in groups.items():
            lab = [str(x) for x in g]
            h, c, v = metrics.homogeneity_completeness_v_measure(y, lab)
            row[k] = dict(v=v, h=h, c=c, k=len(set(lab)))
        out[p] = row
        print(f"{p:10s} types {len(set(y)):3d} | " + " | ".join(f"{k} V {r['v']:.2f} (h {r['h']:.2f} c {r['c']:.2f}, {r['k']})" for k, r in row.items()), flush=True)
    import numpy as np
    for k in ("pipe", "truth-lay", "inf-lay", "pipe+inf", "pipe+truth"):
        print(f"mean {k:10s} V {np.mean([out[p][k]['v'] for p in out]):.3f}  h {np.mean([out[p][k]['h'] for p in out]):.3f}  c {np.mean([out[p][k]['c'] for p in out]):.3f}")
    (HERE / "check.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
