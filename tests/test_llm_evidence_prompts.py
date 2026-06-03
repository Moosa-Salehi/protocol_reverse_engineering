from __future__ import annotations

import json

import pytest

from protocol_re.llm.evidence_builders import (
    build_family_statistics,
    build_field_statistics,
    build_sample_values,
    derive_boundary_scores,
)
from protocol_re.llm import stage_synthesis
from protocol_re.llm.analyze import LLMRequestConfig
from protocol_re.llm.multi_stage import LLMStage, StageConfig
from protocol_re.llm.patches import extract_patches_from_analysis
from protocol_re.llm.stage_relations import apply_relation_validation
from protocol_re.llm.stage_synthesis import prepare_synthesis_evidence
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


def test_field_statistics_and_samples_are_derived_from_messages() -> None:
    fields = [
        {"start": 0, "length": 2, "field_type": "counter", "confidence": 0.9, "evidence": {"unique_values": 2}},
        {"start": 2, "length": 1, "field_type": "constant", "confidence": 0.99},
    ]
    messages = [_msg(1, "010200"), _msg(2, "010300")]

    stats = build_field_statistics(fields, messages)
    samples = build_sample_values(fields, messages)

    assert stats["field_0"]["sample_cardinality"] == 2
    assert stats["field_1"]["dominant_values"][0]["hex"] == "00"
    assert samples[0]["values"][0]["hex"] == "0102"
    assert samples[1]["values"][1]["hex"] == "00"


def test_boundary_scores_and_family_statistics_are_derived_from_segments() -> None:
    fields = [
        {"start": 0, "length": 2, "confidence": 0.9},
        {"start": 2, "length": 2, "confidence": 0.8},
    ]
    details = {
        "message_count": 2,
        "template": "?? ?? 00 05",
        "field_hypotheses": fields,
        "segments": [
            {"start": 0, "end": 2, "evidence": {"boundary_support": 3.2, "feature_stability_score": 0.7}},
            {"start": 2, "end": 4, "evidence": {"boundary_support": 5.1}},
        ],
    }

    scores = derive_boundary_scores(fields, details["segments"])
    family_stats = build_family_statistics(details, messages=[_msg(1, "01020005"), _msg(2, "01030005")])

    assert scores[0]["boundary_after"] == 2
    assert scores[0]["boundary_support"] == 3.2
    assert family_stats["message_count"] == 2
    assert family_stats["field_count"] == 2


def test_synthesis_uses_field_hypotheses_and_computes_total_messages() -> None:
    model = {
        "families": [
            {
                "family_id": "family_0",
                "role": "request",
                "message_count": 10,
                "template": "?? 00",
                "field_hypotheses": [
                    {
                        "start": 0,
                        "length": 1,
                        "field_type": "counter_or_transaction_id",
                        "confidence": 0.95,
                        "evidence": {"unique_values": 10},
                    }
                ],
                "feature_summary": {"length_stats": {"mean": 2}},
            }
        ],
        "relations": [],
        "metadata": {},
    }

    evidence = prepare_synthesis_evidence(model)

    assert evidence["protocol_model"]["total_messages"] == 10
    assert evidence["protocol_model"]["families"][0]["fields"][0]["field_type"] == "counter_or_transaction_id"
    assert evidence["protocol_model"]["families"][0]["fields"][0]["offset"] == 0


def test_synthesis_splits_large_prompt_and_uses_stage_generation_limits(monkeypatch: pytest.MonkeyPatch) -> None:
    families = []
    for i in range(5):
        families.append(
            {
                "family_id": f"family_{i}",
                "role": "request",
                "message_count": 10 - i,
                "template": "?? " * 20,
                "field_hypotheses": [
                    {
                        "start": 0,
                        "length": 2,
                        "field_type": "counter_or_transaction_id",
                        "confidence": 0.9,
                    }
                ],
            }
        )

    requests: list[tuple[str, int]] = []

    def fake_call(prompt: str, config: LLMRequestConfig, request_label: str):
        requests.append((request_label, config.max_tokens))
        body = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({"markdown_summary": request_label})
                        }
                    }
                ]
            }
        )
        return json.loads(body), body

    monkeypatch.setattr(stage_synthesis, "SYNTHESIS_SPLIT_TOKEN_THRESHOLD", 1)
    monkeypatch.setattr(stage_synthesis, "SYNTHESIS_CHUNK_FAMILY_COUNT", 2)
    monkeypatch.setattr(stage_synthesis, "call_openai_compatible_chat_with_raw", fake_call)

    result = stage_synthesis.run_protocol_synthesis_stage(
        protocol_model={"families": families, "relations": [], "metadata": {}},
        config=StageConfig(
            stage=LLMStage.PROTOCOL_SYNTHESIS,
            prompt_template_path="assets/prompts/protocol_synthesis.md",
            max_tokens=1234,
            temperature=0.2,
        ),
        llm_config=LLMRequestConfig(
            model="test-model",
            base_url="https://example.test/v1",
            api_key="test-key",
            max_tokens=4000,
        ),
    )

    assert result.success is True
    assert len(requests) == 3
    assert all(label.startswith("stage 15 protocol synthesis chunk") for label, _max_tokens in requests)
    assert {max_tokens for _label, max_tokens in requests} == {1234}


def test_patch_extraction_reads_nested_synthesis_patches() -> None:
    patches = extract_patches_from_analysis(
        {
            "synthesis": {
                "patches": [
                    {
                        "op": "replace",
                        "path": "/families/0/role",
                        "value": "request",
                        "rationale": "supported",
                    }
                ]
            }
        }
    )

    assert len(patches) == 1
    assert patches[0].path == "/families/0/role"


def test_relation_validation_does_not_apply_llm_discard_to_strong_edge() -> None:
    relation = {
        "request_family_id": "family_4",
        "response_family_id": "family_4",
        "pair_count": 5936,
        "support_ratio": 0.747231,
        "edge_lift": 10.735965,
        "temporal_order_consistency": 1.0,
        "relation_confidence": 0.8,
    }
    decisions = [
        {
            "request_family_id": "family_4",
            "response_family_id": "family_4",
            "decision": "discard",
            "confidence": 0.4,
            "rationale": "overly conservative",
        }
    ]

    kept, _log = apply_relation_validation([relation], decisions, min_confidence=0.7)

    assert len(kept) == 1
    assert kept[0]["llm_discard_overridden"] is True
