"""Shared loading for the parser-synthesis experiments: per protocol, the saved zero-shot run's families and
per-message pipeline edges (same construction as dol/baseline-comparison/scripts/score.py:our_preds), and the
truth-convention per-message boundaries."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from protocol_re.inference.tlv import message_layout_edges  # noqa: E402

PROTOS = ["bacnet", "cip", "dnp3", "enip", "ethercat", "goose", "hart_ip", "iec104", "mms", "modbus", "opcua", "powerlink",
          "s7comm", "zigbee"]
HELDOUT = ["synphasor", "ams", "doip", "cnip"]


def run_data(p: str, mode: str = "zs") -> Path:
    return ROOT / (f"dol/heldout-truth/runs/{mode}" if p in HELDOUT else f"dol/final-v4/{mode}") / p / "data"


def labels_path(p: str) -> Path:
    return ROOT / ("dol/heldout-truth/labels" if p in HELDOUT else "dol/accuracy-push/integrated-labels") / f"{p}.jsonl"


def ann_path(p: str) -> Path:
    return ROOT / ("dol/heldout-truth/annotations" if p in HELDOUT else "dol/accuracy-push/annotations-truthconv") / f"{p}.jsonl"


def load(p: str, mode: str = "zs"):
    data = run_data(p, mode)
    families = json.loads((data / "05_families.json").read_text())
    assign = {int(a["msg_id"]): str(a["family_id"]) for a in json.loads((data / "02_family_assignments.json").read_text())["assignments"]}
    fam_edges = {}
    for fid, d in families.items():
        v = set()
        for f in d.get("field_hypotheses", []) or []:
            s = int(f.get("start", 0) or 0); v.update((s, s + int(f.get("length", 0) or 0)))
        fam_edges[str(fid)] = sorted(v)
    payload, order = {}, []
    for line in (data / "01_messages.jsonl").open(encoding="utf-8"):
        if line.strip():
            m = json.loads(line); i = int(m["msg_id"]); order.append(i); payload[i] = bytes.fromhex(m["payload_hex"])
    pipe = {}
    for i in order:
        fid = assign.get(i)
        e = fam_edges.get(fid or "", [])
        layout = families.get(fid, {}).get("message_layout") if fid else None
        if layout:
            e = message_layout_edges(payload[i], e, layout)
        pipe[i] = sorted({x for x in e if 0 < x < len(payload[i])})
    truth = {}
    for line in ann_path(p).open(encoding="utf-8"):
        if line.strip():
            a = json.loads(line)
            if a.get("boundaries") and a.get("reviewer") != "tshark-cache":
                i = int(a["msg_id"])
                if i in payload:
                    truth[i] = sorted({int(x) for x in a["boundaries"] if 0 < int(x) < len(payload[i])})
    fams = defaultdict(list)
    for i in order:
        f = assign.get(i)
        if f not in (None, "noise"):
            fams[f].append(i)
    labels = {}
    if mode != "zs":
        for line in labels_path(p).open(encoding="utf-8"):
            if line.strip():
                a = json.loads(line); i = int(a["msg_id"])
                if i in payload:
                    labels[i] = sorted({int(x) for x in a["boundaries"] if 0 < int(x) < len(payload[i])})
    return dict(order=order, payload=payload, assign=assign, families=families, pipe=pipe, truth=truth, fams=dict(fams),
                labels=labels)


def prf(pred: dict, truth: dict, ids):
    tp = fp = fn = 0
    for i in ids:
        if i not in truth:
            continue
        p, t = set(pred.get(i, [])), set(truth[i])
        tp += len(p & t); fp += len(p - t); fn += len(t - p)
    P = tp / (tp + fp) if tp + fp else 0.0
    R = tp / (tp + fn) if tp + fn else 0.0
    return dict(tp=tp, fp=fp, fn=fn, p=P, r=R, f1=2 * P * R / (P + R) if P + R else 0.0)
