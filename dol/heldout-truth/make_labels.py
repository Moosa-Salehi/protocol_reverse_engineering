"""Held-out protocols with truth files (truth_files/heldout/<p>.json, built by
dol/truth-file-derivation/scripts/build_truth.py after the method was frozen): truth-convention per-message
annotations (the dol/accuracy-push/scripts/regen_annotations.py rule) and the 50 few-shot labels chosen exactly as on
the benchmark (scripts/select_fewshot_messages.py on the label-free rules run's families, candidates = messages
with a truth-convention annotation).
Output: annotations/<p>.jsonl, labels/<p>.jsonl.  usage: make_labels.py [protocols]"""
import importlib.util, json, subprocess, sys
from collections import Counter
from pathlib import Path
ROOT = Path('/mnt/d/tez/practical/protocol_re'); HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('regen', ROOT / 'dol/accuracy-push/scripts/regen_annotations.py')
regen = importlib.util.module_from_spec(spec); spec.loader.exec_module(regen)
for p in (sys.argv[1:] or ['synphasor', 'ams', 'doip', 'cnip']):
    types = {t['message_type_id']: t for t in json.load(open(ROOT / f'truth_files/heldout/{p}.json'))['ground_truth_protocol']['message_types']}
    cfg = regen.configs.CONFIGS[p]; H = cfg['header_len']
    out, kinds = [], Counter()
    for line in open(ROOT / f'dol/truth-file-derivation/{p}/fields.jsonl'):
        r = json.loads(line); pl = bytes.fromhex(r['payload_hex']); n = int(r['len'])
        k = cfg['key'](r, pl)
        if not k or k[0] not in types:
            kinds['unassigned'] += 1; continue
        e = regen.type_edges(types[f'{p}_header'], 0, n) | regen.type_edges(types[k[0]], H, n) | {H}
        kinds[k[0]] += 1
        out.append({'msg_id': int(r['msg_id']), 'boundaries': sorted({0, n} | {x for x in e if 0 < x < n}), 'reviewer': 'truth-file', 'type': k[0]})
    (HERE / 'annotations').mkdir(exist_ok=True); (HERE / 'labels').mkdir(exist_ok=True)
    with open(HERE / f'annotations/{p}.jsonl', 'w') as fh:
        fh.writelines(json.dumps(x) + '\n' for x in out)
    ann = {x['msg_id']: x['boundaries'] for x in out}
    ids = HERE / f'labels/{p}.ids.json'; ids.write_text(json.dumps(sorted(ann)))
    run = ROOT / f'dol/heldout/{p}/runs/rules-full/data'
    sel = HERE / f'labels/{p}.selected.jsonl'
    subprocess.run([sys.executable, str(ROOT / 'scripts/select_fewshot_messages.py'), str(run / '01_messages.jsonl'),
                    str(run / '02_family_assignments.json'), str(sel), '--k', '50', '--only-ids', str(ids)], check=True, capture_output=True)
    rows = [json.loads(l) for l in open(sel)]
    with open(HERE / f'labels/{p}.jsonl', 'w') as fh:
        fh.writelines(json.dumps({'msg_id': x['msg_id'], 'payload_hex': x['payload_hex'], 'boundaries': ann[x['msg_id']]}) + '\n' for x in rows)
    print(f'{p:10s} annotated {len(out)}/{sum(kinds.values())} types {len(kinds) - ("unassigned" in kinds)} labels {len(rows)}')
