"""Score every tool and protocol_re configuration on the shared sample with the per-message boundary metric
(scripts/diagnostics/31_benchmark_message_boundaries.py: micro P/R/F1 over interior edges, exact match) against
both references, plus message-type clustering (homogeneity / completeness / V-measure / ARI against the
truth-file message types) for the tools that cluster. Run with ~/.venvs/protocol_re."""
import json, os, sys
from sklearn import metrics
from common import ROOT, BENCH, HERE, PROTOCOLS, iter_jsonl
sys.path.insert(0, os.path.join(ROOT, 'src'))
from protocol_re.inference.tlv import message_layout_edges

RUNS = os.environ.get('THESIS_RUNS', 'final-v4')   # run root under dol/ (dol/hdbscan-global/run_final.sh layout)
OURS = {  # configuration -> truth-eval run root
    'ours-det': f'dol/{RUNS}/full',
    'ours-zs': f'dol/{RUNS}/zs',
    'ours-fs50': f'dol/{RUNS}/fs50',
    # same configurations run on the <= 500-message samples only
    'ours-det-s': f'dol/{RUNS}/sample',
    'ours-zs-s': f'dol/{RUNS}/sample-runs/zs',
    'ours-fs50-s': f'dol/{RUNS}/sample-runs/fs50',
}
# earlier runs (per-protocol tuned clustering): dol/iec104-discriminator, dol/baseline-comparison/sample-runs,
# dol/accuracy-push/truth-eval/{zs-gate,integrated4}
OVERRIDE = {}
REFS = {'truth': 'dol/accuracy-push/annotations-truthconv', 'parser': 'finetuning/cluster-free-dataset/annotations'}

def our_preds(run, protocol):
    data = os.path.join(ROOT, run, protocol, 'data')
    families = json.load(open(os.path.join(data, '05_families.json')))
    assignments = {a['msg_id']: str(a['family_id']) for a in json.load(open(os.path.join(data, '02_family_assignments.json')))['assignments']}
    edges = {}
    for fid, details in families.items():
        values = set()
        for field in details.get('field_hypotheses', []) or []:
            start = int(field.get('start', 0) or 0)
            values.update((start, start + int(field.get('length', 0) or 0)))
        edges[str(fid)] = sorted(values)
    ids = set(json.load(open(os.path.join(HERE, 'samples', protocol + '.json'))))
    out = {}
    for r in iter_jsonl(os.path.join(data, '01_messages.jsonl')):
        if r['msg_id'] not in ids:
            continue
        fid = assignments.get(r['msg_id'])
        e = edges.get(fid or '', [])
        layout = families.get(fid, {}).get('message_layout') if fid else None
        if layout:
            e = message_layout_edges(bytes.fromhex(r['payload_hex']), e, layout)
        out[r['msg_id']] = {'boundaries': list(e), 'cluster': fid or 'unassigned'}
    return out

def msg_preds(run, protocol):
    """Per-message edges of stage 04b (before they are reduced to one field list per family)."""
    path = os.path.join(ROOT, run, protocol, 'data', '04b_fewshot_edges.json')
    if not os.path.exists(path):
        return None
    edges = json.load(open(path))['edges']
    return {int(m): {'boundaries': e, 'cluster': None} for m, e in edges.items()}

def tool_preds(tool, protocol):
    path = os.path.join(HERE, 'preds', tool, protocol + '.jsonl')
    if not os.path.exists(path):
        return None
    return {r['msg_id']: r for r in iter_jsonl(path)}

def score(preds, refs, lengths, skip):
    tp = fp = fn = exact = n = marked = positions = 0
    perfect = fields = pfields = 0   # BinPRE "perfection": reference fields whose two edges are predicted with no edge inside
    for mid, truth in refs.items():
        if mid in skip or mid not in lengths:
            continue
        L = lengths[mid]
        t = {e for e in truth if 0 < e < L}
        p = {e for e in (preds.get(mid, {}).get('boundaries') or []) if 0 < e < L}
        tp += len(p & t); fp += len(p - t); fn += len(t - p); exact += p == t; n += 1
        marked += len(p); positions += max(0, L - 1)
        te = sorted(t | {0, L}); pe = p | {0, L}
        for a, b in zip(te, te[1:]):
            fields += 1
            perfect += a in pe and b in pe and not any(a < x < b for x in p)
        pfields += len(pe) - 1   # predicted fields; exact matches among them = perfect fields
    pr = tp / (tp + fp) if tp + fp else 0.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
    return {'messages': n, 'precision': round(pr, 4), 'recall': round(rc, 4), 'f1': round(f1, 4), 'exact': round(exact / n, 4) if n else 0,
            'density': round(marked / positions, 4) if positions else 0,
            'perfection': round(perfect / fields, 4) if fields else 0,
            'field_precision': round(perfect / pfields, 4) if pfields else 0,
            'field_f1': round(2 * perfect / (fields + pfields), 4) if fields + pfields else 0}  # exact-field F1  # share of interior positions predicted as edges

