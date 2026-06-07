from __future__ import annotations

import json

import pytest

from protocol_re.llm.multi_stage import LLMStage, StageConfig, load_cached_response
from protocol_re.llm.stage_boundaries import run_boundary_refinement_stage
from protocol_re.llm.user_responses import save_rendered_prompt
from protocol_re.model.schema import MessageRecord


def _msg(msg_id: int, payload_hex: str) -> MessageRecord:
    return MessageRecord(
        msg_id=msg_id,
        source_file="capture.pcap",
        session_id="s1",
        session_key="s1",
        src_ip="1.1.1.1",
        src_port=1,
        dst_ip="2.2.2.2",
        dst_port=2,
        direction="client->server",
        payload_hex=payload_hex,
        payload_len=len(payload_hex) // 2,
    )


def test_load_cached_response_reads_response_field(tmp_path) -> None:
    raw_response = '{"choices":[{"message":{"content":"{}"}}]}'
    result_path = tmp_path / "boundary_refinement_family_0.json"
    result_path.write_text(json.dumps({"response": raw_response}), encoding="utf-8")

    assert load_cached_response(result_path) == raw_response


def test_cached_stage_response_skips_api_call(monkeypatch: pytest.MonkeyPatch) -> None:
    raw_response = json.dumps({
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "merge_suggestions": [
                            {
                                "fields_to_merge": [0, 1],
                                "merged_field": {"start_offset": 0, "end_offset": 2, "width": 2},
                                "confidence": 0.9,
                                "rationale": "cached",
                            }
                        ]
                    })
                }
            }
        ]
    })

    def fail_api_call(*_args, **_kwargs):
        raise AssertionError("API call should not be used when cached_response is provided")

    monkeypatch.setattr("protocol_re.llm.stage_boundaries.call_openai_compatible_chat_with_raw", fail_api_call)

    result = run_boundary_refinement_stage(
        family_id="family_0",
        fields=[
            {"start": 0, "length": 1, "confidence": 0.8},
            {"start": 1, "length": 1, "confidence": 0.8},
        ],
        messages=[_msg(1, "0102")],
        config=StageConfig(stage=LLMStage.BOUNDARY_REFINEMENT, min_confidence=0.6),
        llm_config=None,
        cached_response=raw_response,
    )

    assert result.success is True
    assert result.response == raw_response
    assert result.applied_count == 1


def test_normal_stage_result_prompt_can_be_saved_with_cached_response(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    raw_response = json.dumps({
        "choices": [
            {
                "message": {
                    "content": json.dumps({"merge_suggestions": []})
                }
            }
        ]
    })

    def fail_api_call(*_args, **_kwargs):
        raise AssertionError("API call should not be used when cached_response is provided")

    monkeypatch.setattr("protocol_re.llm.stage_boundaries.call_openai_compatible_chat_with_raw", fail_api_call)

    result = run_boundary_refinement_stage(
        family_id="family_0",
        fields=[{"start": 0, "length": 1, "confidence": 0.8}],
        messages=[_msg(1, "01")],
        config=StageConfig(stage=LLMStage.BOUNDARY_REFINEMENT, render_only=False),
        llm_config=None,
        cached_response=raw_response,
    )
    prompt_path = tmp_path / "boundary_refinement_family_0_prompt.md"
    save_rendered_prompt(prompt_path, result.prompt)

    assert result.success is True
    assert "Evidence Bundle" in prompt_path.read_text(encoding="utf-8")
