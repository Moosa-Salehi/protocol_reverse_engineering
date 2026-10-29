"""Per-message TLV edges on top of different fixed-edge baselines and with two detectors.

detector 'pipeline': families with tlv_framing in 04_framing.json, chain from its header_length.
detector 'experiment': dol/per-message-segmentation tlv_start (start s, >= 90% exact parses).
Edges per message = fixed family edges before the chain start + TL|V edges of the full-depth parse.
"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np
ROOT = Path('/mnt/d/tez/practical/protocol_re')
def _load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); sys.modules[n] = m; s.loader.exec_module(m); return m
pm = _load('per_message', ROOT / 'dol/per-message-segmentation/scripts/per_message.py')
bench, B, ANN, PROTOS = pm.bench, pm.B, pm.ANN, pm.PROTOS
BASES = {'rules-default': '05_families.json', 'rules-perbyte0.5': '05_families.exp-perbyte0.5.json', 'learned-v2': '05_families.exp-learned-v2.json'}

def run():
    out = {}
    for p in PROTOS:
        d = B / p / 'data'
        assign, msgs, ann, fams, _ = pm.real_inputs(p)
        framing = json.load(open(d / '04_framing.json')).get('families', {})
        starts = {'pipeline': {f: int(v['tlv_framing']['header_length']) for f, v in framing.items() if (v or {}).get('tlv_framing')}}
        exp = {}
        for f, mids in fams.items():
            s = pm.tlv_start([msgs[m] for m in mids])
            if s is not None:
                exp[f] = s
        starts['experiment'] = exp
        out[p] = {}
        for bname, bfile in BASES.items():
            fixed = {f: set(e) - {0} for f, e in bench._family_edges(json.load(open(d / bfile))).items()}
            for det in ('none', 'pipeline', 'experiment'):
                items = []
                for a in ann:
                    mid = int(a['msg_id']); fam = assign.get(mid, '')
                    e = fixed.get(fam, set())
                    s = starts.get(det, {}).get(fam)
                    if s is not None:
                        t = pm.tlv_edges(msgs[mid], s, 'TL|V')
                        if t is not None:
                            e = {x for x in e if x < s} | t
                    items.append((set(a['boundaries']), e, set(), len(msgs[mid])))
                out[p][f'{bname}/{det}'] = pm.llm.score_messages(items)['f1']
        print(p, {k: round(v, 3) for k, v in out[p].items() if v != out[p][k.split('/')[0] + '/none'] or k.endswith('none')}, flush=True)
    keys = list(next(iter(out.values())))
    print('\nmacro F1 (14 protocols)')
    for k in keys:
        print(f'  {k:32s} {np.mean([out[p][k] for p in PROTOS]):.3f}')
    json.dump(out, open(ROOT / 'dol/tlv-integration-check/results.json', 'w'), indent=1)
run()
