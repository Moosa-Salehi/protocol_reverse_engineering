"""Group-model library: LOPO edge scores per (family, length) group, cached, plus prediction modes.

  data, prs, ctxs = setup(min_group, ctx_feats)
  scores = lopo_scores(tag, data)              # protocol -> list of per-group score arrays (cached)
  pred_msgs(p, scores[p], t, mode)             # msg_id -> edges; mode: 'pure' | 'open'
  choose(...)                                  # shared threshold chosen on the other protocols
"""
import pickle

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier

import qh
import pred
import groups as G

TH = np.round(np.arange(0.05, 0.71, 0.05), 2)
STATE = {}


def setup(min_group=G.MIN_GROUP, ctx_feats=False):
    data = {p: G.build(p, min_group, ctx_feats) for p in qh.PROTOS}
    prs = {p: qh.load(p) for p in qh.PROTOS}
    ctxs = {p: pred.Ctx(prs[p]) for p in qh.PROTOS}
    STATE.update(data=data, prs=prs, ctxs=ctxs)
    return data, prs, ctxs


def hgb(**kw):
    args = dict(max_iter=300, learning_rate=0.06, max_depth=5, l2_regularization=1.0, random_state=0)
    args.update(kw)
    return HistGradientBoostingClassifier(**args)


def stack(data, protos, feat=None):
    X, y, w = [], [], []
    for p in protos:
        gs = [g for g in data[p] if g['y'] is not None and g['nann']]
        tot = sum(g['nann'] * len(g['offs']) for g in gs)
        for g in gs:
            X.append(g['X'] if feat is None else feat(g)); y.append(g['y'])
            w.append(np.full(len(g['offs']), g['nann'] / tot))
    w = np.concatenate(w)
    return np.vstack(X), np.concatenate(y), w * len(w) / w.sum()


def lopo_scores(tag, data, feat=None, **kw):
    if pred.MAXLEN != 256:
        tag = f'{tag}-L{pred.MAXLEN}'
    path = qh.OUT / 'preds' / f'scores-{tag}{qh.SUFFIX}.pkl'
    if path.exists():
        return pickle.load(open(path, 'rb'))
    out = {}
    for p in qh.PROTOS:
        m = hgb(**kw).fit(*stack(data, [q for q in qh.PROTOS if q != p], feat))
        out[p] = [m.predict_proba(g['X'] if feat is None else feat(g))[:, 1] for g in data[p]]
    path.parent.mkdir(exist_ok=True)
    pickle.dump(out, open(path, 'wb'))
    return out


def pred_msgs(p, gscores, t, mode='open'):
    pr, ctx, data = STATE['prs'][p], STATE['ctxs'][p], STATE['data'][p]
    out = {}
    for g, q in zip(data, gscores):
        thr = t[g['fam'], g['len']] if isinstance(t, dict) else t
        e = {o for o, s in zip(g['offs'], q) if s >= thr}
        fam = g['fam']
        for m in g['mids']:
            if m not in pr.ann:
                continue
            if mode == 'open' and fam in ctx.fields07:
                out[m] = pred.apply_layout(ctx, m, pred.gated_open(ctx.fields07[fam], e, len(pr.msgs[m]['payload'])))
            else:
                out[m] = pred.apply_layout(ctx, m, set(e))
    return out


def shared_threshold(scores, mode='open'):
    """Per held-out protocol: threshold maximising the mean F1 of the other protocols."""
    prs = STATE['prs']
    f1 = {p: [qh.score(prs[p], pred_msgs(p, scores[p], t, mode))['f1'] for t in TH] for p in qh.PROTOS}
    res, thr = {}, {}
    for H in qh.PROTOS:
        k = int(np.argmax([np.mean([f1[p][i] for p in qh.PROTOS if p != H]) for i in range(len(TH))]))
        thr[H] = float(TH[k])
        res[H] = qh.score(prs[H], pred_msgs(H, scores[H], TH[k], mode))
    return res, thr, f1


def evaluate(sc, mode='open', strings=True, label='', verbose=False):
    """Shared-threshold LOPO evaluation (threshold per held-out protocol chosen on the other 13),
    optionally with the cached string post-process. Returns per-protocol results."""
    import plans as PL
    import post
    prs = STATE['prs']
    P = {p: PL.plans(p) for p in qh.PROTOS} if strings else None

    def predict(p, t):
        pm = pred_msgs(p, sc[p], t, mode)
        return {m: post.apply_plan(e, P[p][m]) for m, e in pm.items()} if strings else pm
    f1 = {p: [qh.score(prs[p], predict(p, t))['f1'] for t in TH] for p in qh.PROTOS}
    res = {}
    for H in qh.PROTOS:
        k = int(np.argmax([np.mean([f1[p][i] for p in qh.PROTOS if p != H]) for i in range(len(TH))]))
        res[H] = qh.score(prs[H], predict(H, TH[k]))
        res[H]['thr'] = float(TH[k])
    text = qh.report(res, label)
    print(text if verbose else text.splitlines()[-1], flush=True)
    return res


_STRUCT = {}


def structure(kind, p, m, b):
    """Cached per-message structural detections: 'ber' (embedded BER) or 'crc' (CRC blocks)."""
    key = (kind, p, m)
    if key not in _STRUCT:
        if kind == 'ber':
            import post
            _STRUCT[key] = post.embedded_ber(b)
        elif kind == 'crc':
            import crc
            lay = crc.find_layout(b)
            _STRUCT[key] = crc.block_edges(b, lay) if lay else None
    return _STRUCT[key]


def post_strings(p, m, b, e, P):
    import post
    return post.apply_plan(e, P[p][m])


def post_ber(p, m, b, e, P):
    for s, t, inner in structure('ber', p, m, b):
        e = {x for x in e if not s < x < t} | {x for x in inner if s <= x <= t}
    return e


def post_crc(keep_first=False):
    def f(p, m, b, e, P):
        st = structure('crc', p, m, b)
        if not st:
            return e
        edges, spans = st
        for i, (s, t) in enumerate(spans):
            if keep_first and i == 0:
                continue
            e = {x for x in e if not s < x < t}
        return {x for x in e if not any(t < x < t + 2 for s, t in spans)} | edges
    return f


def evaluate_post(sc, posts, mode='open', label='', verbose=False):
    import plans as PL
    prs = STATE['prs']
    P = {p: PL.plans(p) for p in qh.PROTOS}

    def predict(p, t):
        out = {}
        for m, e in pred_msgs(p, sc[p], t, mode).items():
            b = prs[p].msgs[m]['payload']
            for f in posts:
                e = f(p, m, b, e, P)
            out[m] = e
        return out
    f1 = {p: [qh.score(prs[p], predict(p, t))['f1'] for t in TH] for p in qh.PROTOS}
    res = {}
    for H in qh.PROTOS:
        k = int(np.argmax([np.mean([f1[p][i] for p in qh.PROTOS if p != H]) for i in range(len(TH))]))
        res[H] = qh.score(prs[H], predict(H, TH[k]))
        res[H]['thr'] = float(TH[k])
    text = qh.report(res, label)
    print(text if verbose else text.splitlines()[-1], flush=True)
    return res
