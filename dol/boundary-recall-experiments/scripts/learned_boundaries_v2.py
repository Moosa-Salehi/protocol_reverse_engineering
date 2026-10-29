"""Leave-one-protocol-out test of a learned boundary scorer, version 2.

One row per (family, offset). Compared with version 1 the features add:
  * a window of per-offset statistics (i-3 .. i+2) instead of the two neighbours,
  * the same statistics pooled over the whole corpus (a byte that is constant
    inside one family often varies across families),
  * nibble entropies (bitfields / flags), correlation with message length,
  * position relative to the framing body start,
  * family context (size, length variability),
and a second stage that sees the first stage's scores for the neighbouring
offsets (fields have typical widths, so neighbouring edges are not independent).

Usage: learned_boundaries_v2.py [tag]   -> results-learned-<tag>.json
"""
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path('/mnt/d/tez/practical/protocol_re')
B = ROOT / 'dol/benchmark-14-protocols'
ANN = ROOT / 'finetuning/cluster-free-dataset/annotations'
OUT = ROOT / 'dol/boundary-recall-experiments'
spec = importlib.util.spec_from_file_location('bench', ROOT / 'scripts/diagnostics/31_benchmark_message_boundaries.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)

PROTOS = 'modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')
MAXLEN = 256
CAP = 2000
TAG = sys.argv[1] if len(sys.argv) > 1 else 'v2'
STATS = ('H', 'distinct', 'top', 'zero', 'mean', 'ascii', 'Hhi', 'Hlo', 'lencorr')


def to_matrix(msgs):
    lens = np.array([min(len(m), MAXLEN) for m in msgs])
    M = np.zeros((len(msgs), MAXLEN), dtype=np.uint8)
    for i, m in enumerate(msgs):
        M[i, :lens[i]] = np.frombuffer(m[:MAXLEN], dtype=np.uint8)
    full = np.array([len(m) for m in msgs], dtype=float)
    return M, lens, full


def _entropy(counts, total, bits):
    p = counts[counts > 0] / total
    return float(-(p * np.log2(p)).sum() / bits)


def column_stats(M, lens, full):
    valid = np.arange(MAXLEN)[None, :] < lens[:, None]
    out = {name: np.zeros(MAXLEN) for name in STATS}
    out['cov'] = valid.mean(0)
    for j in range(MAXLEN):
        v = M[valid[:, j], j]
        if v.size == 0:
            continue
        c = np.bincount(v, minlength=256)
        out['H'][j] = _entropy(c, v.size, 8)
        out['distinct'][j] = min(1.0, (c > 0).sum() / min(v.size, 256))
        out['top'][j] = c.max() / v.size
        out['zero'][j] = c[0] / v.size
        out['mean'][j] = v.mean() / 255
        out['ascii'][j] = c[32:127].sum() / v.size
        out['Hhi'][j] = _entropy(np.bincount(v >> 4, minlength=16), v.size, 4)
        out['Hlo'][j] = _entropy(np.bincount(v & 15, minlength=16), v.size, 4)
        length = full[valid[:, j]]
        if v.std() > 0 and length.std() > 0:
            out['lencorr'][j] = abs(float(np.corrcoef(v, length)[0, 1]))
    return valid, out


def pair_stats(M, valid, H, i):
    both = valid[:, i]
    a, b = M[both, i - 1], M[both, i]
    change = float((a != b).mean())
    joint = np.bincount(a.astype(np.int32) * 256 + b, minlength=65536)
    hj = _entropy(joint, a.size, 8)
    low = min(H[i - 1], H[i])
    nmi = min(1.0, max(0.0, H[i - 1] + H[i] - hj) / low) if low > 1e-6 else 0.0
    return change, nmi


