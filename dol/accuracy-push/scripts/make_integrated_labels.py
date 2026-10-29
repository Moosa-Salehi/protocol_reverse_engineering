"""Labels files for the integrated-pipeline validation: scripts/select_fewshot_messages.py's selection (k=50,
candidates = messages with a truth-convention annotation), boundaries from annotations-truthconv.
Usage: make_integrated_labels.py [protocols]  -> dol/accuracy-push/integrated-labels/<p>.jsonl"""
import json, pickle, subprocess, sys
from pathlib import Path
ROOT = Path('/mnt/d/tez/practical/protocol_re'); D = ROOT / 'dol/accuracy-push'; B = ROOT / 'dol/benchmark-14-protocols'
import os
K = int(os.environ.get('K', '50'))
OUTD = D / ('integrated-labels' if K == 50 else f'integrated-labels-k{K}')
OUTD.mkdir(exist_ok=True)
PROTOS = sys.argv[1].split(',') if len(sys.argv) > 1 else 'modbus,bacnet,cip,dnp3,enip,ethercat,goose,hart_ip,iec104,mms,opcua,powerlink,s7comm,zigbee'.split(',')
for p in PROTOS:
    ann = {json.loads(l)['msg_id']: json.loads(l)['boundaries'] for l in open(D / 'annotations-truthconv' / f'{p}.jsonl')}
    ids = OUTD / f'{p}.ids.json'; ids.write_text(json.dumps(sorted(ann)))
    sel = OUTD / f'{p}.selected.jsonl'
    subprocess.run([sys.executable, str(ROOT / 'scripts/select_fewshot_messages.py'), str(B / p / 'data/01_messages.jsonl'),
                    str(B / p / 'data/02_family_assignments.json'), str(sel), '--k', str(K), '--only-ids', str(ids)], check=True, capture_output=True)
    rows = [json.loads(l) for l in open(sel)]
    with open(OUTD / f'{p}.jsonl', 'w') as fh:
        for r in rows:
            fh.write(json.dumps({'msg_id': r['msg_id'], 'payload_hex': r['payload_hex'], 'boundaries': ann[r['msg_id']]}) + '\n')
    print(f'{p:10s} labelled {len(rows)} (k={K})')
