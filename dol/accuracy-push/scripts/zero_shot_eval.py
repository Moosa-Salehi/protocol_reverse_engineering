"""Zero-shot group models (stage 1 = exp02, stage 2 = exp05-s2) on the active annotation set, evaluated with
strings + embedded BER + CRC post-processing in open and pure mode. Usage: [ANNSET=truthconv] zero_shot_eval.py"""
import pickle, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm, plans as PL
data, prs, ctxs = gm.setup()
s1 = gm.lopo_scores('exp02', data)
s2 = pickle.load(open(qh.OUT / 'preds' / f'scores-exp05-s2{qh.SUFFIX}.pkl', 'rb'))
posts = [gm.post_strings, gm.post_ber, gm.post_crc(False)]
best = None
for name, sc in (('stage1', s1), ('stage2', s2)):
    for mode in ('open', 'pure'):
        r = gm.evaluate_post(sc, posts, mode, label=f'{name} {mode} +posts{qh.SUFFIX}', verbose=True)
        macro = sum(v['f1'] for v in r.values()) / len(r)
        if best is None or macro > best[0]:
            best = (macro, name, mode, sc, r)
macro, name, mode, sc, r = best
print(f'BEST {name} {mode} {macro:.3f}')
P = {p: PL.plans(p) for p in qh.PROTOS}
for p in qh.PROTOS:
    out = {}
    for m, e in gm.pred_msgs(p, sc[p], r[p]['thr'], mode).items():
        b = prs[p].msgs[m]['payload']
        for f in posts:
            e = f(p, m, b, e, P)
        out[m] = e
    pickle.dump(out, open(qh.OUT / 'preds' / f'best0{qh.SUFFIX}-{p}.pkl', 'wb'))
