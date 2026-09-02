#!/usr/bin/env python3
"""Inventory and proportionally sample protocol packets from a PCAP tree on Windows."""
from __future__ import annotations
import argparse, json, math, random, subprocess, sys, tempfile
from pathlib import Path

SUFFIXES={".pcap",".pcapng",".cap"}

def run(cmd:list[str])->str:
    p=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8",errors="replace")
    if p.returncode: raise RuntimeError(p.stderr.strip() or "command failed")
    return p.stdout

def count_frames(tshark:str,path:Path,flt:str)->list[int]:
    text=run([tshark,"-n","-r",str(path),"-Y",flt,"-T","fields","-e","frame.number"])
    return [int(x) for x in text.splitlines() if x.strip().isdigit()]

def allocate(counts:list[int],budget:int,min_per_file:int,max_per_file:int)->list[int]:
    active=[i for i,n in enumerate(counts) if n>0]; result=[0]*len(counts)
    if not active:return result
    if sum(counts)<=budget:return counts[:]
    weights=[math.sqrt(counts[i]) for i in active]; total=sum(weights)
    for i,w in zip(active,weights): result[i]=min(counts[i],max_per_file,max(min_per_file,int(budget*w/total)))
    while sum(result)>budget:
        i=max(active,key=lambda x:result[x]); result[i]-=1
    while sum(result)<budget:
        candidates=[i for i in active if result[i]<min(counts[i],max_per_file)]
        if not candidates:break
        i=max(candidates,key=lambda x:counts[x]/max(1,result[x])); result[i]+=1
    return result

def write_selected(tshark:str,mergecap:str,source:Path,flt:str,frames:list[int],output:Path)->None:
    chunks=[]
    with tempfile.TemporaryDirectory(prefix="protocol_re_sample_") as temp:
        tempdir=Path(temp)
        for index in range(0,len(frames),150):
            subset=frames[index:index+150]; frame_filter="frame.number in {"+",".join(map(str,subset))+"}"; chunk=tempdir/f"{index//150:05d}.pcapng"
            run([tshark,"-n","-r",str(source),"-Y",f"({flt}) && ({frame_filter})","-w",str(chunk)]);chunks.append(chunk)
        if len(chunks)==1: output.write_bytes(chunks[0].read_bytes())
        else: run([mergecap,"-w",str(output),*[str(x) for x in chunks]])

def main()->None:
    p=argparse.ArgumentParser();p.add_argument("--pcap-dir",type=Path,required=True);p.add_argument("--output-dir",type=Path,required=True);p.add_argument("--protocols",type=Path,default=Path(__file__).with_name("protocols.json"));p.add_argument("--budget-per-protocol",type=int,default=20000);p.add_argument("--min-per-file",type=int,default=50);p.add_argument("--max-per-file",type=int,default=3000);p.add_argument("--tshark",default="tshark");p.add_argument("--mergecap",default="mergecap");p.add_argument("--seed",type=int,default=42);p.add_argument("--include-holdout",action="store_true")
    a=p.parse_args();cfg=json.loads(a.protocols.read_text(encoding="utf-8"));selected={**(cfg["holdout"] if a.include_holdout else {}),**cfg["train"]};files=sorted(x for x in a.pcap_dir.rglob("*") if x.is_file() and x.suffix.lower() in SUFFIXES);a.output_dir.mkdir(parents=True,exist_ok=True);rng=random.Random(a.seed);report={"pcap_root":str(a.pcap_dir),"protocols":{}}
    print(f"Inventorying {len(files)} PCAP files against {len(selected)} protocol filters",flush=True)
    holdout_sources=set()
    for protocol,spec in selected.items():
        matches=[]
        is_holdout = protocol in cfg.get("holdout", {})
        for index,path in enumerate(files,1):
            if not is_holdout and a.include_holdout and str(path) in holdout_sources:
                continue
            try:
                frames=count_frames(a.tshark,path,spec["filter"])
            except Exception as exc:
                print(f"WARNING {protocol} {path}: {exc}",file=sys.stderr);continue
            if frames:matches.append((path,frames))
            if index%100==0:print(f"[{protocol}] scanned {index}/{len(files)}",flush=True)
        allocations=allocate([len(x[1]) for x in matches],a.budget_per_protocol,a.min_per_file,a.max_per_file);outdir=a.output_dir/protocol;outdir.mkdir(parents=True,exist_ok=True)
        for stale in outdir.glob("*.pcapng"):
            stale.unlink()
        items=[]
        for file_index,((path,frames),take) in enumerate(zip(matches,allocations)):
            chosen=sorted(rng.sample(frames,take)) if take<len(frames) else frames
            output=outdir/f"{file_index:05d}_{path.stem}.pcapng"
            write_selected(a.tshark,a.mergecap,path,spec["filter"],chosen,output)
            items.append({"source":str(path),"matching_packets":len(frames),"sampled_packets":take,"output":str(output)})
        report["protocols"][protocol]={"filter":spec["filter"],"matching_files":len(matches),"matching_packets":sum(len(x[1]) for x in matches),"sampled_packets":sum(allocations),"budget_per_protocol":a.budget_per_protocol,"min_per_file_requested":a.min_per_file,"max_per_file":a.max_per_file,"files":items}
        if is_holdout:
            holdout_sources.update(str(path) for path,_ in matches)
        print(f"[{protocol}] {len(matches)} files, {sum(len(x[1]) for x in matches)} matches, {sum(allocations)} sampled",flush=True)
    (a.output_dir/"sampling_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
if __name__=="__main__":main()
