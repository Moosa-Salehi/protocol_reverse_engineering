from __future__ import annotations

import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference.tlv import (
    detect_tlv_message_layout,
    message_layout_edges,
    message_tlv_edges,
    parse_ber_elements,
)


def _ber(tag: int, value: bytes) -> bytes:
    if len(value) < 128:
        return bytes([tag, len(value)]) + value
    length_bytes = len(value).to_bytes((len(value).bit_length() + 7) // 8, "big")
    return bytes([tag, 0x80 | len(length_bytes)]) + length_bytes + value


def _goose_like(rng: random.Random) -> bytes:
    """Fixed 8-byte header, then a constructed 0x61 PDU whose string lengths vary."""
    name = bytes(rng.choice(b"ABCDEFGH") for _ in range(rng.randint(10, 30)))
    body = (
        _ber(0x80, name)
        + _ber(0x81, rng.randint(0, 65535).to_bytes(2, "big"))
        + _ber(0x82, name)
        + _ber(0x84, bytes(rng.randrange(256) for _ in range(8)))
        + _ber(0xAB, _ber(0x83, b"\x01") + _ber(0x85, bytes([rng.randrange(256)])))
    )
    pdu = _ber(0x61, body)
    return b"\x03\xe8" + (8 + len(pdu)).to_bytes(2, "big") + b"\x00\x00\x00\x00" + pdu


def test_parse_descends_constructed_elements_and_follows_variable_lengths():
    message = _goose_like(random.Random(1))
    elements = parse_ber_elements(message, 8)
    assert elements is not None
    tags = [message[tag] for tag, _value, _end, _constructed in elements]
    assert tags == [0x61, 0x80, 0x81, 0x82, 0x84, 0xAB, 0x83, 0x85]
    assert elements[-1][2] == len(message)


def test_edges_mark_element_and_value_starts():
    message = bytes.fromhex("61098003414243810201f4")
    assert message_tlv_edges(message, 0) == [0, 2, 4, 7, 9, 11]


def test_truncated_chain_does_not_parse():
    message = bytes.fromhex("61098003414243810201")  # last value byte missing
    assert parse_ber_elements(message, 0) is None
    assert message_tlv_edges(message, 0) is None


def test_layout_detected_on_ber_family_from_its_header_end():
    rng = random.Random(2)
    layout = detect_tlv_message_layout([_goose_like(rng) for _ in range(40)])
    assert layout is not None
    assert layout["kind"] == "tlv_ber"
    assert layout["edge_convention"] == "tag+length|value"
    # the two zero bytes pairs at 4..8 parse as empty elements, so the chain may start there
    assert layout["chain_start"] in (4, 6, 8)


def test_layout_rejects_modbus_tcp():
    """The MBAP header parses by chance (00 00 | 00 06 | 6 bytes); the gates must reject it."""
    rng = random.Random(3)
    messages = []
    for txn in range(60):
        pdu = bytes([1, 3]) + rng.randint(0, 999).to_bytes(2, "big") + rng.randint(1, 10).to_bytes(2, "big")
        messages.append(txn.to_bytes(2, "big") + b"\x00\x00" + (len(pdu) + 1).to_bytes(2, "big") + pdu)
    assert detect_tlv_message_layout(messages) is None


def test_layout_edges_keep_fixed_header_edges_and_fall_back_when_unparsed():
    message = _goose_like(random.Random(4))
    layout = {"kind": "tlv_ber", "chain_start": 8}
    edges = message_layout_edges(message, [0, 2, 4, 8, 30, 50], layout)
    assert {0, 2, 4, 8}.issubset(edges)
    assert set(edges) - {0, 2, 4} == set(message_tlv_edges(message, 8))
    assert message_layout_edges(message[:-1], [0, 2, 4, 8, 30], layout) == [0, 2, 4, 8, 30]
    assert message_layout_edges(message, [0, 2, 30], None) == [0, 2, 30]


def test_benchmark_scorer_uses_message_layouts(tmp_path):
    spec = importlib.util.spec_from_file_location("bench", ROOT / "scripts/diagnostics/31_benchmark_message_boundaries.py")
    bench = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)
    rng = random.Random(5)
    messages = [_goose_like(rng) for _ in range(20)]
    with (tmp_path / "01_messages.jsonl").open("w") as handle:
        for msg_id, payload in enumerate(messages):
            handle.write(json.dumps({"msg_id": msg_id, "payload_hex": payload.hex(), "payload_len": len(payload)}) + "\n")
    (tmp_path / "02_family_assignments.json").write_text(
        json.dumps({"assignments": [{"msg_id": i, "family_id": "F0"} for i in range(len(messages))]})
    )
    fixed = [{"start": edge, "length": 0} for edge in (2, 4, 8)]
    (tmp_path / "families.json").write_text(json.dumps({
        "F0": {"field_hypotheses": fixed, "message_layout": {"kind": "tlv_ber", "chain_start": 8}}
    }))
    annotations = tmp_path / "ann.jsonl"
    with annotations.open("w") as handle:
        for msg_id, payload in enumerate(messages):
            truth = [0, 2, 4, 8] + message_tlv_edges(payload, 8)
            handle.write(json.dumps({"msg_id": msg_id, "boundaries": sorted(set(truth)), "reviewer": "tshark"}) + "\n")
    with_layout = bench.score_protocol(tmp_path, annotations, "families.json")
    fixed_only = bench.score_protocol(tmp_path, annotations, "families.json", use_message_layouts=False)
    assert with_layout["f1"] == 1.0
    assert with_layout["message_layout_families"] == 1
    assert fixed_only["f1"] < 0.6
