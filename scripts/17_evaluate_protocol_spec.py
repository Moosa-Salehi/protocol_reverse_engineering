#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _ratio(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return round((2 * precision * recall) / (precision + recall), 6) if precision + recall else 0.0


def _prf(tp: int, fp: int, fn: int) -> Dict[str, Any]:
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    return {
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


def _field_ref(owner_id: str, field: Dict[str, Any], fallback_name: str) -> Dict[str, Any]:
    return {
        "owner_id": owner_id,
        "field_name": str(field.get("name") or field.get("field_type") or fallback_name),
        "start": int(field.get("start", 0) or 0),
        "length": _field_len(field),
        "field_type": str(field.get("field_type") or field.get("type") or "unknown"),
    }


def _predicted_field_ref(family_id: str, field: Dict[str, Any], index: int) -> Dict[str, Any]:
    return {
        "owner_id": family_id,
        "field_name": str(field.get("field_type") or field.get("label") or f"field_{index}"),
        "start": int(field.get("start", 0) or 0),
        "length": _field_len(field),
        "field_type": str(field.get("field_type") or field.get("label") or "unknown"),
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
    p_type = _norm(predicted.get("field_type") or predicted.get("label"))
    t_type = _norm(truth.get("field_type") or truth.get("type") or truth.get("name"))
    if not p_type or not t_type:
        return 0.0
    if p_type == t_type:
        return 1.0
    if p_type in t_type or t_type in p_type:
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


def _family_match_score(family: Dict[str, Any], message_type: Dict[str, Any]) -> float:
    p_tokens = _family_tokens(family)
    t_tokens = _truth_tokens(message_type)
    token_score = len(p_tokens & t_tokens) / len(p_tokens | t_tokens) if p_tokens or t_tokens else 0.0
    p_fields = family.get("field_hypotheses", []) or []
    t_fields = message_type.get("fields", []) or []
    if not t_fields:
        field_score = 0.0
    else:
        field_score = min(len(p_fields), len(t_fields)) / max(len(p_fields), len(t_fields), 1)
    role_score = 1.0 if _norm(family.get("role")) and _norm(family.get("role")) == _norm(message_type.get("role")) else 0.0
    return round(max(token_score, (0.5 * field_score) + (0.3 * token_score) + (0.2 * role_score)), 6)


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


def _message_type_matches(predicted: Sequence[Dict[str, Any]], truth: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    candidates = [
        (str(family.get("family_id")), str(message_type.get("message_type_id")), _family_match_score(family, message_type))
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
        predicted_fields = list((families_by_id.get(family_id) or {}).get("field_hypotheses", []) or [])
        truth_fields = list((truth_by_id.get(truth_id) or {}).get("fields", []) or [])
        candidates = []
        for p_index, predicted in enumerate(predicted_fields):
            for t_index, truth in enumerate(truth_fields):
                boundary = _interval_score(predicted, truth)
                semantic = _semantic_score(predicted, truth)
                score = max(boundary, (0.7 * boundary) + (0.3 * semantic))
                candidates.append((str(p_index), str(t_index), score))
        for p_index, t_index, _ in _greedy_matches(candidates, 0.5):
            predicted = predicted_fields[int(p_index)]
            truth = truth_fields[int(t_index)]
            matches.append(
                {
                    "predicted": _predicted_field_ref(family_id, predicted, int(p_index)),
                    "ground_truth": _field_ref(truth_id, truth, f"field_{t_index}"),
                    "boundary_score": _interval_score(predicted, truth),
                    "semantic_score": _semantic_score(predicted, truth),
                }
            )
    return matches


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


def evaluate_protocol_spec(model_data: Dict[str, Any], ground_truth_bundle: Dict[str, Any]) -> Dict[str, Any]:
    predicted_protocol = model_data.get("predicted_protocol", {}) or {}
    ground_truth_protocol = (ground_truth_bundle.get("ground_truth_protocol") or ground_truth_bundle.get("predicted_protocol") or {})
    families = predicted_protocol.get("families", []) or []
    truth_types = ground_truth_protocol.get("message_types", []) or []
    predicted_relations = predicted_protocol.get("relations", []) or []
    truth_relations = ground_truth_protocol.get("relations", []) or []

    message_matches = _message_type_matches(families, truth_types)
    families_by_id = {str(item.get("family_id")): item for item in families}
    truth_by_id = {str(item.get("message_type_id")): item for item in truth_types}
    family_to_truth = {item["predicted_family_id"]: item["ground_truth_message_type_id"] for item in message_matches}
    field_matches = _field_matches(families_by_id, truth_by_id, message_matches)
    relation_matches = _relation_matches(predicted_relations, truth_relations, family_to_truth, families_by_id, truth_by_id)

    predicted_field_total = sum(len((family.get("field_hypotheses", []) or [])) for family in families)
    truth_field_total = sum(len((message_type.get("fields", []) or [])) for message_type in truth_types)
    semantic_tp = sum(1 for item in field_matches if float(item.get("semantic_score", 0.0) or 0.0) >= 0.5)

    message_metrics = _prf(len(message_matches), max(0, len(families) - len(message_matches)), max(0, len(truth_types) - len(message_matches)))
    boundary_metrics = _prf(len(field_matches), max(0, predicted_field_total - len(field_matches)), max(0, truth_field_total - len(field_matches)))
    semantic_metrics = _prf(semantic_tp, max(0, predicted_field_total - semantic_tp), max(0, truth_field_total - semantic_tp))
    relation_metrics = _prf(len(relation_matches), max(0, len(predicted_relations) - len(relation_matches)), max(0, len(truth_relations) - len(relation_matches)))
    overall = round((message_metrics["f1_score"] + boundary_metrics["f1_score"] + semantic_metrics["f1_score"] + relation_metrics["f1_score"]) / 4, 6)

    matched_predicted_fields = {(item["predicted"]["owner_id"], item["predicted"]["start"], item["predicted"].get("length")) for item in field_matches}
    matched_truth_fields = {(item["ground_truth"]["owner_id"], item["ground_truth"]["start"], item["ground_truth"].get("length")) for item in field_matches}
    unmatched_predicted_fields = []
    for family in families:
        family_id = str(family.get("family_id"))
        for index, field in enumerate(family.get("field_hypotheses", []) or []):
            ref = _predicted_field_ref(family_id, field, index)
            if (ref["owner_id"], ref["start"], ref.get("length")) not in matched_predicted_fields:
                unmatched_predicted_fields.append(ref)
    unmatched_truth_fields = []
    for message_type in truth_types:
        truth_id = str(message_type.get("message_type_id"))
        for index, field in enumerate(message_type.get("fields", []) or []):
            ref = _field_ref(truth_id, field, f"field_{index}")
            if (ref["owner_id"], ref["start"], ref.get("length")) not in matched_truth_fields:
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
            "predicted_families": sorted(set(families_by_id) - set(family_to_truth)),
            "ground_truth_message_types": sorted(set(truth_by_id) - set(family_to_truth.values())),
            "predicted_fields": unmatched_predicted_fields,
            "ground_truth_fields": unmatched_truth_fields,
        },
        "notes": [
            "Message type matching uses protocol-agnostic token, role, and field-count similarity.",
            "Field boundary matching uses byte-range overlap; semantic matching compares normalized field labels/types.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a reverse-engineered protocol spec against ground truth.")
    parser.add_argument("evaluation_model_data_json", help="Prepared model data from 16_prepare_evaluation_data.py")
    parser.add_argument("ground_truth_json", help="Ground truth JSON using evaluation_input.schema.json ground_truth_protocol shape")
    parser.add_argument("output_json", help="Output final evaluation report JSON")
    args = parser.parse_args()

    report = evaluate_protocol_spec(_load_json(args.evaluation_model_data_json), _load_json(args.ground_truth_json))
    report["inputs"] = {
        "predicted_protocol_file": args.evaluation_model_data_json,
        "ground_truth_protocol_file": args.ground_truth_json,
    }
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(f"[+] Wrote final protocol evaluation report to {output_path}")


if __name__ == "__main__":
    main()
