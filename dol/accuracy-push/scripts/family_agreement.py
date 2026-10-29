"""Label-free homogeneity of each family: mean F1 between every message's predicted edges and the family's
majority edges (both restricted to the message length). Usage: [ANNSET=..] family_agreement.py <tag> [protocols]"""
import json, pickle, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import split_by_layout as S
tag = sys.argv[1]
protos = sys.argv[2].split(',') if len(sys.argv) > 2 else 'modbus,bacnet,goose,dnp3,iec104,hart_ip,cip,opcua,ethercat'.split(',')
B = S.ROOT / 'dol/benchmark-14-protocols'


def agreement(pred, mids, lens):
    votes, reach = Counter(), Counter()
    for m in mids:
        votes.update(e for e in pred[m] if 0 < e < lens[m]); reach.update(range(1, lens[m]))
    maj = {e for e, c in votes.items() if c >= 0.5 * reach[e]}
    f = []
    for m in mids:
        a = {e for e in pred[m] if 0 < e < lens[m]}; b = {e for e in maj if e < lens[m]}
        f.append(1.0 if not a and not b else 2 * len(a & b) / max(1, len(a) + len(b)))
    return sum(f) / len(f)


for p in protos:
    pred = S.load_preds(p, tag)
    assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(B / p / 'data/02_family_assignments.json'))['assignments']}
    lens = {int(json.loads(l)['msg_id']): int(json.loads(l)['payload_len']) for l in open(B / p / 'data/01_messages.jsonl') if l.strip()}
    fams = defaultdict(list)
    for m in pred:
        if m in assign and assign[m] != 'noise':
            fams[assign[m]].append(m)
    vals = sorted(((agreement(pred, ms, lens), len(ms), f) for f, ms in fams.items()), key=lambda x: -x[1])
    w = sum(n for _, n, _ in vals)
    print(f"{p:9s} msg-weighted agreement {sum(a * n for a, n, _ in vals) / w:.3f}  families: " + ' '.join(f'{a:.2f}({n})' for a, n, _ in vals[:8]))