report = {}
for protocol in PROTOCOLS:
    ids = set(json.load(open(os.path.join(HERE, 'samples', protocol + '.json'))))
    lengths = {r['msg_id']: r['payload_len'] for r in iter_jsonl(os.path.join(BENCH, protocol, 'data', '01_messages.jsonl')) if r['msg_id'] in ids}
    refs = {name: {a['msg_id']: [int(e) for e in a['boundaries']] for a in iter_jsonl(os.path.join(ROOT, path, protocol + '.jsonl')) if a['msg_id'] in ids}
            for name, path in REFS.items()}
    types = {a['msg_id']: a.get('type') for a in iter_jsonl(os.path.join(ROOT, REFS['truth'], protocol + '.jsonl')) if a['msg_id'] in ids}
    labelled = {a['msg_id'] for a in iter_jsonl(os.path.join(ROOT, 'dol/accuracy-push/integrated-labels', protocol + '.jsonl'))}
    sweep = sorted(d for d in os.listdir(os.path.join(HERE, 'preds')) if d.startswith('netzob-eq'))
    systems = {tool: tool_preds(tool, protocol) for tool in ['nemesys', 'netzob', 'netplier', 'sup-copy-offsets', 'sup-copy-align'] + sweep}
    for name, run in OURS.items():
        run = OVERRIDE.get((name, protocol), run)
        if os.path.exists(os.path.join(ROOT, run, protocol, 'data', '05_families.json')):
            systems[name] = our_preds(run, protocol)
    for name, cfg in (('ours-zs-msg', 'zs'), ('ours-fs50-msg', 'fs50')):
        systems[name] = msg_preds(f'dol/{RUNS}/{cfg}', protocol)
    # reference baseline: a boundary after every byte (recall 1; precision = share of byte positions that are edges)
    systems['every-byte'] = {mid: {'boundaries': list(range(1, L))} for mid, L in lengths.items()}
    report[protocol] = {}
    for name, preds in systems.items():
        if preds is None:
            continue
        skip = labelled if name.startswith('ours-fs50') or name.startswith('sup-') else set()
        row = {ref: score(preds, refs[ref], lengths, skip) for ref in REFS}
        clustered = [m for m in sorted(types) if m not in skip and preds.get(m, {}).get('cluster') not in (None, 'fail')]
        if clustered and name != 'nemesys' and any(preds[m].get('cluster') is not None for m in clustered):
            truth_labels = [types[m] for m in clustered]
            pred_labels = [str(preds[m]['cluster']) for m in clustered]
            row['clustering'] = {
                'messages': len(clustered), 'true_types': len(set(truth_labels)), 'clusters': len(set(pred_labels)),
                'homogeneity': round(metrics.homogeneity_score(truth_labels, pred_labels), 4),
                'completeness': round(metrics.completeness_score(truth_labels, pred_labels), 4),
                'v_measure': round(metrics.v_measure_score(truth_labels, pred_labels), 4),
                'ari': round(metrics.adjusted_rand_score(truth_labels, pred_labels), 4)}
        report[protocol][name] = row
json.dump(report, open(os.path.join(HERE, 'scores.json'), 'w'), indent=2)

names = ['every-byte', 'sup-copy-offsets', 'sup-copy-align', 'nemesys', 'netzob', 'netplier', 'ours-det', 'ours-zs', 'ours-fs50', 'ours-zs-msg', 'ours-fs50-msg', 'ours-det-s', 'ours-zs-s', 'ours-fs50-s']
for ref in REFS:
    print(f'\n== per-message boundary F1 vs {ref} reference')
    print(f"{'protocol':10s}" + ''.join(f'{n:>11s}' for n in names))
    for protocol in PROTOCOLS:
        print(f'{protocol:10s}' + ''.join(f"{report[protocol][n][ref]['f1']:>11.3f}" if n in report[protocol] else f"{'-':>11s}" for n in names))
    print(f"{'macro':10s}" + ''.join(f"{sum(report[p][n][ref]['f1'] for p in PROTOCOLS if n in report[p]) / max(1, sum(n in report[p] for p in PROTOCOLS)):>11.3f}" for n in names))
print('\n== message-type clustering V-measure / ARI (truth-file types)')
for protocol in PROTOCOLS:
    print(f'{protocol:10s}' + ''.join(
        f"{report[protocol][n]['clustering']['v_measure']:>6.2f}/{report[protocol][n]['clustering']['ari']:<5.2f}" if 'clustering' in report[protocol].get(n, {}) else f"{'-':>12s}"
        for n in names[4:]))
