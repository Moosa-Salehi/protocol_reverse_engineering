"""Macro F1 of the loose periodic post-process across detector thresholds (no files written)."""
import itertools, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import periodic as P
from bench_periodic import PROTOS, B, ANN, bench, family_messages, add_edges, is_marker_file

msgs = {p: family_messages(B / p / 'data') for p in PROTOS}
bases = {b: {p: json.load(open(B / p / 'data' / f'05_families.exp-{b}.json')) for p in PROTOS} for b in ('learned-v2', 'base')}
payload_len, assign, ann = {}, {}, {}
for p in PROTOS:
    d = B / p / 'data'
    assign[p] = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    payload_len[p] = {int(m['msg_id']): int(m['payload_len']) for m in bench._iter_jsonl(d / '01_messages.jsonl')}
    ann[p] = [r for r in bench._iter_jsonl(ANN / f'{p}.jsonl') if r.get('reviewer') not in bench.COARSE_REVIEWERS and r.get('boundaries')]

def f1(p, fams):
    edges = bench._family_edges(fams); tp = fp = fn = 0
    for r in ann[p]:
        L = payload_len[p].get(int(r['msg_id']))
        if L is None: continue
        t = {int(e) for e in r['boundaries'] if 0 < int(e) < L}
        pr = {e for e in edges.get(assign[p].get(int(r['msg_id']), ''), []) if 0 < e < L}
        tp += len(pr & t); fp += len(pr - t); fn += len(t - pr)
    return 2 * tp / max(2 * tp + fp + fn, 1)

grid = dict(R2_MIN=(0.05, 0.1, 0.2), STATS_SPLIT=(0.6, 0.8, 0.9), STATS_REPEATS=(4, 8, 16), R2_RATIO=(0.5, 0.7, 0.9))
default = dict(R2_MIN=0.1, STATS_SPLIT=0.8, STATS_REPEATS=8, R2_RATIO=0.7)
rows = []
for name, vals in grid.items():          # one parameter at a time around the default
    for v in vals:
        cfg = dict(default, **{name: v})
        for k, x in cfg.items(): setattr(P, k, x)
        det = {p: {f: P.detect_family(m, 'loose') for f, m in msgs[p].items()} for p in PROTOS}
        res = {}
        for b, fb in bases.items():
            per = []
            for p in PROTOS:
                mk = is_marker_file(fb[p])
                new = {f: add_edges(d, {e for r in det[p].get(f, []) for e in r['edges']}, mk)[0] for f, d in fb[p].items()}
                per.append(f1(p, new))
            res[b] = sum(per) / len(per)
        n = sum(len(v) for d in det.values() for v in d.values())
        rows.append(dict(cfg, regions=n, **res))
        print(f"{name}={v:<5} regions={n:3d}  macro F1 learned-v2 {res['learned-v2']:.3f}  base {res['base']:.3f}", flush=True)
json.dump(rows, open(Path(__file__).parent.parent / 'sensitivity.json', 'w'), indent=1)
