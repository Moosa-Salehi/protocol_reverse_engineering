"""Layout-aware family refinement (user idea, 2026-10-29): split a stage-04 family where groups of its messages
confidently disagree on their field layout.

Edge probabilities come from the zero-shot boundary model applied WITHOUT families (one family; feature groups are
exact-length groups, so every message of a length group shares one probability vector). Inside a family, the
length groups are clustered agglomeratively (complete linkage) with
    distance(a, b) = number of offsets o < min(len_a, len_b, K) where one says p >= HI and the other p <= LO,
and the family is split at distance >= D into parts holding at least MIN_SHARE of its messages (smaller parts join
the nearest kept part). One noisy edge never splits a family when D >= 2.
"""
from __future__ import annotations

import importlib.util
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "src"))
from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402

TS = ROOT / "assets/pre_trained/fewshot_boundary_training.npz"
K, HI, LO = 64, 0.7, 0.3


def _b32():
    spec = importlib.util.spec_from_file_location("b32", ROOT / "scripts/diagnostics/32_build_fewshot_training_set.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def edge_probabilities(order: List[int], payload: Dict[int, bytes], exclude=(), training_set=TS) -> Dict[int, np.ndarray]:
    """Per message: probability that a field starts at offset o (index o, 0..K-1), family-free."""
    one = {i: "all" for i in order}
    body = _b32().body_starts(order, payload, one)
    groups = fsb.build_rows(order, one, payload, body, {})
    X, y, w, _ = fsb.load_training_set(str(training_set), exclude)
    model = fsb.hgb().fit(X, y, sample_weight=w)
    out: Dict[int, np.ndarray] = {}
    for g in groups:
        v = np.full(K, np.nan)
        s = model.predict_proba(g["X"])[:, 1]
        for o, p in zip(g["offs"], s):
            if o < K:
                v[o] = p
        for m in g["mids"]:
            out[m] = v
    return out


def _dist(a: np.ndarray, b: np.ndarray) -> int:
    ok = ~np.isnan(a) & ~np.isnan(b)
    return int(np.sum(ok & (((a >= HI) & (b <= LO)) | ((a <= LO) & (b >= HI)))))


def refine(order: List[int], family_of: Dict[int, Optional[str]], probs: Dict[int, np.ndarray],
           D: int = 2, min_share: float = 0.1, min_msgs: int = 20) -> Dict[int, Optional[str]]:
    fams: Dict[str, List[int]] = defaultdict(list)
    for m in order:
        f = family_of.get(m)
        if f not in (None, "noise") and m in probs:
            fams[str(f)].append(m)
    new = dict(family_of)
    for f, mids in fams.items():
        # unique probability vectors (one per length group) with their message counts
        keyed: Dict[int, List[int]] = defaultdict(list)
        for m in mids:
            keyed[id(probs[m])].append(m)
        units = list(keyed.values())
        if len(units) < 2:
            continue
        vecs = [probs[u[0]] for u in units]
        # complete-linkage agglomeration with threshold D
        clusters = [[k] for k in range(len(units))]
        dm = np.array([[_dist(vecs[a], vecs[b]) for b in range(len(units))] for a in range(len(units))])
        while True:
            best = None
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    d = max(dm[a, b] for a in clusters[i] for b in clusters[j])
                    if d < D and (best is None or d < best[0]):
                        best = (d, i, j)
            if best is None:
                break
            _, i, j = best
            clusters[i] += clusters.pop(j)
        if len(clusters) < 2:
            continue
        size = [sum(len(units[k]) for k in c) for c in clusters]
        total = sum(size)
        keep = [i for i, s in enumerate(size) if s >= max(min_msgs, min_share * total)]
        if len(keep) < 2:
            continue
        for i, c in enumerate(clusters):            # small parts join the nearest kept part
            if i in keep:
                continue
            tgt = min(keep, key=lambda k: min(dm[a, b] for a in c for b in clusters[k]))
            clusters[tgt] = clusters[tgt] + c
        order_keep = sorted(keep, key=lambda i: -sum(len(units[k]) for k in clusters[i]))
        for rank, i in enumerate(order_keep):
            name = f if rank == 0 else f"{f}_L{rank}"
            for k in clusters[i]:
                for m in units[k]:
                    new[m] = name
    return new
