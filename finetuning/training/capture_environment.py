#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, platform, subprocess, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    import torch
    packages={}
    for name in ("unsloth","torch","transformers","datasets","accelerate","peft","bitsandbytes","trl","safetensors"):
        try: packages[name]=getattr(__import__(name),"__version__","unknown")
        except Exception as exc: packages[name]=f"unavailable: {exc}"
    data={"python":sys.version,"platform":platform.platform(),"packages":packages,"cuda":{"available":torch.cuda.is_available(),"version":torch.version.cuda,"device":torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,"bf16_supported":bool(torch.cuda.is_available() and torch.cuda.is_bf16_supported())}}
    try: data["git_commit"]=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    except Exception: pass
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(data,indent=2),encoding="utf-8"); print(json.dumps(data,indent=2))
if __name__=="__main__": main()
