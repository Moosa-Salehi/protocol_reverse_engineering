"""Pipeline post-process after stage 07: rebuild each family's fields from learned edges.

Edge model: learned-v2 stage 1 trained on the 14 benchmark protocols minus --exclude
(the corpus's own protocol, so nothing about it is learned from labels). Threshold:
message-weighted family-level F1 on the training protocols, from nested out-of-sample
scores (the `-msgsel` variant of global_seg.py).

Fields: cut points are 0, the predicted edges and the family end. A new field that equals a
stage-07 field keeps that record; one inside a stage-07 field is a piece of it (same type);
one spanning several keeps the first field's record if all share a type, else becomes `blob`.
Families with a per-message TLV `message_layout` are left unchanged.

Usage: apply_learned.py <data_dir> --exclude <protocol>
The stage-07 original is kept as 05_families.pre-learned.json.
"""
import argparse
import importlib.util
import json
import pickle
import shutil
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('global_seg', HERE / 'global_seg.py')
gs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gs)
v2 = gs.v2
MODELS = gs.OUT / 'models'


def train(exclude):
    path = MODELS / f'stage1-msgsel-excl-{exclude}.pkl'
    if path.exists():
        return pickle.load(open(path, 'rb'))
    protos = [p for p in gs.PROTOS if p != exclude]
    data = {p: gs.load_protocol(p) for p in protos}
    for p in protos:
        gs.count_messages(p)
    gs.SELECT = 'msg'
    model = gs.edge_model(data, protos)
    es = {}
    for p in protos:   # out-of-sample scores for every training protocol
        m = gs.edge_model(data, [q for q in protos if q != p])
        es[p] = {fam: m.predict_proba(f['X'])[:, 1] for fam, f in data[p].items()}
    def edges(t):
        return {(p, fam): [o for o, q in zip(f['offs'], es[p][fam]) if q >= t] for p in protos for fam, f in data[p].items()}
    thr = float(max(np.arange(0.05, 0.71, 0.05), key=lambda t: gs.fast_f1(data, protos, edges(t))))
    MODELS.mkdir(parents=True, exist_ok=True)
    pickle.dump((model, thr), open(path, 'wb'))
    return model, thr


def family_edges(data_dir, model, thr):
    """Predicted edges per family, features exactly as learned_boundaries_v2.load_protocol."""
    assign = {int(x['msg_id']): x['family_id'] for x in json.load(open(data_dir / '02_family_assignments.json'))['assignments']}
    framing = json.load(open(data_dir / '04_framing.json')).get('families', {})
    by, everything = defaultdict(list), []
    for m in v2.bench._iter_jsonl(data_dir / '01_messages.jsonl'):
        payload = bytes.fromhex(m['payload_hex'])
        everything.append(payload)
        fam = assign.get(int(m['msg_id']))
        if fam and fam != 'noise':
            by[fam].append(payload)
    step = max(1, len(everything) // 8000)
    cM, clens, cfull = v2.to_matrix(everything[::step])
    cvalid, cst = v2.column_stats(cM, clens, cfull)
    out = {}
    for fam, msgs in by.items():
        layouts = (framing.get(fam) or {}).get('layout_hypotheses') or [{}]
        body_start = layouts[0].get('body_start')
        X, offs = v2.family_rows(msgs, (cvalid, cst, cM), int(body_start) if body_start else None)
        if offs:
            q = model.predict_proba(X)[:, 1]
            out[fam] = ([o for o, s in zip(offs, q) if s >= thr], max(offs) + 1)
    return out


def rebuild(details, edges, L):
    hyps = sorted(details.get('field_hypotheses', []) or [], key=lambda h: int(h.get('start', 0) or 0))
    if not hyps:
        return details, 0
    end = max(L, max(int(h['start']) + int(h['length']) for h in hyps))
    cuts = sorted({0, end, *[e for e in edges if 0 < e < end]})
    old = [(int(h['start']), int(h['start']) + int(h['length']), h) for h in hyps]
    fam_id = hyps[0].get('family_id')
    new = []
    for a, b in zip(cuts, cuts[1:]):
        over = [(s, e, h) for s, e, h in old if s < b and e > a]
        same = [h for s, e, h in over if (s, e) == (a, b)]
        if same:
            new.append(same[0]); continue
        if len(over) == 1 or (over and len({h.get('field_type') for _, _, h in over}) == 1):
            h = over[0][2]
            piece = dict(h, start=a, length=b - a)
        else:
            piece = {'family_id': fam_id, 'start': a, 'length': b - a, 'field_type': 'blob', 'confidence': 0.5,
                     'endian': None, 'evidence': {}, 'attributes': {}}
        piece['attributes'] = dict(piece.get('attributes') or {}, learned_edges=True)
        new.append(piece)
    changed = len({(int(h['start']), int(h['length'])) for h in new} ^ {(s, e - s) for s, e, _ in old})
    return dict(details, field_hypotheses=new), changed


def split_wide(details, edges, min_width=3, max_width=None):
    """Gated variant: keep every stage-07 field; split only fields of >= min_width bytes at the
    learned edges strictly inside them (pieces keep the field's record). TLV-layout families unchanged.
    max_width: leave fields longer than this whole (arrays / data blocks stay one field)."""
    if details.get('message_layout'):
        return details, 0
    out, added = [], 0
    for h in details.get('field_hypotheses', []) or []:
        a = int(h.get('start', 0) or 0)
        b = a + int(h.get('length', 0) or 0)
        cuts = sorted(e for e in set(edges) if a < e < b) if b - a >= min_width and (max_width is None or b - a <= max_width) else []
        if not cuts:
            out.append(h)
            continue
        for lo, hi in zip([a] + cuts, cuts + [b]):
            out.append(dict(h, start=lo, length=hi - lo, attributes=dict(h.get('attributes') or {}, learned_split=True, parent_span=[a, b])))
        added += len(cuts)
    return dict(details, field_hypotheses=out), added


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data_dir'); ap.add_argument('--exclude', required=True)
    ap.add_argument('--gate', choices=['off', 'wide'], default='off',
                    help="wide: only split stage-07 fields wider than 2 bytes, never remove stage-07 edges")
    ap.add_argument('--max-width', type=int, default=None, help='with --gate wide: do not split fields longer than this')
    a = ap.parse_args()
    d = Path(a.data_dir)
    model, thr = train(a.exclude)
    pred = family_edges(d, model, thr)
    fams_path = d / '05_families.json'
    shutil.copy(fams_path, d / '05_families.pre-learned.json')
    fams = json.load(open(fams_path))
    total = skipped = 0
    for fam, details in fams.items():
        if details.get('message_layout'):
            skipped += 1; continue
        if fam in pred:
            if a.gate == 'wide':
                fams[fam], k = split_wide(details, pred[fam][0], max_width=a.max_width)
            else:
                fams[fam], k = rebuild(details, *pred[fam])
            total += k
    json.dump(fams, open(fams_path, 'w'), indent=2)
    print(f'[+] learned edges (excl {a.exclude}, threshold {thr:.2f}, gate {a.gate}, max width {a.max_width}): {total} field changes, {skipped} TLV-layout families kept')


if __name__ == '__main__':
    main()
