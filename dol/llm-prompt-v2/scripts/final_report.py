"""Final table: learned-v2, + TLV per-message parsing, + prompt-v2 variant A (gated / ungated).

Real protocols: TLV families (dol/per-message-segmentation) take per-message TLV edges
(convention TL|V, the leave-one-out choice for both BER protocols); every other family
takes learned-v2 or the LLM edges. Synthetic test protocols (fixed generator) have no
TLV families. Writes final-results.json / final-results.txt.
"""
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re')
EXP = ROOT / 'dol/llm-prompt-v2'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pv = _load('prompt_v2', EXP / 'scripts/prompt_v2.py')
pm = _load('per_message', ROOT / 'dol/per-message-segmentation/scripts/per_message.py')
llm, bench, B, ANN, PROTOS = pv.llm, pv.bench, pv.B, pv.ANN, pv.PROTOS
FAMOUS = ('modbus', 'dnp3', 's7comm')
VARIANT = 'A'


def family_sets(entries, variant):
    sets = {'v2': {}, 'gated': {}, 'ungated': {}}
    regions, status = {}, Counter()
    for e in entries:
        v2e = set(e['v2_edges'])
        inside = llm.interior(e['regions'])
        regions[e['family']] = inside
        got = pv.model_edges(e, variant) if variant in e['prompts'] else None
        status['answered' if got is not None else ('no-region' if variant not in e['prompts'] else 'missing')] += 1
        sets['v2'][e['family']] = v2e
        if got is None:
            sets['gated'][e['family']] = sets['ungated'][e['family']] = v2e
        else:
            sets['gated'][e['family']] = {x for x in v2e if x not in inside} | {x for x in got if x in inside}
            sets['ungated'][e['family']] = {x for x in got if 0 < x < e['shown']} | {x for x in v2e if x >= e['shown']}
    return sets, regions, status


def real(p, entries, tlv_fams):
    d = B / p / 'data'
    assign, msgs, ann, fams, fixed = pm.real_inputs(p)
    sets, regions, _ = family_sets(entries, VARIANT)
    status = family_sets([e for e in entries if e['family'] not in tlv_fams], VARIANT)[2]   # TLV families are not sent
    sets['rules'] = {f: set(e) - {0} for f, e in bench._family_edges(json.load(open(d / llm.RULES_FILE))).items()}
    tlv = {}
    for fam in tlv_fams:
        mids = fams[fam]
        s = pm.tlv_start([msgs[m] for m in mids])
        if s is None:
            continue
        for mid in mids:
            e = pm.tlv_edges(msgs[mid], s, 'TL|V')
            if e is not None:
                tlv[mid] = {x for x in fixed.get(fam, set()) if x < s} | e
    columns = {'rules': ('rules', False), 'v2': ('v2', False), 'v2+tlv': ('v2', True),
               'v2+tlv+llm-gated': ('gated', True), 'v2+tlv+llm-ungated': ('ungated', True)}
    out = {}
    for col, (source, use_tlv) in columns.items():
        items = []
        for a in ann:
            mid = int(a['msg_id']); fam = assign.get(mid, '')
            e = tlv[mid] if use_tlv and mid in tlv else sets[source].get(fam, set())
            items.append((set(a['boundaries']), e, regions.get(fam, set()), len(msgs[mid])))
        out[col] = llm.score_messages(items)
    return out, status


def synthetic(p, entries, variant):
    sets, regions, status = family_sets(entries, variant)
    items = defaultdict(list)
    for e in entries:
        for line in bench._iter_jsonl(EXP / 'truth' / f"test-synth__{p}__{e['family']}.jsonl"):
            for v, s in sets.items():
                items[v].append((set(line['boundaries']), s[e['family']], regions[e['family']], line['len']))
    return {v: llm.score_messages(items[v]) for v in sets}, status


def tokens(entries, variant):
    t = Counter()
    for e in entries:
        if variant in e['prompts']:
            path = EXP / 'responses' / f"{e['prompts'][variant]['file'][:-4]}.json"
            if path.exists():
                u = llm.parse_response(path)[1]
                t.update(tin=int(u.get('prompt_tokens') or 0), tout=int(u.get('completion_tokens') or 0), requests=1)
    return dict(t)


