#!/usr/bin/env python3
"""Fail when approved training and holdout JSONL contain likely leakage."""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

def load(paths):
    rows=[]
    for path in paths:
        for number,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
            if line.strip(): rows.append((path,number,json.loads(line)))
    return rows

def prompt(row): return row["messages"][1]["content"]
def digest(text): return hashlib.sha256(text.encode("utf-8")).hexdigest()
def evidence_text(text):
    match=re.search(r"## Evidence Bundle\s*```json\s*(.*?)\s*```",text,re.IGNORECASE|re.DOTALL)
    return match.group(1) if match else text

def main():
    p=argparse.ArgumentParser(); p.add_argument("--train",type=Path,nargs="+",required=True); p.add_argument("--holdout",type=Path,nargs="*",default=[]); p.add_argument("--protocols",type=Path,default=Path(__file__).with_name("protocols.json")); p.add_argument("--sampling-report",type=Path); a=p.parse_args()
    train,holdout=load(a.train),load(a.holdout); errors=[]
    config=json.loads(a.protocols.read_text(encoding="utf-8")); aliases={name:[name,*spec.get("aliases",[])] for group in config.values() for name,spec in group.items()}
    train_hashes={digest(prompt(r)) for _,_,r in train}; holdout_hashes={digest(prompt(r)) for _,_,r in holdout}
    overlap=train_hashes & holdout_hashes
    if overlap: errors.append(f"{len(overlap)} identical prompts occur in both train and holdout")
    if a.sampling_report:
        sampling=json.loads(a.sampling_report.read_text(encoding="utf-8")).get("protocols",{})
        train_names=set(config.get("train",{})); holdout_names=set(config.get("holdout",{}))
        train_sources={x["source"] for name in train_names for x in sampling.get(name,{}).get("files",[])}
        holdout_sources={x["source"] for name in holdout_names for x in sampling.get(name,{}).get("files",[])}
        shared_sources=train_sources & holdout_sources
        if shared_sources: errors.append(f"{len(shared_sources)} source PCAP files contributed to both train and holdout protocols")
    for label,rows in (("train",train),("holdout",holdout)):
        seen=set()
        for path,line,row in rows:
            text=prompt(row); h=digest(text)
            if h in seen: errors.append(f"duplicate {label} prompt: {path}:{line}")
            seen.add(h)
            meta=row.get("metadata",{}); protocol=str(meta.get("protocol","")).lower()
            for alias in aliases.get(protocol,[protocol] if protocol else []):
                if re.search(rf"(?<![a-z0-9]){re.escape(alias.lower())}(?![a-z0-9])",text.lower()): errors.append(f"protocol alias {alias!r} leaked into prompt: {path}:{line}"); break
            lowered=evidence_text(text).lower()
            for marker in ('"semantic_role"','"semantic_labels"','"human_label"','"wireshark_name"','trusted wireshark dissector'):
                if marker in lowered: errors.append(f"target marker {marker!r} leaked into prompt: {path}:{line}")
    if errors: raise SystemExit("Leakage audit failed:\n- " + "\n- ".join(errors[:100]))
    print(json.dumps({"train_records":len(train),"holdout_records":len(holdout),"cross_set_prompt_overlap":0,"status":"passed"},indent=2))
if __name__=="__main__": main()
