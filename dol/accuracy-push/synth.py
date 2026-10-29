"""Synthetic training groups from the fixed generator (dol/synthetic-generator-fix), same features and
group definition as groups.py: (message type, exact length) groups, majority labels from exact edges."""
import importlib.util
import pickle
from collections import Counter, defaultdict

import numpy as np

import qh
import pred
import groups as G

spec = importlib.util.spec_from_file_location('synth_fixed', qh.ROOT / 'dol/synthetic-generator-fix/synthetic_protocols_fixed.py')
SG = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SG)


def synth_protocol(seed, min_group=G.MIN_GROUP):
    rng = np.random.default_rng(seed)
    types = SG.generate_protocol(rng)
    everything = [m for msgs, _, _ in types for m in msgs]
    step = max(1, len(everything) // 8000)
    cM, clens, cfull = pred.v2.to_matrix(everything[::step])
    cvalid, cst = pred.v2.column_stats(cM, clens, cfull)
    out = []
    for t, (msgs, edges, header_len) in enumerate(types):
        by = defaultdict(list)
        for k, m in enumerate(msgs):
            by[len(m)].append(k)
        parts = [(ln, ks) for ln, ks in by.items() if len(ks) >= min_group]
        rest = [k for ln, ks in by.items() if len(ks) < min_group for k in ks]
        if rest:
            parts.append((None, rest))
        for ln, ks in parts:
            gm_ = [msgs[k] for k in ks[:G.CAPG]]
            X, offs = pred.v2.family_rows(gm_, (cvalid, cst, cM), header_len or None)
            if not offs:
                continue
            c = Counter(e for k in ks for e in edges[k])
            reach = Counter(o for k in ks for o in range(1, len(msgs[k])))
            y = np.array([c[o] >= 0.5 * max(1, reach[o]) for o in offs])
            out.append(dict(fam=f'type{t}', len=ln, mids=[], X=X, offs=offs, y=y, nann=len(ks)))
    return out


def synth_set(n, seed0=7000):
    path = qh.CACHE / f'synth-{n}-{seed0}.pkl'
    if path.exists():
        return pickle.load(open(path, 'rb'))
    out = {f'synth{i}': synth_protocol(seed0 + i) for i in range(n)}
    pickle.dump(out, open(path, 'wb'))
    return out
