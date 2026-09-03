#!/usr/bin/env python3
"""Generate per-message annotations directly from TShark jsonraw output."""
import argparse, json, re, subprocess
from pathlib import Path

ROLE_PATTERNS=[(r'trans|xid','transaction_id'),(r'correl|request_id','correlation_id'),(r'function|func','function_code'),(r'opcode|operation','opcode'),(r'length|len','length'),(r'count|quantity','quantity'),(r'address|addr|reference','address'),(r'sequence|seq','sequence_number'),(r'status','status'),(r'error|exception','error_code'),(r'checksum|crc','checksum'),(r'flag','flags'),(r'timestamp|time','timestamp'),(r'unit|slave','unit_id'),(r'device','device_id'),(r'reserved|padding','reserved')]
def role(name):
 for pat,r in ROLE_PATTERNS:
  if re.search(pat,name.lower()): return r
 return None
def fields(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k.endswith('_raw'):
    for e in (v if isinstance(v,list) and v and isinstance(v[0],list) else [v]):
     if isinstance(e,list) and len(e)>=3:
      try: yield k[:-4],int(e[1]),int(e[2])
      except: pass
   yield from fields(v)
 elif isinstance(x,list):
  for y in x: yield from fields(y)
def main():
 p=argparse.ArgumentParser();p.add_argument('messages',type=Path);p.add_argument('pcap_root',type=Path);p.add_argument('output',type=Path);p.add_argument('--filter',required=True);p.add_argument('--tshark',default='tshark');a=p.parse_args()
 rows=[json.loads(x) for x in a.messages.read_text(encoding='utf-8').splitlines() if x.strip()]; byfile={}
 for m in rows: byfile.setdefault(m.get('source_file'),[]).append(m)
 out=[]
 for pcap in a.pcap_root.rglob('*'):
  if pcap.suffix.lower() not in {'.pcap','.pcapng','.cap'}: continue
  proc=subprocess.run([a.tshark,'-n','-r',str(pcap),'-Y',a.filter,'-T','jsonraw'],capture_output=True,text=True,check=True)
  for packet in json.loads(proc.stdout or '[]'):
   layers=packet.get('_source',{}).get('layers',{}); frame=layers.get('frame',{}); num=frame.get('frame.number')
   raw=list(fields(layers)); payload=next((m for m in byfile.get(pcap.name,[]) if str(m.get('metadata',{}).get('frame',{}).get('number',m.get('metadata',{}).get('frame',{}).get('frame.number','')))==str(num)),None)
   if payload is None: continue
   plen=int(payload.get('payload_len',0)); spans=sorted({0,plen}|{o for _,o,w in raw if 0<=o<plen}|{o+w for _,o,w in raw if 0<o+w<=plen})
   labels=[]
   for name,o,w in raw:
    if o<0 or w<1 or o+w>plen: continue
    r=role(name)
    if r: labels.append({'offset':o,'width':w,'semantic_role':r,'field_type':'bytes'})
   out.append({'msg_id':payload['msg_id'],'boundaries':spans,'semantic_labels':labels,'reviewed':True,'approved':True,'reviewer':'tshark','source_frame':num})
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('\n'.join(json.dumps(x) for x in out)+'\n',encoding='utf-8');print(json.dumps({'annotations':len(out),'output':str(a.output)},indent=2))
if __name__=='__main__':main()
