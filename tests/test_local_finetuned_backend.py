"""Tests for the local fine-tuned backend (protocol_re.llm.local_finetuned) and
its integration hooks in stage_boundaries / stage_semantics."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from protocol_re.llm.local_finetuned import (  # noqa: E402
    LocalInferenceConfig,
    aggregate_boundaries,
    aggregate_semantics,
    extract_json_object,
    parse_boundary_prediction,
    parse_semantic_prediction,
    render_local_prompt,
    run_local_boundary_refinement,
    run_local_semantic_labeling,
)
from protocol_re.llm.multi_stage import LLMStage, StageConfig  # noqa: E402
from protocol_re.llm.stage_boundaries import run_boundary_refinement_stage  # noqa: E402
from protocol_re.llm.stage_semantics import run_semantic_labeling_stage  # noqa: E402
from protocol_re.model.schema import MessageRecord  # noqa: E402


def make_message(msg_id: int = 1, payload_hex: str = "0103000a0002", direction: str = "request") -> MessageRecord:
    return MessageRecord(
        msg_id=msg_id,
        source_file="test.pcap",
        session_id="s1",
        session_key="k1",
        src_ip="1.1.1.1",
        src_port=1,
        dst_ip="2.2.2.2",
        dst_port=2,
        direction=direction,
        payload_hex=payload_hex,
        payload_len=len(payload_hex) // 2,
    )


# ---------------------------------------------------------------------------
# Prompt rendering: must byte-match the SFT training format
# ---------------------------------------------------------------------------

def test_render_local_prompt_matches_training_format():
    message = make_message(payload_hex="01 03 00 0a".replace(" ", ""))
    prompt = render_local_prompt("boundary_refinement", message)
    assert prompt.startswith("### TASK: boundary_refinement\n\n")
    assert "## Evidence Bundle" in prompt
    expected_evidence = {
        "messages": [
            {
                "msg_id": message.msg_id,
                "direction": "request",
                "payload_len": message.payload_len,
                "payload_hex": message.payload_hex,
            }
        ]
    }
    assert json.dumps(expected_evidence, separators=(",", ":")) in prompt


# ---------------------------------------------------------------------------
# JSON repair + prediction parsing
# ---------------------------------------------------------------------------

def test_extract_json_object_tolerates_fences_and_prose():
    assert extract_json_object('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json_object('Here you go: {"a": 1} hope that helps') == {"a": 1}
    assert extract_json_object("not json at all") is None


def test_parse_boundary_prediction_validates_offsets():
    obj = {"boundaries": [0, 1, 4, 12, "bad", -3]}
    assert parse_boundary_prediction(obj, payload_len=12) == [0, 1, 4, 12]
    # missing start offset -> unusable
    assert parse_boundary_prediction({"boundaries": [1, 4]}, 12) == []
    # out of range entries are dropped; with only an out-of-range start-adjacent
    # edge left, [0] is still a valid (trivial) boundary set
    assert parse_boundary_prediction({"boundaries": [0, 99]}, 12) == [0]
    # nested task envelope
    assert parse_boundary_prediction({"boundary_refinement": {"boundaries": [0, 12]}}, 12) == [0, 12]
    assert parse_boundary_prediction(None, 12) == []


def test_parse_semantic_prediction_validates_roles_and_ranges():
    obj = {
        "semantic_labels": [
            {"offset": 0, "width": 1, "semantic_role": "function_code", "field_type": "uint8"},
            {"offset": 1, "width": 2, "semantic_role": "made_up_role"},
            {"offset": 5, "width": 2, "semantic_role": "length"},  # out of range
            {"offset": 3, "width": "x", "semantic_role": "status"},  # bad width
        ]
    }
    labels = parse_semantic_prediction(obj, payload_len=6)
    assert labels == [{"offset": 0, "width": 1, "semantic_role": "function_code", "field_type": "uint8"}]


# ---------------------------------------------------------------------------
# Consensus aggregation
# ---------------------------------------------------------------------------

def test_aggregate_boundaries_intersection_with_support():
    per_message = [
        [0, 1, 4, 10],
        [0, 1, 4, 10],
        [0, 2, 4, 10],
    ]
    # support 0.5 of 3 usable -> threshold 2: offsets 0,4,10 pass; 1 (2 votes) passes; 2 (1 vote) fails
    assert aggregate_boundaries(per_message, payload_len=10, min_support=0.5) == [0, 1, 4, 10]
    # stricter support drops offset 1
    assert aggregate_boundaries(per_message, payload_len=10, min_support=0.99) == [0, 4, 10]


def test_aggregate_boundaries_handles_no_usable_predictions():
    assert aggregate_boundaries([[], []], payload_len=8, min_support=0.5) == [0, 8]
    assert aggregate_boundaries([], payload_len=8, min_support=0.5) == [0, 8]


def test_aggregate_semantics_majority_vote_and_confidence():
    per_message = [
        [{"offset": 0, "width": 1, "semantic_role": "function_code", "field_type": "uint8"}],
        [{"offset": 0, "width": 1, "semantic_role": "function_code", "field_type": "uint8"}],
        [{"offset": 0, "width": 1, "semantic_role": "opcode", "field_type": "uint8"}],
    ]
    result = aggregate_semantics(per_message, min_support=0.5)
    assert len(result) == 1
    assert result[0]["semantic_role"] == "function_code"
    assert result[0]["confidence"] == pytest.approx(2 / 3, abs=1e-3)
    assert result[0]["support"] == "2/3"


# ---------------------------------------------------------------------------
# Stage integration: llm_call hook produces StageResults the existing pipeline consumes
# ---------------------------------------------------------------------------

FIELDS = [
    {"start": 0, "length": 1, "field_type": "bytes", "confidence": 0.8},
    {"start": 1, "length": 2, "field_type": "bytes", "confidence": 0.7},
    {"start": 3, "length": 3, "field_type": "bytes", "confidence": 0.6},
]


def _fake_local_chat(monkeypatch, boundary_payload: str, semantic_payload: str):
    def fake_call(prompt, base_url, model, api_key, temperature, max_tokens, timeout, retries=2, retry_delay=1.0, request_label=""):
        if "### TASK: boundary_refinement" in prompt:
            return boundary_payload
        return semantic_payload

    import protocol_re.llm.local_finetuned as local

    monkeypatch.setattr(local, "call_local_chat", fake_call)


def test_run_local_boundary_refinement_end_to_end(monkeypatch):
    _fake_local_chat(monkeypatch, '{"boundaries": [0, 1, 4, 6]}', "{}")
    messages = [make_message(msg_id=i, payload_hex="0103000a0002") for i in range(3)]
    llm = LocalInferenceConfig(base_url="http://127.0.0.1:8080", max_samples=3)
    raw, boundaries, used = run_local_boundary_refinement("family_0", messages, llm)
    assert used == 3
    assert boundaries == [0, 1, 4, 6]
    parsed = json.loads(raw)
    assert parsed["boundaries"] == [0, 1, 4, 6]
    assert parsed["backend"] == "local_finetuned"


def test_stage_boundaries_uses_llm_call(monkeypatch):
    _fake_local_chat(monkeypatch, '{"boundaries": [0, 1, 6]}', "{}")
    messages = [make_message(payload_hex="0103000a0002")]
    llm = LocalInferenceConfig(max_samples=1)
    config = StageConfig(stage=LLMStage.BOUNDARY_REFINEMENT, min_confidence=0.6)

    def llm_call(prompt, family_id, task):
        raw, _b, _u = run_local_boundary_refinement(family_id, messages, llm)
        return raw

    result = run_boundary_refinement_stage(
        family_id="family_0",
        fields=FIELDS,
        messages=messages,
        config=config,
        llm_config=None,
        llm_call=llm_call,
    )
    assert result.success
    # [0,1,6] merges the 2-byte and 3-byte fields into one 5-byte field
    log_applied = [entry for entry in result.validation_log if entry.get("applied")]
    assert log_applied, f"expected an applied merge log, got: {result.validation_log}"
    assert result.applied_count >= 1
    updated = log_applied[0]["updated_fields"]
    assert updated[0]["start"] == 0
    assert sum(f["length"] for f in updated) == 6
    assert len(updated) == 2  # 3 fields merged into 2


def test_stage_semantics_uses_llm_call(monkeypatch):
    _fake_local_chat(
        monkeypatch,
        "{}",
        '{"semantic_labels": [{"offset": 0, "width": 1, "semantic_role": "function_code", "field_type": "uint8"}]}',
    )
    messages = [make_message(payload_hex="0103000a0002")]
    llm = LocalInferenceConfig(max_samples=1)
    config = StageConfig(stage=LLMStage.SEMANTIC_LABELING, min_confidence=0.5)

    def llm_call(prompt, family_id, task):
        raw, _labels, _u = run_local_semantic_labeling(family_id, messages, FIELDS, llm)
        return raw

    result = run_semantic_labeling_stage(
        family_id="family_0",
        fields=FIELDS,
        config=config,
        llm_config=None,
        messages=messages,
        llm_call=llm_call,
    )
    assert result.success, result.error
    assert result.applied_count == 1
    labeled = [entry for entry in result.validation_log if entry.get("applied")]
    assert labeled[0]["label"]["semantic_role"] == "function_code"
    assert labeled[0]["label"]["field_index"] == 0


def test_stage_boundaries_llm_call_response_bypasses_confidence_gate():
    # The aggregate response carries confidence 0.99 so the direct-boundary
    # path is used regardless of --min-confidence.
    raw = json.dumps({"family_id": "f", "boundaries": [0, 6], "confidence": 0.99})
    messages = [make_message(payload_hex="0103000a0002")]
    config = StageConfig(stage=LLMStage.BOUNDARY_REFINEMENT, min_confidence=0.99)
    result = run_boundary_refinement_stage(
        family_id="f",
        fields=FIELDS,
        messages=messages,
        config=config,
        llm_config=None,
        llm_call=lambda prompt, family_id, task: raw,
    )
    assert result.success
    assert result.validation_log[0]["applied"] is True or result.validation_log[0]["valid"] is True
