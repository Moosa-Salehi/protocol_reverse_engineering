"""Stack the periodic-array post-process (loose mode) on top of each variant.

Reads dol/global-segmentation/families/<protocol>/05_families.exp-<variant>.json (and the
saved learned-v2 file), adds the detected array edges with the same code as
dol/periodic-array-experiments, writes ...exp-<variant>+periodic.json next to it and
scores with the official per-message scorer.

Usage: stack_periodic.py [tag]   -> dol/global-segmentation/results<tag>-periodic.{json,txt}  (tag e.g. -msgsel)
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re')
OUT = ROOT / 'dol/global-segmentation'
PER = ROOT / 'dol/periodic-array-experiments/scripts'
sys.path.insert(0, str(PER))
import periodic  # noqa: E402
from bench_periodic import add_edges, family_messages  # noqa: E402

spec = importlib.util.spec_from_file_location('bench', ROOT / 'scripts/diagnostics/31_benchmark_message_boundaries.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
B = ROOT / 'dol/benchmark-14-protocols'
ANN = ROOT / 'finetuning/cluster-free-dataset/annotations'
PROTOS = 'modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')
VARIANTS = ('v2', 'stage1', 'dp-edge', 'dp-full')
TAG = sys.argv[1] if len(sys.argv) > 1 else ''


def main():
    results = {}
    for p in PROTOS:
        by = family_messages(B / p / 'data')
        det = {fam: {e for r in periodic.detect_family(msgs, 'loose') for e in r['edges']} for fam, msgs in by.items()}
        results[p] = {}
        for v in VARIANTS:
            src = B / p / 'data' / '05_families.exp-learned-v2.json' if v == 'v2' else OUT / 'families' / p / f'05_families.exp-{v}{TAG}.json'
            fams = json.load(open(src))
            for fam in fams:
                if det.get(fam):
                    fams[fam], _ = add_edges(fams[fam], det[fam], markers=True)   # zero-length edge markers
            dst = OUT / 'families' / p / f'05_families.exp-{v}{TAG if v != "v2" else ""}+periodic.json'
            dst.parent.mkdir(parents=True, exist_ok=True)
            json.dump(fams, open(dst, 'w'))
            results[p][v] = bench.score_protocol(B / p / 'data', ANN / f'{p}.jsonl', str(dst))
        print(p, ' '.join(f"{v} {results[p][v]['f1']:.3f}" for v in VARIANTS), flush=True)
    json.dump(results, open(OUT / f'results{TAG}-periodic.json', 'w'), indent=1)
    lines = [f"{'+periodic':10s} " + ' '.join(f'{v:>20s}' for v in VARIANTS)]
    for p in PROTOS:
        lines.append(f'{p:10s} ' + ' '.join(f"{results[p][v]['precision']:.2f}/{results[p][v]['recall']:.2f}/{results[p][v]['f1']:.3f}".rjust(20) for v in VARIANTS))
    lines.append(f"{'macro F1':10s} " + ' '.join(f"{np.mean([results[p][v]['f1'] for p in PROTOS]):20.3f}" for v in VARIANTS))
    text = '\n'.join(lines)
    print(text)
    (OUT / f'results{TAG}-periodic.txt').write_text(text + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
