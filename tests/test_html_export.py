from __future__ import annotations

import json

from protocol_re.export.html import (
    _byte_ruler,
    _family_refinement_blocks,
    _llm_analysis_block,
    _stage_status_metrics,
    render_protocol_model_html,
)


def test_byte_ruler_caps_template_to_family_modal_length() -> None:
    family = {
        "family_id": "family_0",
        "template": " ".join(["00"] * 20),
        "segments": [{"start": 0, "end": 20}],
        "feature_summary": {
            "structure_stats": {
                "length_profile": {
                    "kind": "mostly_fixed",
                    "modal_length": 12,
                    "modal_ratio": 0.96,
                }
            }
        },
    }
    labels = [
        {"start": 0, "length": 6, "label": "header", "field_type": "bytes"},
        {"start": 10, "length": 8, "label": "payload", "field_type": "bytes"},
        {"start": 18, "length": 2, "label": "noise", "field_type": "bytes"},
    ]

    html = _byte_ruler(family, labels=labels)

    assert "--cols:12" in html
    assert "+8" in html
    assert "grid-column:11 / span 2" in html
    assert "grid-column:19" not in html
    assert "clipped at modal length 12" in html


def test_llm_analysis_displays_serialized_chat_response_content() -> None:
    response = json.dumps(
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Recovered protocol response text.",
                    }
                }
            ]
        }
    )

    html = _llm_analysis_block({"model": "test-model", "response": response})

    assert "Recovered protocol response text." in html
    assert "No LLM analysis text is available." not in html


def test_family_refinement_hides_llm_api_failures() -> None:
    stage_results = {
        "boundary_refinement": {
            "family_0": {
                "result": {
                    "success": False,
                    "error": "network error",
                    "error_category": "llm_api",
                }
            }
        },
        "semantic_labeling": {
            "family_0": {
                "result": {
                    "success": True,
                    "validation_log": [],
                }
            }
        },
    }

    html = _family_refinement_blocks("family_0", stage_results)

    assert "LLM Boundary Refinement" not in html
    assert "network error" not in html
    assert "LLM Semantic Refinement" in html


def test_stage_metrics_use_validation_log_instead_of_stale_counts() -> None:
    result = {
        "success": True,
        "applied_count": 3,
        "rejected_count": 0,
        "validation_log": [
            {"applied": True},
            {"applied": False},
            {"applied": False},
        ],
    }

    html = _stage_status_metrics(result, "semantic_labeling")

    assert "<strong>1</strong><span>Applied/kept</span>" in html
    assert "<strong>2</strong><span>Rejected/discarded</span>" in html


def test_report_uses_body_level_tooltip_overlay() -> None:
    html = render_protocol_model_html({"families": [], "relations": []})

    assert 'id="report-tooltip"' in html
    assert "z-index: 2147483647" in html
    assert 'document.addEventListener("pointerover"' in html


def test_family_ruler_prefers_final_field_hypothesis_semantics() -> None:
    model = {
        "families": [
            {
                "family_id": "family_0",
                "message_count": 1,
                "template": "00 04",
                "segments": [{"start": 0, "end": 2}],
                "field_hypotheses": [
                    {
                        "start": 0,
                        "length": 2,
                        "field_type": "uint16",
                        "confidence": 0.8,
                        "attributes": {
                            "semantic_role": "constant",
                            "semantic_confidence": 0.99,
                            "encoding_type": "uint16_be",
                        },
                    }
                ],
                "semantic_summary": {
                    "field_labels": [
                        {
                            "start": 0,
                            "length": 2,
                            "label": "length",
                            "field_type": "uint16",
                            "confidence": 1.0,
                        }
                    ]
                },
            }
        ],
        "relations": [],
    }

    html = render_protocol_model_html(model)

    assert "constant · bytes 0..1 · uint16_be" in html
    assert "length · bytes 0..1 · uint16" not in html
