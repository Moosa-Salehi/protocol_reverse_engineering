"""Second-level discriminator chosen by layout agreement (prototype; settings fixed before any run, judged on the
held-out protocols).

For every family whose per-message zero-shot layouts disagree (agreement < FewShotBoundaries.SPLIT_AGREE, the
threshold the pipeline already uses to split families), every candidate type byte after the first discriminator
(or from offset 0 when stage 04 found none) is tried as a split key. Candidates: present in >= 90% of the family's
messages, 2-16 effective values (99% mass), most common value <= 98%, not a length field. The split keeps value
groups with >= SPLIT_MIN_SHARE of the family and >= SPLIT_MIN_SIZE messages (the rest fold into the largest group).
Chosen: the candidate with the largest gain in size-weighted layout agreement, ties to the earliest offset; applied
only when the gain is >= MIN_GAIN.

Layout of a message = its zero-shot edges (stage 04b) below LAYOUT_SPAN bytes; agreement of a group = mean F1 of
each member's layout against the group's majority layout (edges present in >= half of the members reaching them).
usage: layout_select.py   (scores the saved default runs: 14 benchmark + 4 held-out protocols)"""
import json, os, sys
from collections import Counter, defaultdict
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, f'{ROOT}/src'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from protocol_re.config.thresholds import FewShotBoundaries as _FS
from protocol_re.corpus.message_corpus import load_corpus_jsonl
from protocol_re.inference.discriminator_fields import _effective_cardinality, _length_field_match_ratio, _length_relation_share
from protocol_re.inference.tlv import detect_tlv_framing
from hier import P, H, truth_types, scores, run_dir

DEPTH, LAYOUT_SPAN, MIN_GAIN, MIN_COVERAGE, MAX_CARD = 64, 64, 0.05, 0.9, 16


def layout(edges, n):
    return frozenset(e for e in edges if 0 < e < min(n, LAYOUT_SPAN))


def agreement(members, lay, length):
    """Mean F1 of each member's layout against the group's majority layout."""
    reach = Counter(); hits = Counter()
    for m in members:
        for e in range(1, min(length[m], LAYOUT_SPAN)):
            reach[e] += 1
        hits.update(lay[m])
    major = {e for e, c in hits.items() if c * 2 >= reach[e]}
    tot = 0.0
    for m in members:
        a = lay[m]; b = {e for e in major if e < min(length[m], LAYOUT_SPAN)}
        tot += 1.0 if not a and not b else 2 * len(a & b) / (len(a) + len(b))
    return tot / len(members)


def best_split(members, payload, lay, length, start):
    n = len(members)
    base = agreement(members, lay, length)
    if base >= _FS.SPLIT_AGREE:
        return None
    msgs = [payload[m] for m in members]
    if detect_tlv_framing(msgs) is not None:          # a BER family's type is its tag sequence
        return None
    best = None
    for o in range(start, start + DEPTH):
        vals = {m: payload[m][o] for m in members if len(payload[m]) > o}
        if len(vals) < MIN_COVERAGE * n:
            continue
        counts = Counter(vals.values())
        eff = _effective_cardinality(counts, len(vals), 0.01)
        if eff < 2 or eff > MAX_CARD or counts.most_common(1)[0][1] / len(vals) > 0.98:
            continue
        if _length_field_match_ratio(msgs, o, 1) >= 0.85 or _length_relation_share(msgs, o, 1) >= 0.85:
            continue
        keep = [v for v, c in counts.items() if c >= max(_FS.SPLIT_MIN_SHARE * n, _FS.SPLIT_MIN_SIZE)]
        if len(keep) < 2:
            continue
        largest = max(keep, key=lambda v: (counts[v], -v))
        groups = defaultdict(list)
        for m in members:
            v = vals.get(m, largest)
            groups[v if v in keep else largest].append(m)
        gain = sum(len(g) * agreement(g, lay, length) for g in groups.values()) / n - base
        if best is None or gain > best[0] + 1e-9:
            best = (gain, o, dict(groups))
    if best is None or best[0] < MIN_GAIN:
        return None
    return best


def refine(p):
    d = run_dir(p)
    recs = load_corpus_jsonl(f'{d}/01_messages.jsonl')
    payload = {r.msg_id: bytes.fromhex(r.payload_hex) for r in recs}
    length = {m: len(b) for m, b in payload.items()}
    edges = json.load(open(f'{d}/04b_fewshot_edges.json'))['edges']
    lay = {m: layout(edges.get(str(m), []), length[m]) for m in payload}
    fa = json.load(open(f'{d}/02_family_assignments.json'))
    ref = fa['metadata'].get('discriminator_refinement') or {}
    start = int(ref['offset']) + int(ref['width']) if ref.get('applied') else 0
    base = {a['msg_id']: a['family_id'] for a in fa['assignments']}
    members = defaultdict(list)
    for m, f in base.items():
        if f != 'noise' and m in payload:
            members[f].append(m)
    new, dec = dict(base), {}
    for f, ms in sorted(members.items()):
        if len(ms) < 2 * _FS.SPLIT_MIN_SIZE:
            continue
        s = best_split(ms, payload, lay, length, start)
        if s is None:
            continue
        gain, o, groups = s
        for v, g in groups.items():
            for m in g:
                new[m] = f'{f}.{v}'
        dec[f] = (o, len(groups), round(gain, 3))
    return base, new, dec


if __name__ == '__main__':
    print(dict(DEPTH=DEPTH, LAYOUT_SPAN=LAYOUT_SPAN, MIN_GAIN=MIN_GAIN, SPLIT_AGREE=_FS.SPLIT_AGREE,
               SPLIT_MIN_SHARE=_FS.SPLIT_MIN_SHARE, SPLIT_MIN_SIZE=_FS.SPLIT_MIN_SIZE))
    agg = defaultdict(list); out = {}
    for p in H + P:
        base, new, dec = refine(p)
        types = truth_types(p); b = scores(base, types); n = scores(new, types)
        agg['heldout' if p in H else 'bench'].append((b, n)); out[p] = dict(before=b, after=n, splits=dec)
        print(f"{p:10s} types={b['types']:3d} fams {b['k']:3d}->{n['k']:3d}  V {b['v']:.3f}->{n['v']:.3f}  ARI {b['ari']:.3f}->{n['ari']:.3f}"
              f"  H {b['h']:.2f}->{n['h']:.2f} C {b['c']:.2f}->{n['c']:.2f}  splits={len(dec)} "
              + ' '.join(f"{k}@{v[0]}x{v[1]}(+{v[2]})" for k, v in list(dec.items())[:4]))
    for g, rows in agg.items():
        m = lambda i, k: sum(r[i][k] for r in rows) / len(rows)
        print(f"{g:8s} mean V {m(0,'v'):.3f}->{m(1,'v'):.3f}  ARI {m(0,'ari'):.3f}->{m(1,'ari'):.3f}  families {m(0,'k'):.1f}->{m(1,'k'):.1f}")
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'layout_select.json'), 'w'), indent=1)
