"""Global segmentation search over typed field hypotheses (idea 1).

learned-v2 decides every offset on its own (score >= threshold). Here a family is
segmented as a whole: candidate fields [s, e) are scored by a field classifier and
dynamic programming picks the tiling of [0, L) with the largest summed field
weight (PVParser / BinaryInferno style: compare complete segmentations instead of
committing to boundaries one at a time).

  edge model    learned-v2 stage 1 (same rows and features). Its scores are always
                out of sample: for the held-out protocol H from a model trained
                without H, for a training protocol P from a model trained without
                H and P (nested), so the field model learns how far to trust them.
  candidates    widths 1..8 at every offset, wider blobs (10..128), and a field
                from s to the family end L (arrays, strings, tails).
  field label   [s, e) is exactly one annotated field (s and min(e, len) are edges,
                no edge between) in >= half the annotated messages that reach s.
  features      edge scores at s, at e and inside; byte statistics inside and next
                to the field; typed fits (length / counter / range / smooth / joint);
                IEEE float plausibility; contextual entropy-profile divergence.
  search        weight(field) = logit(p) + beta, max-weight tiling by DP; edges are
                the field starts. beta is chosen on the training protocols with
                out-of-fold field scores (4 protocol groups), never on the held-out one.

Variants (all leave-one-protocol-out over the 14 benchmark protocols):
  stage1     edge model alone, threshold chosen on the training protocols
  dp-edge    DP with a field model that only sees the edge-score features
  dp-full    DP with all field features
Scores: official per-message scorer (scripts/diagnostics/31_benchmark_message_boundaries.py).

Usage: global_seg.py            -> dol/global-segmentation/{results.json,results.txt,families/}
"""
import importlib.util
import json
import pickle
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path('/mnt/d/tez/practical/protocol_re')
OUT = ROOT / 'dol/global-segmentation'
SCRIPTS = ROOT / 'dol/boundary-recall-experiments/scripts'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v2 = _load('learned_boundaries_v2', SCRIPTS / 'learned_boundaries_v2.py')
typed = _load('typed_fields', ROOT / 'dol/typed-field-hypotheses/scripts/typed_fields.py')
bench, B, ANN, PROTOS, MAXLEN, CAP = v2.bench, v2.B, v2.ANN, v2.PROTOS, v2.MAXLEN, v2.CAP
import os
if os.environ.get('PROTOS'):
    PROTOS = os.environ['PROTOS'].split(',')
TAG = os.environ.get('TAG', '')              # suffix for result / family files
SELECT = os.environ.get('SELECT', 'family')   # family: family-level edge F1; msg: families weighted by annotated messages
THRESHOLDS = np.arange(0.05, 0.71, 0.05) if os.environ.get('WIDE_THR') else np.arange(0.2, 0.71, 0.05)

W_TYPED = tuple(range(1, 9))
W_BLOB = (10, 12, 16, 20, 24, 32, 48, 64, 96, 128)
N_CTX = 24              # context bytes per family for the profile signal
GROUPS = 4              # protocol groups for out-of-fold field scores (beta choice)
BETAS = np.arange(-4.0, 8.01, 0.5)
V2_FILE = '05_families.exp-learned-v2.json'


# ---------------------------------------------------------------- per-family evidence

def _H(counts):
    counts = counts[counts > 0]
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