def family_rows(msgs, corpus, body_start):
    msgs = msgs[:CAP]
    n = len(msgs)
    M, lens, full = to_matrix(msgs)
    valid, st = column_stats(M, lens, full)
    cvalid, cst, cM = corpus
    med = float(np.median(full))
    distinct_lengths = len(set(full.tolist()))
    get = lambda arr, j: float(arr[j]) if 0 <= j < MAXLEN else 0.0
    rows, offs = [], []
    for i in range(1, int(lens.max())):
        if valid[:, i].sum() < max(3, 0.05 * n):
            break
        change, nmi = pair_stats(M, valid, st['H'], i)
        cchange, cnmi = pair_stats(cM, cvalid, cst['H'], i) if cvalid[:, i].sum() >= 3 else (0.0, 0.0)
        row = []
        for name in STATS:  # family window i-3 .. i+2
            row += [get(st[name], j) for j in range(i - 3, i + 3)]
        for name in ('H', 'distinct', 'top', 'zero', 'Hhi', 'Hlo', 'lencorr'):  # corpus window i-2 .. i+1
            row += [get(cst[name], j) for j in range(i - 2, i + 2)]
        row += [
            st['H'][i] - st['H'][i - 1], abs(st['H'][i] - st['H'][i - 1]),
            cst['H'][i] - cst['H'][i - 1], abs(cst['H'][i] - cst['H'][i - 1]),
            change, nmi, cchange, cnmi,
            st['cov'][i], get(st['cov'], i - 1) - st['cov'][i], st['cov'][i] - get(st['cov'], i + 1),
            cst['cov'][i], get(cst['cov'], i - 1) - cst['cov'][i],
            float(st['H'][i - 1] < 1e-9), float(st['H'][i] < 1e-9),
            float(cst['H'][i - 1] < 1e-9), float(cst['H'][i] < 1e-9),
            i % 2 == 0, i % 4 == 0, min(i, 64) / 64, i / max(med, 1), (med - i) / max(med, 1),
            float(body_start is not None), float(body_start is not None and i == body_start),
            float(body_start is not None and i > body_start),
            ((i - body_start) % 2 == 0) if body_start is not None else 0.0,
            min((i - body_start), 64) / 64 if body_start is not None and i >= body_start else -1.0,
            np.log2(n) / 15, min(distinct_lengths, 32) / 32, min(med, 512) / 512,
        ]
        rows.append(row)
        offs.append(i)
    return np.array(rows, dtype=float), offs


