"""Pipeline step after stage 04: split each family by its messages' predicted layout, so every family the later
stages (framing, boundaries, the protocol model and the truth-file evaluator) see has one consistent layout.

Layout signature of a message = its predicted edges below SIG_BYTES (labelled messages use their annotated edges).
Inside a family, messages sharing a signature form a sub-family `<family>_L<k>` when there are >= MIN_SIZE of
them (at most MAX_SPLITS per family, largest first); the rest, and messages without a prediction, stay in
the original family id. Rewrites 02_family_assignments.json (original kept as 02_family_assignments.pre-split.json).

Usage: split_by_layout.py <data_dir> <protocol> <tag>     (predictions: dol/accuracy-push/preds/<tag>-<protocol>.pkl)
"""
import json
import os
import pickle
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
OUT = ROOT / 'dol/accuracy-push'
SIG_BYTES = int(os.environ.get('SPLIT_SIG_BYTES', '32'))
MIN_SIZE = int(os.environ.get('SPLIT_MIN_SIZE', '5'))
MAX_SPLITS = int(os.environ.get('SPLIT_MAX', '40'))
# conservative policy (SPLIT_POLICY=2): skip homogeneous families and BER-structured families, and only split
# off signatures that hold a real share of the family
POLICY = int(os.environ.get('SPLIT_POLICY', '1'))
AGREE = float(os.environ.get('SPLIT_AGREE', '0.97'))
FRAC = float(os.environ.get('SPLIT_FRAC', '0.05'))
sys.path.insert(0, str(OUT))


def load_preds(p, tag):
    pred = pickle.load(open(OUT / 'preds' / f'{tag}-{p}.pkl', 'rb'))
    seen_path = OUT / 'preds' / f'{tag}-seen-{p}.pkl'
    if seen_path.exists():
        seen = set(pickle.load(open(seen_path, 'rb')))
        ann_dir = OUT / f"annotations-{os.environ['ANNSET']}" if os.environ.get('ANNSET') else ROOT / 'finetuning/cluster-free-dataset/annotations'
        for line in open(ann_dir / f'{p}.jsonl'):
            if line.strip():
                a = json.loads(line)
                if int(a['msg_id']) in seen and a.get('boundaries'):
                    pred[int(a['msg_id'])] = set(int(x) for x in a['boundaries'])
    return pred


def agreement(pred, mids, lens):
    """Mean F1 between each message's predicted edges and the family's majority edges."""
    votes, reach = Counter(), Counter()
    for m in mids:
        votes.update(e for e in pred[m] if 0 < e < lens[m]); reach.update(range(1, lens[m]))
    maj = {e for e, c in votes.items() if c >= 0.5 * reach[e]}
    f = []
    for m in mids:
        a = {e for e in pred[m] if 0 < e < lens[m]}; b = {e for e in maj if e < lens[m]}
        f.append(1.0 if not a and not b else 2 * len(a & b) / max(1, len(a) + len(b)))
    return sum(f) / max(1, len(f))


def ber_family(payloads):
    import pred as PR
    sample = payloads[:200]
    return sum(PR.root_start(b) is not None for b in sample) >= 0.6 * max(1, len(sample))


def main():
    d, p, tag = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
    pred = load_preds(p, tag)
    lens, payloads = {}, {}
    for line in open(d / '01_messages.jsonl'):
        if line.strip():
            m = json.loads(line)
            lens[int(m['msg_id'])] = int(m['payload_len'])
            payloads[int(m['msg_id'])] = bytes.fromhex(m['payload_hex'])
    skipped = Counter()
    path = d / '02_family_assignments.json'
    doc = json.load(open(path))
    shutil.copy(path, d / '02_family_assignments.pre-split.json')
    by_fam = defaultdict(list)
    for a in doc['assignments']:
        by_fam[str(a['family_id'])].append(a)
    new_ids, splits = {}, 0
    for fam, rows in by_fam.items():
        if fam == 'noise':
            continue
        sig = {}
        for a in rows:
            mid = int(a['msg_id'])
            if mid in pred:
                n = lens.get(mid, 0)
                sig[mid] = tuple(sorted(e for e in pred[mid] if 0 < e < min(n, SIG_BYTES)))
        counts = Counter(sig.values())
        min_size = MIN_SIZE
        if POLICY == 2:
            mids = list(sig)
            if agreement(pred, mids, lens) >= AGREE:
                skipped['homogeneous'] += 1; continue
            if ber_family([payloads[m] for m in mids]):
                skipped['ber'] += 1; continue
            min_size = max(MIN_SIZE, int(FRAC * len(rows)))
        keep = [s for s, c in counts.most_common(MAX_SPLITS if POLICY != 2 else 8) if c >= min_size]
        if len(keep) <= 1:
            continue
        label = {s: f'{fam}_L{k}' for k, s in enumerate(keep)}
        for mid, s in sig.items():
            if s in label:
                new_ids[mid] = label[s]
        splits += len(keep)
    for a in doc['assignments']:
        mid = int(a['msg_id'])
        if mid in new_ids:
            a['family_id'] = new_ids[mid]
    json.dump(doc, open(path, 'w'))
    print(f'[+] layout split ({tag}): {len(new_ids)} messages moved into {splits} sub-families '
          f'(signature < {SIG_BYTES} B, policy {POLICY}, skipped {dict(skipped)})')


if __name__ == '__main__':
    main()