def context_signal(M, lens, n_off):
    """ctx[i] for the edge between bytes i-1 and i: max over context bytes c of
    |H(a|c)/H(a) - H(b|c)/H(b)| (bytes of one field react alike to a context)."""
    valid = np.arange(MAXLEN)[None, :] < lens[:, None]
    full_cols = [j for j in range(min(n_off, MAXLEN)) if valid[:, j].mean() >= 0.9]
    cands = []
    for j in full_cols:
        u, inv = np.unique(M[:, j], return_inverse=True)
        if 2 <= len(u) <= 64:
            cands.append((_H(np.bincount(inv)), j, inv.ravel()))
    cands = sorted(cands, reverse=True)[:N_CTX]
    ctx = np.full(MAXLEN + 1, -1.0)
    for i in range(1, n_off):
        rows = valid[:, i]
        if rows.sum() < 20:
            continue
        a, b = M[rows, i - 1].astype(np.int64), M[rows, i].astype(np.int64)
        Ha, Hb = _H(np.bincount(a)), _H(np.bincount(b))
        if Ha < 1e-9 or Hb < 1e-9:
            continue
        best = 0.0
        for Hc, j, inv in cands:
            if abs(j - i) <= 2 or abs(j - (i - 1)) <= 2:
                continue
            c = inv[rows]
            ha = _H(np.bincount(c * 256 + a)) - Hc
            hb = _H(np.bincount(c * 256 + b)) - Hc
            best = max(best, abs(ha / Ha - hb / Hb))
        ctx[i] = best
    return ctx


def float_score(M, lens, s, w):
    """Share of messages whose [s, s+w) reads as a plausible IEEE float (best byte order)."""
    rows = lens >= s + w
    if rows.sum() < 5:
        return 0.0
    raw = np.ascontiguousarray(M[rows, s:s + w])
    if len(np.unique(raw, axis=0)) < 3:
        return 0.0
    best = 0.0
    lo, hi = (1e-6, 1e7) if w == 4 else (1e-9, 1e12)
    for order in ('>', '<'):
        with np.errstate(all='ignore'):
            v = np.abs(raw.view(f'{order}f{w}').ravel().astype(np.float64))
        ok = (v == 0) | ((v > lo) & (v < hi))
        best = max(best, float(ok.mean()))
    return best


def family_evidence(msgs, sessions, offs):
    """Byte statistics, typed fits, floats and context signal for one family."""
    msgs = msgs[:CAP]
    M, lens, full = v2.to_matrix(msgs)
    valid, st = v2.column_stats(M, lens, full)
    L = max(offs) + 1
    ff = typed.FamilyFits(msgs, sessions[:CAP])
    ctx = context_signal(M, lens, L)
    return dict(M=M, lens=lens, st=st, cov=st['cov'], L=L, ff=ff, ctx=ctx)


def candidates(L):
    out = []
    for s in range(L):
        for w in W_TYPED + W_BLOB:
            if s + w < L:
                out.append((s, s + w))
        out.append((s, L))
    return sorted(set(out))


def field_labels(ann, cands, L):
    """Majority label per candidate from the family's annotated messages."""
    if not ann:
        return None
    ann = ann[:CAP]
    n = len(ann)
    isB = np.zeros((n, MAXLEN + 2), dtype=bool)
    lens = np.zeros(n, dtype=np.int64)
    for k, bounds in enumerate(ann):
        ln = bounds[-1]
        lens[k] = ln
        isB[k, [b for b in bounds if b <= MAXLEN + 1]] = True
        if ln > MAXLEN + 1:
            isB[k, MAXLEN + 1] = True      # treat the cap as an edge for long messages
    C = np.concatenate([np.zeros((n, 1), dtype=np.int64), np.cumsum(isB, axis=1)], axis=1)   # C[:, k] = edges in [0, k)
    lab = np.zeros(len(cands), dtype=bool)
    idx = np.arange(n)
    for c, (s, e) in enumerate(cands):
        reach = np.minimum(lens, MAXLEN + 1) > s
        if reach.sum() == 0:
            continue
        ee = np.minimum(e, np.minimum(lens, MAXLEN + 1))
        ok = isB[:, s] & isB[idx, ee] & ((C[idx, ee] - C[:, s + 1]) == 0)
        lab[c] = ok[reach].mean() >= 0.5
    return lab


