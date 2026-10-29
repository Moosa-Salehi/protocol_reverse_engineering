"""Typed whole-field hypotheses as boundary evidence (learned-v2 + field fits).

The five pairwise signals (varvar-signals.log) compare two neighbouring bytes and
score AUC ~0.5 on var|var edges. Here every candidate field [s, e) around an
offset is read as one unsigned integer (both byte orders) and tested for what
real fields do:
  len      value = message length - c for one constant c (length field)
  counter  increases by 1..16 between consecutive messages of a session/direction
  range    p5..p95 spread is small relative to the width (enum, address, quantity)
  smooth   consecutive values are close (measurements, timestamps)
  joint    entropy of the combined value / summed byte entropies (low = bytes move together)
For offset i (edge between i-1 and i) the candidates are the fields ending at i,
starting at i, and spanning i, of widths 1, 2, 4. The fits are appended to the
learned-v2 rows and the two-stage model is retrained leave-one-protocol-out with
the same procedure, threshold choice and families as learned-v2.

Usage: typed_fields.py [topk]     -> results under dol/typed-field-hypotheses/
  topk: keep only the k typed features with the highest var|var ROC AUC, chosen
        inside each fold on the training protocols only (results-top<k>.*)
"""
import importlib.util
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path('/mnt/d/tez/practical/protocol_re')
OUT = ROOT / 'dol/typed-field-hypotheses'
SCRIPTS = ROOT / 'dol/boundary-recall-experiments/scripts'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v2 = _load('learned_boundaries_v2', SCRIPTS / 'learned_boundaries_v2.py')
llm = _load('llm_boundaries', ROOT / 'dol/llm-varying-boundaries/scripts/llm_boundaries.py')
bench, B, ANN, PROTOS, MAXLEN, CAP = v2.bench, v2.B, v2.ANN, v2.PROTOS, v2.MAXLEN, v2.CAP

ENDING = (1, 2, 4)
STARTING = (1, 2, 4)
SPANNING = ((1, 1), (2, 2), (1, 3), (3, 1))   # (bytes before i, bytes after i)
FITS = ('len', 'counter', 'range', 'smooth', 'joint')
TOPK = int(sys.argv[1]) if __name__ == '__main__' and len(sys.argv) > 1 else None
SYNTH_TAG = os.environ.get('SYNTH_TAG', '')          # e.g. -fixedsynth when SYNTH_GENERATOR points at the fixed copy
SYNTH_ONLY = bool(os.environ.get('SYNTH_ONLY'))       # skip the real leave-one-out folds (unchanged by the generator)
SUFFIX = (f'-top{TOPK}' if TOPK else '') + SYNTH_TAG


# ---------------------------------------------------------------- field fits