def ci(diffs, seed=0):
    rng = np.random.default_rng(seed)
    bs = [rng.choice(diffs, len(diffs)).mean() for _ in range(10000)]
    return float(np.mean(diffs)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    manifest = json.load(open(EXP / 'manifest.json'))
    tlv = defaultdict(set)
    for p, f in json.load(open(EXP / 'tlv-families.json')):
        tlv[p].add(f)
    by = defaultdict(list)
    for e in manifest:
        by[(e['set'], e['protocol'])].append(e)
    res = {'real': {}, 'synthetic': {}, 'synthetic-v1': {}, 'tokens': {}}
    for p in PROTOS:
        entries = [e for e in by[('real', p)] if e['family'] not in tlv[p]]
        res['real'][p], status = real(p, by[('real', p)], tlv[p])
        res['real'][p]['status'] = dict(status)
        res['tokens'][p] = tokens(entries, VARIANT)
    synth_names = sorted({p for s, p in by if s == 'test-synth'})
    for p in synth_names:
        res['synthetic'][p], status = synthetic(p, by[('test-synth', p)], VARIANT)
        res['synthetic'][p]['status'] = dict(status)
        res['synthetic-v1'][p], _ = synthetic(p, by[('test-synth', p)], 'V1U')
        res['tokens'][p] = tokens(by[('test-synth', p)], VARIANT)
    json.dump(res, open(EXP / 'final-results.json', 'w'), indent=1)

    L = []
    cols = ['rules', 'v2', 'v2+tlv', 'v2+tlv+llm-gated', 'v2+tlv+llm-ungated']
    L.append('== real protocols: per-message boundary F1 (LLM = prompt v2, variant A, gpt-5.5 low) ==')
    L.append(f"{'protocol':10s} " + ' '.join(f'{c:>8s}' for c in ('rules', 'v2', '+tlv', '+gated', '+ungated'))
             + '   region P/R  v2 | gated | ungated   answered   tok in/out (k)')
    for p in PROTOS:
        r = res['real'][p]; st = r['status']; t = res['tokens'][p]
        L.append(f"{p:10s} " + ' '.join(f"{r[c]['f1']:8.3f}" for c in cols) + '   '
                 + ' | '.join(f"{r[c]['region']['precision']:.2f}/{r[c]['region']['recall']:.2f}" for c in ('v2', 'v2+tlv+llm-gated', 'v2+tlv+llm-ungated'))
                 + f"   {st.get('answered', 0)}/{st.get('answered', 0) + st.get('missing', 0)}"
                 + f"   {t.get('tin', 0) / 1000:.1f}/{t.get('tout', 0) / 1000:.1f}")
    for name, names in (('macro, all 14', PROTOS), ('macro, w/o modbus/dnp3/s7comm', [p for p in PROTOS if p not in FAMOUS])):
        L.append(f"{name:10s} " + ' '.join(f"{np.mean([res['real'][p][c]['f1'] for p in names]):8.3f}" for c in cols))
    L.append('')
    for base, col in (('v2+tlv', 'v2+tlv+llm-gated'), ('v2+tlv', 'v2+tlv+llm-ungated'), ('v2', 'v2+tlv')):
        for name, names in (('all 14', PROTOS), ('w/o famous', [p for p in PROTOS if p not in FAMOUS])):
            d = np.array([res['real'][p][col]['f1'] - res['real'][p][base]['f1'] for p in names])
            m, lo, hi = ci(d)
            L.append(f"  {col:20s} - {base:8s} {name:11s} mean {m:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  up/down {(d > .005).sum()}/{(d < -.005).sum()}")
    L.append('')
    L.append('== synthetic test protocols (fixed generator, seed 20261015): per-message boundary F1 ==')
    L.append(f"{'protocol':10s} {'v2':>8s} {'A gated':>8s} {'A ungat':>8s} {'v1 ungat':>8s}   answered   tok in/out (k)")
    for p in synth_names:
        r = res['synthetic'][p]; st = r['status']; t = res['tokens'][p]
        L.append(f"{p:10s} {r['v2']['f1']:8.3f} {r['gated']['f1']:8.3f} {r['ungated']['f1']:8.3f} {res['synthetic-v1'][p]['ungated']['f1']:8.3f}"
                 f"   {st.get('answered', 0)}/{st.get('answered', 0) + st.get('missing', 0)}   {t.get('tin', 0) / 1000:.1f}/{t.get('tout', 0) / 1000:.1f}")
    L.append(f"{'macro':10s} " + ' '.join(f"{np.mean([res[k][p][v]['f1'] for p in synth_names]):8.3f}"
                                          for k, v in (('synthetic', 'v2'), ('synthetic', 'gated'), ('synthetic', 'ungated'), ('synthetic-v1', 'ungated'))))
    for v in ('gated', 'ungated'):
        d = np.array([res['synthetic'][p][v]['f1'] - res['synthetic'][p]['v2']['f1'] for p in synth_names])
        m, lo, hi = ci(d)
        L.append(f"  A {v:8s} - v2  mean {m:+.3f}  95% CI [{lo:+.3f}, {hi:+.3f}]  up/down {(d > .005).sum()}/{(d < -.005).sum()}")
    tin = sum(t.get('tin', 0) for t in res['tokens'].values()); tout = sum(t.get('tout', 0) for t in res['tokens'].values())
    L.append(f"\ntokens of this stage (variant A, answered requests): in {tin}, out {tout}")
    text = '\n'.join(L)
    print(text)
    (EXP / 'final-results.txt').write_text(text + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