def static_features(ev, cands):
    """Edge-score-free part of the candidate rows (computed once per family)."""
    st, cov, L, ff, ctx, M, lens = ev['st'], ev['cov'], ev['L'], ev['ff'], ev['ctx'], ev['M'], ev['lens']
    H = st['H']
    g = lambda a, j: float(a[j]) if 0 <= j < MAXLEN else 0.0
    rows = []
    for s, e in cands:
        w = e - s
        span = H[s:min(e, MAXLEN)]
        const = span < 1e-9
        fits = ff.fits(s, e) if w <= 4 else np.zeros(len(typed.FITS))
        f32 = float_score(M, lens, s, 4) if w == 4 else 0.0
        f64 = float_score(M, lens, s, 8) if w == 8 else 0.0
        ictx = ctx[s + 1:e]
        ictx = ictx[ictx >= 0]
        rows.append([span.mean(), span.max(), span.min(), span[0], span[-1], const.mean(), float(const.all()),
                     float(const.any() and not const.all()), g(H, s - 1), g(H, e),
                     g(st['ascii'], s), st['ascii'][s:min(e, MAXLEN)].mean(), st['zero'][s:min(e, MAXLEN)].mean(),
                     st['Hhi'][s:min(e, MAXLEN)].mean(), st['Hlo'][s:min(e, MAXLEN)].mean(),
                     g(cov, s), g(cov, e - 1) - g(cov, e) if e < MAXLEN else 0.0,
                     *fits, f32, f64,
                     ictx.max() if ictx.size else -1.0, ctx[s], ctx[e] if e <= MAXLEN else -1.0])
    return np.array(rows, dtype=float)


def edge_features(f, edge_p):
    """Rows from the edge scores (edge_p[i - 1] = score of offset i, i = 1..L-1)."""
    cands, L = f['cands'], f['ev']['L']
    p = np.ones(L + 1)
    p[1:L] = edge_p
    lo = np.log(np.clip(p, 1e-4, 1 - 1e-4) / np.clip(1 - p, 1e-4, 1))
    clo = np.concatenate([[0.0], np.cumsum(lo)])            # clo[k] = sum lo[0:k]
    cge = np.concatenate([[0], np.cumsum(p >= 0.5)])
    S = np.array([c[0] for c in cands]); E = np.array([c[1] for c in cands]); W = E - S
    inner_sum = np.where(W > 1, clo[E] - clo[S + 1], 0.0)
    inner_cnt = np.where(W > 1, cge[E] - cge[S + 1], 0)
    inner_max = np.array([p[s + 1:e].max() if e - s > 1 else 0.0 for s, e in cands])
    inner_mean = np.where(W > 1, (np.concatenate([[0.0], np.cumsum(p)])[E] - np.concatenate([[0.0], np.cumsum(p)])[S + 1]) / np.maximum(W - 1, 1), 0.0)
    n = len(f['ev']['lens'])
    return np.column_stack([W, np.log2(W), (E == L).astype(float), S / L, (L - E) / L, np.full(len(S), L / 256),
                            np.full(len(S), np.log2(n) / 15), p[S], p[E], inner_max, inner_mean, inner_cnt, inner_sum,
                            np.minimum(lo[S], 4) + np.minimum(lo[E], 4)])


def field_features(f, edge_p):
    base = edge_features(f, edge_p)
    return base, np.hstack([base, f['static']])


# ---------------------------------------------------------------- data

def load_protocol(p):
    cache = OUT / 'cache' / f'{p}.pkl'
    if cache.exists():
        return pickle.load(open(cache, 'rb'))
    data = v2.load_protocol(p)
    d = B / p / 'data'
    assign = {int(x['msg_id']): x['family_id'] for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    by, ses = defaultdict(list), defaultdict(list)
    for m in bench._iter_jsonl(d / '01_messages.jsonl'):
        fam = assign.get(int(m['msg_id']))
        if fam and fam != 'noise':
            by[fam].append(bytes.fromhex(m['payload_hex']))
            ses[fam].append((m.get('session_id'), m.get('direction')))
    ann = defaultdict(list)
    for r in bench._iter_jsonl(ANN / f'{p}.jsonl'):
        if r.get('reviewer') in bench.COARSE_REVIEWERS or not r.get('boundaries'):
            continue
        fam = assign.get(int(r['msg_id']))
        if fam is not None:
            ann[fam].append(sorted(int(b) for b in r['boundaries']))
    fams = {}
    for fam, (X, offs, y) in data.items():
        ev = family_evidence(by[fam], ses[fam], offs)
        cands = candidates(ev['L'])
        fams[fam] = dict(X=X, offs=offs, y=y, ev=ev, cands=cands, lab=field_labels(ann.get(fam), cands, ev['L']),
                         static=static_features(ev, cands))
    for f in fams.values():
        f['ev'].pop('ff', None)            # typed fits already live in f['static']
    cache.parent.mkdir(parents=True, exist_ok=True)
    pickle.dump(fams, open(cache, 'wb'))
    return fams


# ---------------------------------------------------------------- models

def hgb():
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, max_depth=5, l2_regularization=1.0, random_state=0)


