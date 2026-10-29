"""Can a strong general LLM place field boundaries where statistics run out?

The error analysis showed that most missed edges sit between two bytes that
both vary inside the family. This experiment marks those "varying regions"
(runs of >= 2 consecutive non-constant bytes) per family, shows the model an
anonymised evidence bundle (aligned samples, per-offset statistics, the
learned-v2 edges and scores) and asks for the field edges inside the regions.

Variants
  gated    model edges only inside region interiors, learned-v2 edges elsewhere
  ungated  model gives every edge in the displayed range, learned-v2 beyond it

Phases (each writes under dol/llm-varying-boundaries/):
  prepare   learned-v2 scores (leave-one-protocol-out for the 14 real protocols,
            trained on all 14 for the synthetic ones), regions, prompts, cost
            estimate. No network access.
  call      sends the prompts (needs OPENAI_API_KEY), stores raw responses.
            call <variant> [protocol,...]
  score     applies the responses, writes 05_families.exp-llm-*.json and the
            result tables.
"""
import concurrent.futures
import importlib.util
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re')
EXP = ROOT / 'dol/llm-varying-boundaries'
SCRIPTS = ROOT / 'dol/boundary-recall-experiments/scripts'
sys.path.insert(0, str(ROOT / 'src'))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v2 = _load('learned_boundaries_v2', SCRIPTS / 'learned_boundaries_v2.py')
# SYNTH_GENERATOR selects the generator file; the default is the original (int64-bytes bug, see
# dol/synthetic-generator-fix), kept so the v1 results stay reproducible.
synth = _load('synthetic_protocols', Path(os.environ.get('SYNTH_GENERATOR', SCRIPTS / 'synthetic_protocols.py')))
bench, B, ANN, PROTOS, MAXLEN, CAP = v2.bench, v2.B, v2.ANN, v2.PROTOS, v2.MAXLEN, v2.CAP

N_SYNTH = 8
SYNTH_SEED = 20261015          # v3 trained on seed 0; v2 never sees synthetic data anyway
MAX_TYPES_PER_SYNTH = 6
SHOW = 128                     # offsets shown to the model; regions beyond keep the statistical edges
N_SAMPLES = 8
VARIANTS = ('gated', 'ungated')
RULES_FILE = '05_families.exp-perbyte0.5.json'
V2_FILE = '05_families.exp-learned-v2.json'


# ---------------------------------------------------------------- data loading

