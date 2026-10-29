"""Cached per-message string plans (post.string_plan) for annotated messages."""
import pickle
import qh
import post


def plans(p):
    path = qh.CACHE / f'plans-{p}{qh.SUFFIX}.pkl'
    if path.exists():
        return pickle.load(open(path, 'rb'))
    pr = qh.load(p)
    out = {m: post.string_plan(pr.msgs[m]['payload']) for m in pr.ann}
    pickle.dump(out, open(path, 'wb'))
    return out