def edge_model(data, protos):
    X = np.vstack([f['X'] for p in protos for f in data[p].values()])
    y = np.concatenate([f['y'] for p in protos for f in data[p].values()])
    w = np.concatenate([np.full(len(f['offs']), 1.0 / sum(len(u['offs']) for u in data[p].values())) for p in protos for f in data[p].values()])
    return hgb().fit(X, y, sample_weight=w * len(w))


def field_rows(data, protos, feats, which):
    X = np.vstack([feats[(p, fam)][which] for p in protos for fam in data[p]])
    y = np.concatenate([data[p][fam]['lab'] for p in protos for fam in data[p]])
    w = np.concatenate([np.full(len(data[p][fam]['cands']), 1.0 / sum(len(u['cands']) for u in data[p].values())) for p in protos for fam in data[p]])
    return X, y, w * len(w)


def dp_edges(cands, logit, L, beta):
    """Max-weight tiling of [0, L); returns field starts > 0."""
    ends = defaultdict(list)
    for (s, e), q in zip(cands, logit):
        ends[e].append((s, q + beta))
    best = np.full(L + 1, -np.inf)
    best[0] = 0.0
    back = np.zeros(L + 1, dtype=np.int64)
    for e in range(1, L + 1):
        for s, q in ends[e]:
            v = best[s] + q
            if v > best[e]:
                best[e], back[e] = v, s
    edges, e = [], L
    while e > 0:
        s = int(back[e])
        if s > 0:
            edges.append(s)
        e = s
    return sorted(edges)


def logit(pr):
    pr = np.clip(pr, 1e-4, 1 - 1e-4)
    return np.log(pr / (1 - pr))


# ---------------------------------------------------------------- scoring

def write_and_score(p, edges_by_fam, name):
    fams = {fam: {'field_hypotheses': [{'start': int(o), 'length': 0} for o in edges]} for fam, edges in edges_by_fam.items()}
    path = OUT / 'families' / p / f'05_families.exp-{name}{TAG}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(fams, open(path, 'w'))
    return bench.score_protocol(B / p / 'data', ANN / f'{p}.jsonl', str(path))


def fast_f1(data, protos, edges):
    """Family-level edge F1 on training protocols (for threshold / beta choice), protocols weighted equally."""
    out = []
    for p in protos:
        tp = fp = fn = 0
        for fam, f in data[p].items():
            pred = set(edges[(p, fam)])
            truth = {o for o, t in zip(f['offs'], f['y']) if t}
            k = NMSG.get((p, fam), 1) if SELECT == 'msg' else 1
            tp += k * len(pred & truth); fp += k * len(pred - truth); fn += k * len(truth - pred)
        out.append(2 * tp / max(2 * tp + fp + fn, 1))
    return float(np.mean(out))


NMSG = {}


def count_messages(p):
    d = B / p / 'data'
    assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    for r in bench._iter_jsonl(ANN / f'{p}.jsonl'):
        if r.get('reviewer') not in bench.COARSE_REVIEWERS and r.get('boundaries') and int(r['msg_id']) in assign:
            key = (p, assign[int(r['msg_id'])])
            NMSG[key] = NMSG.get(key, 0) + 1


