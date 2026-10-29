"""Periodic-array post-process on the 14-protocol benchmark.

For every protocol and family, detect array regions (periodic.py) and add their
periodic edges to an existing family file. Writes
  dol/periodic-array-experiments/bench/<protocol>/data/05_families.exp-periodic-<mode>-<base>.json
(next to links to the run's 01_messages.jsonl / 02_family_assignments.json so the
benchmark scorer can read them) and scores every variant per message.

Usage: bench_periodic.py [modes] [bases]
       e.g. bench_periodic.py strict,length,loose learned-v2,base,perbyte0.5
"""
import importlib.util
import json
import os
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import periodic  # noqa: E402

ROOT = Path('/mnt/d/tez/practical/protocol_re')
B = ROOT / 'dol/benchmark-14-protocols'
ANN = ROOT / 'finetuning/cluster-free-dataset/annotations'
OUT = HERE.parent
spec = importlib.util.spec_from_file_location('bench', ROOT / 'scripts/diagnostics/31_benchmark_message_boundaries.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
PROTOS = 'modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')


def family_messages(data_dir):
    assign = {int(x['msg_id']): str(x['family_id'])
              for x in json.load(open(data_dir / '02_family_assignments.json'))['assignments']}
    by = defaultdict(list)
    for m in bench._iter_jsonl(data_dir / '01_messages.jsonl'):
        fam = assign.get(int(m['msg_id']))
        if fam and fam != 'noise':
            by[fam].append(bytes.fromhex(m['payload_hex']))
    return by


def add_edges(details, new_edges, markers):
    """Split the family's field hypotheses at new_edges.

    Rules-style files (fields with a length) are split in place, so the result is a
    valid stage-07 artifact; an edge outside every field is dropped. Learned-style
    files (zero-length edge markers, markers=True) get a marker per new edge.
    """
    hyps = details.get('field_hypotheses', []) or []
    if markers:
        have = {int(h.get('start', 0) or 0) for h in hyps}
        extra = [{'start': e, 'length': 0, 'attributes': {'periodic_edge': True}} for e in sorted(new_edges - have)]
        return dict(details, field_hypotheses=hyps + extra), len(extra)
    out, added = [], 0
    for h in hyps:
        a = int(h.get('start', 0) or 0)
        b = a + int(h.get('length', 0) or 0)
        cuts = sorted(e for e in new_edges if a < e < b)
        if not cuts:
            out.append(h)
            continue
        bounds = [a] + cuts + [b]
        for lo, hi in zip(bounds, bounds[1:]):
            piece = dict(h, start=lo, length=hi - lo)
            piece['attributes'] = dict(h.get('attributes') or {}, periodic_split=True, parent_span=[a, b])
            out.append(piece)
        added += len(cuts)
    return dict(details, field_hypotheses=out), added


def is_marker_file(fams):
    hyps = [h for d in fams.values() for h in d.get('field_hypotheses', []) or []]
    return bool(hyps) and all(int(h.get('length', 0) or 0) == 0 for h in hyps)


def link(src, dst):
    if dst.exists() or dst.is_symlink():
        return
    try:
        os.symlink(src, dst)
    except OSError:
        shutil.copy(src, dst)


def main():
    modes = (sys.argv[1] if len(sys.argv) > 1 else 'strict,length,loose').split(',')
    bases = (sys.argv[2] if len(sys.argv) > 2 else 'learned-v2,base,perbyte0.5').split(',')
    detections = {}
    table = defaultdict(dict)
    for p in PROTOS:
        src = B / p / 'data'
        dst = OUT / 'bench' / p / 'data'
        dst.mkdir(parents=True, exist_ok=True)
        for name in ('01_messages.jsonl', '02_family_assignments.json'):
            link(src / name, dst / name)
        t = time.time()
        msgs = family_messages(src)
        detections[p] = {mode: {fam: periodic.detect_family(m, mode) for fam, m in msgs.items()} for mode in modes}
        for base in bases:
            fams = json.load(open(src / f'05_families.exp-{base}.json'))
            markers = is_marker_file(fams)
            table[p][base] = bench.score_protocol(src, ANN / f'{p}.jsonl', f'05_families.exp-{base}.json')
            for mode in modes:
                new, n_added = {}, 0
                for fam, details in fams.items():
                    edges = {e for r in detections[p][mode].get(fam, []) for e in r['edges']}
                    new[fam], k = add_edges(details, edges, markers)
                    n_added += k
                name = f'05_families.exp-periodic-{mode}-{base}.json'
                json.dump(new, open(dst / name, 'w'))
                table[p][f'{mode}-{base}'] = dict(bench.score_protocol(dst, ANN / f'{p}.jsonl', name), edges_added=n_added)
        n_reg = {mode: sum(len(v) for v in detections[p][mode].values()) for mode in modes}
        print(f'{p:10s} regions {n_reg}  ({time.time() - t:.0f}s)', flush=True)

    cols = [c for base in bases for c in [base] + [f'{m}-{base}' for m in modes]]
    print(f"\n{'protocol':10s} " + ' '.join(f'{c:>22s}' for c in cols))
    print(f"{'':10s} " + ' '.join(f"{'P    R    F1':>22s}" for _ in cols))
    for p in PROTOS:
        print(f'{p:10s} ' + ' '.join(f"{table[p][c]['precision']:.2f} {table[p][c]['recall']:.2f} {table[p][c]['f1']:.3f}".rjust(22) for c in cols))
    mean = lambda c, k: sum(table[p][c][k] for p in PROTOS) / len(PROTOS)
    print(f"{'macro':10s} " + ' '.join(f"{mean(c, 'precision'):.2f} {mean(c, 'recall'):.2f} {mean(c, 'f1'):.3f}".rjust(22) for c in cols))
    json.dump(table, open(OUT / 'results-bench.json', 'w'), indent=1)
    json.dump(detections, open(OUT / 'detections-bench.json', 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
