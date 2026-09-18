#!/usr/bin/env python3
"""Create dataset composition and tokenizer-aware length statistics."""
from __future__ import annotations
import argparse, json, math
from collections import Counter
from pathlib import Path

def stats(values):
    if not values: return {"count":0,"min":0,"max":0,"mean":0,"p95":0}
    ordered=sorted(values); return {"count":len(values),"min":ordered[0],"max":ordered[-1],"mean":sum(values)/len(values),"p95":ordered[min(len(ordered)-1,math.ceil(.95*len(ordered))-1)]}

def main():
    p=argparse.ArgumentParser(); p.add_argument("input",type=Path,nargs="+"); p.add_argument("--tokenizer",required=True); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    tok = None
    tokenizer_error = None
    try:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.tokenizer)
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        tokenizer_error = str(exc)
    protocols=Counter(); tasks=Counter(); families=Counter(); prompt_tokens=[]; target_tokens=[]; fields=[]; boundaries=[]; records=0
    for path in a.input:
        for line_no,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
            if not line.strip(): continue
            row=json.loads(line); records+=1; meta=row.get("metadata",{}); protocol=meta.get("protocol","unknown"); task=meta.get("task","unknown")
            protocols[protocol]+=1; tasks[task]+=1; families[f"{protocol}:{meta.get('family_id','unknown')}"]+=1
            messages=row["messages"]; target=messages[-1]["content"]
            if tok is not None:
                rendered=tok.apply_chat_template(messages[:-1],tokenize=False,add_generation_prompt=True)
                prompt_tokens.append(len(tok(rendered,add_special_tokens=False)["input_ids"]))
                target_tokens.append(len(tok(target,add_special_tokens=False)["input_ids"]))
            parsed=json.loads(target)
            fields.append(len(parsed.get("semantic_labels",[]))); boundaries.append(len(parsed.get("boundaries",[])))
    if not records: raise ValueError("Dataset is empty")
    report={"tokenizer":a.tokenizer,"tokenizer_available":tok is not None,"tokenizer_error":tokenizer_error,"tokenizer_revision":(getattr(tok,"_commit_hash",None) or tok.init_kwargs.get("_commit_hash")) if tok is not None else None,"records":records,"protocols":dict(sorted(protocols.items())),"tasks":dict(sorted(tasks.items())),"families":dict(sorted(families.items())),"prompt_tokens":stats(prompt_tokens),"target_tokens":stats(target_tokens),"semantic_fields_per_record":stats(fields),"boundaries_per_record":stats(boundaries)}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2),encoding="utf-8"); print(json.dumps(report,indent=2))
if __name__=="__main__": main()
