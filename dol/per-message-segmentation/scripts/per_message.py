"""Per-message segmentation for layouts that shift from message to message.

A family has one edge list, so any field after a variable-length field lands at
a different offset in every message, and no fixed edge list can be right (the
fixed-offset ceiling is 0.39 for GOOSE and 0.41 for OPC UA). Two stages, applied
per family on top of learned-v2, each producing edges per message:

  TLV  BER tag-length-value chains (definite lengths, constructed tags descend).
       A family is TLV from offset s when >= 90% of its messages parse exactly to
       their end from s with >= 3 non-empty elements and >= 2 distinct tags; the
       smallest such s is used. Edge
       convention (which of tag / length / value starts are edges) is chosen
       leave-one-protocol-out on the other protocols where TLV fires.
  LP   length / count prefixes. A field of width 1/2/4 (either byte order) at
       offset p whose span (value * unit, unit 1/2/4) fits inside >= 98% of the
       messages, takes >= 3 distinct values, does not run to the message end in
       most messages, and explains message length (entropy of length - span is
       >= 0.5 bit below the entropy of length), and realigning makes the bytes after
       the span >= 1 bit more regular than leaving them at fixed offsets (a real
       prefix is followed by structure; a total length by nothing or a checksum).
       The first such p is used: edges
       at p, p+w and at the span end of each message; inside the span one edge
       per element when unit > 1; the tail after the span is realigned, scored
       with the learned-v2 model as its own virtual family and searched again
       (depth <= 2).
Thresholds are fixed a priori and never tuned on scores. The non-empty/distinct-tag
and realignment conditions were added after a first detection pass fired on
non-TLV families (e.g. Modbus MBAP parsed by chance); only detections, not scores,
were looked at.

Usage: per_message.py   -> results under dol/per-message-segmentation/
"""
import functools
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path('/mnt/d/tez/practical/protocol_re')
OUT = ROOT / 'dol/per-message-segmentation'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


llm = _load('llm_boundaries', ROOT / 'dol/llm-varying-boundaries/scripts/llm_boundaries.py')
v2, bench, B, ANN, PROTOS, MAXLEN, CAP = llm.v2, llm.bench, llm.B, llm.ANN, llm.PROTOS, llm.MAXLEN, llm.CAP

TLV_SHARE, TLV_MIN_ELEMENTS, TLV_MAX_START = 0.9, 3, 64
LP_FIT, LP_MIN_DISTINCT, LP_GAIN_BITS, LP_REALIGN_BITS, LP_MAX_DEPTH = 0.98, 3, 0.5, 1.0, 2
CONVENTIONS = ('T|L|V', 'TL|V', 'TLV')
SYNTH_TAG = os.environ.get('SYNTH_TAG', '')
SYNTH_ONLY = bool(os.environ.get('SYNTH_ONLY'))
LP_CONFIG = os.environ.get('LP_CONFIG')               # json file with tuned LP thresholds (from tune_lp_dev.py)
if LP_CONFIG:
    globals().update(json.load(open(LP_CONFIG))['config'])


# ---------------------------------------------------------------- BER TLV

def parse_tlv(buf, pos, end, depth=0):
    """Elements (tag, len, value, value_end, constructed) covering buf[pos:end] exactly, or None."""
    out = []
    while pos < end:
        tag = pos
        p = pos + 1
        if buf[tag] & 0x1F == 0x1F:                      # multi-byte tag number
            while p < end and buf[p] & 0x80 and p - tag < 4:
                p += 1
            p += 1
        if p >= end:
            return None
        ln = p
        first = buf[p]
        if first < 0x80:
            length, p = first, p + 1
        elif first == 0x80 or first > 0x84:              # indefinite or absurd length
            return None
        else:
            n = first & 0x7F
            if p + 1 + n > end:
                return None
            length, p = int.from_bytes(buf[p + 1:p + 1 + n], 'big'), p + 1 + n
        if p + length > end:
            return None
        constructed = bool(buf[tag] & 0x20) and length > 0
        out.append((tag, ln, p, p + length, constructed))
        if constructed and depth < 8:
            inner = parse_tlv(buf, p, p + length, depth + 1)
            if inner is not None:
                out.extend(inner)
            else:                                          # treat as primitive
                out[-1] = (tag, ln, p, p + length, False)
        pos = p + length
    return out


