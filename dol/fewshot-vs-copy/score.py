"""Few-shot 50 vs copy baselines through the pipeline: macro scores and paired bootstrap (fs50 - copy) over the
14 protocols. Writes score.json. usage: score.py"""
import json, random
ROOT = '/mnt/d/tez/practical/protocol_re'
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
RUNS = {'fs50': 'dol/final-v4/fs50', 'copy-offsets': 'dol/fewshot-vs-copy/runs/copy-offsets', 'copy-align': 'dol/fewshot-vs-copy/runs/copy-align',
        'zs': 'dol/final-v4/zs'}
def get(d, p):
    r = json.load(open(f'{ROOT}/{d}/{p}/data/15_evaluation_result.json')); m = r['metrics']
    return dict(overall=r['summary']['overall_score'], bnd=m['field_boundary']['f1_score'], sem=m['field_semantics']['f1_score'],
                mt=m['message_type_matching']['f1_score'], rel=m['relations']['f1_score'])
V = {c: {p: get(d, p) for p in P} for c, d in RUNS.items()}
def boot(d):
    rng = random.Random(0); b = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(10000))
    return sum(d) / len(d), b[250], b[9750]
out = {'macro': {c: {k: sum(V[c][p][k] for p in P) / 14 for k in V[c][P[0]]} for c in V}, 'per_protocol': V, 'delta': {}}
for c in ('copy-offsets', 'copy-align'):
    for k in ('overall', 'bnd', 'sem'):
        d = [V['fs50'][p][k] - V[c][p][k] for p in P]
        m, lo, hi = boot(d)
        out['delta'][f'fs50-{c}:{k}'] = dict(d=m, lo=lo, hi=hi, up=sum(x > 0.005 for x in d), down=sum(x < -0.005 for x in d))
json.dump(out, open(f'{ROOT}/dol/fewshot-vs-copy/score.json', 'w'), indent=1)
for c, v in out['macro'].items(): print(c, {k: round(x, 3) for k, x in v.items()})
for k, v in out['delta'].items(): print(k, {a: round(b, 3) for a, b in v.items()})
