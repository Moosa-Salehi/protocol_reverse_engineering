"""Old (per-protocol tuned clustering) vs new (global setting + the robustness fixes) for every result-table
configuration: macro overall / boundary / semantics / message-type F1, paired bootstrap of the overall difference
over protocols, ups/downs; then the new table vs the new rule-based run."""
import json, random, os
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
N = 'hdbscan-global/final'
CONF = [  # name, old root, new root, old IEC 104 override
    ('rules', 'iec104-discriminator/truth-eval-14', f'{N}/full', None),
    ('zero-shot', 'accuracy-push/truth-eval/zs-gate', f'{N}/zs', 'iec104-discriminator/zs'),
    ('zs+shared', 'accuracy-push/truth-eval/zs-gate-shared', f'{N}/zs-shared', None),
    ('few-shot 10', 'accuracy-push/truth-eval/budget-k10', f'{N}/fs10', None),
    ('few-shot 20', 'accuracy-push/truth-eval/budget-k20', f'{N}/fs20', None),
    ('few-shot 50', 'accuracy-push/truth-eval/integrated4', f'{N}/fs50', 'iec104-discriminator/fs50'),
    ('rules, sample', 'baseline-comparison/sample-runs/det', f'{N}/sample', None),
    ('zs, sample', 'baseline-comparison/sample-runs/zs', f'{N}/sample-runs/zs', None),
    ('fs50, sample', 'baseline-comparison/sample-runs/fs50', f'{N}/sample-runs/fs50', None),
]
def load(root, p):
    path = f'{root}/{p}/data/15_evaluation_result.json'
    if not os.path.exists(path): return None
    r = json.load(open(path)); m = r['metrics']
    return dict(overall=r['summary']['overall_score'], bnd=m['field_boundary']['f1_score'], sem=m['field_semantics']['f1_score'], mt=m['message_type_matching']['f1_score'])
def ci(d, B=10000):
    rng = random.Random(0); b = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(B))
    return b[int(.025 * B)], b[int(.975 * B)]
out = {}
for name, old, new, override in CONF:
    o = {p: load(override if (override and p == 'iec104') else old, p) for p in P}
    n = {p: load(new, p) for p in P}
    if any(v is None for v in n.values()):
        print(f'{name:14s} incomplete'); continue
    d = [n[p]['overall'] - o[p]['overall'] for p in P]
    lo, hi = ci(d)
    mac = lambda s, k: sum(s[p][k] for p in P) / 14
    print(f"{name:14s} overall {mac(o,'overall'):.3f}->{mac(n,'overall'):.3f} ({sum(d)/14:+.3f} [{lo:+.3f},{hi:+.3f}] up/down {sum(x>0.005 for x in d)}/{sum(x<-0.005 for x in d)})"
          f"  bnd {mac(o,'bnd'):.3f}->{mac(n,'bnd'):.3f}  sem {mac(o,'sem'):.3f}->{mac(n,'sem'):.3f}  mt {mac(o,'mt'):.3f}->{mac(n,'mt'):.3f}")
    down = [(p, round(o[p]['overall'], 3), round(n[p]['overall'], 3)) for p in P if n[p]['overall'] < o[p]['overall'] - 0.005]
    if down: print('     down:', down)
    out[name] = {p: n[p] for p in P}
json.dump(out, open('hdbscan-global/final_summary.json', 'w'), indent=1)
