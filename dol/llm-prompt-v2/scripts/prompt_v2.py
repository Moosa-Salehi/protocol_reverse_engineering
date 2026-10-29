"""LLM boundary prompt, version 2: neutral framing, full field list, developed on
synthetic protocols only.

Changes against dol/llm-varying-boundaries (prompt v1):
  * the preamble no longer says the detector over-cuts payloads; it states both
    error kinds and that missed edges between two varying bytes are the most common;
  * the model returns the layout of the shown range as consecutive typed fields
    (start, width, type, byte order); edges are the field starts;
  * one reply serves both variants: gated (model edges only inside the varying
    regions, learned-v2 elsewhere) and ungated (model edges in the shown range);
  * variant A adds typed whole-field fits (length / counter evidence from
    dol/typed-field-hypotheses) to the evidence; variant B does not.

Prompt development (A vs B) uses a fresh synthetic set (seed DEV_SEED). The chosen
variant then runs once on the synthetic test set of the v1 experiment (seed
20261015) and on the 14 real protocols; nothing is tuned on either.

Phases:
  prepare            dev + test prompts, cost estimate (no network)
  call <set> <var>   set = dev | test-synth | real, var = A | B
  score <set> <var>
"""
import concurrent.futures
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re')
EXP = ROOT / 'dol/llm-prompt-v2'
# synthetic data from the fixed generator (the original wrote int64 buffers: 8 bytes per intended byte)
os.environ.setdefault('SYNTH_GENERATOR', str(ROOT / 'dol/synthetic-generator-fix/synthetic_protocols_fixed.py'))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module          # worker processes pickle functions by module name
    spec.loader.exec_module(module)
    return module


llm = _load('llm_boundaries', ROOT / 'dol/llm-varying-boundaries/scripts/llm_boundaries.py')
tf = _load('typed_fields', ROOT / 'dol/typed-field-hypotheses/scripts/typed_fields.py')
v2, bench, B, ANN, PROTOS, CAP = llm.v2, llm.bench, llm.B, llm.ANN, llm.PROTOS, llm.CAP
synth = llm.synth

DEV_SEED = 777
V1 = ROOT / 'dol/llm-varying-boundaries'


# ---------------------------------------------------------------- data

def synthetic_set(seed):
    rng = np.random.default_rng(seed)
    out = {}
    for index in range(llm.N_SYNTH):
        types = synth.generate_protocol(rng)[:llm.MAX_TYPES_PER_SYNTH]
        out[f'dev{index}' if seed == DEV_SEED else f'synth{index}'] = {
            f't{t}': (m, e, h if rng.random() < 0.7 else None) for t, (m, e, h) in enumerate(types)}
    return out


