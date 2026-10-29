"""Diagnostic: stage-1 group model trained on ALL 14 protocols (in-sample) - can the features express the
truth at all? Also leave-one-out with the protocol itself duplicated as its own neighbour is NOT done."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh, gm
data, prs, ctxs = gm.setup()
m = gm.hgb().fit(*gm.stack(data, qh.PROTOS))
sc = {p: [m.predict_proba(g['X'])[:, 1] for g in data[p]] for p in qh.PROTOS}
for mode in ('pure', 'open'):
    res, thr, f1 = gm.shared_threshold(sc, mode)
    print(qh.report(res, f'IN-SAMPLE {mode}'))
