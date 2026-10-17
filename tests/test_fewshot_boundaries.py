from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference import fewshot_boundaries as fsb


def test_crc16_dnp_check_value():
    # CRC-16/DNP check value for "123456789"
    spec = next(s for s in fsb.CRC_CATALOGUE if s[0] == "DNP")
    assert fsb.crc16(b"123456789", spec) == 0xEA82


def test_crc_blocks_are_found_and_kept_atomic():
    spec = next(s for s in fsb.CRC_CATALOGUE if s[0] == "DNP")
    header = bytes([0x05, 0x64, 0x20, 0xC4, 0x01, 0x00, 0x02, 0x00])
    body = bytes(range(40))
    frame = header + fsb.crc16(header, spec).to_bytes(2, "little")
    for k in range(0, len(body), 16):
        block = body[k:k + 16]
        frame += block + fsb.crc16(block, spec).to_bytes(2, "little")
    assert fsb.crc_layout(frame)[:2] == (8, 16)
    edges = fsb.post_crc(frame, {3, 15, 30})
    assert 15 not in edges and 30 not in edges          # inside data blocks
    assert {8, 10, 26, 28} <= edges                     # header CRC, first block and its CRC


def test_length_prefixed_string_is_one_field():
    msg = b"\x01\x02" + (5).to_bytes(4, "little") + b"hello" + b"\x09"
    edges = fsb.post_strings(msg, {2, 8, 9})
    assert {2, 6, 11} <= edges and not {8, 9} & edges


def test_selection_is_deterministic_and_covers_strata():
    rng = random.Random(1)
    payload = {i: bytes(rng.randrange(256) for _ in range(8 if i < 50 else 300)) for i in range(60)}
    family_of = {i: "a" if i % 2 else "b" for i in payload}
    first = fsb.select_messages(list(payload), family_of, payload, 6)
    assert first == fsb.select_messages(list(payload), family_of, payload, 6)
    assert any(len(payload[m]) == 300 for m in first)    # the long messages carry most bytes: covered first


def test_transfer_follows_shifted_fields():
    a = b"\x10\x20" + b"abc" + b"\x00\x01\x02\x03"
    b = b"\x10\x20" + b"abcdef" + b"\x00\x01\x02\x03"
    edges, _ = fsb.transfer(a, [2, 5, 7], b)
    assert 2 in edges and 8 in edges and 10 in edges


def _synthetic(rng: random.Random, n: int = 400):
    """Two message types; type 1: [op=1][id:2][len:1][value:2]; type 2: [op=2][id:2][count:2][flags:1][crc:1]."""
    order, payload, labels_all, family_of = [], {}, {}, {}
    for i in range(n):
        if i % 2:
            m = bytes([1]) + rng.randrange(65536).to_bytes(2, "big") + bytes([2]) + rng.randrange(65536).to_bytes(2, "big")
            edges = [0, 1, 3, 4, 6]
        else:
            m = bytes([2]) + rng.randrange(65536).to_bytes(2, "big") + rng.randrange(300).to_bytes(2, "big") + bytes([rng.randrange(4), rng.randrange(256)])
            edges = [0, 1, 3, 5, 6, 7]
        order.append(i); payload[i] = m; labels_all[i] = edges; family_of[i] = "family_0"
    return order, payload, labels_all, family_of


def test_predict_split_and_apply_end_to_end(tmp_path):
    rng = random.Random(7)
    training = {}
    for name in ("p1", "p2"):
        order, payload, labels_all, family_of = _synthetic(rng)
        training[name] = fsb.build_rows(order, family_of, payload, {}, labels_all)
    path = tmp_path / "train.npz"
    fsb.save_training_set(path, training)
    X, y, w, n = fsb.load_training_set(path, exclude=["p2"])
    assert n == 1 and len(X) == len(y) == len(w)

    order, payload, labels_all, family_of = _synthetic(rng)
    labelled = {m: labels_all[m] for m in fsb.select_messages(order, family_of, payload, 10)}
    pred, summary = fsb.predict_edges(order, family_of, payload, {}, labelled, path)
    assert summary["labelled_messages"] == 10 and set(pred) == set(order)
    tp = sum(len({e for e in pred[m] if 0 < e < len(payload[m])} & set(labels_all[m])) for m in order)
    total = sum(len([e for e in labels_all[m] if 0 < e < len(payload[m])]) for m in order)
    assert tp / total > 0.8

    moved, split = fsb.split_families(family_of, pred, payload)
    assert split["sub_families"] >= 2                     # the family mixes two layouts
    new_family = {m: moved.get(m, f) for m, f in family_of.items()}
    families = {f: {"field_hypotheses": [{"family_id": f, "start": 0, "length": len(payload[next(m for m in order if new_family[m] == f)]),
                                          "field_type": "blob", "attributes": {}}]} for f in set(new_family.values())}
    summary = fsb.apply_to_families(families, new_family, pred, {m: len(b) for m, b in payload.items()})
    assert summary["families_rebuilt"] == len(families)
    assert all(len(d["field_hypotheses"]) >= 4 for d in families.values())