def families(set_name):
    """protocol -> family -> dict(msgs, sessions, truth or None, offs, proba, threshold, corpus)."""
    out = {}
    if set_name == 'real':
        scores = json.load(open(V1 / 'v2_scores.json'))
        for p in PROTOS:
            fams, everything = llm.real_families(p)
            corpus = llm.corpus_stats(everything)
            d = B / p / 'data'
            assign = {int(x['msg_id']): x['family_id'] for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
            sess = defaultdict(list)
            for m in bench._iter_jsonl(d / '01_messages.jsonl'):
                fam = assign.get(int(m['msg_id']))
                if fam and fam != 'noise':
                    sess[fam].append((m.get('session_id'), m.get('direction')))
            out[p] = {}
            for fam, s in scores[p]['families'].items():
                out[p][fam] = dict(msgs=fams[fam][0], sessions=sess[fam][:CAP], truth=None, offs=s['offs'],
                                   proba=s['proba'], threshold=scores[p]['threshold'], corpus=corpus)
        return out
    # synthetic sets: learned-v2 scores from the model trained on all 14 real protocols
    scores = None
    protos = llm.synthetic_protocols() if set_name == 'test-synth' else synthetic_set(DEV_SEED)
    model = None
    for sp, fams in protos.items():
        corpus = llm.corpus_stats([m for msgs, _, _ in fams.values() for m in msgs])
        out[sp] = {}
        for f, (msgs, edges, body_start) in fams.items():
            if scores is not None:
                if f not in scores[sp]['families']:
                    continue
                s = scores[sp]['families'][f]; offs, proba, thr = s['offs'], s['proba'], scores[sp]['threshold']
            else:
                X, offs = v2.family_rows(msgs, corpus, body_start)
                if not offs:
                    continue
                if model is None:
                    model = _all_real_model()
                proba, thr = [float(q) for q in llm.apply_v2(model, X)], model[2]
            out[sp][f] = dict(msgs=msgs[:CAP], sessions=[0] * len(msgs[:CAP]), truth=(msgs, edges), offs=offs,
                              proba=proba, threshold=thr, corpus=corpus)
    return out


def _all_real_model():
    data = {p: v2.load_protocol(p) for p in PROTOS}
    return llm.train_v2(data, list(PROTOS))


# ---------------------------------------------------------------- prompt

PREAMBLE = """You are analysing an unknown binary message format. Nothing is known about it beyond the evidence below; do not assume it is any particular published format.

All messages below were grouped into one message family by a clustering step (they are believed to share one layout). Offsets are 0-based byte positions; all messages are aligned at offset 0. A field edge at offset k means a new field starts at byte k.

A statistical boundary detector has proposed edges (marked * in the table). Measured on other formats, it is reliable where a constant byte meets a varying byte. Its errors are of two kinds, and both occur:
  - missed edges between two bytes that both vary (the most common error), e.g. two adjacent 2-byte integers, or a 1-byte code followed by a 1-byte value;
  - extra edges that cut one long varying field (text, an opaque blob, a wide integer) into pieces."""

FITS_HELP = """Whole-field tests (each candidate field read as one unsigned integer, both byte orders; only strong results are listed, and only for windows whose first and last byte both vary):
  length   share of messages where value = message length - c for one constant c
  counter  share of consecutive messages (same session and direction) where the value grows by 1..16"""

TASK = """Task
Describe the layout of offsets 0..{last} as consecutive fields. For each field give its start, its width in bytes, a type (const, length, counter, id, enum, flags, integer, timestamp, text, blob, padding, checksum, other) and, for multi-byte numbers, the byte order (BE or LE). Fields must follow each other without gaps, start at 0 and cover offset {last} (the last field may extend past it). Keep the detector's edges where a constant byte meets a varying one unless the samples clearly contradict them. Inside the varying regions decide from the value patterns: byte order and magnitude (a small big-endian number has a near-constant high byte first), bytes that change together, increments between messages, values that match the message length, ASCII text, padding. Keep the note to at most three sentences.

Answer with one JSON object and nothing else:
{{"fields": [{{"start": 0, "width": 2, "type": "...", "order": "BE"}}, ...], "note": "..."}}"""


def fits_block(fam, length):
    ff = tf.FamilyFits(fam['msgs'], fam['sessions'])
    varies = [len(set(ff.M[ff.lens > j, j].tolist())) > 1 for j in range(length)]
    lines = []
    for s in range(length):
        for w in (1, 2, 4):
            # a window that starts or ends on a constant byte fits exactly as well as the
            # narrower one without it, so it says nothing about the width: skip it
            if s + w > length or not (varies[s] and varies[s + w - 1]):
                continue
            f = ff.fits(s, s + w)
            hits = []
            if f[0] >= 0.9:
                hits.append(f'length {f[0]:.2f}')
            if f[1] >= 0.8:
                hits.append(f'counter {f[1]:.2f}')
            if hits:
                lines.append(f'  [{s}, {s + w}) width {w}: ' + ', '.join(hits))
    return lines


def build(fam, label, variant):
    rows, regions, samples, length = llm.family_evidence(fam['msgs'], fam['corpus'], fam['offs'], fam['proba'], fam['threshold'])
    if not regions:
        return None, regions, length
    text = llm.render_evidence(label, len(fam['msgs']), rows, regions, samples, length, fam['threshold'])
    if variant == 'V1U':                 # control: the v1 ungated prompt, unchanged
        return llm.build_prompt('ungated', text, length), regions, length
    if variant == 'A':
        lines = fits_block(fam, length)
        text += '\n\n' + FITS_HELP + '\n' + ('\n'.join(lines) if lines else '  (no strong results)')
    return PREAMBLE + '\n\n' + text + '\n\n' + TASK.format(last=length - 1) + '\n', regions, length


def prepare(set_names, variants):
    (EXP / 'prompts').mkdir(parents=True, exist_ok=True)
    manifest = json.load(open(EXP / 'manifest.json')) if (EXP / 'manifest.json').exists() else []
    done = {(e['set'], e['protocol'], e['family']) for e in manifest}
    for set_name in set_names:
        for p, fams in families(set_name).items():
            for index, (fam, data) in enumerate(sorted(fams.items())):
                if (set_name, p, fam) in done:
                    continue
                label = f'F{index}'
                entry = {'set': set_name, 'protocol': p, 'family': fam, 'label': label, 'prompts': {}}
                for variant in variants:
                    prompt, regions, length = build(data, label, variant)
                    entry.update(regions=regions, shown=length, threshold=data['threshold'],
                                 v2_edges=sorted(o for o, q in zip(data['offs'], data['proba']) if q >= data['threshold']))
                    if prompt:
                        name = f'{set_name}__{p}__{label}__{variant}.txt'
                        (EXP / 'prompts' / name).write_text(prompt, encoding='utf-8')
                        entry['prompts'][variant] = {'file': name, 'chars': len(prompt)}
                if set_name != 'real':
                    msgs, edges = data['truth']
                    (EXP / 'truth').mkdir(exist_ok=True)
                    with open(EXP / 'truth' / f'{set_name}__{p}__{fam}.jsonl', 'w') as fh:
                        for m, cuts in zip(msgs, edges):
                            fh.write(json.dumps({'len': len(m), 'boundaries': cuts}) + '\n')
                manifest.append(entry)
            print(set_name, p, 'done', flush=True)
    json.dump(manifest, open(EXP / 'manifest.json', 'w'), indent=1)
    cost(manifest)


def add_variant(set_name, variant):
    """Add prompts of another variant to the families already in the manifest."""
    manifest = json.load(open(EXP / 'manifest.json'))
    fams = families(set_name)
    for e in manifest:
        if e['set'] != set_name or variant in e['prompts']:
            continue
        prompt, regions, length = build(fams[e['protocol']][e['family']], e['label'], variant)
        assert regions == [tuple(r) for r in e['regions']] or regions == e['regions'], (e['protocol'], e['family'])
        if prompt:
            name = f"{set_name}__{e['protocol']}__{e['label']}__{variant}.txt"
            (EXP / 'prompts' / name).write_text(prompt, encoding='utf-8')
            e['prompts'][variant] = {'file': name, 'chars': len(prompt), 'format': 'edges' if variant == 'V1U' else 'fields'}
    json.dump(manifest, open(EXP / 'manifest.json', 'w'), indent=1)
    cost(manifest)


def cost(manifest):
    t = defaultdict(Counter)
    for e in manifest:
        for v, meta in e['prompts'].items():
            t[(e['set'], v)].update(requests=1, chars=meta['chars'])
    print(f"{'set':12s} {'var':3s} {'requests':>8s} {'in tok (est)':>12s}")
    for (s, v), c in sorted(t.items()):
        # 0.7 x chars/2.5: the measured ratio of real prompt tokens to the chars/2.5 estimate in the v1 run
        print(f"{s:12s} {v:3s} {c['requests']:8d} {int(0.7 * c['chars'] / 2.5):12d}")


# ---------------------------------------------------------------- call / score

def call(set_name, variant, workers=2):
    (EXP / 'responses').mkdir(exist_ok=True)
    jobs = []
    # families handled by the TLV stage (dol/per-message-segmentation) are not sent
    skip = {tuple(x) for x in json.load(open(EXP / 'tlv-families.json'))} if set_name == 'real' else set()
    for e in json.load(open(EXP / 'manifest.json')):
        if e['set'] != set_name or variant not in e['prompts'] or (e['protocol'], e['family']) in skip:
            continue
        name = e['prompts'][variant]['file'][:-4]
        out = EXP / 'responses' / f'{name}.json'
        if not out.exists():
            jobs.append((name, (EXP / 'prompts' / e['prompts'][variant]['file']).read_text(encoding='utf-8'), str(out)))
    print(f'{len(jobs)} requests, {workers} workers', flush=True)
    with concurrent.futures.ProcessPoolExecutor(workers) as pool:
        for name, status, secs in pool.map(llm._call_one, jobs):
            print(f'{name}: {status} ({secs:.0f}s)', flush=True)


def model_edges(entry, variant):
    path = EXP / 'responses' / f"{entry['prompts'][variant]['file'][:-4]}.json"
    if not path.exists():
        return None
    parsed, usage = llm.parse_response(path)
    try:
        if entry['prompts'][variant].get('format') == 'edges':      # v1 prompt answers with an edge list
            starts = {int(x) for x in parsed.get('edges', [])}
        else:
            starts = {int(f['start']) for f in parsed.get('fields', []) if isinstance(f, dict)}
    except (TypeError, ValueError):
        return None
    return (starts - {0}) or None


def score(set_name, variant):
    manifest = [e for e in json.load(open(EXP / 'manifest.json')) if e['set'] == set_name]
    by = defaultdict(list)
    for e in manifest:
        by[e['protocol']].append(e)
    results = {}
    for p, entries in by.items():
        sets = {'v2': {}, 'gated': {}, 'ungated': {}}
        regions, status = {}, Counter()
        for e in entries:
            v2e = set(e['v2_edges'])
            inside = llm.interior(e['regions'])
            regions[e['family']] = inside
            got = model_edges(e, variant) if variant in e['prompts'] else None
            status['answered' if got is not None else ('missing' if variant in e['prompts'] else 'no-region')] += 1
            sets['v2'][e['family']] = v2e
            if got is None:
                sets['gated'][e['family']] = sets['ungated'][e['family']] = v2e
                continue
            sets['gated'][e['family']] = {x for x in v2e if x not in inside} | {x for x in got if x in inside}
            sets['ungated'][e['family']] = {x for x in got if 0 < x < e['shown']} | {x for x in v2e if x >= e['shown']}
        items = defaultdict(list)
        if set_name == 'real':
            d = B / p / 'data'
            assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
            plen = {int(m['msg_id']): int(m['payload_len']) for m in bench._iter_jsonl(d / '01_messages.jsonl')}
            for a in bench._iter_jsonl(ANN / f'{p}.jsonl'):
                if a.get('reviewer') in bench.COARSE_REVIEWERS or int(a['msg_id']) not in plen or not a.get('boundaries'):
                    continue
                fam = assign.get(int(a['msg_id']), '')
                for v, s in sets.items():
                    items[v].append((set(a['boundaries']), s.get(fam, set()), regions.get(fam, set()), plen[int(a['msg_id'])]))
            out = EXP / 'families' / variant / p
            out.mkdir(parents=True, exist_ok=True)
            for v in ('gated', 'ungated'):
                json.dump({f: {'field_hypotheses': [{'start': o, 'length': 0} for o in sorted(e)]} for f, e in sets[v].items()},
                          open(out / f'05_families.exp-llm-v2prompt-{variant}-{v}.json', 'w'))
        else:
            for e in entries:
                for line in bench._iter_jsonl(EXP / 'truth' / f"{set_name}__{p}__{e['family']}.jsonl"):
                    for v, s in sets.items():
                        items[v].append((set(line['boundaries']), s[e['family']], regions[e['family']], line['len']))
        results[p] = {v: llm.score_messages(items[v]) for v in sets}
        results[p]['status'] = dict(status)
        tok = Counter()
        for e in entries:
            if variant in e['prompts']:
                path = EXP / 'responses' / f"{e['prompts'][variant]['file'][:-4]}.json"
                if path.exists():
                    u = llm.parse_response(path)[1]
                    tok.update(tin=int(u.get('prompt_tokens') or 0), tout=int(u.get('completion_tokens') or 0))
        results[p]['tokens'] = dict(tok)
    json.dump(results, open(EXP / f'results-{set_name}-{variant}.json', 'w'), indent=1)
    lines = [f"{set_name} variant {variant}", f"{'protocol':10s} {'v2':>6s} {'gated':>6s} {'ungated':>7s}   region P/R v2 | gated | ungated   answered  tok in/out (k)"]
    for p, r in results.items():
        lines.append(f"{p:10s} {r['v2']['f1']:6.3f} {r['gated']['f1']:6.3f} {r['ungated']['f1']:7.3f}   "
                     + ' | '.join(f"{r[v]['region']['precision']:.2f}/{r[v]['region']['recall']:.2f}" for v in ('v2', 'gated', 'ungated'))
                     + f"   {r['status'].get('answered', 0)}/{r['status'].get('answered', 0) + r['status'].get('missing', 0)}"
                     + f"   {r['tokens'].get('tin', 0) / 1000:.1f}/{r['tokens'].get('tout', 0) / 1000:.1f}")
    lines.append(f"{'macro':10s} " + ' '.join(f"{np.mean([r[v]['f1'] for r in results.values()]):{w}.3f}" for v, w in (('v2', 6), ('gated', 6), ('ungated', 7))))
    text = '\n'.join(lines)
    print(text)
    (EXP / f'results-{set_name}-{variant}.txt').write_text(text + '\n', encoding='utf-8')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'prepare':
        prepare(sys.argv[2].split(','), sys.argv[3].split(','))
    elif cmd == 'add':
        add_variant(sys.argv[2], sys.argv[3])
    elif cmd == 'cost':
        cost(json.load(open(EXP / 'manifest.json')))
    elif cmd == 'call':
        call(sys.argv[2], sys.argv[3], workers=int(os.environ.get('LLM_WORKERS', 2)))
    elif cmd == 'score':
        score(sys.argv[2], sys.argv[3])
