#!/usr/bin/env python3
"""Promote reviewed candidate JSONL records into an approved dataset."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> None:
    p=argparse.ArgumentParser(); p.add_argument("input",type=Path); p.add_argument("output",type=Path)
    a=p.parse_args(); approved=[]; rejected=0
    for line_no,line in enumerate(a.input.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        record=json.loads(line); meta=record.get("metadata",{})
        messages=record.get("messages")
        if not isinstance(messages,list) or len(messages)!=3 or [m.get("role") for m in messages] != ["system","user","assistant"]:
            raise ValueError(f"Invalid chat record at line {line_no}")
        try: json.loads(messages[-1]["content"])
        except Exception as exc: raise ValueError(f"Assistant target is not JSON at line {line_no}") from exc
        if meta.get("reviewed") is True and meta.get("approved") is True:
            if not str(meta.get("reviewer", "")).strip():
                raise ValueError(f"Approved record has no metadata.reviewer at line {line_no}")
            approved.append(record)
        else: rejected += 1
    if not approved: raise ValueError("No records have metadata.reviewed=true and metadata.approved=true")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in approved)+"\n",encoding="utf-8")
    print(json.dumps({"approved":len(approved),"rejected":rejected,"output":str(a.output)},indent=2))
if __name__=="__main__": main()
