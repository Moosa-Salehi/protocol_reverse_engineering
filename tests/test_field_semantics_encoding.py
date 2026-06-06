from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference.boundary_detection import infer_field_hypotheses
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