class FamilyFits:
    """Caches fits of candidate fields [s, e) for one family."""

    def __init__(self, msgs, sessions):
        self.M, self.lens, self.full = v2.to_matrix(msgs)
        self.full_len = np.array([len(m) for m in msgs], dtype=np.int64)
        # consecutive message pairs inside one session and direction, in capture order
        order = defaultdict(list)
        for k, key in enumerate(sessions):
            order[key].append(k)
        self.pairs = np.array([(a, b) for ks in order.values() for a, b in zip(ks, ks[1:])], dtype=np.int64).reshape(-1, 2)
        self.cache = {}

    def fits(self, s, e):
        if (s, e) in self.cache:
            return self.cache[(s, e)]
        w = e - s
        valid = self.lens >= e
        out = np.zeros(len(FITS))
        if s < 0 or e > MAXLEN or valid.sum() < 3:
            self.cache[(s, e)] = out
            return out
        cols = self.M[:, s:e].astype(np.int64)
        best = np.zeros(4)
        for little in ((False,) if w == 1 else (False, True)):
            weights = 256 ** (np.arange(w) if little else np.arange(w)[::-1])
            value = cols @ weights
            v = value[valid]
            distinct = len(np.unique(v))
            if distinct >= 2:
                diff = self.full_len[valid] - v
                _, counts = np.unique(diff, return_counts=True)
                best[0] = max(best[0], counts.max() / v.size)
            pv = self.pairs[valid[self.pairs[:, 0]] & valid[self.pairs[:, 1]]] if len(self.pairs) else self.pairs
            if distinct >= 3 and len(pv) >= 3:
                d = (value[pv[:, 1]] - value[pv[:, 0]]) % (256 ** w)
                best[1] = max(best[1], float(((d >= 1) & (d <= 16)).mean()))
                signed = np.minimum(d, 256 ** w - d)
                best[3] = max(best[3], 1 - np.log2(np.median(signed) + 1) / (8 * w))
            spread = np.percentile(v, 95) - np.percentile(v, 5)
            best[2] = max(best[2], 1 - np.log2(spread + 1) / (8 * w))
        out[:4] = best
        # joint entropy of the field relative to its bytes
        rows = cols[valid]
        _, inv = np.unique(rows, axis=0, return_inverse=True)
        hj = _entropy(np.bincount(inv.ravel()))
        hb = sum(_entropy(np.bincount(rows[:, k], minlength=256)) for k in range(w))
        out[4] = hj / hb if hb > 1e-9 else 1.0
        self.cache[(s, e)] = out
        return out

    def row(self, i):
        feats = []
        for w in ENDING:
            feats.append(self.fits(i - w, i))
        for w in STARTING:
            feats.append(self.fits(i, i + w))
        span = [self.fits(i - a, i + b) for a, b in SPANNING]
        feats += span
        sides = np.max(np.stack(feats[:len(ENDING) + len(STARTING)]), axis=0)
        feats.append(np.max(np.stack(span), axis=0) - sides)   # does a field across i fit better than fields at i?
        return np.concatenate(feats)


def _entropy(counts):
    counts = counts[counts > 0]
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


# ---------------------------------------------------------------- data

