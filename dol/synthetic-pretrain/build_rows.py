"""Synthetic boundary-model training rows (idea 1): generate N random protocols (gen.py), turn each into the same
112-dim (family, length)-group rows as scripts/diagnostics/32_build_fewshot_training_set.py and save one npz per
chunk. Families are the true message types, with a fraction of type pairs merged to imitate imperfect family
discovery (stage 04 output is never perfectly pure on the real protocols).

usage: build_rows.py <out.npz> <first-seed> <n-protocols> [messages-per-protocol]
"""
from __future__ import annotations

import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from gen import generate_protocol  # noqa: E402
from protocol_re.inference import fewshot_boundaries as fsb  # noqa: E402
from protocol_re.inference.framing import infer_framing_hypotheses  # noqa: E402

MERGE_P = 0.25


def protocol_rows(seed: int, n_messages: int):
    r = random.Random(seed)
    msgs = generate_protocol(r, n_messages)
    types = sorted({m["type"] for m in msgs})
    fam = {t: t for t in types}
    for t in types:                       # merge some types into another one (impure families)
        if r.random() < MERGE_P and len(types) > 2:
            fam[t] = fam[r.choice(types)]
    order = list(range(len(msgs)))
    payload = {i: m["payload"] for i, m in enumerate(msgs)}
    family_of = {i: fam[m["type"]] for i, m in enumerate(msgs)}
    labels = {i: m["boundaries"] for i, m in enumerate(msgs)}
    grouped = defaultdict(list)
    for i in order:
        grouped[family_of[i]].append(payload[i].hex())
    framing = infer_framing_hypotheses(grouped)["families"]
    body = {}
    for f, res in framing.items():
        best = (res.get("layout_hypotheses") or [{}])[0]
        if best.get("body_start"):
            body[f] = int(best["body_start"])
    return fsb.build_rows(order, family_of, payload, body, labels), msgs


def main():
    out, first, n = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    n_messages = int(sys.argv[4]) if len(sys.argv) > 4 else 600
    per = {}
    for s in range(first, first + n):
        rows, _ = protocol_rows(s, n_messages)
        if any(g["y"] is not None and g["nann"] for g in rows):
            per[f"syn{s:05d}"] = rows
        if (s - first) % 50 == 0:
            print(f"seed {s}: {sum(len(g['offs']) for g in rows)} rows", flush=True)
    fsb.save_training_set(out, per)
    print(f"wrote {out} ({len(per)} protocols)")


if __name__ == "__main__":
    main()
