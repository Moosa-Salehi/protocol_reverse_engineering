"""Rescore saved runs with content-based pairing; compare with the shipped evaluator. usage: rescore_all.py"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[2]; HERE = Path(__file__).parent
P = ["bacnet","cip","dnp3","enip","ethercat","goose","hart_ip","iec104","mms","modbus","opcua","powerlink","s7comm","zigbee"]
H = ["synphasor","ams","doip","cnip"]
RUNS = {"zs": ("dol/final-v4/zs", P), "fs50": ("dol/final-v4/fs50", P), "rules": ("dol/final-v4/full", P),
        "fs10": ("dol/final-v4/fs10", P), "oracle-clusters": ("dol/oracle-ceilings/runs/oracle-clusters", P),
        "fs50+oracle-clusters": ("dol/oracle-ceilings/runs/fs50-oracle-clusters", P),
        "ho-zs": ("dol/heldout-truth/runs/zs", H), "ho-rules": ("dol/heldout-truth/runs/rules", H), "ho-fs50": ("dol/heldout-truth/runs/fs50", H)}
M = ["overall", "message_type_matching", "field_boundary", "field_semantics", "relations"]
def metrics(f):
    r = json.load(open(f)); return {"overall": r["summary"]["overall_score"], **{k: r["metrics"][k]["f1_score"] for k in M[1:]}}
res = {}
for name, (run, protos) in RUNS.items():
    res[name] = {}
    for p in protos:
        d = ROOT / run / p / "data"
        if not (d / "15_evaluation_result.json").exists(): continue
        truth = ROOT / ("truth_files/heldout" if p in H else "truth_files") / f"{p}.json"
        ann = ROOT / ("dol/heldout-truth/annotations" if p in H else "dol/accuracy-push/annotations-truthconv") / f"{p}.jsonl"
        out = HERE / "runs" / name / f"{p}.json"; out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists():
            subprocess.run([sys.executable, str(HERE / "rescore.py"), str(d), str(truth), str(ann), str(out)], check=True, capture_output=True)
        res[name][p] = {"old": metrics(d / "15_evaluation_result.json"), "new": metrics(out)}
    ps = list(res[name])
    print(f"{name:22s} n={len(ps):2d} " + "  ".join(f"{m[:8]} {np.mean([res[name][p]['old'][m] for p in ps]):.3f}->{np.mean([res[name][p]['new'][m] for p in ps]):.3f}" for m in M), flush=True)
(HERE / "rescore.json").write_text(json.dumps(res, indent=1))
