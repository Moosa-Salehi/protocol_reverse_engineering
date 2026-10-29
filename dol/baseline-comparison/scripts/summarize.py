"""Summaries of scores.json for the thesis: macro values, paired bootstrap CIs over protocols, wins, runtimes."""
import json, os, random
from common import HERE, PROTOCOLS
r = json.load(open(os.path.join(HERE, 'scores.json')))
names = ['nemesys', 'netzob', 'netplier', 'ours-det', 'ours-zs', 'ours-fs50', 'ours-det-s', 'ours-zs-s', 'ours-fs50-s']
def f1(p, n, ref): return r[p][n][ref]['f1'] if n in r[p] else 0.0
def ci(a, b, ref, B=10000):
    d = [f1(p, a, ref) - f1(p, b, ref) for p in PROTOCOLS]
    rng = random.Random(0); boots = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(B))
    return sum(d) / len(d), boots[int(0.025 * B)], boots[int(0.975 * B)], sum(x > 0 for x in d), sum(x < 0 for x in d)
for ref in ('truth', 'parser'):
    print(f'== {ref}: macro F1 / precision / recall')
    for n in names:
        print(f"  {n:10s} F1={sum(f1(p,n,ref) for p in PROTOCOLS)/14:.3f} P={sum(r[p][n][ref]['precision'] for p in PROTOCOLS if n in r[p])/14:.3f} "
              f"R={sum(r[p][n][ref]['recall'] for p in PROTOCOLS if n in r[p])/14:.3f}")
    common = [p for p in PROTOCOLS if all(n in r[p] for n in names)]
    print(f'  macro over the {len(common)} protocols every tool finished: ' + ' '.join(f'{n}={sum(f1(p,n,ref) for p in common)/len(common):.3f}' for n in names))
    oracle = [max(f1(p, b, ref) for b in ('nemesys', 'netzob', 'netplier')) for p in PROTOCOLS]
    print(f'  per-protocol best baseline (oracle) macro {sum(oracle)/14:.3f}')
    for ours in ('ours-det', 'ours-zs', 'ours-fs50', 'ours-det-s', 'ours-zs-s', 'ours-fs50-s'):
        for base in ('nemesys', 'netzob', 'netplier'):
            m, lo, hi, up, down = ci(ours, base, ref)
            print(f'  {ours} - {base}: {m:+.3f} [{lo:+.3f}, {hi:+.3f}] wins {up}/{down}')
        d = [f1(p, ours, ref) - o for p, o in zip(PROTOCOLS, oracle)]
        print(f'  {ours} vs oracle baseline: mean {sum(d)/14:+.3f}, wins {sum(x>0 for x in d)}/{sum(x<0 for x in d)}')
print('== clustering (protocols with >= 2 true types)')
multi = [p for p in PROTOCOLS if r[p]['ours-det'].get('clustering', {}).get('true_types', 0) >= 2]
print('  protocols:', len(multi), multi)
for n in names[1:]:
    rows = [r[p][n]['clustering'] for p in multi if 'clustering' in r[p].get(n, {})]
    if rows:
        print(f"  {n:10s} covered={len(rows):2d} V={sum(x['v_measure'] for x in rows)/len(rows):.3f} ARI={sum(x['ari'] for x in rows)/len(rows):.3f} "
              f"H={sum(x['homogeneity'] for x in rows)/len(rows):.3f} C={sum(x['completeness'] for x in rows)/len(rows):.3f} clusters={sum(x['clusters'] for x in rows)/len(rows):.1f}")
print('== runtime (s) per tool, sum over protocols')
for t in ('nemesys', 'netzob', 'netplier'):
    secs = {p: json.load(open(os.path.join(HERE, 'preds', t, p + '.meta.json')))['seconds'] for p in PROTOCOLS if os.path.exists(os.path.join(HERE, 'preds', t, p + '.meta.json'))}
    print(f'  {t:9s} total={sum(secs.values()):8.1f} max={max(secs.values()):7.1f} ({max(secs, key=secs.get)})')