def tlv_start(msgs):
    sample = msgs[:300]
    upper = min(TLV_MAX_START, min(len(m) for m in sample) - 2)
    for s in range(0, max(upper, 0)):
        ok = 0
        for m in sample:
            elems = parse_tlv(m, s, len(m))
            ok += (elems is not None and len(m) - s >= 8
                   and sum(e[3] > e[2] for e in elems) >= TLV_MIN_ELEMENTS      # non-empty values
                   and len({m[e[0]] for e in elems}) >= 2)                     # more than one tag
        if ok >= TLV_SHARE * len(sample):
            return s
    return None


def tlv_edges(m, s, convention):
    elems = parse_tlv(m, s, len(m))
    if elems is None:
        return None
    edges = {s}
    for tag, ln, val, vend, constructed in elems:
        edges.add(tag)
        if convention == 'T|L|V':
            edges.update((ln, val))
        elif convention == 'TL|V':
            edges.add(val)
        edges.add(vend)
    return edges


# ---------------------------------------------------------------- length prefixes

def _entropy(values):
    _, c = np.unique(values, return_counts=True)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def find_prefix(msgs, start=0, limit=None):
    """First (p, w, little, unit) after `start` that explains the length variation, or None."""
    if len(msgs) < 5:
        return None
    lens = np.array([len(m) for m in msgs])
    if len(set(lens.tolist())) < 3:
        return None
    h_len = _entropy(lens)
    limit = min(limit or llm.SHOW, int(np.percentile(lens, 90)))
    for p in range(start, limit):
        best = None
        for w in (1, 2, 4):
            cover = np.array([len(m) >= p + w for m in msgs])
            if cover.mean() < LP_FIT:
                continue
            for little in ((False,) if w == 1 else (False, True)):
                vals = np.array([int.from_bytes(m[p:p + w], 'little' if little else 'big') if c else -1 for m, c in zip(msgs, cover)])
                for unit in (1, 2, 4):
                    span = vals * unit
                    fits = cover & (span >= 0) & (p + w + span <= lens)
                    if fits.mean() < LP_FIT or len(set(span[fits].tolist())) < LP_MIN_DISTINCT:
                        continue
                    if (p + w + span[fits] == lens[fits]).mean() > 0.5:      # a total-length field, not a prefix
                        continue
                    gain = h_len - _entropy(lens[fits] - span[fits])
                    if gain < LP_GAIN_BITS:
                        continue
                    realign = _realign_gain(msgs, lens, fits, p + w + span)
                    if realign >= LP_REALIGN_BITS and (best is None or realign > best[0]):
                        best = (realign, p, w, little, unit)
        if best:
            return best[1:]
    return None


def _realign_gain(msgs, lens, fits, ends, k_max=8):
    """Mean byte entropy just after the span: at fixed offsets minus realigned at each span end."""
    idx = np.flatnonzero(fits & (lens - ends >= 4))
    if len(idx) < 5:
        return 0.0
    k = int(min(k_max, np.median(lens[idx] - ends[idx])))
    ref = int(np.median(ends[idx]))
    aligned = [_entropy(np.array([msgs[i][ends[i] + j] for i in idx if ends[i] + j < len(msgs[i])])) for j in range(k)]
    fixed = [_entropy(np.array([msgs[i][ref + j] for i in idx if ref + j < len(msgs[i])])) for j in range(k)]
    return float(np.mean(fixed) - np.mean(aligned))


# ---------------------------------------------------------------- per-message edges

