"""Learned boundary prior for the selection score: the zero-shot boundary model (shipped training rows, the target
protocol excluded, as in the pipeline's default configuration) gives every (family, offset) a mean edge probability.
prior_bits(edges) = sum over offsets 1..len-1 of -log2 p (edge) or -log2 (1 - p) (no edge). Cached per protocol."""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import common

sys.path.insert(0, str(common.ROOT / "scripts/diagnostics"))
from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402

CACHE = Path(__file__).resolve().parent / "prior_cache"
TS = common.ROOT / "assets/pre_trained/fewshot_boundary_training.npz"


def family_probability(p: str, d) -> dict:
    CACHE.mkdir(exist_ok=True)
    f = CACHE / f"{p}.json"
    if f.exists():
        return {k: {int(o): v for o, v in m.items()} for k, m in json.loads(f.read_text()).items()}
    import importlib.util
    spec = importlib.util.spec_from_file_location("b32", common.ROOT / "scripts/diagnostics/32_build_fewshot_training_set.py")
    b32 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b32)
    family_of = {i: d["assign"].get(i) for i in d["order"]}
    body = b32.body_starts(d["order"], d["payload"], family_of)
    _pred, info = fsb.predict_edges_zeroshot(d["order"], family_of, d["payload"], body, str(TS),
                                             exclude=[p] if p in common.PROTOS else [], posts=())
    fp = {str(k): {int(o): float(v) for o, v in m.items()} for k, m in info["family_probability"].items()}
    f.write_text(json.dumps(fp))
    return fp


def prior_bits(probs: dict, payloads, edge_lists, eps: float = 0.02) -> float:
    total = 0.0
    for b, e in zip(payloads, edge_lists):
        es = set(e)
        for o in range(1, min(len(b), fsb.MAXLEN)):
            q = min(1 - eps, max(eps, probs.get(o, 0.5)))
            total += -math.log2(q) if o in es else -math.log2(1 - q)
    return total
