"""Counter-likeness per offset: over consecutive messages of the same session and direction whose byte value
differs, the share of changes that are +1 (mod 256). usage: counter_test.py <protocol> [max_offset]"""
import json, sys, collections
p = sys.argv[1]; mo = int(sys.argv[2]) if len(sys.argv) > 2 else 16
recs = [json.loads(l) for l in open(f'/mnt/d/tez/practical/protocol_re/dol/benchmark-14-protocols/{p}/data/01_messages.jsonl')]
streams = collections.defaultdict(list)
for r in sorted(recs, key=lambda r: (r['session_id'], r['timestamp'], r['msg_id'])):
    streams[(r['session_id'], r['direction'])].append(bytes.fromhex(r['payload_hex']))
for o in range(mo):
    changes = inc = 0
    for s in streams.values():
        vals = [m[o] for m in s if len(m) > o]
        for a, b in zip(vals, vals[1:]):
            if a != b:
                changes += 1; inc += (b - a) % 256 == 1
    print(f'  off{o:2d} changes={changes:6d} +1 share={inc / changes if changes else 0:.2f}')
