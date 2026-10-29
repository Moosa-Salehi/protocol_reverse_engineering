"""Print the detector's intermediate evidence for every family of a protocol.
Usage: diag.py <protocol> [max families]"""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import periodic as P
from bench_periodic import family_messages, B, ANN, bench
from collections import defaultdict, Counter
p = sys.argv[1]; k = int(sys.argv[2]) if len(sys.argv) > 2 else 6
d = B / p / 'data'
msgs = family_messages(d)
assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
votes = defaultdict(Counter); size = Counter()
for r in bench._iter_jsonl(ANN / f'{p}.jsonl'):
    if r.get('reviewer') in bench.COARSE_REVIEWERS: continue
    f = assign.get(int(r['msg_id'])); size[f] += 1; votes[f].update(r['boundaries'][1:-1])
rng = np.random.default_rng(0)
for fam, m in sorted(msgs.items(), key=lambda kv: -len(kv[1]))[:k]:
    m = m[:P.CAP]; M, lens, full = P.to_matrix(m); valid, st = P.column_stats(M, lens)
    g, nl = P.length_gcd(full)
    mm = max(3, int(0.05 * len(m)))
    truth = sorted(e for e, c in votes[fam].items() if c >= 0.5 * size[fam])
    print(f'== {fam} n={len(m)} lengths={sorted(Counter(full.tolist()).most_common(8))} gcd={g} nlen={nl}')
    print('   truth edges', truth[:60])
    print('   H', ' '.join(f'{x:.1f}' for x in st['H'][:min(80, lens.max())]))
    for s, e in P.varying_runs(st, mm):
        t = {pp: P.period_test(st, s, e, pp, rng) for pp in P.PERIODS}
        print(f'   run [{s},{e}) len {e-s}', {pp: (None if v is None else {a: round(b, 3) for a, b in v.items()}) for pp, v in t.items()})
