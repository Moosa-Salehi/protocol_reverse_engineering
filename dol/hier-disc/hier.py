"""Hierarchical discriminator refinement (prototype, applied after stage 04's one-level refinement).

Inside every refined family with enough messages, search for a second type byte AFTER the first discriminator, with
the existing label-free rule (detect_global_discriminator on one family: the window whose value best explains the
exact message length, behind the constant / length-field / correlation-id / session-bound / cardinality gates).
The family is split by that value when the rule finds one; small sub-families fold back into the largest sibling.
A fixed-length family cannot be split (its length carries no information), so data bytes do not split a type.

usage (inner loop, no pipeline run): hier.py [variant ...]  scores the families of the saved default runs before and
after the split against the per-message truth types (V-measure, ARI, homogeneity, completeness, family count) on the
14 benchmark protocols and the 4 held-out protocols."""
import dataclasses, json, os, sys
from collections import Counter, defaultdict
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, f'{ROOT}/src')
from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.discriminator_fields import detect_global_discriminator
from protocol_re.inference.tlv import detect_tlv_framing

P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
H = ['synphasor', 'ams', 'doip', 'cnip']


def _ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0.0] * len(xs); i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(pairs):
    if len(pairs) < 3:
        return 0.0
    a = _ranks([x for x, _ in pairs]); b = _ranks([y for _, y in pairs])
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)); va = sum((x - ma) ** 2 for x in a); vb = sum((y - mb) ** 2 for y in b)
    return cov / (va * vb) ** 0.5 if va and vb else 0.0