def real_typed(p, data_p):
    """Typed-fit rows for the families and offsets of v2.load_protocol(p)."""
    d = B / p / 'data'
    assign = {int(x['msg_id']): x['family_id'] for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    by = defaultdict(list)
    for m in bench._iter_jsonl(d / '01_messages.jsonl'):
        fam = assign.get(int(m['msg_id']))
        if fam and fam != 'noise':
            by[fam].append((bytes.fromhex(m['payload_hex']), (m.get('session_id'), m.get('direction'))))
    out = {}
    for fam, (X, offs, y) in data_p.items():
        items = by[fam][:CAP]
        ff = FamilyFits([m for m, _ in items], [k for _, k in items])
        out[fam] = np.array([ff.row(i) for i in offs])
    return out


def synthetic_data():
    """Same 8 synthetic test protocols (and body starts) as the LLM experiment."""
    protos = llm.synthetic_protocols()
    data, truth = {}, {}
    for sp, fams in protos.items():
        everything = [m for msgs, _, _ in fams.values() for m in msgs]
        corpus = llm.corpus_stats(everything)
        data[sp], truth[sp] = {}, {}
        for f, (msgs, edges, body_start) in fams.items():
            X, offs = v2.family_rows(msgs, corpus, body_start)
            if not offs:
                continue
            ff = FamilyFits(msgs[:CAP], [0] * len(msgs[:CAP]))      # one session, generation order
            T = np.array([ff.row(i) for i in offs])
            votes = np.zeros(MAXLEN + 1); reach = np.zeros(MAXLEN + 1)
            for m, cuts in zip(msgs, edges):
                votes[[c for c in cuts if c < MAXLEN]] += 1
                reach[1:min(len(m), MAXLEN)] += 1
            y = np.array([votes[o] >= 0.5 * max(1, reach[o]) for o in offs])
            data[sp][f] = (X, T, offs, y)
            truth[sp][f] = (msgs, edges, corpus)
    return data, truth


# ---------------------------------------------------------------- model (same procedure as learned-v2)

def train(data, train_protos):
    X, y, w = v2.stack(data, train_protos)
    stage1 = v2.fit(X, y, w)
    oof = {}
    for inner in train_protos:
        model = v2.fit(*v2.stack(data, [p for p in train_protos if p != inner]))
        for fam, (Xf, offs, yf) in data[inner].items():
            oof[(inner, fam)] = model.predict_proba(Xf)[:, 1]
    X2 = np.vstack([v2.neighbour_features(v[0], oof[(p, fam)]) for p in train_protos for fam, v in data[p].items()])
    stage2 = v2.fit(X2, y, w)
    p2 = stage2.predict_proba(X2)[:, 1]
    t = max(np.arange(0.2, 0.71, 0.05), key=lambda t: v2._f1(y, p2 >= t, w))
    return stage1, stage2, float(t)


def predict(model, X):
    stage1, stage2, t = model
    return stage2.predict_proba(v2.neighbour_features(X, stage1.predict_proba(X)[:, 1]))[:, 1]


def main():
    (OUT / 'families').mkdir(parents=True, exist_ok=True)
    base, typed = {}, {}
    for p in PROTOS:
        base[p] = v2.load_protocol(p)
        T = real_typed(p, base[p])
        typed[p] = {fam: (np.hstack([X, T[fam]]), offs, y) for fam, (X, offs, y) in base[p].items()}
        print(p, 'families', len(base[p]), 'rows', sum(len(v[1]) for v in base[p].values()), flush=True)
    sdata, struth = synthetic_data()
    print('synthetic families', sum(len(f) for f in sdata.values()), flush=True)
    manifest = {(e['protocol'], e['family']): e for e in json.load(open(ROOT / 'dol/llm-varying-boundaries/manifest.json'))}

    # single-feature separation on var|var rows (both bytes vary inside the family), real protocols
    names = [f'{kind}{w}:{fit}' for kind, ws in (('end', ENDING), ('start', STARTING), ('span', [f'{a}+{b}' for a, b in SPANNING]), ('spanminus', ['']))
             for w in ws for fit in FITS]
    rows, labels = [], []
    for p in PROTOS:
        for fam, (X, offs, y) in typed[p].items():
            nx = X.shape[1] - len(names)
            varvar = (X[:, 2] > 1e-9) & (X[:, 3] > 1e-9)   # family entropy of bytes i-1 and i (v2 window i-3..i+2)
            rows.append(X[varvar, nx:]); labels.append(y[varvar])
    R, Y = np.vstack(rows), np.concatenate(labels)
    aucs = sorted(((max(roc_auc_score(Y, R[:, k]), 1 - roc_auc_score(Y, R[:, k])), names[k]) for k in range(R.shape[1]) if R[:, k].std() > 0), reverse=True)
    lines = [f'var|var rows {len(Y)} (edge share {Y.mean():.2f}); best single typed-fit features, ROC AUC (direction-free):']
    lines += [f'  {n:24s} {a:.3f}' for a, n in aucs[:12]]

    nbase = next(iter(next(iter(base.values())).values()))[0].shape[1]

    def select(train_protos):
        """Columns to keep: all v2 columns + the TOPK typed columns ranked on the training protocols."""
        if not TOPK:
            return None
        Rt = np.vstack([X[(X[:, 2] > 1e-9) & (X[:, 3] > 1e-9), nbase:] for p in train_protos for X, _, _ in typed[p].values()])
        Yt = np.concatenate([y[(X[:, 2] > 1e-9) & (X[:, 3] > 1e-9)] for p in train_protos for X, _, y in typed[p].values()])
        auc = [max(roc_auc_score(Yt, Rt[:, k]), 1 - roc_auc_score(Yt, Rt[:, k])) if Rt[:, k].std() > 0 else 0.5 for k in range(Rt.shape[1])]
        return np.concatenate([np.arange(nbase), nbase + np.argsort(auc)[::-1][:TOPK]])

    def view(cols):
        return typed if cols is None else {p: {f: (X[:, cols], o, y) for f, (X, o, y) in fams.items()} for p, fams in typed.items()}

    results = {}
    for held in ([] if SYNTH_ONLY else PROTOS):
        cols = select([p for p in PROTOS if p != held])
        data = view(cols)
        model = train(data, [p for p in PROTOS if p != held])
        fams = {}
        for fam, (X, offs, y) in data[held].items():
            q = predict(model, X)
            fams[fam] = {'field_hypotheses': [{'start': o, 'length': 0} for o, s in zip(offs, q) if s >= model[2]]}
        path = OUT / 'families' / held / f'05_families.exp-typed{SUFFIX}.json'
        path.parent.mkdir(exist_ok=True)
        json.dump(fams, open(path, 'w'))
        results[held] = {'typed': bench.score_protocol(B / held / 'data', ANN / f'{held}.jsonl', str(path)),
                         'v2': bench.score_protocol(B / held / 'data', ANN / f'{held}.jsonl', llm.V2_FILE),
                         'threshold': model[2]}
        results[held]['region'] = region_scores(held, fams, manifest)
        print(held, 'v2', results[held]['v2']['f1'], 'typed', results[held]['typed']['f1'], flush=True)

    # synthetic: models trained on all 14 real protocols
    cols_all = select(list(PROTOS))
    model_typed = train(view(cols_all), list(PROTOS))
    model_base = train(base, list(PROTOS))
    for sp, fams in sdata.items():
        items = defaultdict(list)
        for f, (X, T, offs, y) in fams.items():
            XT = np.hstack([X, T]) if cols_all is None else np.hstack([X, T])[:, cols_all]
            e_typed = {o for o, s in zip(offs, predict(model_typed, XT)) if s >= model_typed[2]}
            q_base = predict(model_base, X)
            e_base = {o for o, s in zip(offs, q_base) if s >= model_base[2]}
            msgs, edges, corpus = struth[sp][f]
            # varying regions computed on the generated data (they depend on constant bytes only)
            inside = llm.interior(llm.family_evidence(msgs[:CAP], corpus, offs, q_base, model_base[2])[1])
            for m, cuts in zip(msgs, edges):
                items['typed'].append((set(cuts), e_typed, inside, len(m)))
                items['v2'].append((set(cuts), e_base, inside, len(m)))
        results[sp] = {v: llm.score_messages(items[v]) for v in items}
        print(sp, 'v2', results[sp]['v2']['f1'], 'typed', results[sp]['typed']['f1'], flush=True)

    json.dump(results, open(OUT / f'results{SUFFIX}.json', 'w'), indent=1)
    lines.append('')
    lines.append(f"{'protocol':10s} {'v2':>7s} {'typed':>7s}   region P/R v2 -> typed")
    for p in results:
        r = results[p]
        reg = r['region'] if p in PROTOS else {k: r[k]['region'] for k in ('v2', 'typed')}
        lines.append(f"{p:10s} {r['v2']['f1']:7.3f} {r['typed']['f1']:7.3f}   {reg['v2']['precision']:.2f}/{reg['v2']['recall']:.2f} -> {reg['typed']['precision']:.2f}/{reg['typed']['recall']:.2f}")
    for group, names_ in (([] if SYNTH_ONLY else [('real', PROTOS)]) + [('synthetic', [p for p in results if p.startswith('synth')])]):
        lines.append(f"{'macro ' + group:16s} v2 {np.mean([results[p]['v2']['f1'] for p in names_]):.3f}  typed {np.mean([results[p]['typed']['f1'] for p in names_]):.3f}")
    text = '\n'.join(lines)
    print(text)
    (OUT / f'results{SUFFIX}.txt').write_text(text + '\n', encoding='utf-8')


def region_scores(p, fams, manifest):
    """Per-message P/R inside the varying regions for v2 and typed (same regions as the LLM run)."""
    d = B / p / 'data'
    assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    plen = {int(m['msg_id']): int(m['payload_len']) for m in bench._iter_jsonl(d / '01_messages.jsonl')}
    sets = {'typed': {f: set(e) - {0} for f, e in bench._family_edges(fams).items()},
            'v2': {f: set(e) - {0} for f, e in bench._family_edges(json.load(open(d / llm.V2_FILE))).items()}}
    out = {}
    for v, s in sets.items():
        items = []
        for a in bench._iter_jsonl(ANN / f'{p}.jsonl'):
            if a.get('reviewer') in bench.COARSE_REVIEWERS or int(a['msg_id']) not in plen or not a.get('boundaries'):
                continue
            fam = assign.get(int(a['msg_id']), '')
            items.append((set(a['boundaries']), s.get(fam, set()), llm.interior(manifest.get((p, fam), {}).get('regions', [])), plen[int(a['msg_id'])]))
        out[v] = llm.score_messages(items)['region']
    return out


if __name__ == '__main__':
    main()
