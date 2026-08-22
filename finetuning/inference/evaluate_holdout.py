#!/usr/bin/env python3
"""Evaluate a causal LM on approved holdout chat JSONL records."""
from __future__ import annotations
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def parse_args():
    p=argparse.ArgumentParser(); p.add_argument("--data",type=Path,required=True); p.add_argument("--model",required=True); p.add_argument("--adapter",type=Path); p.add_argument("--output",type=Path,required=True); p.add_argument("--max-new-tokens",type=int,default=512); p.add_argument("--max-input-tokens",type=int,default=4096); p.add_argument("--seed",type=int,default=42); return p.parse_args()

def main():
    a=parse_args(); torch.manual_seed(a.seed); data_bytes=a.data.read_bytes(); rows=[json.loads(x) for x in data_bytes.decode("utf-8").splitlines() if x.strip()]
    if not rows: raise ValueError("Holdout dataset is empty")
    for index,row in enumerate(rows,1):
        roles=[m.get("role") for m in row.get("messages",[])]
        if roles != ["system","user","assistant"]: raise ValueError(f"Invalid chat roles at record {index}")
        if row.get("metadata",{}).get("task") not in {"boundary_refinement","semantic_labeling"}: raise ValueError(f"Invalid task at record {index}")
        json.loads(row["messages"][-1]["content"])
    tok=AutoTokenizer.from_pretrained(a.adapter or a.model)
    model=AutoModelForCausalLM.from_pretrained(a.model,torch_dtype="auto",device_map="auto")
    if a.adapter:
        from peft import PeftModel
        model=PeftModel.from_pretrained(model,a.adapter)
    model.eval(); totals=defaultdict(lambda:{"count":0,"valid_json":0,"exact":0,"tp":0,"fp":0,"fn":0,"parse_errors":0})
    predictions=[]
    for row in rows:
        meta=row.get("metadata",{}); protocol=meta.get("protocol","unknown"); task=meta.get("task","unknown"); family=str(meta.get("family_id","unknown"))
        prompt=tok.apply_chat_template(row["messages"][:-1],tokenize=False,add_generation_prompt=True)
        inputs=tok(prompt,return_tensors="pt",add_special_tokens=False).to(model.device)
        if inputs["input_ids"].shape[1] > a.max_input_tokens: raise ValueError(f"Prompt exceeds {a.max_input_tokens} tokens for {protocol}/{family}/{task}")
        with torch.no_grad(): out=model.generate(**inputs,max_new_tokens=a.max_new_tokens,do_sample=False,pad_token_id=tok.eos_token_id)
        text=tok.decode(out[0][inputs["input_ids"].shape[1]:],skip_special_tokens=True).strip()
        try: pred=json.loads(text); valid=True
        except Exception: pred=None; valid=False
        target=json.loads(row["messages"][-1]["content"]); exact=pred==target
        if task=="semantic_labeling":
            def roles(value):
                return {(x.get("field_index"),x.get("semantic_role")) for x in value.get("semantic_labels",[])} if isinstance(value,dict) else set()
            pset,tset=roles(pred),roles(target)
        elif task=="boundary_refinement":
            pset=set(pred.get("boundaries",[])) if isinstance(pred,dict) else set(); tset=set(target.get("boundaries",[]))
        else: pset,tset=set(),set()
        for key in (("overall",task),("protocol",protocol,task),("family",protocol,family,task)):
            stat=totals[key]; stat["count"]+=1; stat["valid_json"]+=int(valid); stat["parse_errors"]+=int(not valid); stat["exact"]+=int(exact); stat["tp"]+=len(pset&tset); stat["fp"]+=len(pset-tset); stat["fn"]+=len(tset-pset)
        predictions.append({"metadata":meta,"prediction":pred,"raw":text,"target":target})
    report={}
    for key,s in totals.items():
        pden=s["tp"]+s["fp"]; rden=s["tp"]+s["fn"]; fden=2*s["tp"]+s["fp"]+s["fn"]
        d={"count":s["count"],"valid_json":s["valid_json"],"parse_errors":s["parse_errors"],"json_validity":s["valid_json"]/s["count"],"exact_match":s["exact"]/s["count"],"true_positive":s["tp"],"false_positive":s["fp"],"false_negative":s["fn"],"precision":s["tp"]/pden if pden else 0.0,"recall":s["tp"]/rden if rden else 0.0,"f1":2*s["tp"]/fden if fden else 0.0}
        report["/".join(key)]=d
    generation={"seed":a.seed,"do_sample":False,"max_input_tokens":a.max_input_tokens,"max_new_tokens":a.max_new_tokens}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps({"model":a.model,"adapter":str(a.adapter) if a.adapter else None,"dataset_sha256":hashlib.sha256(data_bytes).hexdigest(),"generation":generation,"records":len(rows),"metrics":report,"predictions":predictions},indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))
if __name__=="__main__": main()
