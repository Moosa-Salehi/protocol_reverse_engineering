"""Can anything separate true edges from non-edges between two varying bytes?

Only offsets where both neighbouring bytes vary inside the family are kept
(85% of the learned scorer's missed edges). For each, candidate signals are
computed and scored by ROC AUC (0.5 = useless, 1.0 = perfect), per protocol and
pooled with protocols weighted equally:

  nmi          normalised mutual information of the two bytes (static, already a feature)
  cochange     how much more often the two bytes change *together* between
               consecutive messages of a session than independent bytes would
               (bytes of one number move together: a low byte wraps and the
               high byte steps; separate fields change on their own schedules)
  carry        share of high-byte changes that coincide with a low-byte wrap,
               in big- and little-endian reading (a counter's carry)
  joint_delta  how much smoother the 2-byte value is between consecutive
               messages than its bytes taken separately
  echo         for request/response sessions: both bytes are copied together
               from the previous message of the other direction
"""
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location('v2', HERE / 'learned_boundaries_v2.py')
v2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v2)
B, PROTOS = v2.B, v2.PROTOS


def sequences(p):
    """family -> list of sessions, each a time-ordered list of (direction, bytes); plus all sessions."""
    d = B / p / 'data'
    assign = {int(x['msg_id']): x['family_id'] for x in json.load(open(d / '02_family_assignments.json'))['assignments']}
    by_session = defaultdict(list)
    for m in v2.bench._iter_jsonl(d / '01_messages.jsonl'):
        by_session[m.get('session_id')].append((m.get('timestamp') or 0, int(m['msg_id']), m.get('direction'), bytes.fromhex(m['payload_hex'])))
    fam_seq = defaultdict(list)
    sessions = []
    for rows in by_session.values():
        rows.sort()
        sessions.append(rows)
        per_fam = defaultdict(list)
        for _, mid, direction, payload in rows:
            per_fam[assign.get(mid)].append(payload)
        for fam, msgs in per_fam.items():
            if len(msgs) >= 2:
                fam_seq[fam].append(msgs)
    return fam_seq, sessions, assign


def signals(seqs, i):
    """Signals for the edge between byte i-1 and byte i, from consecutive messages of one family."""
    a_ch = b_ch = both = n = 0
    carry_be = carry_le = hi_be = hi_le = 0
    d_joint, d_a, d_b = [], [], []
    for msgs in seqs:
        for x, y in zip(msgs, msgs[1:]):
            if len(x) <= i or len(y) <= i:
                continue
            n += 1
            ca, cb = x[i - 1] != y[i - 1], x[i] != y[i]
            a_ch += ca; b_ch += cb; both += ca and cb
            if ca:  # big-endian: i-1 is the high byte, i the low byte
                hi_be += 1
                carry_be += (y[i] < x[i])
            if cb:  # little-endian: i is the high byte
                hi_le += 1
                carry_le += (y[i - 1] < x[i - 1])
            jx, jy = x[i - 1] * 256 + x[i], y[i - 1] * 256 + y[i]
            d_joint.append(abs(jy - jx)); d_a.append(abs(int(y[i - 1]) - x[i - 1])); d_b.append(abs(int(y[i]) - x[i]))
    if n < 5 or not a_ch or not b_ch:
        return None
    pa, pb = a_ch / n, b_ch / n
    cochange = (both / n) / max(pa * pb, 1e-9)
    carry = max(carry_be / max(hi_be, 1), carry_le / max(hi_le, 1))
    joint = np.median(d_joint) / 65535
    separate = (np.median(d_a) + np.median(d_b)) / 2 / 255
    joint_delta = separate - joint
    return [cochange, carry, joint_delta]


def echo_signal(sessions, assign, fam, i):
    """Share of messages of `fam` whose bytes i-1..i equal the same bytes of the previous
    other-direction message, minus the share for each byte alone (both copied together)."""
    both = single = n = 0
    for rows in sessions:
        prev = None
        for _, mid, direction, payload in rows:
            if assign.get(mid) == fam and prev is not None and prev[0] != direction and len(prev[1]) > i and len(payload) > i:
                n += 1
                eq_a, eq_b = payload[i - 1] == prev[1][i - 1], payload[i] == prev[1][i]
                both += eq_a and eq_b
                single += (eq_a + eq_b) / 2
            prev = (direction, payload)
    if n < 5:
        return None
    return both / n - (single / n) ** 2


def main():
    pooled = defaultdict(list)
    print(f"{'protocol':10s} {'rows':>5s} {'edges':>5s}  " + ' '.join(f'{s:>11s}' for s in ('nmi', 'cochange', 'carry', 'joint_delta', 'echo')))
    for p in PROTOS:
        data = v2.load_protocol(p)
        fam_seq, sessions, assign = sequences(p)
        rows = []
        for fam, (X, offs, y) in data.items():
            for k, (o, t) in enumerate(zip(offs, y)):
                if X[k, 2] < 1e-9 or X[k, 3] < 1e-9:
                    continue  # keep var|var only
                sig = signals(fam_seq.get(fam, []), o)
                if sig is None:
                    continue
                e = echo_signal(sessions, assign, fam, o)
                rows.append((t, X[k, 87], *sig, np.nan if e is None else e))
        if len(rows) < 10:
            print(f'{p:10s} {len(rows):5d}  too few var|var rows with session order')
            continue
        R = np.array(rows, dtype=float)
        y = R[:, 0].astype(bool)
        out = []
        for col in range(1, R.shape[1]):
            mask = ~np.isnan(R[:, col])
            if y[mask].all() or (~y[mask]).all() or mask.sum() < 10:
                out.append(float('nan')); continue
            # an edge should show LOW dependence, so score with the negated signal
            out.append(roc_auc_score(y[mask], -R[mask, col]))
            pooled[col].append(out[-1])
        print(f'{p:10s} {len(R):5d} {int(y.sum()):5d}  ' + ' '.join(f'{v:11.2f}' for v in out))
    print(f"{'mean AUC':10s} {'':>11s}  " + ' '.join(f'{np.nanmean(pooled[c]):11.2f}' for c in range(1, 6)))


if __name__ == '__main__':
    main()
