from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from protocol_re.inference.boundary_detection import infer_field_hypotheses, infer_segments
from protocol_re.inference.framing import FramingFieldRegion, FramingLayoutHypothesis, _dedupe_layouts, _header_boundary_scores
from protocol_re.corpus.request_response_pairing import pair_request_response_messages
from protocol_re.inference.request_response_relations import _echo_candidates, _length_correlation_relations
from protocol_re.llm.refinement import refine_protocol_model
from protocol_re.llm.patches import JsonPatchOperation
from protocol_re.model.schema import FamilyAssignment, MessageRecord
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


def test_known_good_llm_semantic_patch_improves_overall_score_delta() -> None:
    base_protocol = {
        "protocol_name": "toy",
        "version": "0.1",
        "metadata": {},
        "families": [
            {
                "family_id": "family_0",
                "role": "request",
                "message_count": 4,
                "template": "?? ??",
                "field_hypotheses": [
                    {
                        "family_id": "family_0",
                        "start": 0,
                        "length": 2,
                        "field_type": "identifier",
                        "confidence": 0.8,
                        "attributes": {},
                    }
                ],
            },
            {
                "family_id": "family_1",
                "role": "response",
                "message_count": 4,
                "template": "?? ??",
                "field_hypotheses": [
                    {
                        "family_id": "family_1",
                        "start": 0,
                        "length": 2,
                        "field_type": "identifier",
                        "confidence": 0.8,
                        "attributes": {},
                    }
                ],
            },
        ],
        "relations": [
            {
                "request_family_id": "family_0",
                "response_family_id": "family_1",
                "pair_count": 4,
                "avg_pair_score": 0.95,
                "support_ratio": 1.0,
                "edge_lift": 3.0,
                "temporal_order_consistency": 1.0,
            },
            {
                "request_family_id": "family_1",
                "response_family_id": "family_0",
                "pair_count": 1,
                "avg_pair_score": 0.2,
                "support_ratio": 0.05,
                "edge_lift": 0.5,
                "temporal_order_consistency": 0.1,
            },
        ],
    }
    patch_bundle = {
        "patches": [
            JsonPatchOperation(
                op="replace",
                path="/families/0/field_hypotheses/0/field_type",
                value="uint16_be",
                evidence_refs=["families[0].fields[0].length", "field_statistics.field_0.cardinality"],
                rationale="two-byte transaction identifier",
            ).to_dict(),
            JsonPatchOperation(
                op="add",
                path="/families/0/field_hypotheses/0/attributes/semantic_role",
                value="transaction_id",
                evidence_refs=["relations[0].echo_fields", "semantic_labeling_summary"],
                rationale="echoed transaction identifier",
            ).to_dict(),
            JsonPatchOperation(
                op="remove",
                path="/relations/1",
                evidence_refs=["relations[1].support_ratio", "relation_validation_summary.discarded_relations"],
                rationale="false relation edge with weak statistical support",
            ).to_dict(),
        ]
    }

    refined_protocol, validation = refine_protocol_model(
        base_protocol,
        patch_bundle,
        evidence={
            "families": [{"fields": [{"length": 2}], "semantic_labels": [{"label": "transaction_id"}]}, {}],
            "relations": [
                {"support_ratio": 1.0, "edge_lift": 3.0},
                {"support_ratio": 0.05, "edge_lift": 0.5},
            ],
        },
    )
    report = eval_spec.evaluate_protocol_spec_with_refinement(
        {
            "predicted_protocol": refined_protocol,
            "base_predicted_protocol": base_protocol,
            "refined_predicted_protocol": refined_protocol,
        },
        {
            "ground_truth_protocol": {
                "protocol_name": "toy",
                "message_types": [
                    {
                        "message_type_id": "toy_request",
                        "role": "request",
                        "fields": [
                            {
                                "name": "transaction_identifier",
                                "start": 0,
                                "length": 2,
                                "field_type": "uint16",
                            }
                        ],
                    },
                    {
                        "message_type_id": "toy_response",
                        "role": "response",
                        "fields": [
                            {
                                "name": "transaction_identifier",
                                "start": 0,
                                "length": 2,
                                "field_type": "uint16",
                            }
                        ],
                    },
                ],
                "relations": [
                    {
                        "request_message_type_id": "toy_request",
                        "response_message_type_id": "toy_response",
                    }
                ],
            }
        },
    )

    assert validation["accepted_patch_count"] == 3
    assert report["refinement_comparison"]["overall_score_delta"] > 0


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