def split_family(records, start, depth, min_split_messages, min_sub_share, min_structure_mi):
    """(offset relative to `start`, width, value per msg_id) of the second-level discriminator, or None."""
    sliced = []
    for r in records:
        payload = r.payload_hex[2 * start:]
        sliced.append(dataclasses.replace(r, payload_hex=payload, payload_len=len(payload) // 2))
    sliced = [r for r in sliced if r.payload_len > 0]
    if len(sliced) < min_split_messages:
        return None
    # a TLV/BER family's type is its tag sequence (stage 04 keys those by it), not a byte
    if detect_tlv_framing([bytes.fromhex(r.payload_hex) for r in records]) is not None:
        return None
    # A count field (items, registers) explains length better than a type code does: length grows with its value.
    # Such a pick is masked (set constant, which the constant-byte gate then excludes) and the search repeated.
    for _attempt in range(int(os.environ.get('MAX_RETRIES', 4))):
        d = detect_global_discriminator(sliced, {r.msg_id: 'f' for r in sliced}, max_offset=depth)
        if d is None or not d.get('label_free') or d.get('structure_mi', 0.0) < min_structure_mi:
            return None
        o, w = int(d['offset']), int(d['width'])
        pairs = [(int.from_bytes(bytes.fromhex(r.payload_hex)[o:o + w], 'big'), r.payload_len) for r in sliced if r.payload_len >= o + w]
        if abs(spearman(pairs)) < float(os.environ.get('MAX_MONOTONE', 0.8)):
            break
        sliced = [dataclasses.replace(r, payload_hex=r.payload_hex[:2 * o] + '00' * w + r.payload_hex[2 * (o + w):])
                  if r.payload_len >= o + w else r for r in sliced]
    else:
        return None
    values = {}
    for r in sliced:
        b = bytes.fromhex(r.payload_hex)
        values[r.msg_id] = int.from_bytes(b[o:o + w], 'big') if o + w <= len(b) else -1
    counts = Counter(values.values())
    big = [v for v, c in counts.items() if c >= max(min_sub_share * len(values), 5)]
    if len(big) < 2:
        return None
    return o, w, values, big, d


def hierarchical(records, assignments, first_offset, first_width, *, depth=32, min_split_messages=40,
                 min_sub_share=0.05, min_structure_mi=0.2):
    """New family per msg_id, and per-family split decisions."""
    by_id = {r.msg_id: r for r in records}
    members = defaultdict(list)
    for a in assignments:
        if a['family_id'] != 'noise' and a['msg_id'] in by_id:
            members[a['family_id']].append(by_id[a['msg_id']])
    start = first_offset + first_width
    out, decisions = {}, {}
    for fid, recs in sorted(members.items()):
        s = split_family(recs, start, depth, min_split_messages, min_sub_share, min_structure_mi)
        if s is None:
            for r in recs:
                out[r.msg_id] = fid
            continue
        o, w, values, big, d = s
        largest = max(big, key=lambda v: (sum(1 for x in values.values() if x == v), -v))
        for r in recs:
            v = values.get(r.msg_id, largest)
            out[r.msg_id] = f'{fid}.{v if v in big else largest}'
        decisions[fid] = {'offset': start + o, 'width': w, 'sub_families': len(big), 'structure_mi': d.get('structure_mi')}
    return out, decisions


def truth_types(p):
    if p in H:
        return {a['msg_id']: a['type'] for a in map(json.loads, open(f'{ROOT}/dol/heldout/{p}/annotations_typed.jsonl'))}
    return {a['msg_id']: a.get('type') for a in map(json.loads, open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl'))
            if a.get('type')}


def scores(fam, types):
    from sklearn import metrics
    ids = [m for m in types if m in fam and fam[m] != 'noise']
    y = [types[m] for m in ids]; z = [fam[m] for m in ids]
    return dict(v=metrics.v_measure_score(y, z), ari=metrics.adjusted_rand_score(y, z), h=metrics.homogeneity_score(y, z),
                c=metrics.completeness_score(y, z), k=len(set(fam.values()) - {'noise'}), types=len(set(y)))


def run_dir(p):
    return f'{ROOT}/dol/heldout/{p}/runs/zs-full/data' if p in H else f'{ROOT}/dol/final-v4/zs/{p}/data'


if __name__ == '__main__':
    cfg = dict(depth=int(os.environ.get('DEPTH', 32)), min_split_messages=int(os.environ.get('MIN_SPLIT', 40)),
               min_sub_share=float(os.environ.get('MIN_SHARE', 0.05)), min_structure_mi=float(os.environ.get('MIN_SMI', 0.2)))
    print('config', cfg)
    agg = defaultdict(list); out = {}
    for p in P + H:
        d = run_dir(p)
        recs = load_corpus_jsonl(f'{d}/01_messages.jsonl')
        fa = json.load(open(f'{d}/02_family_assignments.json'))
        ref = fa['metadata'].get('discriminator_refinement') or {}
        base = {a['msg_id']: a['family_id'] for a in fa['assignments']}
        types = truth_types(p)
        b = scores(base, types)
        if ref.get('applied'):
            new, dec = hierarchical(recs, fa['assignments'], int(ref['offset']), int(ref['width']), **cfg)
        else:
            new, dec = base, {}
        n = scores(new, types)
        group = 'heldout' if p in H else 'bench'
        agg[group].append((b, n)); out[p] = dict(before=b, after=n, splits=dec)
        print(f"{p:10s} types={b['types']:3d} fams {b['k']:3d}->{n['k']:3d}  V {b['v']:.3f}->{n['v']:.3f}  ARI {b['ari']:.3f}->{n['ari']:.3f}"
              f"  H {b['h']:.2f}->{n['h']:.2f} C {b['c']:.2f}->{n['c']:.2f}  splits={len(dec)} "
              + ' '.join(f"{k}@{v['offset']}x{v['sub_families']}" for k, v in list(dec.items())[:4]))
    for g, rows in agg.items():
        m = lambda i, k: sum(r[i][k] for r in rows) / len(rows)
        print(f"{g:8s} mean V {m(0,'v'):.3f}->{m(1,'v'):.3f}  ARI {m(0,'ari'):.3f}->{m(1,'ari'):.3f}  families {m(0,'k'):.1f}->{m(1,'k'):.1f}")
    json.dump(dict(config=cfg, protocols=out), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hier.json'), 'w'), indent=1, default=str)
