"""Default configuration with vs without --discriminator-split.
Benchmark (14): truth-file metrics (overall, boundary, semantics, message types, relations; paired bootstrap CI over
protocols) and family clustering against the per-message truth types (V-measure, ARI).
Held-out (4): per-message boundary F1 against the parser annotations on the comparison sample, and clustering
(V-measure, ARI) against the spec-derived types. -> score.json, score.txt"""
import json, os, random, sys
ROOT = '/mnt/d/tez/practical/protocol_re'; HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f'{ROOT}/dol/hier-disc'); sys.path.insert(0, f'{ROOT}/src')
from hier import P, H, truth_types, scores
from protocol_re.inference.tlv import message_layout_edges
KEYS = {'overall': None, 'bnd': 'field_boundary', 'sem': 'field_semantics', 'mt': 'message_type_matching', 'rel': 'relations'}

def ev(d):
    r = json.load(open(f'{d}/15_evaluation_result.json'))
    return {k: (r['summary']['overall_score'] if m is None else r['metrics'][m]['f1_score']) for k, m in KEYS.items()}

def fams(d):
    return {a['msg_id']: a['family_id'] for a in json.load(open(f'{d}/02_family_assignments.json'))['assignments']}

def per_message(d, p):
    fm = json.load(open(f'{d}/05_families.json')); assign = fams(d)
    edges = {f: sorted({x for fl in det.get('field_hypotheses', []) or [] for x in (int(fl.get('start', 0) or 0), int(fl.get('start', 0) or 0) + int(fl.get('length', 0) or 0))}) for f, det in fm.items()}
    ids = set(json.load(open(f'{ROOT}/dol/heldout/{p}/sample.json')))
    ann = {a['msg_id']: a['boundaries'] for a in map(json.loads, open(f'{ROOT}/dol/heldout/{p}/annotations_typed.jsonl')) if a['msg_id'] in ids}
    tp = fp = fn = 0
    for l in open(f'{d}/01_messages.jsonl'):
        r = json.loads(l); m = r['msg_id']
        if m not in ann: continue
        L = r['payload_len']; f = assign.get(m); e = edges.get(f, [])
        lay = fm.get(f, {}).get('message_layout') if f else None
        if lay: e = message_layout_edges(bytes.fromhex(r['payload_hex']), e, lay)
        t = {x for x in ann[m] if 0 < x < L}; q = {x for x in e if 0 < x < L}
        tp += len(t & q); fp += len(q - t); fn += len(t - q)
    Pr = tp / max(1, tp + fp); R = tp / max(1, tp + fn); return 2 * Pr * R / max(1e-9, Pr + R)

def ci(d, B=10000):
    rng = random.Random(0); bs = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(B))
    return sum(d) / len(d), bs[int(.025 * B)], bs[int(.975 * B)], sum(x > .005 for x in d), sum(x < -.005 for x in d)

out = {'bench': {}, 'heldout': {}}; lines = []
for p in P:
    a, b = f'{ROOT}/dol/final-v4/zs/{p}/data', f'{HERE}/zs/{p}/data'
    t = truth_types(p)
    out['bench'][p] = {'before': {**ev(a), **scores(fams(a), t)}, 'after': {**ev(b), **scores(fams(b), t)}}
for k in list(KEYS) + ['v', 'ari', 'k']:
    d = [out['bench'][p]['after'][k] - out['bench'][p]['before'][k] for p in P]
    m, lo, hi, up, dn = ci(d)
    lines.append(f"bench {k:8s} {sum(out['bench'][p]['before'][k] for p in P)/14:.3f} -> {sum(out['bench'][p]['after'][k] for p in P)/14:.3f}"
                 f"  diff {m:+.3f} [{lo:+.3f}, {hi:+.3f}] up/down {up}/{dn}")
for p in P:
    b, a = out['bench'][p]['before'], out['bench'][p]['after']
    lines.append(f"  {p:10s} " + ' '.join(f"{k}={b[k]:.3f}->{a[k]:.3f}" for k in ('overall', 'bnd', 'mt', 'v', 'ari')) + f" fams {b['k']}->{a['k']}")
for p in H:
    a, b = f'{ROOT}/dol/heldout/{p}/runs/zs-full/data', f'{HERE}/heldout/{p}/data'
    t = truth_types(p)
    out['heldout'][p] = {'before': {'pm': per_message(a, p), **scores(fams(a), t)}, 'after': {'pm': per_message(b, p), **scores(fams(b), t)}}
    bb, aa = out['heldout'][p]['before'], out['heldout'][p]['after']
    lines.append(f"  heldout {p:10s} " + ' '.join(f"{k}={bb[k]:.3f}->{aa[k]:.3f}" for k in ('pm', 'v', 'ari')) + f" fams {bb['k']}->{aa['k']}")
for k in ('pm', 'v', 'ari'):
    lines.append(f"heldout mean {k}: {sum(out['heldout'][p]['before'][k] for p in H)/4:.3f} -> {sum(out['heldout'][p]['after'][k] for p in H)/4:.3f}")
json.dump(out, open(f'{HERE}/score.json', 'w'), indent=1); open(f'{HERE}/score.txt', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))
