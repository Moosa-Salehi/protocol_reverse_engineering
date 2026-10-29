"""All truth-convention annotations of a protocol as a --fewshot-labels file (oracle boundaries ceiling)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
p, ann, msgs, out = sys.argv[1:5]
payload = {}
for line in open(msgs):
    m = json.loads(line); payload[int(m['msg_id'])] = m['payload_hex']
with open(out, 'w') as fh:
    for line in open(ann):
        a = json.loads(line); i = int(a['msg_id'])
        if a.get('boundaries') and i in payload and a.get('reviewer') != 'tshark-cache':
            fh.write(json.dumps({'msg_id': i, 'payload_hex': payload[i], 'boundaries': a['boundaries']}) + '\n')
