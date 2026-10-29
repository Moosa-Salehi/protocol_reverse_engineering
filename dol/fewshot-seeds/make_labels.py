"""Few-shot label sets for other selection seeds (same rule as dol/accuracy-push/scripts/make_integrated_labels.py,
k=50, truth-file convention; seed 20261017 is the thesis's main run). usage: make_labels.py <seed> -> labels-seed<seed>/<p>.jsonl"""
import json, subprocess, sys
from pathlib import Path
ROOT = Path('/mnt/d/tez/practical/protocol_re'); D = ROOT / 'dol/accuracy-push'; B = ROOT / 'dol/benchmark-14-protocols'
seed = sys.argv[1]; OUTD = Path(__file__).parent / f'labels-seed{seed}'; OUTD.mkdir(exist_ok=True)
for p in 'modbus,bacnet,cip,dnp3,enip,ethercat,goose,hart_ip,iec104,mms,opcua,powerlink,s7comm,zigbee'.split(','):
    ann = {json.loads(l)['msg_id']: json.loads(l)['boundaries'] for l in open(D / 'annotations-truthconv' / f'{p}.jsonl')}
    ids = OUTD / f'{p}.ids.json'; ids.write_text(json.dumps(sorted(ann)))
    sel = OUTD / f'{p}.selected.jsonl'
    subprocess.run([sys.executable, str(ROOT / 'scripts/select_fewshot_messages.py'), str(B / p / 'data/01_messages.jsonl'),
                    str(B / p / 'data/02_family_assignments.json'), str(sel), '--k', '50', '--seed', seed, '--only-ids', str(ids)],
                   check=True, capture_output=True)
    rows = [json.loads(l) for l in open(sel)]
    with open(OUTD / f'{p}.jsonl', 'w') as fh:
        for r in rows:
            fh.write(json.dumps({'msg_id': r['msg_id'], 'payload_hex': r['payload_hex'], 'boundaries': ann[r['msg_id']]}) + '\n')
    print(f'seed {seed} {p:10s} labelled {len(rows)}')
