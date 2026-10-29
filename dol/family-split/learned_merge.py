"""Learned family merge (zero-shot), offline proxy, 2026-10-29.

A gradient-boosted classifier decides whether two families of a capture are the same message type. Training pairs
come from the OTHER benchmark protocols' saved zero-shot runs (leave-one-protocol-out; label = both families' majority
truth type is the same); the target protocol's labels are used only for scoring. Pair features are label-free:
direction agreement, constant-and-equal / constant-and-conflicting offsets (first K bytes), first conflict offset,
mean Jensen-Shannon divergence of the byte distributions over the common prefix, length-set overlap, median-length
ratio, size ratio, overlap of request/response partner families. Pairs with p >= TAU are merged (union-find,
largest family keeps its name). Proxy: message-type F1 with content pairing (offline.mt_f1).
usage: learned_merge.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[0] / "llm-parser-synthesis"))
import common  # noqa: E402
from offline import mt_f1  # noqa: E402
from signals import load_pairs  # noqa: E402

K, MIN = 32, 20
TAUS = (0.5, 0.7, 0.9)


def dists(mids, payload, med):
    D = np.zeros((min(K, med), 256))
    for m in mids[:2000]:
        b = payload[m]
        for o in range(min(K, med, len(b))):
            D[o, b[o]] += 1
    return D / np.maximum(1, D.sum(1, keepdims=True))


def js(p, q):
    m = (p + q) / 2
    f = lambda a, b: np.sum(np.where(a > 0, a * np.log2(np.where(a > 0, a, 1) / np.where(b > 0, b, 1)), 0))  # noqa: E731
    return 0.5 * f(p, m) + 0.5 * f(q, m)


def protocol_pairs(p):
    d = common.load(p)
    types = {}
    for line in common.ann_path(p).open():
        a = json.loads(line)
        if a.get("type"):
            types[int(a["msg_id"])] = a["type"]
    direction = {}
    for line in open(common.run_data(p) / "01_messages.jsonl"):
        m = json.loads(line); direction[int(m["msg_id"])] = m.get("direction") or ""
    partner = load_pairs(p)
    fams = {f: ms for f, ms in d["fams"].items() if len(ms) >= MIN}
    info = {}
    for f, ms in fams.items():
        lens = [len(d["payload"][m]) for m in ms]
        med = int(np.median(lens))
        D = dists(ms, d["payload"], med)
        const = {o: int(np.argmax(D[o])) for o in range(len(D)) if D[o].max() >= 0.95}
        tc = Counter(types[m] for m in ms if m in types)
        info[f] = dict(n=len(ms), med=med, lens=set(lens), D=D, const=const,
                       dir=Counter(direction.get(m, "") for m in ms).most_common(1)[0][0],
                       partners=Counter(d["assign"].get(partner[m]) for m in ms if m in partner),
                       type=tc.most_common(1)[0][0] if tc else None)
    X, y, keys = [], [], []
    for a, b in combinations(sorted(fams), 2):
        A, B = info[a], info[b]
        n = min(len(A["D"]), len(B["D"]))
        eq = sum(1 for o in range(n) if o in A["const"] and o in B["const"] and A["const"][o] == B["const"][o])
        cf = [o for o in range(n) if o in A["const"] and o in B["const"] and A["const"][o] != B["const"][o]]
        jsd = float(np.mean([js(A["D"][o], B["D"][o]) for o in range(n)])) if n else 1.0
        pa, pb = set(A["partners"]), set(B["partners"])
        X.append([float(A["dir"] == B["dir"]), eq / max(1, n), len(cf) / max(1, n), (cf[0] / K) if cf else 1.0, jsd,
                  len(A["lens"] & B["lens"]) / len(A["lens"] | B["lens"]), min(A["med"], B["med"]) / max(A["med"], B["med"]),
                  min(A["n"], B["n"]) / max(A["n"], B["n"]), len(pa & pb) / max(1, len(pa | pb)), n / K])
        y.append(int(A["type"] is not None and A["type"] == B["type"]))
        keys.append((a, b))
    return d, types, np.array(X), np.array(y), keys


def apply_merges(d, keys, prob, tau):
    parent = {}
    find = lambda x: x if parent.get(x, x) == x else find(parent[x])  # noqa: E731
    size = {f: len(ms) for f, ms in d["fams"].items()}
    for (a, b), p in sorted(zip(keys, prob), key=lambda t: -t[1]):
        if p >= tau:
            ra, rb = find(a), find(b)
            if ra != rb:
                if size[ra] < size[rb]:
                    ra, rb = rb, ra
                parent[rb] = ra; size[ra] += size[rb]
    return {m: (find(f) if f not in (None, "noise") else f) for m, f in d["assign"].items()}


def main():
    data = {p: protocol_pairs(p) for p in common.PROTOS + common.HELDOUT}
    print("pairs / positives:", {p: (len(v[3]), int(v[3].sum())) for p, v in data.items()}, flush=True)
    res = {}
    for p in common.PROTOS + common.HELDOUT:
        train = [q for q in common.PROTOS if q != p and len(data[q][3])]
        X = np.vstack([data[q][2] for q in train]); y = np.concatenate([data[q][3] for q in train])
        w = np.concatenate([np.full(len(data[q][3]), 1.0 / len(data[q][3])) for q in train])
        clf = HistGradientBoostingClassifier(max_iter=200, max_depth=3, learning_rate=0.05, random_state=0).fit(X, y, sample_weight=w * len(w) / w.sum())
        d, types, Xp, yp, keys = data[p]
        prob = clf.predict_proba(Xp)[:, 1] if len(Xp) else np.array([])
        row = {"base": mt_f1(d["assign"], types)[0]}
        for tau in TAUS:
            row[f"tau{tau}"] = mt_f1(apply_merges(d, keys, prob, tau), types)[0]
        if len(yp) and yp.any() and not yp.all():
            from sklearn.metrics import roc_auc_score
            row["auc"] = roc_auc_score(yp, prob)
        res[p] = row
        print(f"{p:10s} " + "  ".join(f"{k} {v:.3f}" for k, v in row.items()), flush=True)
    for name, S in (("benchmark", common.PROTOS), ("held-out", common.HELDOUT)):
        print(name + ": " + "  ".join(f"{k} {np.mean([res[p][k] for p in S]):.3f}" for k in ["base"] + [f"tau{t}" for t in TAUS]))
    (HERE / "learned_merge.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