def test_length_validator_preserves_adjacent_protocol_id_boundary() -> None:
    messages = [
        f"abcd1001{payload_len:04x}" + ("aa" * payload_len)
        for payload_len in (1, 2, 3, 4, 5, 6)
    ]

    segments = infer_segments(
        messages,
        score_threshold=99.0,
        enable_merging=True,
        length_match_threshold=0.8,
        framing_summary={"layout_hypotheses": [{"confidence": 1.0, "body_start": 2, "header_end": 2}]},
        isolate_body_opcode=False,
    )
    spans = [(segment.start, segment.end) for segment in segments]

    assert (2, 4) in spans
    assert (4, 6) in spans
    assert (2, 6) not in spans
    length_segment = next(segment for segment in segments if (segment.start, segment.end) == (4, 6))
    assert length_segment.evidence["semantic_hint"] == "length"
    assert length_segment.evidence["length_match_ratio"] == 1.0


def test_body_opcode_is_isolated_as_standalone_field() -> None:
    # MBAP(7) + PDU; function code at offset 7 is constant within the family,
    # address (8-9) and quantity (10-11) vary. Without isolation the constant
    # opcode is merged rightward into a wider field; with isolation it must
    # stay a 1-byte field of its own.
    messages = [
        f"{txn:04x}00000006" + "01" + "03" + f"{addr:04x}" + "0001"
        for txn, addr in [(1, 8), (2, 19), (3, 100), (4, 200), (5, 7), (6, 41)]
    ]
    framing = {"layout_hypotheses": [{"confidence": 1.0, "body_start": 7, "header_end": 7}]}

    isolated = infer_segments(messages, framing_summary=framing, isolate_body_opcode=True)
    spans = [(segment.start, segment.end) for segment in isolated]
    assert (7, 8) in spans  # opcode isolated as its own byte
    # no segment starts at the opcode offset and extends past it
    assert not any(start == 7 and end > 8 for start, end in spans)
    opcode = next(seg for seg in isolated if (seg.start, seg.end) == (7, 8))
    assert opcode.kind == "constant"

    not_isolated = infer_segments(messages, framing_summary=framing, isolate_body_opcode=False)
    merged_spans = [(segment.start, segment.end) for segment in not_isolated]
    # Pre-fix behaviour: the opcode is fused into a wider field starting at 7.
    assert any(start == 7 and end > 8 for start, end in merged_spans)


def test_variable_leading_body_byte_is_not_force_split() -> None:
    # When the first body byte is high-cardinality it is not an opcode and must
    # not be force-split: isolation should leave the segmentation unchanged.
    messages = [
        f"{txn:04x}00000006" + f"{lead:02x}" + f"{rest:08x}"
        for txn, lead, rest in [
            (1, 0x10, 0x11112222), (2, 0x37, 0x33334444), (3, 0x9a, 0x55556666),
            (4, 0xc1, 0x77778888), (5, 0x2d, 0x9999aaaa), (6, 0xf4, 0xbbbbcccc),
        ]
    ]
    framing = {"layout_hypotheses": [{"confidence": 1.0, "body_start": 7, "header_end": 7}]}

    isolated = infer_segments(messages, framing_summary=framing, isolate_body_opcode=True)
    baseline = infer_segments(messages, framing_summary=framing, isolate_body_opcode=False)
    assert [(s.start, s.end) for s in isolated] == [(s.start, s.end) for s in baseline]


def test_boundary_support_blends_segment_confidence() -> None:
    messages = ["01020204" for _ in range(6)]

    segments = infer_segments(
        messages,
        score_threshold=99.0,
        enable_merging=False,
        enable_length_validator=False,
        boundary_confidence_weight=0.5,
    )

    assert len(segments) == 1
    assert segments[0].evidence["boundary_support_ratio"] == 1.0

    split_segments = infer_segments(
        messages,
        score_threshold=99.0,
        enable_merging=False,
        enable_length_validator=False,
        framing_summary={"layout_hypotheses": [{"confidence": 1.0, "body_start": 2, "header_end": 2}]},
        boundary_confidence_weight=0.5,
        isolate_body_opcode=False,
    )

    assert [(segment.start, segment.end) for segment in split_segments] == [(0, 2), (2, 4)]
    assert split_segments[0].evidence["boundary_support_ratio"] == 0.0
    assert split_segments[0].evidence["consistency_confidence"] < segments[0].confidence


