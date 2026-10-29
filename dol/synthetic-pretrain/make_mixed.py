"""Training-set npz for the pipeline (main.py --fewshot-training-set) from the shipped real rows plus synthetic rows:
variant 'mixed' (real + synthetic, synthetic total weight = 13 real protocol units) or 'syn' (synthetic only).
Zero-shot thresholds: per excluded real protocol the value chosen on held-out synthetic protocols in the offline run
(offline json, variant C or B), and '*' (no exclusion, unseen protocols) chosen the same way with every real protocol.

usage: make_mixed.py <mixed|syn> <offline.json> <out.npz> <syn.npz>[,<syn2.npz>...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eval_offline as eo  # noqa: E402

ROOT = HERE.parents[1]


def main():
    variant, offline, out, syn_paths = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4].split(",")
    real = np.load(ROOT / "assets/pre_trained/fewshot_boundary_training.npz")
    names = [str(x) for x in real["protocols"]]
    Xs, ys, ws, ps, nsyn = eo.load(syn_paths)
    hold = ps % 10 == 0
    train = ~hold
    ntrain = len(np.unique(ps[train]))
    off = json.loads(offline.read_text())
    tag = "C" if variant == "mixed" else "B"
    thr = {q: off[q][tag]["t"] for q in names}
    # '*' threshold: model on everything (real + synthetic train), chosen on held-out synthetic protocols
    if variant == "mixed":
        wr = real["weight"].astype(float)
        X = np.vstack([real["X"], Xs[train]]); y = np.concatenate([real["y"], ys[train]])
        w = np.concatenate([wr, ws[train] * (len(names) / ntrain)])
    else:
        X, y, w = Xs[train], ys[train], ws[train].astype(float)
    m = eo.fsb.hgb().fit(X, y, sample_weight=w * len(w) / w.sum())
    thr["*"] = eo.heldout_threshold(m, Xs[hold], ys[hold], ws[hold], ps[hold])
    print("thresholds", thr)
    syn_names = [f"syn{k:05d}" for k in range(ntrain)]
    uniq = np.unique(ps[train]); remap = {int(u): k for k, u in enumerate(uniq)}
    syn_proto = np.array([remap[int(x)] for x in ps[train]], dtype=np.int32)
    if variant == "mixed":
        Xo = np.vstack([real["X"], Xs[train]]).astype(np.float32)
        yo = np.concatenate([real["y"], ys[train]])
        po = np.concatenate([real["proto"].astype(np.int32), syn_proto + len(names)])
        wo = np.concatenate([real["weight"], (ws[train] * (len(names) - 1) / ntrain).astype(np.float32)])
        allnames = names + syn_names
    else:   # real names kept (no rows) so exclusion lookups resolve; thresholds keyed by real names too
        Xo, yo, po, wo, allnames = Xs[train].astype(np.float32), ys[train], syn_proto, ws[train].astype(np.float32), syn_names
    np.savez_compressed(out, X=Xo, y=yo, proto=po.astype(np.int16 if len(allnames) < 32000 else np.int32), weight=wo,
                        protocols=np.array(allnames), zs_threshold_protocols=np.array(list(thr)),
                        zs_thresholds=np.array(list(thr.values()), dtype=float))
    print(f"wrote {out}: {len(yo)} rows, {len(allnames)} protocols")


if __name__ == "__main__":
    main()
