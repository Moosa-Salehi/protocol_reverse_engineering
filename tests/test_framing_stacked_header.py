from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference.framing import _anchor_stacked_headers, _counted_region_start, infer_framing_hypotheses


def _ethercat_like(rng: random.Random, count: int = 300) -> list[str]:
    """2-byte frame header (11-bit LE length of what follows, type bits above) and
    three back-to-back datagram headers that are nearly constant, then data."""
    messages = []
    for _ in range(count):
        datagrams = b""
        for k in range(3):
            data = bytes(rng.randrange(256) for _ in range(rng.choice([2, 4, 6, 8])))
            datagrams += bytes([0x04, k]) + b"\x00\x10\x30\x01" + len(data).to_bytes(2, "little") + b"\x00\x00" + data + b"\x00\x00"
        header = (len(datagrams) | 0x1000).to_bytes(2, "little")
        messages.append((header + datagrams).hex())
    return messages


def _modbus_like(rng: random.Random, count: int = 300) -> list[str]:
    messages = []
    for i in range(count):
        pdu = bytes([3, rng.randrange(256)]) + bytes(rng.randrange(256) for _ in range(rng.choice([2, 4, 8, 16])))
        messages.append(((i % 65536).to_bytes(2, "big") + b"\x00\x00" + (len(pdu) + 1).to_bytes(2, "big") + b"\x01" + pdu).hex())
    return messages


def test_counted_region_start_finds_masked_length():
    found = _counted_region_start({"f": _ethercat_like(random.Random(1))})
    assert found is not None
    assert found["start"] == 2


def test_stacked_headers_are_anchored_at_the_counted_region():
    result = infer_framing_hypotheses({"family_0": _ethercat_like(random.Random(2))})
    best = result["families"]["family_0"]["layout_hypotheses"][0]
    assert best["body_start"] == 2
    assert best["evidence"]["mode"] == "counted_length_anchor"
    assert best["evidence"]["previous_body_start"] >= 6


def test_only_overshoots_of_at_least_the_minimum_are_anchored():
    messages = _modbus_like(random.Random(3))
    evidence = _counted_region_start({"f": messages})
    assert evidence is not None and evidence["start"] == 6
    c = evidence["start"]

    def family(body_start):
        return {"layout_hypotheses": [{"header_end": body_start, "body_start": body_start, "field_regions": [], "evidence": {}}]}

    results = {"close": family(c + 1), "far": family(c + 5)}
    _anchor_stacked_headers(results, {"close": messages, "far": messages}, evidence)
    assert results["close"]["layout_hypotheses"][0]["body_start"] == c + 1
    assert len(results["close"]["layout_hypotheses"]) == 1
    assert results["far"]["layout_hypotheses"][0]["body_start"] == c
    assert results["far"]["layout_hypotheses"][1]["body_start"] == c + 5


def test_anchor_can_be_disabled():
    corpus = {"family_0": _ethercat_like(random.Random(4))}
    best = infer_framing_hypotheses(corpus, stacked_header_anchor=False)["families"]["family_0"]["layout_hypotheses"][0]
    assert best["evidence"].get("mode") != "counted_length_anchor"
