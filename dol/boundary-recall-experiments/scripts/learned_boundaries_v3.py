"""Leave-one-protocol-out test of the learned boundary scorer with synthetic
training protocols (see synthetic_protocols.py). Same features and two-stage
model as version 2; compares real-only, synthetic-only and combined training.

Usage: learned_boundaries_v3.py <n_synthetic> [seed]
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
v2 = _load('learned_boundaries_v2')
synth = _load('synthetic_protocols')
bench, B, ANN, OUT, PROTOS, MAXLEN = v2.bench, v2.B, v2.ANN, v2.OUT, v2.PROTOS, v2.MAXLEN
N_SYNTH = int(sys.argv[1]) if len(sys.argv) > 1 else 200
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 0


def synthetic_dataset(n, seed):
    rng = np.random.default_rng(seed)
    data = {}
    for index in range(n):
        types = synth.generate_protocol(rng)
        everything = [m for messages, _, _ in types for m in messages]
        step = max(1, len(everything) // 8000)
        cM, clens, cfull = v2.to_matrix(everything[::step])
        cvalid, cst = v2.column_stats(cM, clens, cfull)
        fams = {}
        for t, (messages, edges, header_len) in enumerate(types):
            votes = np.zeros(MAXLEN + 1); reach = np.zeros(MAXLEN + 1)
            for message, cuts in zip(messages, edges):
                votes[[c for c in cuts if c < MAXLEN]] += 1
                reach[1:min(len(message), MAXLEN)] += 1
            # the pipeline's framing stage finds the body start only some of the time
            body_start = header_len if rng.random() < 0.7 else None
            X, offs = v2.family_rows(messages, (cvalid, cst, cM), body_start)
            if not offs:
                continue
            fams[f't{t}'] = (X, offs, np.array([votes[o] >= 0.5 * max(1, reach[o]) for o in offs]))
        if fams:
            data[f'synth{index}'] = fams
    return data


def run(config, real, synthetic, synth_share):
    """synth_share: fraction of the total training weight given to synthetic protocols."""
    results = {}
    cached = None
    for held in PROTOS:
        if config == 'synth' and cached is not None:
            # synthetic-only training does not depend on the held-out protocol
            stage1, stage2, best_t = cached
            results[held] = _score(config, real, held, stage1, stage2, best_t)
            continue
        groups = {}
        if config in ('real', 'both'):
            groups.update({p: real[p] for p in PROTOS if p != held})
        if config in ('synth', 'both'):
            groups.update(synthetic)
        names = list(groups)
        def stack(selected):
            X = np.vstack([v[0] for p in selected for v in groups[p].values()])
            y = np.concatenate([v[2] for p in selected for v in groups[p].values()])
            w = []
            n_real = sum(1 for p in selected if not p.startswith('synth')) or 1
            n_syn = sum(1 for p in selected if p.startswith('synth')) or 1
            for p in selected:
                rows = sum(len(u[1]) for u in groups[p].values())
                share = (synth_share / n_syn) if p.startswith('synth') else ((1 - synth_share) / n_real)
                if config != 'both':
                    share = 1.0 / len(selected)
                w += [np.full(len(v[1]), share / rows) for v in groups[p].values()]
            w = np.concatenate(w)
            return X, y, w * len(w) / w.sum()
        Xtr, ytr, wtr = stack(names)
        stage1 = v2.fit(Xtr, ytr, wtr)
        order = np.random.default_rng(1).permutation(len(names))
        oof = {}
        for fold in range(5):
            inside = [names[i] for i in order if i % 5 == fold]
            model = v2.fit(*stack([names[i] for i in order if i % 5 != fold]))
            for p in inside:
                for fam, (X, offs, y) in groups[p].items():
                    oof[(p, fam)] = model.predict_proba(X)[:, 1]
        X2 = np.vstack([v2.neighbour_features(v[0], oof[(p, fam)]) for p in names for fam, v in groups[p].items()])
        stage2 = v2.fit(X2, ytr, wtr)
        p2 = stage2.predict_proba(X2)[:, 1]
        best_t = max(np.arange(0.2, 0.71, 0.05), key=lambda t: v2._f1(ytr, p2 >= t, wtr))
        cached = (stage1, stage2, best_t)
        results[held] = _score(config, real, held, stage1, stage2, best_t)
    return results


def _score(config, real, held, stage1, stage2, best_t):
    fams = {}
    for fam, (X, offs, y) in real[held].items():
        proba = stage2.predict_proba(v2.neighbour_features(X, stage1.predict_proba(X)[:, 1]))[:, 1]
        fams[fam] = {'field_hypotheses': [{'start': o, 'length': 0} for o, q in zip(offs, proba) if q >= best_t]}
    name = f'05_families.exp-learned-v3-{config}.json'
    json.dump(fams, open(B / held / 'data' / name, 'w'))
    return bench.score_protocol(B / held / 'data', ANN / f'{held}.jsonl', name)


def main():
    real = {p: v2.load_protocol(p) for p in PROTOS}
    synthetic = synthetic_dataset(N_SYNTH, SEED)
    rows = sum(len(v[1]) for f in synthetic.values() for v in f.values())
    pos = sum(int(v[2].sum()) for f in synthetic.values() for v in f.values())
    print(f'synthetic protocols {len(synthetic)} families {sum(len(f) for f in synthetic.values())} rows {rows} edge share {pos / rows:.2f}', flush=True)
    real_rows = sum(len(v[1]) for f in real.values() for v in f.values()); real_pos = sum(int(v[2].sum()) for f in real.values() for v in f.values())
    print(f'real rows {real_rows} edge share {real_pos / real_rows:.2f}', flush=True)
    table = {}
    configs = sys.argv[3].split(',') if len(sys.argv) > 3 else ['real', 'synth', 'both']
    for config, share in ((c, {'real': 0, 'synth': 1, 'both': 0.5}[c]) for c in configs):
        table[config] = run(config, real, synthetic, share)
        print(config, 'macro', round(sum(r['f1'] for r in table[config].values()) / len(PROTOS), 3), flush=True)
    prev = json.load(open(OUT / 'results-cap-scaling.json'))
    print(f"\n{'protocol':10s} {'rules':>7s} " + ' '.join(f'{c:>10s}' for c in table) + f" {'ceiling':>8s}")
    for p in PROTOS:
        print(f"{p:10s} {prev[p]['perbyte0.5']['f1']:7.3f} " + ' '.join(f"{table[c][p]['f1']:10.3f}" for c in table) + f" {prev[p]['oracle50']['f1']:8.3f}")
    m = lambda rows: sum(r['f1'] for r in rows.values()) / len(PROTOS)
    print(f"{'macro F1':10s} {sum(prev[p]['perbyte0.5']['f1'] for p in PROTOS) / len(PROTOS):7.3f} " + ' '.join(f'{m(table[c]):10.3f}' for c in table) + f" {sum(prev[p]['oracle50']['f1'] for p in PROTOS) / len(PROTOS):8.3f}")
    json.dump(table, open(OUT / f'results-learned-v3-n{N_SYNTH}.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