class Segmenter:
    def __init__(self, model, corpus):
        self.model, self.corpus = model, corpus

    def v2_edges(self, msgs):
        X, offs = v2.family_rows(msgs, self.corpus, None)
        if not offs:
            return set()
        q = llm.apply_v2(self.model, X)
        return {o for o, s in zip(offs, q) if s >= self.model[2]}

    def lp(self, msgs, fixed, depth=0):
        """Per-message edges after realigning at a length prefix; None where it does not apply."""
        found = find_prefix(msgs) if depth < LP_MAX_DEPTH else None
        if not found:
            return None, None
        p, w, little, unit = found
        per, tails, owners = [None] * len(msgs), [], []
        for k, m in enumerate(msgs):
            if len(m) < p + w:
                continue
            span = int.from_bytes(m[p:p + w], 'little' if little else 'big') * unit
            end = p + w + span
            if end > len(m):
                continue
            edges = {e for e in fixed if e <= p} | {p, p + w, end}
            if unit > 1:
                edges.update(range(p + w, end, unit))
            per[k] = edges
            if end < len(m):
                tails.append(m[end:]); owners.append((k, end))
        if tails:
            tail_fixed = self.v2_edges(tails[:CAP]) if len(tails) >= 3 else set()
            deeper, _ = self.lp(tails, tail_fixed, depth + 1)
            for j, (k, end) in enumerate(owners):
                tail = deeper[j] if deeper is not None and deeper[j] is not None else tail_fixed
                per[k] |= {end + e for e in tail if 0 < e < len(tails[j])}
        return per, found


def segment_family(msgs, fixed, segmenter, convention):
    """(stage, per-message edge sets or None, detail)."""
    s = tlv_start(msgs)
    if s is not None:
        per = []
        for m in msgs:
            e = tlv_edges(m, s, convention)
            per.append(None if e is None else ({x for x in fixed if x < s} | e))
        return 'tlv', per, s
    per, found = segmenter.lp(msgs, fixed)
    if per is not None:
        return 'lp', per, found
    return None, None, None


# ---------------------------------------------------------------- experiment

@functools.cache
def real_inputs(p):
    d = B / p / 'data'
    assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    msgs = {int(m['msg_id']): bytes.fromhex(m['payload_hex']) for m in bench._iter_jsonl(d / '01_messages.jsonl')}
    ann = [a for a in bench._iter_jsonl(ANN / f'{p}.jsonl') if a.get('reviewer') not in bench.COARSE_REVIEWERS
           and int(a['msg_id']) in msgs and a.get('boundaries')]
    fams = defaultdict(list)
    for mid, fam in assign.items():
        if fam != 'noise':
            fams[fam].append(mid)
    fixed = {f: set(e) - {0} for f, e in bench._family_edges(json.load(open(d / llm.V2_FILE))).items()}
    return assign, msgs, ann, fams, fixed


