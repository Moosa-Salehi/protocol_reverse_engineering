"""Agreement of a truth file with the per-message tshark annotations.

For each message whose type the builder assigns, every fixed-length truth field edge
(converted to a wire offset) is looked up in that message's annotation boundaries.
Reports the share of truth edges that are dissector boundaries (should be close to 1;
gaps/bytes fields the builder inserted can legitimately miss)."""
import json, sys, importlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
cfgs = importlib.import_module('configs').CONFIGS
ROOT = Path('/mnt/d/tez/practical/protocol_re')
for proto in sys.argv[1:]:
    cfg = cfgs[proto]
    truth = json.load(open(ROOT / 'truth_files' / f'{proto}.json'))['ground_truth_protocol']
    types = {t['message_type_id']: t for t in truth['message_types']}
    ann = {}
    for l in open(ROOT / 'finetuning/cluster-free-dataset/annotations' / f'{proto}.jsonl'):
        a = json.loads(l)
        if a.get('reviewer') != 'tshark-cache':
            ann[a['msg_id']] = set(a['boundaries'])
    hit = tot = 0
    H = cfg['header_len']; lo_of = cfg.get('pdu_lo', lambda r: H)
    for l in open(ROOT / 'dol/truth-file-derivation' / proto / 'fields.jsonl'):
        r = json.loads(l)
        if r['msg_id'] not in ann:
            continue
        p = bytes.fromhex(r['payload_hex'])
        k = cfg['key'](r, p)
        if not k or k[0] not in types:
            continue
        lo = lo_of(r)
        edges = set()
        for mt in ([types[f'{proto}_header']] if f'{proto}_header' in types and lo == H else []) + [types[k[0]]]:
            base = 0 if mt['role'] == 'header' else lo
            for f in mt['fields']:
                if 'length' not in f or f['name'].startswith(('data', 'bytes')):
                    continue
                for e in (base + f['start'], base + f['start'] + f['length']):
                    if 0 < e < r['len']:
                        edges.add(e)
        tot += len(edges); hit += len(edges & ann[r['msg_id']])
    print(f'{proto:10s} truth edges that are dissector boundaries: {hit}/{tot} = {hit / max(tot, 1):.3f}')