def real_families(p):
    """family -> (messages[:CAP], body_start) for every family that has annotations."""
    d = B / p / 'data'
    assign = {int(x['msg_id']): x['family_id'] for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    framing = json.load(open(d / '04_framing.json')).get('families', {})
    by, everything = defaultdict(list), []
    for m in bench._iter_jsonl(d / '01_messages.jsonl'):
        payload = bytes.fromhex(m['payload_hex'])
        everything.append(payload)
        fam = assign.get(int(m['msg_id']))
        if fam and fam != 'noise':
            by[fam].append(payload)
    out = {}
    for fam, msgs in by.items():
        layouts = (framing.get(fam) or {}).get('layout_hypotheses') or [{}]
        bs = layouts[0].get('body_start')
        out[fam] = (msgs[:CAP], int(bs) if bs else None)
    return out, everything


def corpus_stats(everything):
    step = max(1, len(everything) // 8000)
    cM, clens, cfull = v2.to_matrix(everything[::step])
    cvalid, cst = v2.column_stats(cM, clens, cfull)
    return cvalid, cst, cM


def synthetic_protocols():
    rng = np.random.default_rng(SYNTH_SEED)
    out = {}
    for index in range(N_SYNTH):
        types = synth.generate_protocol(rng)[:MAX_TYPES_PER_SYNTH]
        fams = {}
        for t, (messages, edges, header_len) in enumerate(types):
            body_start = header_len if rng.random() < 0.7 else None   # as in v3
            fams[f't{t}'] = (messages, edges, body_start)
        out[f'synth{index}'] = fams
    return out


# ---------------------------------------------------------------- learned-v2 scores

def train_v2(data, train):
    X, y, w = v2.stack(data, train)
    stage1 = v2.fit(X, y, w)
    oof = {}
    for inner in train:
        model = v2.fit(*v2.stack(data, [p for p in train if p != inner]))
        for fam, (Xf, offs, yf) in data[inner].items():
            oof[(inner, fam)] = model.predict_proba(Xf)[:, 1]
    X2 = np.vstack([v2.neighbour_features(v[0], oof[(p, fam)]) for p in train for fam, v in data[p].items()])
    stage2 = v2.fit(X2, y, w)
    p2 = stage2.predict_proba(X2)[:, 1]
    t = max(np.arange(0.2, 0.71, 0.05), key=lambda t: v2._f1(y, p2 >= t, w))
    return stage1, stage2, float(t)


def apply_v2(model, X):
    stage1, stage2, _ = model
    return stage2.predict_proba(v2.neighbour_features(X, stage1.predict_proba(X)[:, 1]))[:, 1]


# ---------------------------------------------------------------- evidence

def family_evidence(msgs, corpus, offs, proba, threshold):
    """Per-offset stats, varying regions and samples for one family (offsets < SHOW)."""
    M, lens, full = v2.to_matrix(msgs)
    valid, st = v2.column_stats(M, lens, full)
    cvalid, cst, _ = corpus
    length = min(int(lens.max()), offs[-1] + 1 if offs else 1, SHOW)
    rows = []
    for j in range(length):
        v = M[valid[:, j], j]
        c = Counter(v.tolist())
        top = c.most_common(3)
        rows.append({
            'off': j, 'cov': round(float(valid[:, j].mean()), 2),
            'H': abs(round(float(st['H'][j]) * 8, 2)), 'distinct': len(c),
            'top': [(f'{val:02x}', round(n / v.size, 2)) for val, n in top],
            'const': bool(len(c) == 1), 'cH': abs(round(float(cst['H'][j]) * 8, 2)),
            'cdistinct': int(min(256, round(cst['distinct'][j] * 256))) if cvalid[:, j].sum() else 0,
        })
    score = dict(zip(offs, proba))
    for r in rows:
        r['v2'] = round(float(score[r['off']]), 2) if r['off'] in score else None
        r['edge'] = bool(r['off'] in score and score[r['off']] >= threshold)
    # varying region: maximal run of >= 2 non-constant bytes; its interior offsets are the open edges
    regions, start = [], None
    varying = [not r['const'] and r['cov'] >= 0.05 for r in rows] + [False]
    for j, flag in enumerate(varying):
        if flag and start is None:
            start = j
        elif not flag and start is not None:
            if j - start >= 2:
                regions.append((start, j))
            start = None
    samples = _pick_samples(msgs)
    return rows, regions, samples, length


def _pick_samples(msgs):
    distinct = list(dict.fromkeys(msgs))
    by_len = defaultdict(list)
    for m in distinct:
        by_len[len(m)].append(m)
    picked = []
    # one per distinct length first (shortest .. longest), then spread over the capture
    for n in sorted(by_len)[:N_SAMPLES // 2]:
        picked.append(by_len[n][0])
    step = max(1, len(distinct) // N_SAMPLES)
    for m in distinct[::step]:
        if len(picked) >= N_SAMPLES:
            break
        if m not in picked:
            picked.append(m)
    return picked[:N_SAMPLES]


PREAMBLE = """You are analysing an unknown binary message format. Nothing is known about it beyond the evidence below; do not assume it is any particular published protocol.

All messages below were grouped into one message family by a clustering step (they are believed to share one layout). Offsets are 0-based byte positions from the start of the message, all messages are aligned at offset 0. A field edge at offset k means a new field starts at byte k (the edge lies between byte k-1 and byte k).

A statistical boundary detector has already proposed edges. It is reliable where a constant byte meets a varying byte, but weak inside runs of bytes that all vary (for example a 2-byte integer followed by another 2-byte integer, or a long payload that it wrongly cuts into pieces)."""

COLUMNS = """Per-offset table columns:
  off       byte offset
  cov       share of messages that are long enough to have this byte
  H         byte entropy inside the family, bits (0 = constant, 8 = uniform)
  dist      distinct values inside the family
  top       most frequent values (hex) with their share
  cH/cdist  entropy and distinct values of this offset over the whole capture (all families)
  det       detector score for an edge at this offset (0..1), * = detector places an edge here
  s1..sN    the byte value in sample message 1..N (.. = message too short)"""


def render_evidence(fam_label, n_msgs, rows, regions, samples, length, threshold):
    lens = Counter(len(m) for m in samples)
    out = [f'Family {fam_label}: {n_msgs} messages; sample lengths {sorted(lens)}; offsets 0..{length - 1} shown'
           + (' (messages are longer; the rest is not shown)' if any(len(m) > length for m in samples) else '') + '.']
    out.append('')
    out.append('Sample messages (hex, first %d bytes):' % length)
    for k, m in enumerate(samples, 1):
        out.append(f's{k} len={len(m)}: ' + m[:length].hex(' '))
    out.append('')
    out.append(COLUMNS)
    out.append(f'Detector threshold {threshold:.2f}.')
    head = 'off  cov    H dist top                     cH cdist  det  ' + ' '.join(f's{k}' for k in range(1, len(samples) + 1))
    out.append(head)
    for r in rows:
        top = ','.join(f'{v}:{s:.2f}' for v, s in r['top'])
        det = '  -  ' if r['v2'] is None else f"{r['v2']:.2f}{'*' if r['edge'] else ' '}"
        cells = ' '.join(f'{m[r["off"]]:02x}' if r['off'] < len(m) else '..' for m in samples)
        out.append(f"{r['off']:3d} {r['cov']:4.2f} {r['H']:4.2f} {r['distinct']:4d} {top:22s} {r['cH']:4.2f} {r['cdistinct']:4d} {det} {cells}")
    out.append('')
    out.append('Detector edges: ' + (', '.join(str(r['off']) for r in rows if r['edge']) or 'none'))
    out.append('')
    out.append('Varying regions (runs of consecutive bytes that all vary inside the family; [a, b) = bytes a..b-1):')
    for k, (a, b) in enumerate(regions, 1):
        inner = [r['off'] for r in rows if a < r['off'] < b and r['edge']]
        out.append(f'  R{k}: [{a}, {b})  length {b - a}; open edge positions {a + 1}..{b - 1}; detector edges inside: {inner or "none"}')
    return '\n'.join(out)


TASK_GATED = """Task
For each varying region, decide where the field edges inside it are. Only offsets strictly inside the region (a < k < b) may be given; the region ends themselves are already settled. Use the per-offset statistics, the sample bytes (byte order, value ranges, which bytes move together, counters, lengths, ASCII text, padding), and the usual ways binary formats are built. An empty list means the region is one single field. Keep each reason to one sentence.

Answer with one JSON object and nothing else:
{"regions": [{"id": "R1", "edges": [k, ...], "reason": "..."}, ...]}"""

TASK_UNGATED = """Task
Give the complete list of field edges for offsets 1..{last} of this family. You may keep, remove or add any detector edge, inside or outside the varying regions. Use the per-offset statistics, the sample bytes (byte order, value ranges, which bytes move together, counters, lengths, ASCII text, padding), and the usual ways binary formats are built. Keep the reason to at most three sentences.

Answer with one JSON object and nothing else:
{{"edges": [k, ...], "reason": "..."}}"""


def build_prompt(variant, evidence_text, length):
    task = TASK_GATED if variant == 'gated' else TASK_UNGATED.format(last=length - 1)
    return PREAMBLE + '\n\n' + evidence_text + '\n\n' + task + '\n'


# ---------------------------------------------------------------- prepare

def prepare():
    (EXP / 'prompts').mkdir(parents=True, exist_ok=True)
    data, raw, corpora = {}, {}, {}
    for p in PROTOS:
        fams, everything = real_families(p)
        corpora[p] = corpus_stats(everything)
        raw[p] = {f: msgs for f, (msgs, _) in fams.items()}
        data[p] = v2.load_protocol(p)        # same rows and labels as the published learned-v2 run
        print(p, 'families', len(data[p]), flush=True)
    synthetic = synthetic_protocols()
    synth_data = {}
    for sp, fams in synthetic.items():
        everything = [m for msgs, _, _ in fams.values() for m in msgs]
        corpora[sp] = corpus_stats(everything)
        raw[sp] = {f: msgs for f, (msgs, _, _) in fams.items()}
        synth_data[sp] = {}
        for f, (msgs, edges, body_start) in fams.items():
            X, offs = v2.family_rows(msgs, corpora[sp], body_start)
            if offs:
                synth_data[sp][f] = (X, offs, None)
        # truth for the synthetic scorer
        (EXP / 'synthetic').mkdir(exist_ok=True)
        with open(EXP / 'synthetic' / f'{sp}.jsonl', 'w') as fh:
            for f, (msgs, edges, _) in fams.items():
                for k, (m, cuts) in enumerate(zip(msgs, edges)):
                    fh.write(json.dumps({'family': f, 'k': k, 'payload_hex': m.hex(), 'boundaries': cuts}) + '\n')

    scores = {}
    for held in PROTOS:
        model = train_v2(data, [p for p in PROTOS if p != held])
        scores[held] = {'threshold': model[2], 'families': {
            fam: {'offs': offs, 'proba': [float(q) for q in apply_v2(model, X)]} for fam, (X, offs, y) in data[held].items()}}
        print('v2 lopo', held, 'thr', round(model[2], 2), flush=True)
    model = train_v2(data, list(PROTOS))
    for sp, fams in synth_data.items():
        scores[sp] = {'threshold': model[2], 'families': {
            fam: {'offs': offs, 'proba': [float(q) for q in apply_v2(model, X)]} for fam, (X, offs, _) in fams.items()}}
    print('v2 all-real model thr', round(model[2], 2), flush=True)

    # sanity: regenerated real edges must equal the published learned-v2 family files
    for p in PROTOS:
        pub = bench._family_edges(json.load(open(B / p / 'data' / V2_FILE)))
        mine = {f: sorted(o for o, q in zip(s['offs'], s['proba']) if q >= scores[p]['threshold'])
                for f, s in scores[p]['families'].items()}
        diff = sum(set(pub.get(f, [])) - {0} != set(e) for f, e in mine.items())
        print('check', p, 'families differing from published learned-v2:', diff, flush=True)

    manifest, letters = [], {}
    for p in list(PROTOS) + list(synth_data):
        sc = scores[p]
        for index, (fam, s) in enumerate(sorted(sc['families'].items())):
            msgs = raw[p][fam]
            rows, regions, samples, length = family_evidence(msgs, corpora[p], s['offs'], s['proba'], sc['threshold'])
            label = f'F{index}'                       # anonymous; real family ids can carry hints
            text = render_evidence(label, len(msgs), rows, regions, samples, length, sc['threshold'])
            entry = {'protocol': p, 'family': fam, 'label': label, 'shown': length,
                     'regions': regions, 'n_messages': len(msgs), 'prompts': {}}
            if regions:
                for variant in VARIANTS:
                    prompt = build_prompt(variant, text, length)
                    name = f'{p}__{label}__{variant}.txt'
                    (EXP / 'prompts' / name).write_text(prompt, encoding='utf-8')
                    entry['prompts'][variant] = {'file': name, 'chars': len(prompt)}
            manifest.append(entry)
    json.dump(scores, open(EXP / 'v2_scores.json', 'w'))
    json.dump(manifest, open(EXP / 'manifest.json', 'w'), indent=1)
    cost_report(manifest)


def est_tokens(chars):
    # hex-heavy text tokenises at roughly 2.5-3 characters per token; use the pessimistic end
    return int(chars / 2.5)


def cost_report(manifest, out_tokens=1500):
    print(f"\n{'protocol':10s} {'fams':>4s} {'w/region':>8s} {'requests':>8s} {'in tok (est)':>12s} {'out tok (est)':>13s}")
    tot = Counter()
    by = defaultdict(list)
    for e in manifest:
        by[e['protocol']].append(e)
    for p, es in by.items():
        req = sum(len(e['prompts']) for e in es)
        tin = sum(est_tokens(v['chars']) for e in es for v in e['prompts'].values())
        print(f"{p:10s} {len(es):4d} {sum(bool(e['regions']) for e in es):8d} {req:8d} {tin:12d} {req * out_tokens:13d}")
        tot.update(fams=len(es), req=req, tin=tin, tout=req * out_tokens)
    print(f"{'total':10s} {tot['fams']:4d} {'':8s} {tot['req']:8d} {tot['tin']:12d} {tot['tout']:13d}")


# ---------------------------------------------------------------- call

def llm_config():
    from protocol_re.llm.analyze import LLMRequestConfig
    cfg = json.load(open(ROOT / 'config/llm_config.json'))
    key = os.environ.get('OPENAI_API_KEY')
    if not key:
        sys.exit('OPENAI_API_KEY is not set')
    # streaming keeps the gateway connection alive during long reasoning; model and effort overridable
    return LLMRequestConfig(model=os.environ.get('LLM_MODEL', cfg['model']), base_url=cfg['openai_base_url'], api_key=key,
                            temperature=0.0, max_tokens=int(os.environ.get('LLM_MAX_TOKENS', 16000)), timeout=600,
                            stream=True, reasoning_effort=os.environ.get('LLM_REASONING_EFFORT') or None,
                            max_retries=2, retry_delay_seconds=cfg['retry_delay_seconds'],
                            max_retry_delay_seconds=cfg['max_retry_delay_seconds'],
                            request_interval_seconds=cfg['request_interval_seconds'])


def _call_one(job):
    """Runs in a worker process: analyze.py serialises requests per process."""
    from protocol_re.llm.analyze import call_openai_compatible_chat_with_raw
    name, prompt, out = job
    config = llm_config()
    config.logger = None
    started = time.time()
    try:
        parsed, body = call_openai_compatible_chat_with_raw(prompt, config, request_label=name)
        choice = (parsed.get('choices') or [{}])[0]
        if not (choice.get('message') or {}).get('content'):
            # reasoning used the whole budget: keep the raw reply, but do not count it as an answer
            Path(out + '.truncated').write_text(body, encoding='utf-8')
            return name, f"no content (finish_reason {choice.get('finish_reason')})", time.time() - started
        Path(out).write_text(body, encoding='utf-8')
        return name, 'ok', time.time() - started
    except Exception as exc:  # recorded and retried on the next run
        Path(out + '.error').write_text(f'{type(exc).__name__}: {exc}', encoding='utf-8')
        return name, f'error {exc}', time.time() - started


def call(variant, protocols=None, workers=4, limit=None):
    llm_config()
    (EXP / 'responses').mkdir(exist_ok=True)
    manifest = json.load(open(EXP / 'manifest.json'))
    jobs = []
    for e in manifest:
        if variant not in e['prompts'] or (protocols and e['protocol'] not in protocols):
            continue
        name = e['prompts'][variant]['file'][:-4]
        out = EXP / 'responses' / f'{name}.json'
        if out.exists():
            continue
        jobs.append((name, (EXP / 'prompts' / e['prompts'][variant]['file']).read_text(encoding='utf-8'), str(out)))
    jobs = jobs[:limit] if limit else jobs
    print(f'{len(jobs)} requests, {workers} workers', flush=True)
    with concurrent.futures.ProcessPoolExecutor(workers) as pool:
        for name, status, secs in pool.map(_call_one, jobs):
            print(f'{name}: {status} ({secs:.0f}s)', flush=True)


# ---------------------------------------------------------------- score

def parse_response(path):
    from protocol_re.llm.analyze import extract_message_json
    body = json.loads(path.read_text(encoding='utf-8'))
    try:
        parsed = extract_message_json(body)
    except Exception:
        parsed = {}
    return parsed, body.get('usage') or {}


def interior(regions):
    return {k for a, b in regions for k in range(a + 1, b)}


def variant_edges(entry, v2_edges, variant):
    """Edge set (interior offsets) of one family under a variant; None if the response is missing."""
    if variant == 'v2' or not entry['prompts']:
        return set(v2_edges), 'none'
    path = EXP / 'responses' / f"{entry['prompts'][variant]['file'][:-4]}.json"
    if not path.exists():
        return set(v2_edges), 'missing'
    parsed, _ = parse_response(path)
    inside = interior(entry['regions'])
    if variant == 'gated':
        given = {}
        for r in parsed.get('regions', []) or []:
            try:
                k = int(str(r.get('id', '')).lstrip('Rr')) - 1
                given[k] = {int(x) for x in r.get('edges', [])}
            except (TypeError, ValueError):
                continue
        if not given:
            return set(v2_edges), 'unparsed'
        out = {e for e in v2_edges if e not in inside}
        for k, (a, b) in enumerate(entry['regions']):
            if k in given:
                out |= {e for e in given[k] if a < e < b}
            else:                                   # region not answered: keep the detector
                out |= {e for e in v2_edges if a < e < b}
        return out, 'ok'
    edges = parsed.get('edges')
    if not isinstance(edges, list):
        return set(v2_edges), 'unparsed'
    try:
        llm = {int(x) for x in edges}
    except (TypeError, ValueError):
        return set(v2_edges), 'unparsed'
    shown = entry['shown']
    return {e for e in llm if 0 < e < shown} | {e for e in v2_edges if e >= shown}, 'ok'


def score_messages(items):
    """items: (truth_edges, predicted_edges, region_interior, length). Overall and region-only counts."""
    c = Counter()
    for truth, pred, inside, length in items:
        truth = {e for e in truth if 0 < e < length}
        pred = {e for e in pred if 0 < e < length}
        c['tp'] += len(pred & truth); c['fp'] += len(pred - truth); c['fn'] += len(truth - pred)
        rt, rp = truth & inside, pred & inside
        c['rtp'] += len(rp & rt); c['rfp'] += len(rp - rt); c['rfn'] += len(rt - rp)
        c['n'] += 1
    f = lambda tp, fp, fn: bench._f1(tp, fp, fn)
    return {'messages': c['n'], **f(c['tp'], c['fp'], c['fn']),
            'region': {**f(c['rtp'], c['rfp'], c['rfn']), 'truth_edges': c['rtp'] + c['rfn']}}


def score():
    manifest = json.load(open(EXP / 'manifest.json'))
    scores = json.load(open(EXP / 'v2_scores.json'))
    (EXP / 'families').mkdir(exist_ok=True)
    by = defaultdict(list)
    for e in manifest:
        by[e['protocol']].append(e)
    results, cost = {}, {}
    for p, entries in by.items():
        thr = scores[p]['threshold']
        fam_sets, status = {v: {} for v in ('v2', 'rules') + VARIANTS}, Counter()
        regions = {}
        for e in entries:
            s = scores[p]['families'][e['family']]
            v2_edges = {o for o, q in zip(s['offs'], s['proba']) if q >= thr}
            regions[e['family']] = interior(e['regions'])
            for v in ('v2',) + VARIANTS:
                edges, st = variant_edges(e, v2_edges, v)
                fam_sets[v][e['family']] = edges
                if v in VARIANTS and e['prompts']:
                    status[f'{v}:{st}'] += 1
        tokens = Counter()
        for e in entries:
            for v, meta in e['prompts'].items():
                path = EXP / 'responses' / f"{meta['file'][:-4]}.json"
                if path.exists():
                    usage = parse_response(path)[1]
                    tokens[f'{v}_in'] += int(usage.get('prompt_tokens') or 0)
                    tokens[f'{v}_out'] += int(usage.get('completion_tokens') or 0)
                    tokens[f'{v}_requests'] += 1
        cost[p] = dict(tokens)
        if p in PROTOS:
            d = B / p / 'data'
            fam_sets['rules'] = {f: set(e) - {0} for f, e in bench._family_edges(json.load(open(d / RULES_FILE))).items()}
            for v in VARIANTS:
                out = EXP / 'families' / p
                out.mkdir(exist_ok=True)
                json.dump({f: {'field_hypotheses': [{'start': o, 'length': 0} for o in sorted(edges)]} for f, edges in fam_sets[v].items()},
                          open(out / f'05_families.exp-llm-{v}.json', 'w'))
            assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
            plen = {int(m['msg_id']): int(m['payload_len']) for m in bench._iter_jsonl(d / '01_messages.jsonl')}
            ann = [a for a in bench._iter_jsonl(ANN / f'{p}.jsonl') if a.get('reviewer') not in bench.COARSE_REVIEWERS
                   and int(a['msg_id']) in plen and a.get('boundaries')]
            results[p] = {}
            for v, sets in fam_sets.items():
                items = [(set(a['boundaries']), sets.get(assign.get(int(a['msg_id']), ''), set()),
                          regions.get(assign.get(int(a['msg_id']), ''), set()), plen[int(a['msg_id'])]) for a in ann]
                results[p][v] = score_messages(items)
            # cross-check: the official scorer on the written files gives the same overall F1
            for v in VARIANTS:
                official = bench.score_protocol(d, ANN / f'{p}.jsonl', str(EXP / 'families' / p / f'05_families.exp-llm-{v}.json'))
                assert abs(official['f1'] - results[p][v]['f1']) < 1e-3, (p, v, official, results[p][v])
        else:
            del fam_sets['rules']
            items = defaultdict(list)
            for line in bench._iter_jsonl(EXP / 'synthetic' / f'{p}.jsonl'):
                length = len(line['payload_hex']) // 2
                for v, sets in fam_sets.items():
                    items[v].append((set(line['boundaries']), sets.get(line['family'], set()), regions.get(line['family'], set()), length))
            results[p] = {v: score_messages(items[v]) for v in fam_sets}
        results[p]['status'] = dict(status)
    json.dump({'results': results, 'tokens': cost}, open(EXP / 'results.json', 'w'), indent=1)
    report(results, cost)


def report(results, cost):
    lines = []
    for group, names in (('real (14 protocols, unseen by learned-v2 and by the prompt design)', PROTOS),
                         ('synthetic (cannot be memorised)', [p for p in results if p.startswith('synth')])):
        cols = ['rules', 'v2', 'gated', 'ungated'] if group.startswith('real') else ['v2', 'gated', 'ungated']
        lines.append(f'\n== {group}: per-message boundary F1, and P/R inside varying regions ==')
        lines.append(f"{'protocol':10s} " + ' '.join(f'{c:>7s}' for c in cols) + '   region P/R: ' + '  '.join(f'{c:>11s}' for c in cols[-3:])
                     + f"  {'reg.edges':>9s} {'tok in/out (k)':>15s}")
        for p in names:
            r = results[p]
            tok = cost.get(p, {})
            tin = (tok.get('gated_in', 0) + tok.get('ungated_in', 0)) / 1000
            tout = (tok.get('gated_out', 0) + tok.get('ungated_out', 0)) / 1000
            lines.append(f"{p:10s} " + ' '.join(f"{r[c]['f1']:7.3f}" for c in cols) + '              '
                         + '  '.join(f"{r[c]['region']['precision']:5.2f}/{r[c]['region']['recall']:4.2f}" for c in cols[-3:])
                         + f"  {r['v2']['region']['truth_edges']:9d} {tin:7.1f}/{tout:6.1f}")
        lines.append(f"{'macro F1':10s} " + ' '.join(f"{np.mean([results[p][c]['f1'] for p in names]):7.3f}" for c in cols)
                     + '              ' + '  '.join(f"{np.mean([results[p][c]['region']['precision'] for p in names]):5.2f}/{np.mean([results[p][c]['region']['recall'] for p in names]):4.2f}" for c in cols[-3:]))
    text = '\n'.join(lines)
    print(text)
    (EXP / 'results.txt').write_text(text + '\n', encoding='utf-8')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'prepare':
        prepare()
    elif cmd == 'cost':
        cost_report(json.load(open(EXP / 'manifest.json')))
    elif cmd == 'call':
        protos = sys.argv[3].split(',') if len(sys.argv) > 3 and sys.argv[3] != 'all' else None
        call(sys.argv[2], protos, workers=int(os.environ.get('LLM_WORKERS', 4)),
             limit=int(os.environ['LLM_LIMIT']) if os.environ.get('LLM_LIMIT') else None)
    elif cmd == 'score':
        score()
