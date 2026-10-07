#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from protocol_re.config.thresholds import FamilyRefinement
from protocol_re.utils.logging import setup_stage_logging


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return round((2 * precision * recall) / (precision + recall), 6) if precision + recall else 0.0


def _prf(tp: int, fp: int, fn: int) -> Dict[str, Any]:
    if tp == 0 and fp == 0 and fn == 0:
        # Perfect vacuous agreement: both the prediction and the truth agree
        # the set is empty (e.g. a connectionless protocol like GOOSE has no
        # request/response relations on either side). Scoring this 0.0 would
        # punish protocols for a property they share with the ground truth.
        # The values stay numeric for report consumers, but the metric is
        # flagged not applicable so it is left out of the overall score
        # instead of contributing a free 1.0.
        return {
            "applicable": False,
            "true_positives": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "accuracy": 1.0,
            "precision": 1.0,
            "recall": 1.0,
            "f1_score": 1.0,
        }
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    return {
        "applicable": True,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "accuracy": _ratio(tp, tp + fp + fn),
        "precision": precision,
        "recall": recall,
        "f1_score": _f1(precision, recall),
    }


def _norm(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


CONCRETE_BASE_TYPES = {"uint8", "uint16", "uint32", "uint64", "bytes"}
WIDTH_TO_TYPE = {1: "uint8", 2: "uint16", 4: "uint32", 8: "uint64"}
ROLE_TYPE_EQUIVALENTS = {
    "payload": {"bytes"},
    "data": {"bytes"},
    "blob": {"bytes"},
}


def _attributes(field: Dict[str, Any]) -> Dict[str, Any]:
    attributes = field.get("attributes")
    return attributes if isinstance(attributes, dict) else {}


def _canonical_type(value: Any) -> str:
    token = _norm(value)
    if token.endswith("_be") or token.endswith("_le"):
        return token[:-3]
    return token


def _concrete_type(field: Dict[str, Any], truth: bool = False) -> str:
    attributes = _attributes(field)
    candidates = [
        field.get("encoding_type"),
        attributes.get("encoding_type"),
        attributes.get("encoding"),
        field.get("field_type"),
        field.get("type") if truth else None,
        field.get("label"),
    ]
    for candidate in candidates:
        token = _norm(candidate)
        if not token:
            continue
        canonical = _canonical_type(token)
        if canonical in CONCRETE_BASE_TYPES:
            return token

    length = _field_len(field)
    if length in WIDTH_TO_TYPE:
        return WIDTH_TO_TYPE[length]
    if length is not None and length > 4:
        return "bytes"
    return ""


def _semantic_role(field: Dict[str, Any], truth: bool = False) -> str:
    attributes = _attributes(field)
    return _norm(
        attributes.get("semantic_role")
        or field.get("semantic_role")
        or attributes.get("inferred_role_label")
        or field.get("label")
        or field.get("name")
        or (field.get("field_type") if not _concrete_type(field, truth=truth) else None)
    )


def _field_end(field: Dict[str, Any]) -> int | None:
    start = int(field.get("start", 0) or 0)
    length = field.get("length")
    if length is not None:
        return start + int(length) - 1
    end = field.get("end")
    return int(end) if end is not None else None


def _field_len(field: Dict[str, Any]) -> int | None:
    length = field.get("length")
    if length is not None:
        return int(length)
    end = field.get("end")
    if end is None:
        return None
    return int(end) - int(field.get("start", 0) or 0) + 1


def _tag_value(value: Any) -> int | None:
    """Parse a TLV tag given as an int, a decimal string, or a ``0x..`` string."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    token = str(value).strip().lower()
    if not token:
        return None
    try:
        return int(token, 16) if token.startswith("0x") else int(token)
    except ValueError:
        return None


def _truth_tlv_tag(field: Dict[str, Any]) -> int | None:
    """Tag of a truth field declared as a TLV element (``tlv_tag``), else None."""
    return _tag_value(field.get("tlv_tag"))


def _predicted_tlv_tag(field: Dict[str, Any]) -> int | None:
    """Tag of a predicted TLV element field (stage-07 ``attributes.tlv_tag``)."""
    attributes = _attributes(field)
    tag = _tag_value(attributes.get("tlv_tag"))
    return tag if tag is not None else _tag_value(attributes.get("tlv_tag_hex"))


def _truth_uses_absolute_offsets(message_type: Dict[str, Any]) -> bool:
    tokens = {
        _norm(message_type.get("message_type_id")),
        _norm(message_type.get("name")),
        _norm(message_type.get("role")),
    }
    return any(token and ("header" in token or token in {"transport", "framing"}) for token in tokens)


def _family_body_offset(family: Dict[str, Any]) -> int:
    framing = family.get("framing_summary") if isinstance(family.get("framing_summary"), dict) else {}
    layouts = framing.get("layout_hypotheses", []) if isinstance(framing, dict) else []
    if layouts:
        best = layouts[0] if isinstance(layouts[0], dict) else {}
        body_start = best.get("body_start", best.get("header_end"))
        if body_start is not None:
            return max(0, int(body_start))
    layer = family.get("layer_boundary") if isinstance(family.get("layer_boundary"), dict) else {}
    if layer.get("detected") and layer.get("boundary_offset") is not None:
        return max(0, int(layer.get("boundary_offset")))
    return 0


def _comparison_field(field: Dict[str, Any], offset_shift: int) -> Dict[str, Any]:
    if not offset_shift:
        return field
    shifted = dict(field)
    shifted["start"] = int(shifted.get("start", 0) or 0) - offset_shift
    return shifted


def _field_ref(owner_id: str, field: Dict[str, Any], fallback_name: str) -> Dict[str, Any]:
    field_type = str(_concrete_type(field, truth=True) or field.get("field_type") or field.get("type") or "unknown")
    return {
        "owner_id": owner_id,
        "field_name": str(field.get("name") or field.get("field_type") or field.get("type") or fallback_name),
        "start": int(field.get("start", 0) or 0),
        "length": _field_len(field),
        "field_type": field_type,
    }


def _predicted_field_ref(family_id: str, field: Dict[str, Any], index: int) -> Dict[str, Any]:
    field_type = str(_concrete_type(field) or field.get("field_type") or field.get("label") or "unknown")
    return {
        "owner_id": family_id,
        "field_name": str(field.get("field_type") or field.get("label") or f"field_{index}"),
        "start": int(field.get("start", 0) or 0),
        "length": _field_len(field),
        "field_type": field_type,
    }


def _interval_score(predicted: Dict[str, Any], truth: Dict[str, Any]) -> float:
    p_start = int(predicted.get("start", 0) or 0)
    t_start = int(truth.get("start", 0) or 0)
    p_end = _field_end(predicted)
    t_end = _field_end(truth)
    if p_end is None or t_end is None:
        return 1.0 if p_start == t_start else 0.0
    overlap = max(0, min(p_end, t_end) - max(p_start, t_start) + 1)
    union = max(p_end, t_end) - min(p_start, t_start) + 1
    return round(overlap / union, 6) if union else 0.0


def _semantic_score(predicted: Dict[str, Any], truth: Dict[str, Any]) -> float:
    p_type = _concrete_type(predicted)
    t_type = _concrete_type(truth, truth=True)
    if not p_type or not t_type:
        p_type = _norm(predicted.get("field_type") or predicted.get("label"))
        t_type = _norm(truth.get("field_type") or truth.get("type") or truth.get("name"))
        if not p_type or not t_type:
            return 0.0
    if p_type == t_type:
        return 1.0
    p_base = _canonical_type(p_type)
    t_base = _canonical_type(t_type)
    if p_base and p_base == t_base:
        return 1.0
    if p_type in t_type or t_type in p_type:
        return 0.5
    p_role = _semantic_role(predicted)
    t_role = _semantic_role(truth, truth=True)
    if t_type in ROLE_TYPE_EQUIVALENTS.get(p_role, set()) or p_type in ROLE_TYPE_EQUIVALENTS.get(t_role, set()):
        return 0.5
    return 0.0


def _family_tokens(family: Dict[str, Any]) -> set[str]:
    tokens = {_norm(family.get("family_id")), _norm(family.get("role"))}
    semantic = family.get("semantic_summary") or {}
    tokens.add(_norm(semantic.get("role")))
    for field in family.get("field_hypotheses", []) or []:
        tokens.add(_norm(field.get("field_type")))
    for label in semantic.get("field_labels", []) or []:
        tokens.add(_norm(label.get("label")))
    return {token for token in tokens if token}


def _truth_tokens(message_type: Dict[str, Any]) -> set[str]:
    tokens = {_norm(message_type.get("message_type_id")), _norm(message_type.get("name")), _norm(message_type.get("role"))}
    for field in message_type.get("fields", []) or []:
        tokens.add(_norm(field.get("name")))
        tokens.add(_norm(field.get("field_type") or field.get("type")))
    return {token for token in tokens if token}


_DISCRIMINATOR_ROLES = {"request", "response"}


def _family_discriminator_value(family: Dict[str, Any]) -> str | None:
    """Return the family's constant opcode/discriminator byte as a decimal string.

    A function-code-pure family carries a constant single-byte field at the body
    (post-header) offset whose ``attributes.value_hex`` is that opcode.  Families
    that mix function codes leave that byte variable, so this returns ``None`` and
    matching falls back to structural similarity (the legacy behaviour).
    """
    body_offset = _family_body_offset(family)
    for field in family.get("field_hypotheses", []) or []:
        start = field.get("start")
        if start is None or int(start) != body_offset:
            continue
        if _field_len(field) != 1:
            continue
        value_hex = str(_attributes(field).get("value_hex") or "").strip()
        if not value_hex:
            return None
        try:
            return str(int(value_hex, 16))
        except ValueError:
            return None
    return None


def _truth_discriminator_value(message_type: Dict[str, Any]) -> str | None:
    """Return a truth type's discriminator value (e.g. Modbus function code).

    The convention is a required single-byte field at PDU offset 0 with an
    explicit ``constant_value``.  Header types (absolute offsets, no constant
    opcode at offset 0) and any type lacking such a field return ``None``.
    """
    if _truth_uses_absolute_offsets(message_type):
        return None
    for field in message_type.get("fields", []) or []:
        constant_value = field.get("constant_value")
        if constant_value is None:
            continue
        start = field.get("start")
        if start is None or int(start) != 0 or _field_len(field) != 1:
            continue
        try:
            return str(int(constant_value))
        except (TypeError, ValueError):
            return None
    return None


def _truth_header_length(truth_types: Sequence[Dict[str, Any]]) -> int:
    """Byte length of the shared header described by the header-role truth types."""
    end = 0
    for message_type in truth_types:
        if not _truth_uses_absolute_offsets(message_type):
            continue
        for field in message_type.get("fields", []) or []:
            start, length = field.get("start"), field.get("length")
            if start is None or length is None:
                continue
            end = max(end, int(start) + int(length))
    return end


def corpus_discriminator_scope(
    messages_jsonl: str,
    truth_types: Sequence[Dict[str, Any]],
    min_support: int = FamilyRefinement.MIN_FAMILY_SIZE,
) -> Dict[str, Any]:
    """Discriminator values that actually occur in the captured traffic.

    Reads the byte at PDU offset 0 (right after the truth header) of every
    message. The result depends only on the corpus and the truth file, so every
    pipeline variant evaluated on the same capture is scored against the same
    set of truth types.

    A value counts as present only with at least ``min_support`` messages — the
    smallest group the pipeline can form a family from. Captures of opcode scans
    carry one or two probes for every possible value; those are not recoverable
    message types and must not pull their truth types into scope.
    """
    header_length = _truth_header_length(truth_types)
    present_counts: Dict[str, int] = {}
    response_counts: Dict[str, int] = {}
    message_count = 0
    with open(messages_jsonl, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            payload_hex = str(record.get("payload_hex") or "")
            byte_hex = payload_hex[header_length * 2 : header_length * 2 + 2]
            if len(byte_hex) != 2:
                continue
            message_count += 1
            value = str(int(byte_hex, 16))
            present_counts[value] = present_counts.get(value, 0) + 1
            if _norm(record.get("direction")) == "server_to_client":
                response_counts[value] = response_counts.get(value, 0) + 1
    present = {value for value, count in present_counts.items() if count >= min_support}
    response = {value for value, count in response_counts.items() if count >= min_support}
    return {
        "source": "corpus",
        "header_length": header_length,
        "message_count": message_count,
        "min_support": min_support,
        "present_discriminators": sorted(present, key=int),
        "response_discriminators": sorted(response, key=int),
    }


def _truth_is_structural_tag(truth_types: Sequence[Dict[str, Any]]) -> bool:
    """True when the truth types' constant at PDU offset 0 is shared framing
    rather than a per-message-type discriminator.

    Self-describing protocols (GOOSE/BER, SNMP/ASN.1) wrap every PDU in the
    same constant tag — one constant value across all message types.  A
    Modbus-style function code, by contrast, *varies* across the protocol's
    message types.  The opcode gate therefore only engages when the protocol
    exposes more than one distinct constant at PDU offset 0.
    """
    values = {
        str(field.get("constant_value"))
        for message_type in truth_types
        for field in message_type.get("fields", []) or []
        if field.get("constant_value") is not None
        and field.get("start") is not None
        and int(field.get("start", 0)) == 0
        and _field_len(field) == 1
    }
    return len(values) <= 1


def _family_match_score(
    family: Dict[str, Any],
    message_type: Dict[str, Any],
    *,
    structural_tag: bool = False,
) -> float:
    p_tokens = _family_tokens(family)
    t_tokens = _truth_tokens(message_type)
    token_score = len(p_tokens & t_tokens) / len(p_tokens | t_tokens) if p_tokens or t_tokens else 0.0
    p_fields = family.get("field_hypotheses", []) or []
    t_fields = message_type.get("fields", []) or []
    if not t_fields:
        field_score = 0.0
    else:
        field_score = min(len(p_fields), len(t_fields)) / max(len(p_fields), len(t_fields), 1)
    p_role = _norm(family.get("role"))
    t_role = _norm(message_type.get("role"))
    role_score = 1.0 if p_role and p_role == t_role else 0.0
    base = round(max(token_score, (0.5 * field_score) + (0.3 * token_score) + (0.2 * role_score)), 6)

    # Discriminator gate: when both sides expose an opcode value, they must agree
    # to be the same message type.  This disambiguates structurally isomorphic
    # families (e.g. Modbus FC01 vs FC02 read requests share an identical layout)
    # so the family->truth bijection — and therefore relation credit — is no
    # longer an arbitrary tie-break.  When either side lacks a discriminator the
    # legacy structural score is used unchanged.
    #
    # A constant TLV/BER tag shared by every message type (GOOSE 0x61) is
    # framing, not a discriminator: matching it would zero every structurally
    # correct family.  Structural tags skip the gate.
    p_disc = _family_discriminator_value(family)
    t_disc = _truth_discriminator_value(message_type)
    if p_disc is not None and t_disc is not None and not structural_tag:
        if p_disc != t_disc:
            return 0.0
        role_conflict = p_role in _DISCRIMINATOR_ROLES and t_role in _DISCRIMINATOR_ROLES and p_role != t_role
        return round(max(base, 0.55 if role_conflict else 0.9), 6)
    return base


def _greedy_matches(candidates: Iterable[Tuple[str, str, float]], threshold: float) -> List[Tuple[str, str, float]]:
    selected: List[Tuple[str, str, float]] = []
    used_left: set[str] = set()
    used_right: set[str] = set()
    for left, right, score in sorted(candidates, key=lambda item: (-item[2], item[0], item[1])):
        if score < threshold or left in used_left or right in used_right:
            continue
        selected.append((left, right, score))
        used_left.add(left)
        used_right.add(right)
    return selected


def _message_type_matches(
    predicted: Sequence[Dict[str, Any]], truth: Sequence[Dict[str, Any]], *, structural_tag: bool = False
) -> List[Dict[str, Any]]:
    candidates = [
        (str(family.get("family_id")), str(message_type.get("message_type_id")), _family_match_score(family, message_type, structural_tag=structural_tag))
        for family in predicted
        for message_type in truth
    ]
    return [
        {
            "predicted_family_id": family_id,
            "ground_truth_message_type_id": message_type_id,
            "score": score,
            "reason": "token_field_role_similarity",
        }
        for family_id, message_type_id, score in _greedy_matches(candidates, 0.2)
    ]


def _field_matches(
    families_by_id: Dict[str, Dict[str, Any]],
    truth_by_id: Dict[str, Dict[str, Any]],
    message_matches: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for message_match in message_matches:
        family_id = message_match["predicted_family_id"]
        truth_id = message_match["ground_truth_message_type_id"]
        family = families_by_id.get(family_id) or {}
        truth_type = truth_by_id.get(truth_id) or {}
        predicted_fields = _comparable_predicted_fields(family, truth_type)
        truth_fields = list(truth_type.get("fields", []) or [])
        offset_shift = 0 if _truth_uses_absolute_offsets(truth_type) else _family_body_offset(family)

        # Tag-keyed pass. A truth field declared as a TLV element (``tlv_tag``)
        # has no stable byte offset: its position shifts with the lengths of
        # the elements before it. It is matched to the predicted element that
        # carries the same tag; identifying the element *is* the boundary, so
        # the boundary score is 1.0. Such fields never enter the positional
        # pass, where a missing ``start`` would be misread as offset 0.
        tag_matched_predicted: set[int] = set()
        tag_keyed_truth: set[int] = set()
        predicted_by_tag: Dict[int, int] = {}
        for p_index, predicted in enumerate(predicted_fields):
            tag = _predicted_tlv_tag(predicted)
            if tag is not None:
                predicted_by_tag.setdefault(tag, p_index)
        for t_index, truth in enumerate(truth_fields):
            tag = _truth_tlv_tag(truth)
            if tag is None:
                continue
            tag_keyed_truth.add(t_index)
            p_index = predicted_by_tag.get(tag)
            if p_index is None or p_index in tag_matched_predicted:
                continue
            tag_matched_predicted.add(p_index)
            predicted = predicted_fields[p_index]
            ground_truth_ref = _field_ref(truth_id, truth, f"field_{t_index}")
            ground_truth_ref["tlv_tag"] = tag
            matches.append(
                {
                    "predicted": _predicted_field_ref(family_id, predicted, p_index),
                    "ground_truth": ground_truth_ref,
                    "boundary_score": 1.0,
                    "semantic_score": _semantic_score(predicted, truth),
                    "offset_shift": offset_shift,
                    "match_key": "tlv_tag",
                }
            )

        candidates = []
        for p_index, predicted in enumerate(predicted_fields):
            if p_index in tag_matched_predicted:
                continue
            predicted_for_match = _comparison_field(predicted, offset_shift)
            for t_index, truth in enumerate(truth_fields):
                # Tag-keyed fields are settled above; a field with no start and
                # no tag has no position to compare against.
                if t_index in tag_keyed_truth or truth.get("start") is None:
                    continue
                boundary = _interval_score(predicted_for_match, truth)
                semantic = _semantic_score(predicted, truth)
                score = max(boundary, (0.7 * boundary) + (0.3 * semantic))
                candidates.append((str(p_index), str(t_index), score))
        for p_index, t_index, _ in _greedy_matches(candidates, 0.5):
            predicted = predicted_fields[int(p_index)]
            predicted_for_match = _comparison_field(predicted, offset_shift)
            truth = truth_fields[int(t_index)]
            matches.append(
                {
                    "predicted": _predicted_field_ref(family_id, predicted, int(p_index)),
                    "ground_truth": _field_ref(truth_id, truth, f"field_{t_index}"),
                    "boundary_score": _interval_score(predicted_for_match, truth),
                    "semantic_score": _semantic_score(predicted, truth),
                    "offset_shift": offset_shift,
                }
            )
    return matches


def _comparable_predicted_fields(family: Dict[str, Any], truth_type: Dict[str, Any]) -> List[Dict[str, Any]]:
    predicted_fields = list(family.get("field_hypotheses", []) or [])
    if _truth_uses_absolute_offsets(truth_type):
        return predicted_fields
    body_offset = _family_body_offset(family)
    if body_offset <= 0:
        return predicted_fields
    return [
        field
        for field in predicted_fields
        if int(field.get("start", 0) or 0) >= body_offset
    ]


def _relation_matches(
    predicted_relations: Sequence[Dict[str, Any]],
    truth_relations: Sequence[Dict[str, Any]],
    family_to_truth: Dict[str, str],
    families_by_id: Dict[str, Dict[str, Any]],
    truth_by_id: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    truth_items = [
        (str(item.get("request_message_type_id")), str(item.get("response_message_type_id")), item)
        for item in truth_relations
    ]
    candidates: List[Tuple[str, str, float]] = []
    candidate_details: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def compatible_family_endpoint(family_id: str, mapped_truth_id: str | None, truth_id: str) -> float:
        if mapped_truth_id == truth_id:
            return 1.0
        family = families_by_id.get(family_id) or {}
        truth_type = truth_by_id.get(truth_id) or {}
        family_role = _norm(family.get("role") or (family.get("semantic_summary") or {}).get("role"))
        truth_role = _norm(truth_type.get("role"))
        truth_name = _norm(truth_type.get("name") or "")
        truth_token = _norm(truth_id)
        is_generic_endpoint = truth_token in {"request", "response", "modbus_request", "modbus_response"} or (
            "_fc" not in truth_token and (truth_token.endswith("_request") or truth_token.endswith("_response"))
        )
        if mapped_truth_id is not None and not is_generic_endpoint:
            return 0.0
        if truth_role and family_role == truth_role and truth_role in {"request", "response"} and (mapped_truth_id is None or is_generic_endpoint):
            return 0.75
        if truth_name.endswith("_response") and family_role == "response":
            return 0.75
        if truth_name.endswith("_request") and family_role == "request":
            return 0.75
        return 0.0

    for relation in predicted_relations:
        pred_req = str(relation.get("request_family_id"))
        pred_resp = str(relation.get("response_family_id"))
        mapped_req = family_to_truth.get(pred_req)
        mapped_resp = family_to_truth.get(pred_resp)
        for truth_req, truth_resp, _truth_relation in truth_items:
            request_score = compatible_family_endpoint(pred_req, mapped_req, truth_req)
            response_score = compatible_family_endpoint(pred_resp, mapped_resp, truth_resp)
            score = round(min(request_score, response_score), 6)
            if score < 0.5:
                continue
            candidate_key = (f"{pred_req}->{pred_resp}", f"{truth_req}->{truth_resp}")
            candidates.append((candidate_key[0], candidate_key[1], score))
            candidate_details[candidate_key] = {
                "predicted_request_family_id": pred_req,
                "predicted_response_family_id": pred_resp,
                "ground_truth_request_message_type_id": truth_req,
                "ground_truth_response_message_type_id": truth_resp,
                "score": score,
                "request_match": mapped_req or "role_compatible",
                "response_match": mapped_resp or "role_compatible",
            }

    return [
        candidate_details[(predicted_key, truth_key)]
        for predicted_key, truth_key, _score in _greedy_matches(candidates, 0.5)
    ]


def _header_region_fields(family: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Predicted fields that fall in the framing/header region (before the body)."""
    body_offset = _family_body_offset(family)
    if body_offset <= 0:
        return []
    return [
        field
        for field in family.get("field_hypotheses", []) or []
        if int(field.get("start", 0) or 0) < body_offset
    ]


def _header_match_score(family: Dict[str, Any], header_type: Dict[str, Any]) -> float:
    """Mean best-overlap of a header type's (absolute-offset) fields against a family's header region."""
    p_fields = _header_region_fields(family)
    t_fields = header_type.get("fields", []) or []
    if not p_fields or not t_fields:
        return 0.0
    total = sum(max((_interval_score(p, t) for p in p_fields), default=0.0) for t in t_fields)
    return round(total / len(t_fields), 6)


def _header_type_matches(
    families: Sequence[Dict[str, Any]], header_types: Sequence[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Match shared header-role truth types to the header region of the best-fitting family.

    Every family carries the same framing header (e.g. the Modbus MBAP), so this
    match is *additive*: it does not consume the family from the discriminator-gated
    PDU matching or from relation scoring — it only recovers credit for header
    fields that are physically present but no longer broken out as a standalone
    family after discriminator refinement.
    """
    candidates = [
        (str(family.get("family_id")), str(header_type.get("message_type_id")), _header_match_score(family, header_type))
        for family in families
        for header_type in header_types
    ]
    return [
        {
            "predicted_family_id": family_id,
            "ground_truth_message_type_id": header_type_id,
            "score": score,
            "reason": "header_region_overlap",
        }
        for family_id, header_type_id, score in _greedy_matches(candidates, 0.5)
    ]


def _header_field_matches(
    families_by_id: Dict[str, Dict[str, Any]],
    truth_by_id: Dict[str, Dict[str, Any]],
    header_matches: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    matches: List[Dict[str, Any]] = []
    for header_match in header_matches:
        family = families_by_id.get(header_match["predicted_family_id"]) or {}
        header_type = truth_by_id.get(header_match["ground_truth_message_type_id"]) or {}
        predicted_fields = _header_region_fields(family)
        truth_fields = list(header_type.get("fields", []) or [])
        candidates = []
        for p_index, predicted in enumerate(predicted_fields):
            for t_index, truth in enumerate(truth_fields):
                boundary = _interval_score(predicted, truth)
                semantic = _semantic_score(predicted, truth)
                candidates.append((str(p_index), str(t_index), max(boundary, (0.7 * boundary) + (0.3 * semantic))))
        for p_index, t_index, _ in _greedy_matches(candidates, 0.5):
            predicted = predicted_fields[int(p_index)]
            truth = truth_fields[int(t_index)]
            matches.append(
                {
                    "predicted": _predicted_field_ref(header_match["predicted_family_id"], predicted, int(p_index)),
                    "ground_truth": _field_ref(header_match["ground_truth_message_type_id"], truth, f"field_{t_index}"),
                    "boundary_score": _interval_score(predicted, truth),
                    "semantic_score": _semantic_score(predicted, truth),
                    "offset_shift": 0,
                }
            )
    return matches


def evaluate_protocol_spec(
    model_data: Dict[str, Any],
    ground_truth_bundle: Dict[str, Any],
    corpus_scope: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    predicted_protocol = model_data.get("predicted_protocol", {}) or {}
    ground_truth_protocol = (ground_truth_bundle.get("ground_truth_protocol") or ground_truth_bundle.get("predicted_protocol") or {})
    families = predicted_protocol.get("families", []) or []
    truth_types = ground_truth_protocol.get("message_types", []) or []
    predicted_relations = predicted_protocol.get("relations", []) or []
    truth_relations = ground_truth_protocol.get("relations", []) or []

    # Corpus-conditioned truth scope. A PDU truth type is only in scope when its
    # discriminator (e.g. a Modbus function code) actually occurs in the captured
    # traffic. With ``corpus_scope`` (see corpus_discriminator_scope) that is read
    # from the messages themselves, so the scope cannot move with the prediction.
    # Without it the legacy approximation applies — some predicted family carries
    # that opcode — which lets a pipeline variant that loses a discriminator also
    # drop the truth types it would have been penalised for. This lets one truth
    # file describe a whole protocol family (every Modbus function code, including
    # exception responses) without penalising recall on a capture that exercises
    # only a subset: types for absent opcodes are neither matched nor counted as
    # false negatives, and their relations are dropped too. Header types (no
    # discriminator) and PDU types without a constant opcode are always in scope, so
    # a single-device capture containing only FC 01-06 evaluates exactly as before.
    #
    # Structural-tag protocols are exempt: when the PDU types' constant at offset 0
    # is shared framing (one tag value across the protocol, e.g. GOOSE 0x61) rather
    # than a varying opcode, the constant cannot scope message types, so the
    # exemption is decided against the *full* truth list, then applied after scope
    # filtering. A capture that only exercises some FCs still scopes Modbus types
    # exactly as before.
    structural_tag = _truth_is_structural_tag(truth_types)
    present_discriminators = {_family_discriminator_value(family) for family in families}
    present_discriminators.discard(None)
    # Discriminators carried by a response-direction family. Used to scope echo
    # types (request/response byte-identical, e.g. Modbus write-single FC 05/06)
    # whose request and response share a function code: the response type only
    # makes sense when the capture actually separated the two directions. A
    # direction-blind capture has no response-role family, so the response echo
    # type stays out of scope and is not counted as a false negative.
    response_discriminators = {
        _family_discriminator_value(family)
        for family in families
        if _norm(family.get("role")) == "response"
    }
    response_discriminators.discard(None)
    if corpus_scope is not None:
        present_discriminators = set(corpus_scope.get("present_discriminators") or [])
        response_discriminators = set(corpus_scope.get("response_discriminators") or [])

    def _truth_type_in_scope(message_type: Dict[str, Any]) -> bool:
        discriminator = _truth_discriminator_value(message_type)
        if discriminator is None:
            return True
        # Structural-tag protocol: the constant is shared framing, so it cannot
        # correlate a type with a family the way a varying function code does.
        if structural_tag:
            return True
        if discriminator not in present_discriminators:
            return False
        if message_type.get("scope_requires_response_role"):
            return discriminator in response_discriminators
        return True

    truth_types = [mt for mt in truth_types if _truth_type_in_scope(mt)]
    in_scope_truth_ids = {str(mt.get("message_type_id")) for mt in truth_types}
    truth_relations = [
        relation
        for relation in truth_relations
        if str(relation.get("request_message_type_id")) in in_scope_truth_ids
        and str(relation.get("response_message_type_id")) in in_scope_truth_ids
    ]

    families_by_id = {str(item.get("family_id")): item for item in families}
    truth_by_id = {str(item.get("message_type_id")): item for item in truth_types}

    # Header-role truth types (shared framing, absolute offsets) are matched in a
    # separate additive pass against each family's header region; the remaining
    # (PDU) truth types drive the discriminator-gated 1:1 family matching and all
    # relation scoring.  This recovers credit for a shared header (e.g. the Modbus
    # MBAP) that is present in every family but is no longer broken out as a
    # standalone family once discriminator refinement collapses families by opcode.
    header_types = [mt for mt in truth_types if _truth_uses_absolute_offsets(mt)]
    pdu_types = [mt for mt in truth_types if not _truth_uses_absolute_offsets(mt)]

    pdu_message_matches = _message_type_matches(families, pdu_types, structural_tag=structural_tag)
    header_message_matches = _header_type_matches(families, header_types)
    message_matches = pdu_message_matches + header_message_matches

    family_to_truth = {item["predicted_family_id"]: item["ground_truth_message_type_id"] for item in pdu_message_matches}
    field_matches = _field_matches(families_by_id, truth_by_id, pdu_message_matches)
    field_matches = field_matches + _header_field_matches(families_by_id, truth_by_id, header_message_matches)
    relation_matches = _relation_matches(predicted_relations, truth_relations, family_to_truth, families_by_id, truth_by_id)

    # Body-field scope is keyed by the PDU (FC) match; header carriers additionally
    # contribute their header-region fields to the predicted total.
    matched_truth_by_family = {
        item["predicted_family_id"]: item["ground_truth_message_type_id"]
        for item in pdu_message_matches
    }
    predicted_field_total = 0
    for family in families:
        family_id = str(family.get("family_id"))
        truth_id = matched_truth_by_family.get(family_id)
        truth_type = truth_by_id.get(truth_id) if truth_id is not None else None
        if truth_type is None:
            predicted_field_total += len(family.get("field_hypotheses", []) or [])
        else:
            predicted_field_total += len(_comparable_predicted_fields(family, truth_type))
    for header_match in header_message_matches:
        carrier_id = header_match["predicted_family_id"]
        if carrier_id in matched_truth_by_family:
            predicted_field_total += len(_header_region_fields(families_by_id.get(carrier_id) or {}))
    truth_field_total = sum(len((message_type.get("fields", []) or [])) for message_type in truth_types)
    semantic_tp = sum(1 for item in field_matches if float(item.get("semantic_score", 0.0) or 0.0) >= 0.5)

    matched_family_ids = {item["predicted_family_id"] for item in message_matches}
    matched_truth_ids = {item["ground_truth_message_type_id"] for item in message_matches}
    message_metrics = _prf(
        len(matched_truth_ids),
        sum(1 for family in families if str(family.get("family_id")) not in matched_family_ids),
        sum(1 for mt in truth_types if str(mt.get("message_type_id")) not in matched_truth_ids),
    )
    boundary_metrics = _prf(len(field_matches), max(0, predicted_field_total - len(field_matches)), max(0, truth_field_total - len(field_matches)))
    semantic_metrics = _prf(semantic_tp, max(0, predicted_field_total - semantic_tp), max(0, truth_field_total - semantic_tp))
    relation_metrics = _prf(len(relation_matches), max(0, len(predicted_relations) - len(relation_matches)), max(0, len(truth_relations) - len(relation_matches)))
    
    # Weighted overall score. Metrics that are not applicable (nothing predicted
    # and nothing expected, e.g. relations for a connectionless protocol) are
    # left out and the remaining weights renormalised.
    weighted = [
        (message_metrics, 0.30),
        (boundary_metrics, 0.30),
        (semantic_metrics, 0.25),
        (relation_metrics, 0.15),
    ]
    applicable_weight = sum(weight for metrics, weight in weighted if metrics["applicable"])
    overall = round(
        sum(metrics["f1_score"] * weight for metrics, weight in weighted if metrics["applicable"]) / applicable_weight,
        6,
    ) if applicable_weight else 0.0

    matched_predicted_fields = {(item["predicted"]["owner_id"], item["predicted"]["start"], item["predicted"].get("length")) for item in field_matches}
    matched_truth_fields = {(item["ground_truth"]["owner_id"], item["ground_truth"]["field_name"], item["ground_truth"]["start"], item["ground_truth"].get("length")) for item in field_matches}
    unmatched_predicted_fields = []
    for family in families:
        family_id = str(family.get("family_id"))
        truth_id = matched_truth_by_family.get(family_id)
        truth_type = truth_by_id.get(truth_id) if truth_id is not None else None
        fields = (
            _comparable_predicted_fields(family, truth_type)
            if truth_type is not None
            else list(family.get("field_hypotheses", []) or [])
        )
        for index, field in enumerate(fields):
            ref = _predicted_field_ref(family_id, field, index)
            if (ref["owner_id"], ref["start"], ref.get("length")) not in matched_predicted_fields:
                unmatched_predicted_fields.append(ref)
    unmatched_truth_fields = []
    for message_type in truth_types:
        truth_id = str(message_type.get("message_type_id"))
        for index, field in enumerate(message_type.get("fields", []) or []):
            ref = _field_ref(truth_id, field, f"field_{index}")
            if (ref["owner_id"], ref["field_name"], ref["start"], ref.get("length")) not in matched_truth_fields:
                unmatched_truth_fields.append(ref)

    return {
        "artifact_type": "protocol_re_final_evaluation_report",
        "protocol_name": str(ground_truth_protocol.get("protocol_name") or predicted_protocol.get("protocol_name") or "unknown-industrial-protocol"),
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "overall_score": overall,
            "verdict": "pass" if overall >= 0.8 else "partial" if overall >= 0.5 else "fail",
            "predicted_family_count": len(families),
            "ground_truth_message_type_count": len(truth_types),
            "matched_message_type_count": len(message_matches),
        },
        "truth_scope": {
            "source": "corpus" if corpus_scope is not None else "prediction",
            "in_scope_message_type_ids": sorted(in_scope_truth_ids),
        },
        "metrics": {
            "message_type_matching": message_metrics,
            "field_boundary": boundary_metrics,
            "field_semantics": semantic_metrics,
            "relations": relation_metrics,
        },
        "matches": {
            "message_types": message_matches,
            "fields": field_matches,
            "relations": relation_matches,
        },
        "unmatched": {
            "predicted_families": sorted(set(families_by_id) - matched_family_ids),
            "ground_truth_message_types": sorted(set(truth_by_id) - matched_truth_ids),
            "predicted_fields": unmatched_predicted_fields,
            "ground_truth_fields": unmatched_truth_fields,
        },
        "notes": [
            "Message type matching uses protocol-agnostic token, role, and field-count similarity.",
            "Field boundary matching uses byte-range overlap; semantic matching compares normalized field labels/types.",
        ],
    }


def _score_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "overall_score": (report.get("summary") or {}).get("overall_score"),
        "metrics": report.get("metrics", {}),
    }


def evaluate_protocol_spec_with_refinement(
    model_data: Dict[str, Any],
    ground_truth_bundle: Dict[str, Any],
    corpus_scope: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    report = evaluate_protocol_spec(model_data, ground_truth_bundle, corpus_scope)
    base_protocol = model_data.get("base_predicted_protocol")
    refined_protocol = model_data.get("refined_predicted_protocol")
    if not isinstance(base_protocol, dict) or not isinstance(refined_protocol, dict):
        return report

    base_data = dict(model_data)
    base_data["predicted_protocol"] = base_protocol
    refined_data = dict(model_data)
    refined_data["predicted_protocol"] = refined_protocol
    base_report = evaluate_protocol_spec(base_data, ground_truth_bundle, corpus_scope)
    refined_report = evaluate_protocol_spec(refined_data, ground_truth_bundle, corpus_scope)
    base_score = float((base_report.get("summary") or {}).get("overall_score", 0.0) or 0.0)
    refined_score = float((refined_report.get("summary") or {}).get("overall_score", 0.0) or 0.0)
    report["refinement_comparison"] = {
        "base": _score_summary(base_report),
        "refined": _score_summary(refined_report),
        "overall_score_delta": round(refined_score - base_score, 6),
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a reverse-engineered protocol spec against ground truth.")
    parser.add_argument("evaluation_model_data_json", help="Prepared model data from 16_prepare_evaluation_data.py")
    parser.add_argument("ground_truth_json", help="Ground truth JSON using evaluation_input.schema.json ground_truth_protocol shape")
    parser.add_argument("output_json", help="Output final evaluation report JSON")
    parser.add_argument(
        "--messages-jsonl",
        default=None,
        help="Message corpus (01_messages.jsonl). When given, truth types are scoped by the "
             "discriminator values observed in the corpus instead of by the predicted families.",
    )
    parser.add_argument("--log-dir", default="logs", help="Directory for log files")
    args = parser.parse_args()

    # Setup logging
    logger = setup_stage_logging("17_evaluate_protocol_spec", Path(args.log_dir))

    logger.info("Evaluating protocol specification against ground truth")

    with logger.stage("load_data"):
        logger.info(f"Loading evaluation model data from {args.evaluation_model_data_json}")
        evaluation_model_data = _load_json(args.evaluation_model_data_json)

        logger.info(f"Loading ground truth from {args.ground_truth_json}")
        ground_truth = _load_json(args.ground_truth_json)

    with logger.stage("evaluate_protocol"):
        corpus_scope = None
        if args.messages_jsonl:
            truth_protocol = ground_truth.get("ground_truth_protocol") or ground_truth.get("predicted_protocol") or {}
            corpus_scope = corpus_discriminator_scope(args.messages_jsonl, truth_protocol.get("message_types", []) or [])
            logger.info(
                f"Truth scope from corpus: {len(corpus_scope['present_discriminators'])} discriminator values "
                f"over {corpus_scope['message_count']} messages"
            )
        else:
            logger.warning("No --messages-jsonl given: truth scope falls back to the predicted families")
        report = evaluate_protocol_spec_with_refinement(evaluation_model_data, ground_truth, corpus_scope)
        report["inputs"] = {
            "predicted_protocol_file": args.evaluation_model_data_json,
            "ground_truth_protocol_file": args.ground_truth_json,
        }

        # Log key metrics
        if "overall_score" in report:
            logger.metric("overall_score", report["overall_score"], "score")
        if "message_types" in report:
            mt = report["message_types"]
            logger.metric("message_type_precision", mt.get("precision", 0), "ratio")
            logger.metric("message_type_recall", mt.get("recall", 0), "ratio")
            logger.metric("message_type_f1", mt.get("f1_score", 0), "score")

    with logger.stage("write_output"):
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
        logger.info(f"Wrote evaluation report to {output_path}")

    print(f"[+] Wrote final protocol evaluation report to {output_path}")

    # Log performance summary
    logger.log_stage_summary()


if __name__ == "__main__":
    main()