def test_pairing_infers_direction_from_stable_server_port() -> None:
    records = []
    for index in range(3):
        records.extend(
            [
                MessageRecord(
                    msg_id=index * 2,
                    source_file="capture.pcap",
                    session_id=f"s{index}",
                    session_key=f"s{index}",
                    src_ip=f"10.0.0.{index + 1}",
                    src_port=50000 + index,
                    dst_ip="10.0.0.10",
                    dst_port=502,
                    direction="unknown",
                    payload_hex="0001",
                    payload_len=2,
                    index_in_session=0,
                ),
                MessageRecord(
                    msg_id=index * 2 + 1,
                    source_file="capture.pcap",
                    session_id=f"s{index}",
                    session_key=f"s{index}",
                    src_ip="10.0.0.10",
                    src_port=502,
                    dst_ip=f"10.0.0.{index + 1}",
                    dst_port=50000 + index,
                    direction="unknown",
                    payload_hex="0001",
                    payload_len=2,
                    index_in_session=1,
                ),
            ]
        )

    pairs = pair_request_response_messages(
        records,
        assignments=[FamilyAssignment(msg_id=item.msg_id, family_id=f"f{item.msg_id % 2}") for item in records],
    )

    assert len(pairs) == 3
    assert all(pair.evidence.get("opposite_direction") == 1.0 for pair in pairs)
    assert all("direction_unknown" not in pair.evidence for pair in pairs)
    assert {record.direction for record in records} == {"client_to_server", "server_to_client"}


def test_correlation_id_pairing_survives_orphan_response_offset() -> None:
    # Stream starts mid-conversation with an orphan response, then alternates
    # request/response sharing a 2-byte transaction id at offset 0. Adjacency
    # pairing would couple each response with the *next* request (off by one);
    # correlation-id pairing must recover the true same-transaction pairs.
    def msg(mid, txn, body, idx):
        return MessageRecord(
            msg_id=mid, source_file="c.pcap", session_id="s", session_key="s",
            src_ip="", src_port=0, dst_ip="", dst_port=0, direction="unknown",
            payload_hex=f"{txn:04x}" + body, payload_len=2 + len(body) // 2,
            index_in_session=idx,
        )

    records = [msg(0, 0x1000, "0302002a", 0)]  # orphan response (txn 0x1000)
    mid = 1
    for k, txn in enumerate(range(0x1001, 0x1006)):
        records.append(msg(mid, txn, "03" + f"{k:04x}" + "01", mid))      # request
        records.append(msg(mid + 1, txn, "0302002a", mid + 1))            # response
        mid += 2

    pairs = pair_request_response_messages(
        records,
        assignments=[FamilyAssignment(msg_id=r.msg_id, family_id="f") for r in records],
    )

    assert len(pairs) == 5
    by_txn = {r.msg_id: r.payload_hex[:4] for r in records}
    # every pair couples two messages of the SAME transaction id
    assert all(by_txn[p.request_msg_id] == by_txn[p.response_msg_id] for p in pairs)
    assert all(p.evidence.get("pairing_mode") == "correlation_id" for p in pairs)
    # the orphan response (msg 0) must be left unpaired
    assert all(0 not in (p.request_msg_id, p.response_msg_id) for p in pairs)


def test_transaction_id_echo_not_penalized_as_counter() -> None:
    requests = [value.to_bytes(2, "big") + b"\x03\x00\x01" for value in range(1, 8)]
    responses = [value.to_bytes(2, "big") + b"\x03\x02\x00\x2a" for value in range(1, 8)]

    echoes = _echo_candidates(requests, responses, min_support=0.8)

    assert echoes
    assert echoes[0]["request_offset"] == 0
    assert echoes[0]["response_offset"] == 0
    assert echoes[0]["width"] == 2
    assert echoes[0]["confidence"] >= 0.7


def test_request_count_correlates_with_response_length() -> None:
    requests = [b"\x03\x00\x00" + count.to_bytes(2, "big") for count in (1, 2, 3, 4, 5)]
    responses = [bytes([3, count * 2]) + (b"\x00" * (count * 2)) for count in (1, 2, 3, 4, 5)]

    relations = _length_correlation_relations(requests, responses, min_support=0.75)

    assert any(
        relation["request_offset"] == 3
        and relation["width"] == 2
        and relation["relation_type"] == "request_field_correlates_response_length"
        for relation in relations
    )


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
