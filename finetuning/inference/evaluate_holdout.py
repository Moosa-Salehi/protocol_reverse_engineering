#!/usr/bin/env python3
"""Evaluate a causal LM on approved holdout chat JSONL records."""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def parse_args():
    p=argparse.ArgumentParser(); p.add_argument("--data",type=Path,required=True); p.add_argument("--model",required=True); p.add_argument("--adapter",type=Path); p.add_argument("--output",type=Path,required=True); p.add_argument("--max-new-tokens",type=int,default=512); return p.parse_args()

def main():
    a=parse_args(); rows=[json.loads(x) for x in a.data.read_text(encoding="utf-8").splitlines() if x.strip()]
    tok=AutoTokenizer.from_pretrained(a.adapter or a.model)
    model=AutoModelForCausalLM.from_pretrained(a.model,torch_dtype="auto",device_map="auto")
    if a.adapter:
        from peft import PeftModel
        model=PeftModel.from_pretrained(model,a.adapter)
    model.eval(); totals=defaultdict(lambda:{"count":0,"valid_json":0,"exact":0,"field_tp":0,"field_fp":0,"field_fn":0})
    predictions=[]
    for row in rows:
        meta=row.get("metadata",{}); key=(meta.get("protocol","unknown"),meta.get("task","unknown")); stat=totals[key]; stat["count"]+=1
        prompt=tok.apply_chat_template(row["messages"][:-1],tokenize=False,add_generation_prompt=True)
        inputs=tok(prompt,return_tensors="pt").to(model.device)
        with torch.no_grad(): out=model.generate(**inputs,max_new_tokens=a.max_new_tokens,do_sample=False)
        text=tok.decode(out[0][inputs["input_ids"].shape[1]:],skip_special_tokens=True).strip()
        try: pred=json.loads(text); stat["valid_json"]+=1
        except Exception: pred=None
        target=json.loads(row["messages"][-1]["content"]); exact=pred==target
        if exact: stat["exact"]+=1
        if meta.get("task")=="semantic_labeling":
            def roles(value):
                return {(x.get("field_index"),x.get("semantic_role")) for x in value.get("semantic_labels",[])} if isinstance(value,dict) else set()
            pset,tset=roles(pred),roles(target); stat["field_tp"]+=len(pset&tset); stat["field_fp"]+=len(pset-tset); stat["field_fn"]+=len(tset-pset)
        elif meta.get("task")=="boundary_refinement":
            pset=set(pred.get("boundaries",[])) if isinstance(pred,dict) else set(); tset=set(target.get("boundaries",[])); stat["field_tp"]+=len(pset&tset); stat["field_fp"]+=len(pset-tset); stat["field_fn"]+=len(tset-pset)
        predictions.append({"metadata":meta,"prediction":pred,"raw":text,"target":target})
    report={}
    for key,s in totals.items():
        d=dict(s); d["json_rate"]=s["valid_json"]/s["count"]; d["exact_rate"]=s["exact"]/s["count"]; denom=2*s["field_tp"]+s["field_fp"]+s["field_fn"]; d["boundary_f1"]=2*s["field_tp"]/denom if denom else None; report["/".join(key)]=d
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps({"model":a.model,"adapter":str(a.adapter) if a.adapter else None,"records":len(rows),"metrics":report,"predictions":predictions},indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
