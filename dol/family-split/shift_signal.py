"""Shift-aligned merge rule: for families A, B find the shift s in [-16, 16] maximising the number of offsets where both
are constant with the same value (A at o, B at o+s, o < K); merge when that best shift has >= E matches beyond the
first BASE bytes and no conflicting constant in the aligned region from the first such match on. Precision / recall
over same-type pairs as in aligned_signal.py."""
import json, sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "llm-parser-synthesis")); sys.path.insert(0, ".")
import common
from aligned_signal import consts
MIN, K = 20, 48
def best_shift(a, b):
    best = (0, 0, None)
    for s in range(-16, 17):
        m = [o for o, v in a.items() if o + s in b and b[o + s] == v]
        if len(m) > best[0]:
            best = (len(m), s, m)
    return best
tot = defaultdict(Counter)
for p in common.PROTOS + common.HELDOUT:
    d = common.load(p); types = {}
    for line in common.ann_path(p).open():
        a = json.loads(line)
        if a.get("type"): types[int(a["msg_id"])] = a["type"]
    direction = {int(json.loads(l)["msg_id"]): json.loads(l).get("direction") or "" for l in open(common.run_data(p) / "01_messages.jsonl")}
    fams = {f: ms for f, ms in d["fams"].items() if len(ms) >= MIN}
    info = {f: dict(type=(Counter(types[m] for m in ms if m in types).most_common(1) or [(None, 0)])[0][0],
                    dir=Counter(direction.get(m, "") for m in ms).most_common(1)[0][0], c=consts(ms, d["payload"], 0, K)) for f, ms in fams.items()}
    c = defaultdict(Counter)
    for a, b in combinations(sorted(fams), 2):
        A, B = info[a], info[b]
        if A["dir"] != B["dir"] or A["type"] is None or B["type"] is None: continue
        same = A["type"] == B["type"]
        n, s, m = best_shift(A["c"], B["c"])
        for E, BASE in ((2, 4), (3, 4), (2, 8)):
            beyond = [o for o in (m or []) if o >= BASE]
            ok = False
            if s != 0 and len(beyond) >= E:
                start = min(beyond)
                conf = any(o >= start and o + s in B["c"] and B["c"][o + s] != v for o, v in A["c"].items())
                ok = not conf
            elif s == 0:
                start = BASE
                conf = any(o >= start and o in B["c"] and B["c"][o] != v for o, v in A["c"].items())
                ok = (not conf) and len(beyond) >= E
            c[f"E{E}/B{BASE}"][(ok, same)] += 1
    for r in c: tot[r] += c[r]
    print(p, "  ".join(f"{r}: {c[r][(True, True)]}ok/{c[r][(True, False)]}wrong" for r in c), flush=True)
for r, t in tot.items():
    tp, fp, fn = t[(True, True)], t[(True, False)], t[(False, True)]
    print(f"POOLED {r}: precision {tp / max(1, tp + fp):.2f} recall {tp / max(1, tp + fn):.2f} (ok {tp}, wrong {fp}, missed {fn})")
