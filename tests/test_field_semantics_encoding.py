from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference.boundary_detection import infer_field_hypotheses
from protocol_re.inference.framing import FramingFieldRegion, FramingLayoutHypothesis, _dedupe_layouts, _header_boundary_scores
from protocol_re.model.schema import Segment
from protocol_re.utils.bytes import best_numeric_endian


def _load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


build_model = _load_script("build_protocol_model_stage", "scripts/12_build_protocol_model.py")
prepare_eval = _load_script("prepare_evaluation_data_stage", "scripts/16_prepare_evaluation_data.py")
eval_spec = _load_script("evaluate_protocol_spec_stage", "scripts/17_evaluate_protocol_spec.py")


def test_stage12_merges_encoding_type_and_preserves_semantic_role() -> None:
    field = {
        "family_id": "family_0",
        "start": 0,
        "length": 2,
        "field_type": "counter_or_transaction_id",
        "confidence": 0.9,
        "endian": "big",
    }
    label = {
        "start": 0,
        "length": 2,
        "label": "transaction_id",
        "field_type": "uint16_be",
        "encoding_type": "uint16_be",
        "confidence": 0.8,
        "evidence": {"source": "test"},
    }

    merged = build_model._merge_semantic_label(field, label)
    hypothesis = build_model._build_field_hypothesis(merged).to_dict()

    assert hypothesis["field_type"] == "uint16_be"
    assert hypothesis["attributes"]["semantic_role"] == "transaction_id"
    assert hypothesis["attributes"]["inferred_role_label"] == "counter_or_transaction_id"
    assert hypothesis["attributes"]["encoding_type"] == "uint16_be"


def test_prepare_evaluation_normalizes_legacy_role_field_type() -> None:
    protocol = {
        "families": [
            {
                "family_id": "family_0",
                "field_hypotheses": [
                    {
                        "start": 2,
                        "length": 4,
                        "field_type": "length",
                        "endian": "big",
                        "attributes": {"semantic_role": "length"},
                    }
                ],
            }
        ]
    }

    normalized = prepare_eval._normalize_protocol_field_types(protocol)
    field = normalized["families"][0]["field_hypotheses"][0]

    assert field["field_type"] == "uint32_be"
    assert field["encoding_type"] == "uint32_be"
    assert field["attributes"]["semantic_role"] == "length"
    assert field["attributes"]["inferred_role_label"] == "length"


def test_prepare_evaluation_refreshes_stale_refined_framing_from_base() -> None:
    base = {
        "families": [
            {
                "family_id": "family_0",
                "framing_summary": {"layout_hypotheses": [{"header_end": 7, "body_start": 7}]},
                "field_hypotheses": [],
            }
        ],
        "metadata": {"framing_global_summary": {"common_header_ends": [{"header_end": 7}]}},
    }
    refined = {
        "families": [
            {
                "family_id": "family_0",
                "framing_summary": {"layout_hypotheses": [{"header_end": 6, "body_start": 6}]},
                "field_hypotheses": [],
            }
        ],
        "metadata": {"framing_global_summary": {"common_header_ends": [{"header_end": 6}]}},
    }

    refreshed = prepare_eval._refresh_refined_framing(refined, base)

    assert refreshed["families"][0]["framing_summary"]["layout_hypotheses"][0]["body_start"] == 7
    assert refreshed["metadata"]["framing_global_summary"]["common_header_ends"][0]["header_end"] == 7


def test_semantic_score_matches_concrete_types_and_ignores_endian_variant() -> None:
    predicted = {
        "field_type": "uint16_be",
        "attributes": {"semantic_role": "transaction_id"},
        "start": 0,
        "length": 2,
    }
    truth = {"field_type": "uint16", "name": "transaction_identifier", "start": 0, "length": 2}

    assert eval_spec._semantic_score(predicted, truth) == 1.0


def test_semantic_score_uses_generic_width_fallback() -> None:
    predicted = {"field_type": "counter_or_transaction_id", "start": 0, "length": 1}
    truth = {"field_type": "uint8", "start": 0, "length": 1}

    assert eval_spec._semantic_score(predicted, truth) == 1.0


