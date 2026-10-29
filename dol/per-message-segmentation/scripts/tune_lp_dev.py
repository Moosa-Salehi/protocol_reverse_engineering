"""Tune the length-prefix (LP) thresholds on the synthetic development set only.

The a-priori LP thresholds fired on no family (real or synthetic test). This sweep
uses the dev synthetic protocols of the prompt-v2 experiment (seed 777), which are
never scored; the best setting is written to lp_dev_choice.json and per_message.py
then runs with it on the real and synthetic test protocols unchanged.
"""
import importlib.util
import itertools
import json
import os
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re')
OUT = ROOT / 'dol/per-message-segmentation'
os.environ.setdefault('SYNTH_GENERATOR', str(ROOT / 'dol/synthetic-generator-fix/synthetic_protocols_fixed.py'))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


pm = _load('per_message', OUT / 'scripts/per_message.py')
pv = _load('prompt_v2', ROOT / 'dol/llm-prompt-v2/scripts/prompt_v2.py')
llm, v2 = pm.llm, pm.v2

GRID = {'LP_FIT': (0.95, 0.98), 'LP_MIN_DISTINCT': (2, 3), 'LP_GAIN_BITS': (0.0, 0.25, 0.5), 'LP_REALIGN_BITS': (0.25, 0.5, 1.0)}


def main():
    data = {p: v2.load_protocol(p) for p in pm.PROTOS}
    model = llm.train_v2(data, list(pm.PROTOS))
    dev = pv.synthetic_set(pv.DEV_SEED)
    prepared = []
    for sp, fams in dev.items():
        seg = pm.Segmenter(model, llm.corpus_stats([m for msgs, _, _ in fams.values() for m in msgs]))
        for f, (msgs, edges, body_start) in fams.items():
            X, offs = v2.family_rows(msgs, seg.corpus, body_start)
            fixed = {o for o, q in zip(offs, llm.apply_v2(model, X)) if q >= model[2]} if offs else set()
            prepared.append((sp, msgs, edges, fixed, seg))
    rows = []
    for values in itertools.product(*GRID.values()):
        config = dict(zip(GRID, values))
        for k, v in config.items():
            setattr(pm, k, v)
        items, fired = defaultdict(list), 0
        for sp, msgs, edges, fixed, seg in prepared:
            per, found = seg.lp(msgs, fixed)
            fired += per is not None
            for k, (m, cuts) in enumerate(zip(msgs, edges)):
                e = per[k] if per is not None and per[k] is not None else fixed
                items[sp].append((set(cuts), e, set(), len(m)))
        f1 = float(np.mean([llm.score_messages(v)['f1'] for v in items.values()]))
        rows.append((f1, fired, config))
        print(round(f1, 4), 'fired', fired, config, flush=True)
    base_items = defaultdict(list)
    for sp, msgs, edges, fixed, seg in prepared:
        for m, cuts in zip(msgs, edges):
            base_items[sp].append((set(cuts), fixed, set(), len(m)))
    base = float(np.mean([llm.score_messages(v)['f1'] for v in base_items.values()]))
    best = max(rows, key=lambda r: (r[0], -r[1]))
    print('dev v2 macro', round(base, 4), 'best LP', round(best[0], 4), best[2])
    json.dump({'dev_v2_macro': base, 'best_macro': best[0], 'families_fired': best[1], 'config': best[2],
               'all': [{'f1': r[0], 'fired': r[1], **r[2]} for r in rows]}, open(OUT / 'lp_dev_choice-fixedsynth.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
