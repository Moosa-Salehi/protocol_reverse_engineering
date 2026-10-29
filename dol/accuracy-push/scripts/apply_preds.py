"""Pipeline post-process after stage 07: replace each family's fields with the majority of per-message predictions.

Per-message edges come from dol/accuracy-push/preds/<tag>-<protocol>.pkl (msg_id -> edges). For a few-shot tag,
the labelled messages (<tag>-seen-<protocol>.pkl) contribute their annotated edges (they are given labels).
A family edge e is kept when it appears in >= half of the family's predicted messages that are longer than e.
Fields are rebuilt with dol/global-segmentation/scripts/apply_learned.rebuild (stage-07 records kept where a
field is unchanged or split, `blob` where differently typed fields merge). Families without predictions are
left as stage 07 made them.

Usage: apply_preds.py <data_dir> <protocol> <tag>      (original kept as 05_families.pre-preds.json)
"""
import importlib.util
import json
import pickle
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
OUT = ROOT / 'dol/accuracy-push'
spec = importlib.util.spec_from_file_location('apply_learned', ROOT / 'dol/global-segmentation/scripts/apply_learned.py')
al = importlib.util.module_from_spec(spec)
spec.loader.exec_module(al)


def main():
    d, p, tag = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    pred = pickle.load(open(OUT / 'preds' / f'{tag}-{p}.pkl', 'rb'))
    seen_path = OUT / 'preds' / f'{tag}-seen-{p}.pkl'
    if seen_path.exists():
        seen = set(pickle.load(open(seen_path, 'rb')))
        import os
        ann_dir = OUT / f"annotations-{os.environ['ANNSET']}" if os.environ.get('ANNSET') else ROOT / 'finetuning/cluster-free-dataset/annotations'
        for line in open(ann_dir / f'{p}.jsonl'):
            if line.strip():
                a = json.loads(line)
                if int(a['msg_id']) in seen and a.get('boundaries'):
                    pred[int(a['msg_id'])] = set(int(x) for x in a['boundaries'])
    assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    lens = {}
    for line in open(d / '01_messages.jsonl'):
        if line.strip():
            m = json.loads(line)
            lens[int(m['msg_id'])] = int(m['payload_len'])
    votes, reach, maxlen = defaultdict(Counter), defaultdict(Counter), defaultdict(int)
    for mid, edges in pred.items():
        fam, n = assign.get(mid), lens.get(mid)
        if fam is None or n is None:
            continue
        votes[fam].update(e for e in edges if 0 < e < n)
        reach[fam].update(range(1, n))
        maxlen[fam] = max(maxlen[fam], n)
    path = d / '05_families.json'
    shutil.copy(path, d / '05_families.pre-preds.json')
    fams = json.load(open(path))
    changed = touched = kept_tlv = 0
    for fam, det in fams.items():
        if fam not in votes:
            continue
        edges = sorted(e for e, c in votes[fam].items() if c >= 0.5 * reach[fam][e])
        hyps = sorted(det.get('field_hypotheses', []) or [], key=lambda h: int(h.get('start', 0) or 0))
        tagged = [h for h in hyps if (h.get('attributes') or {}).get('tlv_tag') is not None
                  or (h.get('attributes') or {}).get('tlv_tag_hex') is not None]
        if tagged:
            # BER element fields are matched by their tag, not their offset: keep stage 07's tagged chain and
            # rebuild only the fixed-offset prefix before it with the predicted edges
            s0 = int(tagged[0]['start'])
            prefix = dict(det, field_hypotheses=[h for h in hyps if int(h['start']) + int(h['length']) <= s0])
            rebuilt, k = al.rebuild(prefix, [e for e in edges if e < s0], s0) if prefix['field_hypotheses'] else (prefix, 0)
            rest = [h for h in hyps if int(h['start']) + int(h['length']) > s0]
            fams[fam] = dict(det, field_hypotheses=rebuilt['field_hypotheses'] + rest)
            changed += k; touched += 1; kept_tlv += 1
            continue
        fams[fam], k = al.rebuild(det, edges, maxlen[fam])
        changed += k; touched += 1
    json.dump(fams, open(path, 'w'), indent=2)
    print(f'[+] predicted edges ({tag}): {touched} families rebuilt ({kept_tlv} with their TLV-tagged chain kept), {changed} field changes')


if __name__ == '__main__':
    main()
