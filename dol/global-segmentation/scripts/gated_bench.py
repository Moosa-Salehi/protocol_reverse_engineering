"""Gated learned edges on the 14-protocol benchmark: split only stage-07 fields wider than 2 bytes.

1. Re-runs the *current* stage 07 (rules + periodic loose + TLV layouts, exactly the arguments
   main.py builds) on a copy of each benchmark run, so family assignments match the learned files.
2. Splits every stage-07 field longer than 2 bytes at the learned edges inside it (leave-one-protocol-out
   edges from global_seg.py, e.g. exp-stage1-msgsel); stage-07 edges are never removed.
3. Scores rules and gated variants with the official per-message scorer.

Usage: [MAX_WIDTH=8] gated_bench.py [edge variant ...]   default: stage1-msgsel stage1
       -> dol/global-segmentation/results-gated.{json,txt}
"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re')
OUT = ROOT / 'dol/global-segmentation'
B = ROOT / 'dol/benchmark-14-protocols'
ANN = ROOT / 'finetuning/cluster-free-dataset/annotations'
PY = str(Path.home() / '.venvs/protocol_re/bin/python')
PROTOS = 'modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')
VARIANTS = sys.argv[1:] or ['stage1-msgsel', 'stage1']
MIN_WIDTH = 3
import os
MAX_WIDTH = int(os.environ['MAX_WIDTH']) if os.environ.get('MAX_WIDTH') else None
TAG = f'-max{MAX_WIDTH}' if MAX_WIDTH else ''

sys.path.insert(0, str(ROOT))
import main as pipeline  # noqa: E402
spec = importlib.util.spec_from_file_location('bench', ROOT / 'scripts/diagnostics/31_benchmark_message_boundaries.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
spec = importlib.util.spec_from_file_location('apply_learned', OUT / 'scripts/apply_learned.py')
al = importlib.util.module_from_spec(spec)
spec.loader.exec_module(al)


def current_stage07(p):
    run = OUT / 'bench-current' / p
    d = run / 'data'
    if (d / '05_families.json').exists():
        return d
    d.mkdir(parents=True, exist_ok=True)
    for name in ('01_messages.jsonl', '02_family_assignments.json', '03_family_features.json', '04_framing.json'):
        shutil.copy(B / p / 'data' / name, d / name)
    args = pipeline.parse_args(['--use-existing-messages', '--data-dir', str(d), '--output-dir', str(run / 'output'),
                                '--log-dir', str(run / 'log'), '--llm-render-only'])
    step = next(a for name, a in pipeline.build_pipeline(args) if name == '07_infer_boundaries')
    log = open(run / 'stage07.log', 'w')
    subprocess.run([PY, *step], check=True, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
    return d


def main():
    results = {}
    for p in PROTOS:
        d = current_stage07(p)
        res = {'rules': bench.score_protocol(d, ANN / f'{p}.jsonl', '05_families.json')}
        rules = json.load(open(d / '05_families.json'))
        for v in VARIANTS:
            learned = bench._family_edges(json.load(open(OUT / 'families' / p / f'05_families.exp-{v}.json')))
            fams, added = {}, 0
            for fam, details in rules.items():
                fams[fam], k = al.split_wide(details, learned.get(fam, []), MIN_WIDTH, MAX_WIDTH)
                added += k
            path = OUT / 'families' / p / f'05_families.exp-gated{TAG}-{v}.json'
            json.dump(fams, open(path, 'w'))
            res[f'gated{TAG}-{v}'] = dict(bench.score_protocol(d, ANN / f'{p}.jsonl', str(path)), added_edges=added)
        results[p] = res
        print(p, ' '.join(f"{k} {r['f1']:.3f}" for k, r in res.items()), flush=True)
    json.dump(results, open(OUT / f'results-gated{TAG}.json', 'w'), indent=1)
    cols = list(next(iter(results.values())))
    lines = [f"{'protocol':10s} " + ' '.join(f'{c:>24s}' for c in cols)]
    for p in PROTOS:
        lines.append(f'{p:10s} ' + ' '.join(f"{results[p][c]['precision']:.2f}/{results[p][c]['recall']:.2f}/{results[p][c]['f1']:.3f}".rjust(24) for c in cols))
    lines.append(f"{'macro F1':10s} " + ' '.join(f"{np.mean([results[p][c]['f1'] for p in PROTOS]):24.3f}" for c in cols))
    lines.append(f"{'macro P/R':10s} " + ' '.join(f"{np.mean([results[p][c]['precision'] for p in PROTOS]):.2f}/{np.mean([results[p][c]['recall'] for p in PROTOS]):.2f}".rjust(24) for c in cols))
    text = '\n'.join(lines)
    print(text)
    (OUT / f'results-gated{TAG}.txt').write_text(text + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
