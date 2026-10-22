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


def test_zeroshot_threshold_table_and_prediction(tmp_path):
    rng = random.Random(11)
    training = {}
    for name in ("p1", "p2", "p3"):
        order, payload, labels_all, family_of = _synthetic(rng)
        training[name] = fsb.build_rows(order, family_of, payload, {}, labels_all)
    thresholds = fsb.zeroshot_thresholds(training)
    assert set(thresholds) == {"p1", "p2", "p3", "*"}
    path = tmp_path / "train.npz"
    fsb.save_training_set(path, training, thresholds)
    assert fsb.load_zeroshot_threshold(path, exclude=["p2"]) == thresholds["p2"]
    assert fsb.load_zeroshot_threshold(path) == thresholds["*"]
    order, payload, labels_all, family_of = _synthetic(rng)
    pred, summary = fsb.predict_edges_zeroshot(order, family_of, payload, {}, path, posts=[])
    assert summary["mode"] == "zeroshot" and set(pred) == set(order)


def test_shared_layer_transfer_needs_a_long_common_block():
    header = bytes.fromhex("0300001902f080")                     # TPKT + COTP, 7 bytes
    ref = [("known", header + b"\x32\x01\x00\x00\x00\x01", [0, 1, 2, 4, 5, 6, 7, 13])]
    edges, cov, donor = fsb.shared_layer_edges(header + b"\x99\x10\x20", ref)
    assert donor == "known" and {1, 2, 4, 5, 6} <= edges
    edges, cov, donor = fsb.shared_layer_edges(bytes(range(40, 60)), ref)
    assert donor is None and not edges


def test_gated_keeps_stage07_fields_and_splits_only_wide_ones():
    payload_len = {m: 12 for m in range(10)}
    family_of = {m: "f" for m in range(10)}
    pred = {m: {2, 3, 6, 9} for m in range(10)}
    families = {"f": {"field_hypotheses": [
        {"family_id": "f", "start": 0, "length": 2, "field_type": "counter", "attributes": {}},
        {"family_id": "f", "start": 2, "length": 2, "field_type": "constant", "attributes": {}},
        {"family_id": "f", "start": 4, "length": 4, "field_type": "blob", "attributes": {}}]}}
    fsb.apply_gated(families, family_of, pred, payload_len)
    spans = [(h["start"], h["length"]) for h in families["f"]["field_hypotheses"]]
    assert (2, 2) in spans                 # a 2-byte stage-07 field is not split at 3
    assert (4, 2) in spans and (6, 2) in spans
    assert spans[-1][0] + spans[-1][1] == 12 and (8, 1) in spans   # tail past the last stage-07 field


def test_veto_merges_unlikely_stage07_edges_but_keeps_confident_fields() -> None:
    from protocol_re.inference.fewshot_boundaries import veto_unlikely_edges

    hyps = [
        {"start": 0, "length": 2, "field_type": "length", "confidence": 1.0},
        {"start": 2, "length": 1, "field_type": "blob", "confidence": 0.5},
        {"start": 3, "length": 3, "field_type": "blob", "confidence": 0.5},
        {"start": 6, "length": 2, "field_type": "blob", "confidence": 0.5},
    ]
    # edge 2 bounds the confident length field: kept despite a low probability; edge 3 is vetoed; edge 6 is likely
    merged, vetoed = veto_unlikely_edges(hyps, {2: 0.01, 3: 0.01, 6: 0.9}, threshold=0.05)

    assert vetoed == 1
    assert [(h["start"], h["length"]) for h in merged] == [(0, 2), (2, 4), (6, 2)]
