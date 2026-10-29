"""Ablation table for the thesis (sec:r-ablation) from dol/ablation-final/runs/<variant>/<protocol>.
Per variant: macro overall / boundary / semantics / message-type F1 against the truth files, per-message boundary F1
on the comparison sample (truth-file convention), and the change from the default with a paired bootstrap 95% CI over
the 14 protocols and the number of protocols up / down (|change| > 0.005); for the overall score also an exact paired
sign-flip permutation test (all 2^14 sign patterns, two-sided) with Holm's correction over the 12 components.
usage: gen_tex.py <out.tex>   (run with ~/.venvs/protocol_re)  -> also writes summary.txt"""
import json, os, random, sys
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, f'{ROOT}/dol/baseline-comparison/scripts')
sys.path.insert(0, f'{ROOT}/src')
from common import PROTOCOLS, BENCH, iter_jsonl
from protocol_re.inference.tlv import message_layout_edges

HERE = os.path.dirname(os.path.abspath(__file__))
VARIANTS = [  # (run folder, table label, component group)
    ('no-refine', 'family refinement with the global discriminator', 'families'),
    ('structural-features', 'neural encoder (structural features instead)', 'families'),
    ('no-tlv', 'TLV/BER handling (family merge, framing, layouts)', 'structure'),
    ('no-stacked-anchor', 'stacked-header anchor', 'structure'),
    ('no-hierarchical', 'hierarchical boundaries', 'structure'),
    ('no-periodic', 'periodic arrays', 'structure'),
    ('no-merging', 'anti-fragmentation merging', 'structure'),
    ('no-length-protect', 'length-field protection', 'structure'),
    ('no-opcode-isolation', 'opcode isolation', 'structure'),
    ('no-correlation-id', 'correlation-id detection', 'relations'),
    ('no-gate', 'zero-shot gate (model edges used directly)', 'learned'),
    ('no-posts', 'structural post-processors (strings, BER, CRC)', 'learned'),
]
KEYS = {'overall': None, 'bnd': 'field_boundary', 'sem': 'field_semantics', 'mt': 'message_type_matching', 'rel': 'relations'}
TRUTHCONV = f'{ROOT}/dol/accuracy-push/annotations-truthconv'


def scores(run, p):
    path = f'{run}/{p}/data/15_evaluation_result.json'
    if not os.path.exists(path):
        return None
    r = json.load(open(path))
    out = {'overall': r['summary']['overall_score']}
    for k, m in KEYS.items():
        if m:
            out[k] = r['metrics'][m]['f1_score']
    out['families'] = len(json.load(open(f'{run}/{p}/data/05_families.json')))
    return out


def per_message_f1(run, p):
    """Per-message boundary F1 of the family field lists (and TLV layouts) on the comparison sample, truth convention."""
    d = f'{run}/{p}/data'
    fams = json.load(open(f'{d}/05_families.json'))
    assign = {a['msg_id']: str(a['family_id']) for a in json.load(open(f'{d}/02_family_assignments.json'))['assignments']}
    edges = {}
    for fid, det in fams.items():
        v = set()
        for f in det.get('field_hypotheses', []) or []:
            st = int(f.get('start', 0) or 0); v.update((st, st + int(f.get('length', 0) or 0)))
        edges[fid] = sorted(v)
    ids = set(json.load(open(f'{ROOT}/dol/baseline-comparison/samples/{p}.json')))
    ref = {a['msg_id']: a['boundaries'] for a in iter_jsonl(f'{TRUTHCONV}/{p}.jsonl') if a['msg_id'] in ids}
    tp = fp = fn = 0
    for r in iter_jsonl(f'{BENCH}/{p}/data/01_messages.jsonl'):
        m = r['msg_id']
        if m not in ref:
            continue
        L = r['payload_len']; fid = assign.get(m); e = edges.get(fid, [])
        lay = fams.get(fid, {}).get('message_layout') if fid else None
        if lay:
            e = message_layout_edges(bytes.fromhex(r['payload_hex']), e, lay)
        t = {x for x in ref[m] if 0 < x < L}; q = {x for x in e if 0 < x < L}
        tp += len(t & q); fp += len(q - t); fn += len(t - q)
    P = tp / max(1, tp + fp); R = tp / max(1, tp + fn)
    return 2 * P * R / max(1e-9, P + R)


def ci(d, B=10000):
    rng = random.Random(0); bs = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(B))
    return sum(d) / len(d), bs[int(.025 * B)], bs[int(.975 * B)], sum(x > .005 for x in d), sum(x < -.005 for x in d)


