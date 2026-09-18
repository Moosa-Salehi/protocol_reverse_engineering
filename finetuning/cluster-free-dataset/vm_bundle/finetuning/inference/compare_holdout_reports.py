#!/usr/bin/env python3
"""Compare base-model and fine-tuned holdout evaluation reports."""
from __future__ import annotations
import argparse, json
from pathlib import Path

METRICS=("json_validity","exact_match","precision","recall","f1")

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("--base",type=Path,required=True); p.add_argument("--finetuned",type=Path,required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    base=json.loads(a.base.read_text(encoding="utf-8")); tuned=json.loads(a.finetuned.read_text(encoding="utf-8"))
    if base.get("records") != tuned.get("records"):
        raise ValueError("Reports contain different record counts; comparisons require the identical holdout dataset")
    if not base.get("dataset_sha256") or base.get("dataset_sha256") != tuned.get("dataset_sha256"):
        raise ValueError("Reports were not generated from the identical holdout dataset")
    base_metrics=base.get("metrics",{}); tuned_metrics=tuned.get("metrics",{}); scopes=sorted(set(base_metrics)|set(tuned_metrics)); comparison={}
    for scope in scopes:
        b=base_metrics.get(scope); t=tuned_metrics.get(scope)
        if b is None or t is None: raise ValueError(f"Metric scope {scope!r} is missing from one report")
        comparison[scope]={name:{"base":b.get(name),"finetuned":t.get(name),"delta":t.get(name)-b.get(name)} for name in METRICS}
    payload={"base_model":base.get("model"),"finetuned_model":tuned.get("model"),"adapter":tuned.get("adapter"),"dataset_sha256":base.get("dataset_sha256"),"records":base.get("records"),"comparison":comparison}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(payload,indent=2),encoding="utf-8"); print(json.dumps(comparison,indent=2))
if __name__=="__main__": main()