def main():
    OUT.mkdir(exist_ok=True)
    data = {p: v2.load_protocol(p) for p in PROTOS}
    corpora = {p: llm.corpus_stats(llm.real_families(p)[1]) for p in PROTOS}
    manifest = {(e['protocol'], e['family']): e for e in json.load(open(ROOT / 'dol/llm-varying-boundaries/manifest.json'))}
    per_conv, detail = {}, {}
    for held in ([] if SYNTH_ONLY else PROTOS):
        model = llm.train_v2(data, [p for p in PROTOS if p != held])
        seg = Segmenter(model, corpora[held])
        assign, msgs, ann, fams, fixed = real_inputs(held)
        per_conv[held], detail[held] = {}, {}
        for conv in CONVENTIONS:
            pred = {}
            for fam, mids in fams.items():
                fam_msgs = [msgs[m] for m in mids]
                stage, per, info = segment_family(fam_msgs, fixed.get(fam, set()), seg, conv)
                if stage is None:
                    continue
                detail[held][fam] = (stage, str(info), len(mids))
                for mid, e in zip(mids, per):
                    if e is not None:
                        pred[mid] = (stage, e)
            per_conv[held][conv] = pred
        print(held, 'families segmented:', Counter(s for s, _, _ in detail[held].values()), flush=True)

    def score(p, pred, stages):
        assign, msgs, ann, fams, fixed = real_inputs(p)
        items = []
        for a in ann:
            mid = int(a['msg_id']); fam = assign.get(mid, '')
            e = pred[mid][1] if mid in pred and pred[mid][0] in stages else fixed.get(fam, set())
            items.append((set(a['boundaries']), e, llm.interior(manifest.get((p, fam), {}).get('regions', [])), len(msgs[mid])))
        return llm.score_messages(items)

    tlv_protos = [p for p in PROTOS if any(s == 'tlv' for s, _, _ in detail.get(p, {}).values())]
    results, chosen = {}, {}
    for p in ([] if SYNTH_ONLY else PROTOS):
        others = [q for q in tlv_protos if q != p]
        if others:
            chosen[p] = max(CONVENTIONS, key=lambda c: np.mean([score(q, per_conv[q][c], {'tlv'})['f1'] for q in others]))
        else:
            chosen[p] = 'TL|V'                         # a-priori default: header (tag + length) | value
        pred = per_conv[p][chosen[p]]
        results[p] = {'v2': score(p, {}, set()), 'tlv': score(p, pred, {'tlv'}), 'lp': score(p, pred, {'lp'}),
                      'both': score(p, pred, {'tlv', 'lp'}), 'convention': chosen[p],
                      'segmented': {f: list(v) for f, v in detail[p].items()}}
        print(p, chosen[p], {k: results[p][k]['f1'] for k in ('v2', 'tlv', 'lp', 'both')}, flush=True)

    # synthetic test protocols (no TLV inside; the length prefixes are the arrays)
    model = llm.train_v2(data, list(PROTOS))
    for sp, fams in llm.synthetic_protocols().items():
        everything = [m for msgs_, _, _ in fams.values() for m in msgs_]
        seg = Segmenter(model, llm.corpus_stats(everything))
        items = defaultdict(list)
        stages = Counter()
        for f, (fmsgs, edges, body_start) in fams.items():
            X, offs = v2.family_rows(fmsgs, seg.corpus, body_start)
            fixed = {o for o, q in zip(offs, llm.apply_v2(model, X)) if q >= model[2]} if offs else set()
            stage, per, info = segment_family(fmsgs, fixed, seg, 'TL|V')
            stages[stage] += 1
            inside = set()                      # region metrics are not reported for this stage
            for k, (m, cuts) in enumerate(zip(fmsgs, edges)):
                e = per[k] if per is not None and per[k] is not None else fixed
                items['v2'].append((set(cuts), fixed, inside, len(m)))
                items['both'].append((set(cuts), e, inside, len(m)))
        results[sp] = {v: llm.score_messages(items[v]) for v in items}
        results[sp]['stages'] = dict((str(k), v) for k, v in stages.items())
        print(sp, dict(stages), {k: results[sp][k]['f1'] for k in ('v2', 'both')}, flush=True)

    tag = SYNTH_TAG + ('-lptuned' if LP_CONFIG else '')
    json.dump(results, open(OUT / f'results{tag}.json', 'w'), indent=1)
    lines = [f"{'protocol':10s} {'v2':>6s} {'+TLV':>6s} {'+LP':>6s} {'+both':>6s}  conv   families segmented (tlv/lp)"]
    for p in ([] if SYNTH_ONLY else PROTOS):
        r = results[p]; c = Counter(s for s, _, _ in detail[p].values())
        lines.append(f"{p:10s} {r['v2']['f1']:6.3f} {r['tlv']['f1']:6.3f} {r['lp']['f1']:6.3f} {r['both']['f1']:6.3f}  {r['convention']:6s} {c.get('tlv', 0)}/{c.get('lp', 0)} of {len(real_inputs(p)[3])}")
    if not SYNTH_ONLY:
        lines.append(f"{'macro':10s} " + ' '.join(f"{np.mean([results[p][k]['f1'] for p in PROTOS]):6.3f}" for k in ('v2', 'tlv', 'lp', 'both')))
    S = [p for p in results if p.startswith('synth')]
    lines.append('')
    lines.append(f"{'synthetic':10s} {'v2':>6s} {'+both':>6s}  stages")
    for p in S:
        lines.append(f"{p:10s} {results[p]['v2']['f1']:6.3f} {results[p]['both']['f1']:6.3f}  {results[p]['stages']}")
    lines.append(f"{'macro':10s} {np.mean([results[p]['v2']['f1'] for p in S]):6.3f} {np.mean([results[p]['both']['f1'] for p in S]):6.3f}")
    text = '\n'.join(lines)
    print(text)
    (OUT / f'results{tag}.txt').write_text(text + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
