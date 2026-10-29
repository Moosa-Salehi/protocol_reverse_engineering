"""Value-dynamics features of a field (idea 5): how the field's values behave inside its family, across all families
at the same offset, between paired requests and responses, and over capture time. No byte values or protocol
names enter the feature vector, only statistics, so a classifier trained on synthetic protocols can be applied to
any capture.

Corpus = dict(order, payload, family_of, partner, session, ts) built by load_run() from a pipeline data dir, or by the
synthetic generator adapter (synth_corpus()).
"""
from __future__ import annotations

import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

ROLES = ["transaction_id", "length", "opcode", "address", "unit_id", "quantity", "status", "constant", "payload",
         "sequence_number", "timestamp", "checksum", "flags"]


def load_run(data_dir: Path) -> Dict:
    order, payload, session, ts = [], {}, {}, {}
    for line in (data_dir / "01_messages.jsonl").open(encoding="utf-8"):
        if line.strip():
            m = json.loads(line)
            i = int(m["msg_id"])
            order.append(i)
            payload[i] = bytes.fromhex(m["payload_hex"])
            session[i] = m.get("session_id") or m.get("session_key") or ""
            ts[i] = float(m.get("timestamp") or 0.0)
    family_of = {int(a["msg_id"]): str(a["family_id"]) for a in json.loads((data_dir / "02_family_assignments.json").read_text())["assignments"]}
    partner = {}
    pp = data_dir / "06_pairs.json"
    if pp.exists():
        for p in json.loads(pp.read_text()):
            a, b = int(p["request_msg_id"]), int(p["response_msg_id"])
            partner[a] = b; partner[b] = a
    return finish(dict(order=order, payload=payload, family_of=family_of, partner=partner, session=session, ts=ts))


def finish(c: Dict) -> Dict:
    fams = defaultdict(list)
    for i in c["order"]:
        f = c["family_of"].get(i)
        if f not in (None, "noise"):
            fams[f].append(i)
    c["fams"] = dict(fams)
    c["_cross"] = {}
    return c


def _ints(chunks: List[bytes], little: bool) -> np.ndarray:
    return np.array([int.from_bytes(b, "little" if little else "big") for b in chunks], dtype=np.float64)


def _entropy(counter: Counter, n: int) -> float:
    return -sum(v / n * math.log2(v / n) for v in counter.values()) if n else 0.0


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 3 or a.std() == 0 or b.std() == 0:
        return 0.0
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def _session_steps(mids: List[int], vals: np.ndarray, session: Dict[int, str]):
    """Fraction of consecutive same-session pairs whose value increases by 1-2 / by >0 / stays equal."""
    last: Dict[str, float] = {}
    inc12 = inc = eq = n = 0
    for m, v in zip(mids, vals):
        s = session.get(m, "")
        if s in last:
            d = v - last[s]; n += 1
            inc12 += 1 <= d <= 2; inc += d > 0; eq += d == 0
        last[s] = v
    return (inc12 / n, inc / n, eq / n) if n else (0.0, 0.0, 0.0)


def _cross(c: Dict, s: int, w: int):
    key = (s, w)
    if key in c["_cross"]:
        return c["_cross"][key]
    vals, fams = [], []
    for f, mids in c["fams"].items():
        for m in mids[:400]:
            b = c["payload"][m]
            if len(b) >= s + w:
                vals.append(b[s:s + w]); fams.append(f)
    n = len(vals)
    if n < 2:
        out = (0.0, 0.0, 0.0, 0.0)
    else:
        hv = _entropy(Counter(vals), n); hf = _entropy(Counter(fams), n)
        hj = _entropy(Counter(zip(vals, fams)), n)
        mi = hv + hf - hj
        by = defaultdict(set)
        for v, f in zip(vals, fams):
            by[f].add(v)
        const_frac = sum(1 for f in by if len(by[f]) == 1) / len(by)
        out = (min(1.0, hv / (8 * w)), mi / hf if hf else 0.0, const_frac, math.log2(1 + len(set(vals))))
    c["_cross"][key] = out
    return out


def field_features(c: Dict, fam: str, s: int, w: int, body_start: Optional[int] = None) -> Optional[np.ndarray]:
    mids = [m for m in c["fams"].get(fam, []) if len(c["payload"][m]) >= s + w][:2000]
    if len(mids) < 2 or w <= 0:
        return None
    w8 = min(w, 8)
    chunks = [c["payload"][m][s:s + w8] for m in mids]
    lens = np.array([len(c["payload"][m]) for m in mids], dtype=np.float64)
    n = len(chunks)
    cnt = Counter(chunks)
    H = _entropy(cnt, n)
    f = [w, min(s, 64), s / max(1.0, float(np.median(lens))), float(np.median(lens)) - s - w,
         float(body_start is not None and s < body_start), float(s + w == np.median(lens)),
         len(cnt) / n, math.log2(1 + len(cnt)), H / (8 * w8), cnt.most_common(1)[0][1] / n,
         sum(b.count(0) for b in chunks) / (n * w8), sum(sum(1 for x in b if 32 <= x < 127) for b in chunks) / (n * w8)]
    ts = np.array([c["ts"].get(m, 0.0) for m in mids])
    for little in (False, True):
        v = _ints(chunks, little)
        d = np.diff(v)
        f += [float((d >= 0).mean()) if len(d) else 0.0, float(((d >= 1) & (d <= 2)).mean()) if len(d) else 0.0]
        f += list(_session_steps(mids, v, c["session"]))
        best = 0.0
        for k in range(-8, 9):                                 # value == length - k (total / after-field / layer)
            best = max(best, float((v == lens - k).mean()), float((v == lens - s - w - k).mean()))
        f += [best, _spearman(v, lens), _spearman(v, ts), float((v < 64).mean()),
              math.log2(1 + v.max()) / (8 * w8) if v.max() > 0 else 0.0]
        if w == 4:
            fl = []
            for b in chunks[:500]:
                x = struct.unpack("<f" if little else ">f", b)[0]
                fl.append(math.isfinite(x) and (x == 0 or 1e-4 < abs(x) < 1e7))
            f.append(float(np.mean(fl)))
        else:
            f.append(0.0)
    ors = 0
    for b in cnt:
        ors |= int.from_bytes(b, "big")
    f += [bin(ors).count("1") / (8 * w8), float(np.mean([bin(int.from_bytes(b, "big")).count("1") <= 1 for b in chunks]))]
    f += list(_cross(c, s, w8))
    echo = [c["payload"][m][s:s + w8] == c["payload"][c["partner"][m]][s:s + w8] for m in mids
            if m in c["partner"] and len(c["payload"][c["partner"][m]]) >= s + w8]
    f += [float(np.mean(echo)) if echo else -1.0, len(echo) / n]
    return np.array(f, dtype=np.float32)


# ------------------------------------------------------------- synthetic adapter

def synth_corpus(msgs: List[Dict], merge: Dict[str, str]) -> Dict:
    order = list(range(len(msgs)))
    payload = {i: m["payload"] for i, m in enumerate(msgs)}
    family_of = {i: merge.get(m["type"], m["type"]) for i, m in enumerate(msgs)}
    partner = {}
    for i, m in enumerate(msgs):
        if m.get("pair") is not None:
            partner[i] = m["pair"]; partner[m["pair"]] = i
    session = {i: m.get("session", "s0") for i, m in enumerate(msgs)}
    ts = {i: m.get("t", float(i)) for i in order}
    return finish(dict(order=order, payload=payload, family_of=family_of, partner=partner, session=session, ts=ts))
