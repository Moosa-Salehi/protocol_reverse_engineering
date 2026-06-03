from __future__ import annotations

import json

import pytest

from protocol_re.llm.analyze import extract_message_json
from protocol_re.llm.user_responses import (
    ensure_user_response_placeholder,
    load_user_provided_response,
    make_user_response_path,
)


def test_placeholder_file_is_created_with_response_slots(tmp_path) -> None:
    path = tmp_path / "user_provided_LLM_responses" / "semantic_labeling_F0.json"

    ensure_user_response_placeholder(
        path,
        stage="semantic_labeling",
        prompt_path="data/llm_stage_results/semantic_labeling_F0_prompt.md",
        model="test-model",
        request_label="stage 11b semantic labeling for F0",
        metadata={"family_id": "F0"},
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["model"] == "test-model"
    assert payload["response_text"] == ""
    assert payload["response"] is None
    assert payload["metadata"]["family_id"] == "F0"


def test_empty_placeholder_returns_none(tmp_path) -> None:
    path = tmp_path / "response.json"
    ensure_user_response_placeholder(path, stage="relation_validation")

    assert load_user_provided_response(path) is None


def test_response_text_is_wrapped_as_chat_completion(tmp_path) -> None:
    path = tmp_path / "response.json"
    expected = {"semantic_labels": [{"field_index": 0, "semantic_role": "opcode", "confidence": 0.9, "evidence": ["sample"]}]}
    path.write_text(json.dumps({"model": "manual-model", "response_text": json.dumps(expected)}), encoding="utf-8")

    raw_response = load_user_provided_response(path)

    assert raw_response is not None
    assert extract_message_json(json.loads(raw_response)) == expected


def test_raw_chat_completion_response_is_preserved(tmp_path) -> None:
    path = tmp_path / "response.json"
    raw = {"choices": [{"message": {"content": "{\"validated_relations\": []}"}}]}
    path.write_text(json.dumps({"response": raw}), encoding="utf-8")

    assert json.loads(load_user_provided_response(path) or "{}") == raw


def test_missing_user_response_file_is_an_error(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        load_user_provided_response(tmp_path / "missing.json")


def test_make_user_response_path_sanitizes_identifier() -> None:
    assert make_user_response_path("boundary_refinement", "family/0").name == "boundary_refinement_family_0.json"
