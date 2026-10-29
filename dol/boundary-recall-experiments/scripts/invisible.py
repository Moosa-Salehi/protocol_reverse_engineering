import json, importlib.util
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
ROOT=Path('/mnt/d/tez/practical/protocol_re'); B=ROOT/'dol/benchmark-14-protocols'; ANN=ROOT/'finetuning/cluster-free-dataset/annotations'
PROTOS='modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')
print(f"{'protocol':10s} {'true edges':>10s} {'both sides constant in family':>30s} {'...and constant across corpus':>30s}")
tot=[0,0,0]
for p in PROTOS:
    d=B/p/'data'; a={int(x['msg_id']):x['family_id'] for x in json.load(open(d/'02_family_assignments.json'))['assignments']}
    msgs={}
    for line in open(d/'01_messages.jsonl'):
        m=json.loads(line); msgs[int(m['msg_id'])]=bytes.fromhex(m['payload_hex'])
    fam_vals=defaultdict(lambda: defaultdict(set)); corp=defaultdict(set)
    for mid,b in msgs.items():
        f=a.get(mid)
        for j,v in enumerate(b[:300]): fam_vals[f][j].add(v); corp[j].add(v)
    n=inv=invc=0
    for line in open(ANN/f'{p}.jsonl'):
        r=json.loads(line); f=a.get(int(r['msg_id']))
        for e in r['boundaries'][1:-1]:
            if e>=300: continue
            n+=1
            if len(fam_vals[f][e-1])==1 and len(fam_vals[f][e])==1:
                inv+=1
                if len(corp[e-1])==1 and len(corp[e])==1: invc+=1
    tot[0]+=n; tot[1]+=inv; tot[2]+=invc
    print(f"{p:10s} {n:10d} {inv/n:29.0%} {invc/n:29.0%}")
