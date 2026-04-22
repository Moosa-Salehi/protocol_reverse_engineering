from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilyAssignment, FamilySemanticSummary, MessageRecord



def _field_key(field: Dict[str, object]) -> Tuple[int, int]:
    return (int(field.get("start", 0)), int(field.get("length", 0)))



def _covers(field: Dict[str, object], start: int, width: int) -> bool:
    field_start = int(field.get("start", 0))
    field_len = int(field.get("length", 0))
    field_end = field_start + field_len
    return field_start <= start and (start + width) <= field_end



def _best_covering_field(fields: Sequence[Dict[str, object]], start: int, width: int) -> Optional[Dict[str, object]]:
    candidates = [field for field in fields if _covers(field, start, width)]
    if not candidates:
        return None
    candidates.sort(key=lambda field: (int(field.get("length", 0)), int(field.get("start", 0))))
    return candidates[0]



def summarize_semantics(
    family_data: Dict[str, object],
    relations_payload: Dict[str, object],
) -> Dict[str, object]:
    role_hints = relations_payload.get("role_hints", {}) or {}
    family_edges = relations_payload.get("family_edges", []) or []
    semantics: Dict[str, object] = {}

    edges_by_request: Dict[str, List[Dict[str, object]]] = {}
    edges_by_response: Dict[str, List[Dict[str, object]]] = {}
    for edge in family_edges:
        edges_by_request.setdefault(edge["request_family_id"], []).append(edge)
        edges_by_response.setdefault(edge["response_family_id"], []).append(edge)

    for family_id, details in family_data.items():
        fields = list(details.get("field_hypotheses", []))
        field_labels: List[Dict[str, object]] = []
        notes: List[str] = []
        role_hint = role_hints.get(family_id, {})
        role = role_hint.get("role_hint", "unknown")
        role_conf = 0.0
        req_like = float(role_hint.get("request_like_pairs", 0))
        resp_like = float(role_hint.get("response_like_pairs", 0))
        total_like = req_like + resp_like
        if total_like > 0:
            role_conf = max(req_like, resp_like) / total_like

        for field in fields:
            label = {
                "start": field.get("start"),
                "length": field.get("length"),
                "label": field.get("field_type", "unknown"),
                "confidence": field.get("confidence", 0.0),
                "evidence": dict(field.get("evidence", {})),
            }
            field_labels.append(label)

        for edge in edges_by_request.get(family_id, []):
            for echo in edge.get("echo_fields", []):
                field = _best_covering_field(fields, int(echo["request_offset"]), int(echo["width"]))
                if field is None:
                    continue
                field_labels.append(
                    {
                        "start": field["start"],
                        "length": field["length"],
                        "label": "echoed_request_field",
                        "confidence": echo.get("support", 0.0),
                        "evidence": {
                            "response_family_id": edge["response_family_id"],
                            "response_offset": echo["response_offset"],
                            "support": echo.get("support", 0.0),
                        },
                    }
                )
                if int(field["length"]) in (2, 4):
                    field_labels.append(
                        {
                            "start": field["start"],
                            "length": field["length"],
                            "label": "transaction_or_correlation_id",
                            "confidence": min(0.99, 0.55 + 0.4 * float(echo.get("support", 0.0))),
                            "evidence": {
                                "response_family_id": edge["response_family_id"],
                                "echo_support": echo.get("support", 0.0),
                            },
                        }
                    )
            for rel in edge.get("length_relations", []):
                field = _best_covering_field(fields, int(rel["request_offset"]), int(rel["width"]))
                if field is None:
                    continue
                field_labels.append(
                    {
                        "start": field["start"],
                        "length": field["length"],
                        "label": "response_size_selector",
                        "confidence": rel.get("support", 0.0),
                        "evidence": {
                            "relation_type": rel.get("relation_type"),
                            "response_family_id": edge["response_family_id"],
                            "support": rel.get("support", 0.0),
                        },
                    }
                )

        for edge in edges_by_response.get(family_id, []):
            if edge.get("echo_fields"):
                notes.append(
                    f"Echoes request fields from {edge['request_family_id']} with up to {len(edge['echo_fields'])} strong offset matches."
                )
            if edge.get("length_relations"):
                notes.append(
                    f"Response size is tied to request fields from {edge['request_family_id']}."
                )

        deduped_labels: Dict[Tuple[int, int, str], Dict[str, object]] = {}
        for item in field_labels:
            key = (int(item["start"]), int(item["length"]), str(item["label"]))
            existing = deduped_labels.get(key)
            if existing is None or float(item.get("confidence", 0.0)) > float(existing.get("confidence", 0.0)):
                deduped_labels[key] = item

        semantics[family_id] = FamilySemanticSummary(
            family_id=family_id,
            role=role,
            confidence=round(role_conf, 4),
            field_labels=sorted(deduped_labels.values(), key=lambda item: (int(item["start"]), str(item["label"]))),
            notes=notes[:10],
        ).to_dict()

    return semantics