def load_protocol(p):
    d = B / p / 'data'
    assign = {int(x['msg_id']): x['family_id'] for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    framing = json.load(open(d / '04_framing.json')).get('families', {})
    by = defaultdict(list)
    everything = []
    for m in bench._iter_jsonl(d / '01_messages.jsonl'):
        payload = bytes.fromhex(m['payload_hex'])
        everything.append(payload)
        fam = assign.get(int(m['msg_id']))
        if fam and fam != 'noise':
            by[fam].append(payload)
    step = max(1, len(everything) // 8000)
    cM, clens, cfull = to_matrix(everything[::step])
    cvalid, cst = column_stats(cM, clens, cfull)
    votes = defaultdict(lambda: np.zeros(MAXLEN + 1))
    reach = defaultdict(lambda: np.zeros(MAXLEN + 1))
    for r in bench._iter_jsonl(ANN / f'{p}.jsonl'):
        if r.get('reviewer') in bench.COARSE_REVIEWERS:
            continue
        fam = assign.get(int(r['msg_id']))
        if fam is not None:
            edges = [e for e in r['boundaries'][1:-1] if e < MAXLEN]
            votes[fam][edges] += 1
            reach[fam][1:min(r['boundaries'][-1], MAXLEN)] += 1
    fams = {}
    for fam, msgs in by.items():
        if fam not in reach:
            continue
        layouts = (framing.get(fam) or {}).get('layout_hypotheses') or [{}]
        body_start = layouts[0].get('body_start')
        X, offs = family_rows(msgs, (cvalid, cst, cM), int(body_start) if body_start else None)
        if not offs:
            continue
        y = np.array([votes[fam][o] >= 0.5 * max(1, reach[fam][o]) for o in offs])
        fams[fam] = (X, offs, y)
    return fams


def neighbour_features(X, proba):
    """Stage-2 input: the row plus stage-1 scores of offsets i-3 .. i+3 (same family)."""
    pad = np.concatenate([np.zeros(3), proba, np.zeros(3)])
    ctx = np.stack([pad[k:k + len(proba)] for k in range(7)], axis=1)
    return np.hstack([X, ctx])


def fit(X, y, w):
    return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, max_depth=5, l2_regularization=1.0, random_state=0).fit(X, y, sample_weight=w)


def stack(data, protos):
    X = np.vstack([v[0] for p in protos for v in data[p].values()])
    y = np.concatenate([v[2] for p in protos for v in data[p].values()])
    # every protocol counts equally, however many families / offsets it has
    w = np.concatenate([np.full(len(v[1]), 1.0 / sum(len(u[1]) for u in data[p].values())) for p in protos for v in data[p].values()])
    return X, y, w * len(w)


def main():
    data = {}
    for p in PROTOS:
        data[p] = load_protocol(p)
        print(p, 'families', len(data[p]), 'rows', sum(len(v[1]) for v in data[p].values()), flush=True)

    results = {}
    for held in PROTOS:
        train = [p for p in PROTOS if p != held]
        Xtr, ytr, wtr = stack(data, train)
        stage1 = fit(Xtr, ytr, wtr)
        # Stage-1 scores for the training rows must come from models that did not
        # see that protocol, or stage 2 would learn to trust them too much.
        oof = {}
        for inner in train:
            rest = [p for p in train if p != inner]
            model = fit(*stack(data, rest))
            for fam, (X, offs, y) in data[inner].items():
                oof[(inner, fam)] = model.predict_proba(X)[:, 1]
        X2 = np.vstack([neighbour_features(v[0], oof[(p, fam)]) for p in train for fam, v in data[p].items()])
        stage2 = fit(X2, ytr, wtr)
        # Decision threshold: best mean F1 over the training protocols (out-of-fold stage-2 is
        # approximated by stage-2 on out-of-fold stage-1 scores).
        p2 = stage2.predict_proba(X2)[:, 1]
        best_t = max(np.arange(0.2, 0.71, 0.05), key=lambda t: _f1(ytr, p2 >= t, wtr))
        fams = {}
        for fam, (X, offs, y) in data[held].items():
            proba = stage2.predict_proba(neighbour_features(X, stage1.predict_proba(X)[:, 1]))[:, 1]
            fams[fam] = {'field_hypotheses': [{'start': o, 'length': 0} for o, q in zip(offs, proba) if q >= best_t]}
        name = f'05_families.exp-learned-{TAG}.json'
        json.dump(fams, open(B / held / 'data' / name, 'w'))
        results[held] = dict(bench.score_protocol(B / held / 'data', ANN / f'{held}.jsonl', name), threshold=round(float(best_t), 2))
        print(held, results[held]['f1'], 'thr', results[held]['threshold'], flush=True)

    prev = json.load(open(OUT / 'results-cap-scaling.json'))
    print(f"\n{'protocol':10s} {'rules':>7s} {'learned ' + TAG + ' (P / R / F1)':>30s} {'ceiling':>8s}")
    for p in PROTOS:
        r = results[p]
        print(f"{p:10s} {prev[p]['perbyte0.5']['f1']:7.3f} {r['precision']:14.2f} / {r['recall']:.2f} / {r['f1']:.3f} {prev[p]['oracle50']['f1']:8.3f}")
    mean = lambda k: sum(prev[p][k]['f1'] for p in PROTOS) / len(PROTOS)
    print(f"{'macro F1':10s} {mean('perbyte0.5'):7.3f} {'':>23s}{sum(r['f1'] for r in results.values()) / len(PROTOS):.3f} {mean('oracle50'):8.3f}")
    json.dump(results, open(OUT / f'results-learned-{TAG}.json', 'w'), indent=1)


def _f1(y, pred, w):
    tp = (w * (y & pred)).sum()
    fp = (w * (~y & pred)).sum()
    fn = (w * (y & ~pred)).sum()
    return 2 * tp / max(2 * tp + fp + fn, 1e-9)


if __name__ == '__main__':
    main()
