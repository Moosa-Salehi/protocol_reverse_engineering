"""Robustness of the overall score (thesis sec:r-metrics): rescore the saved final-v4 runs with
  (a) the default evaluator (check: must reproduce 15_evaluation_result.json),
  (b) equal weights for the four metrics,
  (c) optimal one-to-one matching (Hungarian, scipy linear_sum_assignment over pairs above the same thresholds)
      instead of the greedy matcher, default weights,
  (d) both.
The evaluator module is imported unchanged; only its matcher is swapped for (c, d). -> scores.json, scores.txt"""
import importlib.util, json, os, random, sys
import numpy as np
from scipy.optimize import linear_sum_assignment
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, f'{ROOT}/src')
spec = importlib.util.spec_from_file_location('ev17', f'{ROOT}/scripts/17_evaluate_protocol_spec.py')
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
greedy = ev._greedy_matches

def hungarian(candidates, threshold):
    cands = [(a, b, s) for a, b, s in candidates if s >= threshold]
    if not cands:
        return []
    L = sorted({a for a, _, _ in cands}); R = sorted({b for _, b, _ in cands})
    li = {x: i for i, x in enumerate(L)}; ri = {x: i for i, x in enumerate(R)}
    M = np.zeros((len(L), len(R)))
    for a, b, s in cands:
        M[li[a], ri[b]] = max(M[li[a], ri[b]], s)
    rows, cols = linear_sum_assignment(M, maximize=True)
    return [(L[i], R[j], float(M[i, j])) for i, j in zip(rows, cols) if M[i, j] >= threshold]

PROTOCOLS = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua',
             'powerlink', 's7comm', 'zigbee']
CONFIGS = {'rules': 'full', 'zs': 'zs', 'fs10': 'fs10', 'fs20': 'fs20', 'fs50': 'fs50'}
KEYS = ('message_type_matching', 'field_boundary', 'field_semantics', 'relations')
W_DEFAULT = (0.30, 0.30, 0.25, 0.15); W_EQUAL = (0.25, 0.25, 0.25, 0.25)

def overall(metrics, weights):
    w = [(metrics[k], x) for k, x in zip(KEYS, weights) if metrics[k].get('applicable', True)]
    tot = sum(x for _, x in w)
    return sum(m['f1_score'] * x for m, x in w) / tot if tot else 0.0

def evaluate(d, truth_path, matcher):
    ev._greedy_matches = matcher
    model = json.load(open(f'{d}/14_evaluation_model_data.json')); truth = json.load(open(truth_path))
    tp = truth.get('ground_truth_protocol') or truth.get('predicted_protocol') or {}
    scope = ev.corpus_discriminator_scope(f'{d}/01_messages.jsonl', tp.get('message_types', []) or [])
    return ev.evaluate_protocol_spec_with_refinement(model, truth, scope)

res = {}
for c, sub in CONFIGS.items():
    res[c] = {}
    for p in PROTOCOLS:
        d = f'{ROOT}/dol/final-v4/{sub}/{p}/data'
        stored = json.load(open(f'{d}/15_evaluation_result.json'))['summary']['overall_score']
        g = evaluate(d, f'{ROOT}/truth_files/{p}.json', greedy)['metrics']
        h = evaluate(d, f'{ROOT}/truth_files/{p}.json', hungarian)['metrics']
        res[c][p] = {'stored': stored, 'default': overall(g, W_DEFAULT), 'equal': overall(g, W_EQUAL),
                     'hungarian': overall(h, W_DEFAULT), 'hungarian_equal': overall(h, W_EQUAL),
                     'hungarian_mt': h['message_type_matching']['f1_score'], 'greedy_mt': g['message_type_matching']['f1_score']}
        assert abs(res[c][p]['default'] - stored) < 1e-4, (c, p, stored, res[c][p]['default'])
json.dump(res, open(os.path.join(os.path.dirname(__file__), 'scores.json'), 'w'), indent=1)

def ci(a, b, var, B=10000):
    d = [res[a][p][var] - res[b][p][var] for p in PROTOCOLS]
    rng = random.Random(0); bs = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(B))
    return sum(d) / 14, bs[int(.025 * B)], bs[int(.975 * B)], sum(x > .005 for x in d), sum(x < -.005 for x in d)
out = []
for var in ('default', 'equal', 'hungarian', 'hungarian_equal'):
    out.append(f'== {var}: macro ' + ' '.join(f'{c}={sum(res[c][p][var] for p in PROTOCOLS)/14:.3f}' for c in CONFIGS))
    for c in ('zs', 'fs10', 'fs20', 'fs50'):
        m, lo, hi, up, dn = ci(c, 'rules', var)
        out.append(f'   {c} - rules {m:+.3f} [{lo:+.3f}, {hi:+.3f}] up/down {up}/{dn}')
    m, lo, hi, up, dn = ci('fs50', 'zs', var); out.append(f'   fs50 - zs {m:+.3f} [{lo:+.3f}, {hi:+.3f}] up/down {up}/{dn}')
    order = sorted(CONFIGS, key=lambda c: -sum(res[c][p][var] for p in PROTOCOLS))
    out.append('   ranking: ' + ' > '.join(order))
changed = sum(abs(res[c][p]['hungarian_mt'] - res[c][p]['greedy_mt']) > 1e-9 for c in CONFIGS for p in PROTOCOLS)
out.append(f'message-type F1 changed by optimal matching in {changed} of {len(CONFIGS)*14} runs')
open(os.path.join(os.path.dirname(__file__), 'scores.txt'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