def main():
    t0 = time.time()
    data = {}
    for p in PROTOS:
        data[p] = load_protocol(p)
        count_messages(p)
        print(p, 'families', len(data[p]), 'candidates', sum(len(f['cands']) for f in data[p].values()),
              f'{time.time() - t0:.0f}s', flush=True)

    # nested edge scores: es[(H, P)] = scores for protocol P from a model trained without H and P
    pair_models = {}
    def edge_scores(excl, p):
        key = frozenset(excl)
        if key not in pair_models:
            pair_models[key] = edge_model(data, [q for q in PROTOS if q not in key])
        m = pair_models[key]
        return {fam: m.predict_proba(f['X'])[:, 1] for fam, f in data[p].items()}

    results = {}
    for held in PROTOS:
        train = [p for p in PROTOS if p != held]
        es = {p: edge_scores({held, p}, p) for p in train}
        es[held] = edge_scores({held}, held)
        feats = {}
        for p in PROTOS:
            for fam, f in data[p].items():
                feats[(p, fam)] = field_features(f, es[p][fam])

        res = {}
        # stage1: threshold edge scores (threshold chosen on training protocols)
        def thr_edges(t, protos):
            return {(p, fam): [o for o, q in zip(f['offs'], es[p][fam]) if q >= t] for p in protos for fam, f in data[p].items()}
        t1 = max(THRESHOLDS, key=lambda t: fast_f1(data, train, thr_edges(t, train)))
        e1 = thr_edges(t1, [held])
        res['stage1'] = write_and_score(held, {fam: e1[(held, fam)] for fam in data[held]}, 'stage1')

        for which, name in ((0, 'dp-edge'), (1, 'dp-full')):
            # out-of-fold field scores on the training protocols, for choosing beta
            groups = [train[k::GROUPS] for k in range(GROUPS)]
            oof = {}
            for g in groups:
                m = hgb().fit(*field_rows(data, [p for p in train if p not in g], feats, which))
                for p in g:
                    for fam in data[p]:
                        oof[(p, fam)] = logit(m.predict_proba(feats[(p, fam)][which])[:, 1])
            def dp_all(beta, protos, scores):
                return {(p, fam): dp_edges(data[p][fam]['cands'], scores[(p, fam)], data[p][fam]['ev']['L'], beta)
                        for p in protos for fam in data[p]}
            beta = max(BETAS, key=lambda b: fast_f1(data, train, dp_all(b, train, oof)))
            model = hgb().fit(*field_rows(data, train, feats, which))
            sc = {(held, fam): logit(model.predict_proba(feats[(held, fam)][which])[:, 1]) for fam in data[held]}
            ed = dp_all(beta, [held], sc)
            res[name] = write_and_score(held, {fam: ed[(held, fam)] for fam in data[held]}, name)
            res[name]['beta'] = float(beta)
        res['v2'] = bench.score_protocol(B / held / 'data', ANN / f'{held}.jsonl', V2_FILE)
        res['stage1']['threshold'] = float(t1)
        results[held] = res
        print(held, ' '.join(f"{k} {v['f1']:.3f}" for k, v in res.items()), f"beta {res['dp-full']['beta']:+.2f}",
              f'{time.time() - t0:.0f}s', flush=True)
        json.dump(results, open(OUT / f'results{TAG}.json', 'w'), indent=1)

    variants = ('v2', 'stage1', 'dp-edge', 'dp-full')
    lines = [f"{'protocol':10s} " + ' '.join(f'{v:>20s}' for v in variants)]
    for p in PROTOS:
        lines.append(f'{p:10s} ' + ' '.join(f"{results[p][v]['precision']:.2f}/{results[p][v]['recall']:.2f}/{results[p][v]['f1']:.3f}".rjust(20) for v in variants))
    lines.append(f"{'macro F1':10s} " + ' '.join(f"{np.mean([results[p][v]['f1'] for p in PROTOS]):20.3f}" for v in variants))
    lines.append(f"{'macro P/R':10s} " + ' '.join(f"{np.mean([results[p][v]['precision'] for p in PROTOS]):.2f}/{np.mean([results[p][v]['recall'] for p in PROTOS]):.2f}".rjust(20) for v in variants))
    text = '\n'.join(lines)
    print(text)
    (OUT / f'results{TAG}.txt').write_text(text + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