def test_best_numeric_endian_prefers_monotonic_low_variance_interpretation() -> None:
    chunks = [value.to_bytes(2, "little") for value in (1, 2, 3, 4, 5, 6)]

    endian, stats = best_numeric_endian(chunks)

    assert endian == "little"
    assert stats["little"]["sequence_score"] > stats["big"]["sequence_score"]


def test_boundary_counter_endian_is_data_driven() -> None:
    messages = [f"{value:04x}" for value in (1, 2, 3, 4, 5, 6)]
    segments = [Segment(start=0, end=2, kind="variable", confidence=0.9)]

    fields = infer_field_hypotheses("family_0", messages, segments)

    assert fields[0].field_type == "counter_or_transaction_id"
    assert fields[0].endian == "big"
    assert fields[0].evidence["selected_endian"] == "big"


def test_framing_layout_ranking_uses_raw_score_before_shorter_offset() -> None:
    layouts = [
        FramingLayoutHypothesis(
            family_id="family_0",
            header_start=0,
            header_end=6,
            body_start=6,
            body_end=None,
            confidence=1.0,
            evidence={"score": 6.5, "preferred_layer_boundary": 7},
        ),
        FramingLayoutHypothesis(
            family_id="family_0",
            header_start=0,
            header_end=7,
            body_start=7,
            body_end=None,
            confidence=1.0,
            evidence={"score": 6.6, "preferred_layer_boundary": 7},
        ),
    ]

    assert _dedupe_layouts(layouts)[0].header_end == 7


def test_framing_layout_ranking_prefers_detected_layer_edge_over_later_body_score() -> None:
    layouts = [
        FramingLayoutHypothesis(
            family_id="family_0",
            header_start=0,
            header_end=7,
            body_start=7,
            body_end=None,
            confidence=1.0,
            evidence={"score": 6.0, "preferred_layer_boundary": 7},
        ),
        FramingLayoutHypothesis(
            family_id="family_0",
            header_start=0,
            header_end=12,
            body_start=12,
            body_end=None,
            confidence=1.0,
            evidence={"score": 8.0, "preferred_layer_boundary": 7},
        ),
    ]

    assert _dedupe_layouts(layouts)[0].header_end == 7


def test_header_boundary_prefers_length_plus_selector_edge_over_full_message() -> None:
    stats = [
        {"coverage": 1.0, "stable_ratio": 0.2, "entropy": 1.0, "unique_ratio": 0.8, "cardinality": 10}
        for _ in range(12)
    ]
    stats[6] = {"coverage": 1.0, "stable_ratio": 1.0, "entropy": 0.0, "unique_ratio": 0.01, "cardinality": 1}
    fields = [
        FramingFieldRegion(0, 2, "transaction_or_counter", 0.9),
        FramingFieldRegion(4, 6, "length", 1.0, {"relation": "body_after_field"}),
        FramingFieldRegion(7, 12, "discriminator", 0.9),
    ]
    tail_scores = {boundary: {"tail_variability_jump": 0.0} for boundary in range(13)}

    scores = _header_boundary_scores([], stats, fields, tail_scores, 12)
    best_boundary = max(scores, key=lambda boundary: scores[boundary]["score"])

    assert scores[7]["preferred_layer_boundary"] == 7
    assert best_boundary == 7


def test_field_matching_shifts_absolute_prediction_for_body_relative_truth() -> None:
    family = {
        "family_id": "family_0",
        "framing_summary": {"layout_hypotheses": [{"header_end": 7, "body_start": 7}]},
        "field_hypotheses": [
            {"start": 7, "length": 1, "field_type": "uint8"},
        ],
    }
    truth = {
        "message_type_id": "body_type",
        "role": "request",
        "fields": [
            {"name": "function_code", "start": 0, "length": 1, "field_type": "uint8"},
        ],
    }

    matches = eval_spec._field_matches(
        {"family_0": family},
        {"body_type": truth},
        [{"predicted_family_id": "family_0", "ground_truth_message_type_id": "body_type"}],
    )

    assert len(matches) == 1
    assert matches[0]["boundary_score"] == 1.0
    assert matches[0]["semantic_score"] == 1.0
    assert matches[0]["offset_shift"] == 7
