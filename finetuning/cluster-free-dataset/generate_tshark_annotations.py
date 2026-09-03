#!/usr/bin/env python3
"""Generate per-message annotations directly from TShark jsonraw output."""
import argparse, json, re, subprocess
from pathlib import Path

ROLE_PATTERNS=[(r'trans|xid','transaction_id'),(r'correl|request_id','correlation_id'),(r'function|func','function_code'),(r'opcode|operation','opcode'),(r'length|len','length'),(r'count|quantity','quantity'),(r'address|addr|reference','address'),(r'sequence|seq','sequence_number'),(r'status','status'),(r'error|exception','error_code'),(r'checksum|crc','checksum'),(r'flag','flags'),(r'timestamp|time','timestamp'),(r'unit|slave','unit_id'),(r'device','device_id'),(r'reserved|padding','reserved')]
def role(name):
 for pat,r in ROLE_PATTERNS:
  if re.search(pat,name.lower()): return r
 return None
def scalar(value):
 if isinstance(value,list): return scalar(value[0]) if value else ''
 if isinstance(value,dict):
  for k in ('show','value','raw'): 
   if k in value: return scalar(value[k])
 return value
def frame_number(layers):
 if isinstance(layers,dict):
  for k,v in layers.items():
   if k in ('frame.number','frame_frame_number','number') or k.endswith('frame_number'):
    value=scalar(v)
    if value not in (None,''): return value
   found=frame_number(v)
   if found not in (None,''): return found
 elif isinstance(layers,list):
  for v in layers:
   found=frame_number(v)
   if found not in (None,''): return found
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
def packet_frame_hex(layers):
 if isinstance(layers,dict):
  value=layers.get('frame_raw')
  if isinstance(value,list) and value:
   if isinstance(value[0],list): value=value[0]
   if value: return re.sub(r'[^0-9a-f]','',str(value[0]).lower())
  frame=layers.get('frame')
  if isinstance(frame,dict):
   value=frame.get('frame_raw')
   if isinstance(value,list) and value:
    if isinstance(value[0],list): value=value[0]
    if value: return re.sub(r'[^0-9a-f]','',str(value[0]).lower())
 return ''
def main():
 p=argparse.ArgumentParser();p.add_argument('messages',type=Path);p.add_argument('pcap_root',type=Path);p.add_argument('output',type=Path);p.add_argument('--filter',required=True);p.add_argument('--tshark',default='tshark');a=p.parse_args()
 rows=[json.loads(x) for x in a.messages.read_text(encoding='utf-8').splitlines() if x.strip()]; byfile={}
 for m in rows: byfile.setdefault(m.get('source_file'),[]).append(m)
 cached=[]
 for m in rows:
  meta=m.get('metadata',{}); spans=meta.get('field_spans',[]); frame=re.sub(r'[^0-9a-f]','',str(meta.get('frame_raw','')).lower()); payload_hex=re.sub(r'[^0-9a-f]','',str(m.get('payload_hex','')).lower())
  if not spans or not frame or not payload_hex: continue
  pos=frame.find(payload_hex)
  if pos < 0: continue
  start=pos//2; plen=int(m.get('payload_len',0)); boundaries={0,plen}; labels=[]
  for s in spans:
   off=int(s.get('offset',-1))-start; width=int(s.get('width',0))
   if off<0 or width<1 or off+width>plen: continue
   boundaries.update((off,off+width)); r=role(str(s.get('field','')))
   if r: labels.append({'offset':off,'width':width,'semantic_role':r,'field_type':'bytes'})
  if len(boundaries) > 2:
   cached.append({'msg_id':m['msg_id'],'boundaries':sorted(boundaries),'semantic_labels':labels,'reviewed':True,'approved':True,'reviewer':'tshark-cache','source_frame':meta.get('frame_number')})
 cached_by_id={x['msg_id']:x for x in cached}
 out=list(cached); used=set(cached_by_id); packets=0; unmatched=0; errors=[]
 for pcap in a.pcap_root.rglob('*'):
  if pcap.suffix.lower() not in {'.pcap','.pcapng','.cap'}: continue
  try:
   proc=subprocess.run([a.tshark,'-n','-r',str(pcap),'-Y',a.filter,'-T','jsonraw'],capture_output=True,text=True,check=True)
  except subprocess.CalledProcessError as exc:
   errors.append({'pcap':str(pcap),'returncode':exc.returncode}); continue
  for packet in json.loads(proc.stdout or '[]'):
   packets += 1
   layers=packet.get('_source',{}).get('layers',{}); frame=layers.get('frame',{}) if isinstance(layers,dict) else {}; num=scalar(frame.get('frame_frame_number', frame.get('frame.number', frame.get('number')))) or frame_number(layers)
   raw=list(fields(layers)); frame_hex=packet_frame_hex(layers); candidates=[m for m in byfile.get(pcap.name,[]) if m.get('msg_id') not in used]
   payload=next((m for m in candidates if str(m.get('metadata',{}).get('frame_number',m.get('metadata',{}).get('frame',{}).get('number',m.get('metadata',{}).get('frame',{}).get('frame.number',''))))==str(num) and re.sub(r'[^0-9a-f]','',str(m.get('payload_hex','')).lower()) in frame_hex),None)
   if payload is None and frame_hex:
    payload=next((m for m in candidates if re.sub(r'[^0-9a-f]','',str(m.get('payload_hex','')).lower()) in frame_hex),None)
   if payload is None: unmatched += 1; continue
   plen=int(payload.get('payload_len',0))
   payload_hex=re.sub(r'[^0-9a-f]','',str(payload.get('payload_hex','')).lower())
   payload_start=frame_hex.find(payload_hex) if payload_hex else -1
   payload_start //= 2
   if payload_start < 0:
    unmatched += 1
    continue
   relative=[(name, o-payload_start, w) for name,o,w in raw]
   spans=sorted({0,plen}|{o for _,o,w in relative if 0<=o<plen}|{o+w for _,o,w in relative if 0<o+w<=plen})
   labels=[]
   for name,o,w in relative:
    if o<0 or w<1 or o+w>plen: continue
    r=role(name)
    if r: labels.append({'offset':o,'width':w,'semantic_role':r,'field_type':'bytes'})
   if len(spans) <= 2:
    unmatched += 1
    continue
   out.append({'msg_id':payload['msg_id'],'boundaries':spans,'semantic_labels':labels,'reviewed':True,'approved':True,'reviewer':'tshark','source_frame':num}); used.add(payload['msg_id'])
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text('\n'.join(json.dumps(x) for x in out)+'\n',encoding='utf-8');print(json.dumps({'packets_scanned':packets,'packet_match_failures':unmatched,'messages':len(rows),'matched_messages':len(used),'unmatched_messages':len(rows)-len(used),'annotations':len(out),'errors':errors,'output':str(a.output)},indent=2))
if __name__=='__main__':main()
