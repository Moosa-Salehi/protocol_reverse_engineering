from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.clustering.family_discovery import discover_families
from protocol_re.config.thresholds import TlvFraming
from protocol_re.inference.framing import infer_family_framing, infer_framing_hypotheses
from protocol_re.inference.tlv import (
    detect_tlv_framing,
    derive_tlv_field_hypotheses,
    header_field_runs,
    merge_families_by_tlv_signature,
    parse_tlv_message,
    parse_tlv_tree,
)
from protocol_re.model.schema import FamilyAssignment, MessageRecord


def _load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _ber(tag: int, value: bytes) -> bytes:
    """Encode one BER short/long-form element."""
    if len(value) < 128:
        return bytes([tag, len(value)]) + value
    length_bytes = len(value).to_bytes((len(value).bit_length() + 7) // 8, "big")
    return bytes([tag, 0x80 | len(length_bytes)]) + length_bytes + value


# ── GOOSE-like fixture: 8-byte header + 0x61 constructed wrapper + inner TLVs ──

def _goose_like(appid: int = 0x03E8, st_num: int = 1, pad: int = 0) -> bytes:
    header = appid.to_bytes(2, "big") + b"\x00\x00" + b"\x00\x00\x00\x00"
    inner = (
        _ber(0x80, b"LED10CTRL/LLN0$Status")
        + _ber(0x81, b"\x00\x00\x00\x01")
        + _ber(0x82, b"LED10PROT/LLN0$Alarm" + b"\x00" * pad)
        + _ber(0x83, st_num.to_bytes(4, "big"))
        + _ber(0x84, b"\x5c\xd3\xd9\xac\x83\x95\x81\x0a")
    )
    wrapper = _ber(0x61, inner)
    total = 8 + len(wrapper)
    return header[:2] + total.to_bytes(2, "big") + header[4:] + wrapper


def test_parse_tlv_message_offsets_are_absolute():
    payload = b"\xaa\xbb" + _ber(0x80, b"abc") + _ber(0x81, b"\x00\x01")
    view = parse_tlv_message(payload, header_length=2)
    assert view is not None
    assert [element.tag for element in view.elements] == [0x80, 0x81]
    first, second = view.elements
    assert first.start == 2 and first.value_offset == 4 and first.value_length == 3
    assert second.start == 7 and second.value_offset == 9
    assert first.start + first.length == second.start


def test_parse_tlv_message_rejects_structural_violations():
    # Length beyond end of message
    assert parse_tlv_message(b"\x00\x81\xff\xff", 0) is None
    # BER long form claiming 5 length bytes
    assert parse_tlv_message(b"\x00\x85\x01\x02\x03\x04\x05", 0) is None
    # High-tag-number form unsupported
    assert parse_tlv_message(b"\x1f\x9f\x01\x02", 0) is None
    # Empty chain
    assert parse_tlv_message(b"\x00", 0) is None


def test_parse_tlv_tree_descends_into_wrapper():
    payload = _goose_like()
    view = parse_tlv_tree(payload, header_length=8)
    assert view is not None
    assert view.wrapper is not None and view.wrapper.tag == 0x61
    assert [element.tag for element in view.elements] == [0x80, 0x81, 0x82, 0x83, 0x84]
    # Inner offsets are absolute (start after the 8-byte header + wrapper tag/length)
    assert view.elements[0].start > 8
    assert view.wrapper.start == 8


def test_detect_tlv_framing_finds_header_and_tags():
    messages = [_goose_like(st_num=n % 5) for n in range(40)]
    detection = detect_tlv_framing(messages)
    assert detection is not None
    assert detection.header_length == 8
    assert detection.parse_success_ratio >= TlvFraming.MIN_PARSE_SUCCESS_RATIO
    assert detection.distinct_tags >= TlvFraming.MIN_DISTINCT_TAGS
    assert detection.sequence_count <= 5  # st_num variation does not change tags


def test_detect_tlv_framing_rejects_non_tlv_corpus():
    # Fixed-offset Modbus-like payloads: constant opcode then register bytes
    messages = [bytes([0x00, 0x01, 0x00, 0x00, 0x00, 0x06, 0x01, 0x03]) + b"\x00\x03" for _ in range(30)]
    assert detect_tlv_framing(messages) is None
    # Random payload blobs
    import hashlib

    blobs = [hashlib.sha256(bytes([n])).digest() for n in range(40)]
    assert detect_tlv_framing(blobs) is None


def test_merge_families_by_tlv_signature_collapses_length_buckets():
    messages = [_goose_like(st_num=n, pad=n % 4) for n in range(30)]
    records = [
        MessageRecord(msg_id=index, source_file="t", session_id="s", session_key="k", src_ip="a", src_port=0,
                      dst_ip="b", dst_port=0, direction="unknown", payload_hex=payload.hex(), payload_len=len(payload))
        for index, payload in enumerate(messages)
    ]
    # Bootstrap clustering split one message type across length buckets
    assignments = [
        FamilyAssignment(msg_id=record.msg_id, family_id=f"family_{record.payload_len % 4}") for record in records
    ]
    detection = detect_tlv_framing(messages)
    assert detection is not None
    merged, metadata = merge_families_by_tlv_signature(records, assignments, detection)
    assert metadata["applied"] is True
    assert metadata["family_count_after"] == 1
    assert metadata["family_count_before"] == 4
    assert len({assignment.family_id for assignment in merged}) == 1


def test_derive_tlv_field_hypotheses_matches_goose_layout():
    messages = [_goose_like(st_num=n % 3, pad=n % 3) for n in range(20)]
    detection = detect_tlv_framing(messages)
    assert detection is not None
    hypotheses, segments, metadata = derive_tlv_field_hypotheses("family_x", [m.hex() for m in messages], detection)

    assert metadata["mode"] == "tlv_ber"
    by_start = {hypothesis.start: hypothesis for hypothesis in hypotheses}
    # GT-convention header fields (absolute offsets)
    assert by_start[0].length == 2  # appid
    assert by_start[2].field_type == "uint16"  # length register
    assert by_start[4].attributes.get("value_hex") == "0000"  # reserved_1
    assert by_start[6].attributes.get("value_hex") == "0000"  # reserved_2
    # Constant wrapper tag surfaces at body start
    assert by_start[8].attributes.get("value_hex") == "61"
    # Inner TLV tags become fields with absolute offsets
    tlv_fields = [hypothesis for hypothesis in hypotheses if hypothesis.attributes.get("tlv_tag_hex")]
    assert len(tlv_fields) == 5
    assert all(hypothesis.start >= 8 for hypothesis in tlv_fields)
    # The 0x83 st_num field is uint32 big-endian
    st_num_field = next(h for h in tlv_fields if h.attributes["tlv_tag_hex"] == "0x83")
    assert st_num_field.field_type == "uint32" and st_num_field.endian == "big"


def test_header_field_runs_grouping():
    messages = [b"\x03\xe8\x00\x05", b"\x03\xe8\x00\x09", b"\x03\xe8\x00\x11"]
    runs = header_field_runs(messages, 4)
    assert runs[0] == {"start": 0, "length": 3, "constant": True, "value_hex": "03e800"}
    assert runs[1] == {"start": 3, "length": 1, "constant": False}


def test_framing_hook_prepends_tlv_layout():
    messages = [_goose_like() for _ in range(12)]
    plain = infer_family_framing("family_x", messages)
    upgraded = infer_family_framing("family_x", messages, enable_tlv=True)
    assert "tlv_framing" not in plain
    assert upgraded["tlv_framing"]["header_length"] == 8
    best = upgraded["layout_hypotheses"][0]
    assert best["body_start"] == 8 and best["header_end"] == 8
    assert best["evidence"]["mode"] == "tlv_ber"


def test_infer_framing_hypotheses_flag_passthrough():
    family_messages = {"family_0": [_goose_like().hex() for _ in range(12)]}
    result = infer_framing_hypotheses(family_messages, enable_tlv=True)
    family = result["families"]["family_0"]
    assert family["tlv_framing"]["detected"] is True
    assert family["layout_hypotheses"][0]["body_start"] == 8


def test_discover_families_tlv_merge_flag():
    messages = [_goose_like(st_num=n, pad=n % 3) for n in range(40)]
    records = [
        MessageRecord(msg_id=index, source_file="t", session_id="s", session_key="k", src_ip="a", src_port=0,
                      dst_ip="b", dst_port=0, direction="unknown", payload_hex=payload.hex(), payload_len=len(payload))
        for index, payload in enumerate(messages)
    ]
    result_without = discover_families(records, method="hdbscan", tlv_family_merge=False)
    result_with = discover_families(records, method="hdbscan", tlv_family_merge=True)
    assert result_with.tlv_merge is not None
    assert result_without.tlv_merge is None
    assert result_with.tlv_merge["applied"] is True
    assert result_with.tlv_merge["family_count_after"] == 1
    families_with = {assignment.family_id for assignment in result_with.assignments}
    assert families_with == {"family_0"}


def test_stage07_tlv_override_and_07b_skip():
    stage07 = _load_script("stage07", "scripts/07_infer_boundaries.py")
    # The TLV branch must short-circuit before hierarchical/entropy segmentation.
    source = Path(ROOT / "scripts/07_infer_boundaries.py").read_text(encoding="utf-8")
    assert "--tlv-boundaries" in source
    assert "derive_tlv_field_hypotheses" in source

    stage07b = Path(ROOT / "scripts/07b_refine_boundaries_llm.py").read_text(encoding="utf-8")
    assert "tlv_metadata" in stage07b