def sign_flip_p(d):
    """Exact two-sided paired permutation p-value of the mean difference (all sign patterns)."""
    n, obs = len(d), abs(sum(d))
    hits = sum(1 for mask in range(1 << n) if abs(sum(x if mask >> i & 1 else -x for i, x in enumerate(d))) >= obs - 1e-12)
    return hits / (1 << n)


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); out, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i])); out[i] = run
    return out


res = {}
for v in ['default'] + [x[0] for x in VARIANTS]:
    run = f'{HERE}/runs/{v}'
    rows = {p: scores(run, p) for p in PROTOCOLS}
    if any(r is None for r in rows.values()):
        print('incomplete:', v, [p for p, r in rows.items() if r is None]); continue
    for p in PROTOCOLS:
        rows[p]['pm'] = per_message_f1(run, p)
    res[v] = rows
json.dump(res, open(f'{HERE}/scores.json', 'w'), indent=1)

def persian_number(t):
    t = t.replace('.', '٫')
    if '٫' not in t:
        return t
    return r'\fanum{' + t.translate(str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')) + '}'

L = ['% generated by dol/ablation-final/gen_tex.py -- do not edit by hand',
     r'\newcommand{\AB}[2]{\csname AB:#1:#2\endcsname}', r'\newcommand{\ABF}[2]{\csname ABF:#1:#2\endcsname}']
def put(v, k, t):
    L.append(rf'\expandafter\def\csname AB:{v}:{k}\endcsname{{{t}}}')
    L.append(rf'\expandafter\def\csname ABF:{v}:{k}\endcsname{{{persian_number(t.lstrip("+"))}}}')
summary = []
base = res['default']
for k in ('overall', 'bnd', 'sem', 'mt', 'pm'):
    put('default', k, f"{sum(base[p][k] for p in PROTOCOLS) / 14:.3f}")
done = [v for v, _, _ in VARIANTS if v in res]
raw_p = [sign_flip_p([res[v][p]['overall'] - base[p]['overall'] for p in PROTOCOLS]) for v in done]
holm_p = dict(zip(done, holm(raw_p))); raw_p = dict(zip(done, raw_p))
rows = []
for v, label, group in VARIANTS:
    if v not in res:
        continue
    r = res[v]
    put(v, 'p', f'{raw_p[v]:.3f}'); put(v, 'pholm', f'{holm_p[v]:.3f}')
    summary.append(f'{v:22s} overall sign-flip p={raw_p[v]:.4f} Holm p={holm_p[v]:.4f}')
    cells = [label]
    for k in ('overall', 'pm'):
        m, lo, hi, up, dn = ci([r[p][k] - base[p][k] for p in PROTOCOLS])
        put(v, k, f"{sum(r[p][k] for p in PROTOCOLS) / 14:.3f}")
        put(v, k + 'd', f'{m:+.3f}'); put(v, k + 'lo', f'{lo:+.3f}'); put(v, k + 'hi', f'{hi:+.3f}')
        put(v, k + 'up', str(up)); put(v, k + 'down', str(dn))
        sig = lo > 0 or hi < 0
        val = f'{m:+.3f}'
        cells += [rf'\textbf{{{val}}}' if sig else val, f'[{lo:+.3f}, {hi:+.3f}]', f'{up} / {dn}']
        if k == 'overall':
            cells.append(rf'\textbf{{{holm_p[v]:.3f}}}' if holm_p[v] < 0.05 else f'{holm_p[v]:.3f}')
        summary.append(f'{v:22s} {k:8s} {m:+.3f} [{lo:+.3f}, {hi:+.3f}] up/down {up}/{dn}')
    for k in ('bnd', 'sem', 'mt'):
        m = sum(r[p][k] - base[p][k] for p in PROTOCOLS) / 14
        put(v, k + 'd', f'{m:+.3f}')
        summary.append(f'{v:22s} {k:8s} {m:+.3f}')
    worst = min(PROTOCOLS, key=lambda p: r[p]['overall'] - base[p]['overall'])
    put(v, 'worst', worst); put(v, 'worstd', f"{r[worst]['overall'] - base[worst]['overall']:+.3f}")
    summary.append(f'{v:22s} largest overall drop: {worst} {r[worst]["overall"] - base[worst]["overall"]:+.3f}')
    rows.append(' & '.join(cells) + r' \\')
L.append(r'\newcommand{\AblationRows}{%'); L += rows; L.append('}')
open(sys.argv[1], 'w').write('\n'.join(L) + '\n')
open(f'{HERE}/summary.txt', 'w').write('\n'.join(summary) + '\n')
print('\n'.join(summary))
