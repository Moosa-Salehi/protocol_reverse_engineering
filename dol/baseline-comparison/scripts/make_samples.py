"""Draw the evaluation sample: up to N messages per protocol (seed 0) that both references (truth-file convention
and parser annotations) cover, taken as whole sessions in random order (NetPlier needs request/response pairs);
a session larger than what is left is cut to a contiguous run of its messages. The few-shot configuration's 50 labelled messages are not excluded here (POWERLINK
has 53 annotated messages); the scorer drops them when scoring that configuration."""
import json, os, random, sys
from common import ROOT, BENCH, HERE, PROTOCOLS, iter_jsonl
N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
for p in PROTOCOLS:
    truth = {a['msg_id'] for a in iter_jsonl(os.path.join(ROOT, 'dol/accuracy-push/annotations-truthconv', p + '.jsonl')) if a.get('boundaries')}
    parser = {a['msg_id'] for a in iter_jsonl(os.path.join(ROOT, 'finetuning/cluster-free-dataset/annotations', p + '.jsonl'))
              if a.get('boundaries') and a.get('reviewer') != 'tshark-cache'}
    labelled = {a['msg_id'] for a in iter_jsonl(os.path.join(ROOT, 'dol/accuracy-push/integrated-labels', p + '.jsonl'))}
    payloads = {r['msg_id']: r['payload_hex'] for r in iter_jsonl(os.path.join(BENCH, p, 'data', '01_messages.jsonl'))}
    pool = sorted(truth & parser & set(payloads))
    pool_set = set(pool)
    sessions = {}
    for r in iter_jsonl(os.path.join(BENCH, p, 'data', '01_messages.jsonl')):
        if r['msg_id'] in pool_set:
            sessions.setdefault(r['session_id'], []).append(r['msg_id'])
    order = sorted(sessions)
    random.Random(0).shuffle(order)
    pick = []
    for key in order:
        ids = sessions[key]
        room = N - len(pick)
        if room <= 0:
            break
        if len(ids) > room:
            start = random.Random(key).randrange(len(ids) - room + 1)
            ids = ids[start:start + room]
        pick.extend(ids)
    pick = sorted(pick)
    json.dump(pick, open(os.path.join(HERE, 'samples', p + '.json'), 'w'))
    print(f'{p:10s} truth={len(truth):6d} parser={len(parser):6d} both={len(pool):6d} labelled-in-sample={len(labelled & set(pick)):3d} sample={len(pick)}')
