"""Predictor building blocks on top of qh (quick harness).

* stage-07 fields per family (dol/global-segmentation/bench-current, the current rules + periodic + TLV)
* learned edge scores (learned-v2 stage 1, trained without the scored protocol:
  dol/global-segmentation/models/stage1-msgsel-excl-<p>.pkl) for any group of messages
* gated combination: stage-07 edges + learned edges inside stage-07 fields of >= 3 bytes
* sub-family refinement: split a family by its most informative discriminator byte / length
"""
import importlib.util
import json
import pickle
from collections import defaultdict

import numpy as np

import qh

ROOT = qh.ROOT
spec = importlib.util.spec_from_file_location('learned_boundaries_v2', ROOT / 'dol/boundary-recall-experiments/scripts/learned_boundaries_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
from protocol_re.inference.tlv import message_layout_edges  # noqa: E402

import os
if os.environ.get('MAXLEN'):          # feature window beyond the original 256 bytes (experiment)
    v2.MAXLEN = int(os.environ['MAXLEN'])
MAXLEN = v2.MAXLEN
_models = {}


def model(p):
    if p not in _models:
        _models[p] = pickle.load(open(qh.GS / 'models' / f'stage1-msgsel-excl-{p}.pkl', 'rb'))
    return _models[p]


class Ctx:
    """Per-protocol context: corpus stats, stage-07 families, framing."""

    def __init__(self, pr):
        self.pr = pr
        if pr.name.startswith('x:'):          # extra training protocol: no stage-07 fields
            d = qh.Path(pr.data_dir)
            self.fams07 = {}
        else:
            d = qh.GS / 'bench-current' / pr.name / 'data'
            self.fams07 = json.load(open(d / '05_families.json'))
        self.framing = json.load(open(d / '04_framing.json')).get('families', {})
        everything = [pr.msgs[m]['payload'] for m in pr.order]
        step = max(1, len(everything) // 8000)
        cM, clens, cfull = v2.to_matrix(everything[::step])
        cvalid, cst = v2.column_stats(cM, clens, cfull)
        self.corpus = (cvalid, cst, cM)
        self.fields07 = {}
        for fam, det in self.fams07.items():
            hy = det.get('field_hypotheses', []) or []
            self.fields07[fam] = sorted((int(h['start']), int(h['start']) + int(h['length'])) for h in hy)

    def body_start(self, fam):
        layouts = (self.framing.get(fam) or {}).get('layout_hypotheses') or [{}]
        b = layouts[0].get('body_start')
        return int(b) if b else None

    def scores(self, mids, fam, cap=v2.CAP):
        """Learned edge probabilities for a group of messages: (offsets, proba)."""
        msgs = [self.pr.msgs[m]['payload'] for m in mids[:cap]]
        X, offs = v2.family_rows(msgs, self.corpus, self.body_start(fam))
        if not offs:
            return [], np.array([])
        return offs, model(self.pr.name)[0].predict_proba(X)[:, 1]


def gated_edges(fields, learned, min_width=3, max_width=None):
    """Stage-07 edges plus learned edges strictly inside stage-07 fields of min..max width."""
    edges = set()
    for a, b in fields:
        edges.update((a, b))
        if b - a >= min_width and (max_width is None or b - a <= max_width):
            edges.update(e for e in learned if a < e < b)
    return edges


def gated_open(fields, learned, n, min_width=3):
    """gated_edges, plus learned edges anywhere past the last stage-07 field (uncovered tail)."""
    edges = gated_edges(fields, learned, min_width)
    end = max((b for a, b in fields), default=0)
    edges.update(e for e in learned if e > end and e < n)
    return edges


LAYOUT_FALLBACK = True      # families without a layout (and noise) in BER protocols
LAYOUT_OVERRIDE = False     # also re-anchor families that have a stage-07 layout


def proto_layouts(ctx):
    """Distinct TLV layouts (by chain start) of the protocol's stage-07 families, most frequent first."""
    if not hasattr(ctx, '_layouts'):
        from collections import Counter
        c = Counter()
        lay = {}
        for det in ctx.fams07.values():
            if isinstance(det, dict) and det.get('message_layout'):
                k = det['message_layout']['chain_start']
                c[k] += 1
                lay[k] = det['message_layout']
        ctx._layouts = [lay[k] for k, _ in c.most_common()]
    return ctx._layouts


def root_start(b, max_start=64):
    """Smallest offset where one constructed BER element spans exactly to the end of the message
    and parses with >= 3 non-empty elements and >= 2 distinct tags; None if there is none."""
    from protocol_re.inference.tlv import parse_ber_elements
    for start in range(0, min(max_start, len(b) - 8)):
        el = parse_ber_elements(b, start)
        if not el:
            continue
        t0, v0, e0, c0 = el[0]
        if c0 and e0 == len(b) and sum(ve > vo for _t, vo, ve, _c in el) >= 3 and len({b[t] for t, _v, _e, _c in el}) >= 2:
            return start
    return None


def apply_layout(ctx, mid, edges):
    det = ctx.fams07.get(ctx.pr.msgs[mid]['family'] or '', {})
    b = ctx.pr.msgs[mid]['payload']
    has = isinstance(det, dict) and det.get('message_layout')
    if proto_layouts(ctx) and ((not has and LAYOUT_FALLBACK) or (has and LAYOUT_OVERRIDE)):
        s0 = root_start(b)
        if s0 is not None:
            return set(message_layout_edges(b, sorted(edges), dict(proto_layouts(ctx)[0], chain_start=s0)))
    if has:
        return set(message_layout_edges(b, sorted(edges), det['message_layout']))
    return edges


# ---------------------------------------------------------------- sub-families

def _H(col):
    _, c = np.unique(col, return_counts=True)
    q = c / c.sum()
    return float(-(q * np.log2(q)).sum())


def split_key(payloads, max_off=24, max_card=32, min_cover=0.95):
    """Best discriminator for a group: byte offset (or 'len') whose values most reduce the summed
    per-offset entropy of the other bytes. Returns (key, gain) or (None, 0)."""
    n = len(payloads)
    lens = np.array([len(b) for b in payloads])
    L = int(min(np.percentile(lens, 90), MAXLEN))
    M = np.full((n, L), -1, dtype=np.int16)
    for i, b in enumerate(payloads):
        k = min(len(b), L)
        M[i, :k] = np.frombuffer(b[:k], dtype=np.uint8)
    base = sum(_H(M[:, j]) for j in range(L))
    cands = [('len', lens)]
    for k in range(min(max_off, L)):
        col = M[:, k]
        if (col >= 0).mean() >= min_cover and 2 <= len(np.unique(col)) <= max_card:
            cands.append((k, col))
    best, gain = None, 0.0
    for key, col in cands:
        vals, inv = np.unique(col, return_inverse=True)
        if not 2 <= len(vals) <= max_card:
            continue
        cond = 0.0
        for v in range(len(vals)):
            rows = inv == v
            w = rows.mean()
            cond += w * sum(_H(M[rows, j]) for j in range(L) if j != key)
        own = _H(M[:, key]) if key != 'len' else 0.0
        g = (base - own - cond) / max(base, 1e-9)
        if g > gain:
            best, gain = key, g
    return best, gain


def refine(pr, mids, depth=2, min_size=30, min_gain=0.15):
    """Recursively split a group of message ids by split_key. Returns list of groups."""
    if depth == 0 or len(mids) < 2 * min_size:
        return [mids]
    payloads = [pr.msgs[m]['payload'] for m in mids[:4000]]
    key, gain = split_key(payloads)
    if key is None or gain < min_gain:
        return [mids]
    groups = defaultdict(list)
    for m in mids:
        b = pr.msgs[m]['payload']
        groups[len(b) if key == 'len' else (b[key] if key < len(b) else -1)].append(m)
    big = [g for g in groups.values() if len(g) >= min_size]
    rest = [m for g in groups.values() if len(g) < min_size for m in g]
    out = []
    for g in big:
        out += refine(pr, g, depth - 1, min_size, min_gain)
    if rest:
        out.append(rest)
    return out
