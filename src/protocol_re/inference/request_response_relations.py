from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilyAssignment, MessageRecord, PairRecord
from protocol_re.utils.bytes import hex_to_bytes, safe_int_from_bytes


MAX_ECHO_WIDTH = 4



def _message_lookup(records: Sequence[MessageRecord]) -> Dict[int, MessageRecord]:
    return {record.msg_id: record for record in records}



def _family_lookup(assignments: Sequence[FamilyAssignment]) -> Dict[int, str]:
    return {assignment.msg_id: assignment.family_id for assignment in assignments}



def _pair_by_family(pairs: Sequence[PairRecord]) -> Dict[Tuple[str, str], List[PairRecord]]:
    grouped: Dict[Tuple[str, str], List[PairRecord]] = defaultdict(list)
    for pair in pairs:
        req_family = pair.request_family_id or "unknown_request_family"
        resp_family = pair.response_family_id or "unknown_response_family"
        if req_family.startswith("unknown_") or resp_family.startswith("unknown_"):
            continue
        grouped[(req_family, resp_family)].append(pair)
    return grouped



def _echo_candidates(request_payloads: Sequence[bytes], response_payloads: Sequence[bytes], min_support: float = 0.9) -> List[Dict[str, object]]:
    candidates: List[Dict[str, object]] = []
    if not request_payloads or not response_payloads:
        return candidates

    req_max_len = max((len(payload) for payload in request_payloads), default=0)
    resp_max_len = max((len(payload) for payload in response_payloads), default=0)

    for width in range(1, MAX_ECHO_WIDTH + 1):
        for req_start in range(0, max(0, req_max_len - width + 1)):
            for resp_start in range(0, max(0, resp_max_len - width + 1)):
                usable = 0
                matches = 0
                for request, response in zip(request_payloads, response_payloads):
                    if len(request) < req_start + width or len(response) < resp_start + width:
                        continue
                    usable += 1
                    if request[req_start : req_start + width] == response[resp_start : resp_start + width]:
                        matches += 1
                if usable == 0:
                    continue
                support = matches / usable
                if support >= min_support:
                    candidates.append(
                        {
                            "request_offset": req_start,
                            "response_offset": resp_start,
                            "width": width,
                            "support": round(support, 4),
                            "usable_pairs": usable,
                        }
                    )
    candidates.sort(key=lambda item: (-item["support"], -item["width"], item["request_offset"], item["response_offset"]))
    return candidates[:20]



def _length_relations(request_payloads: Sequence[bytes], response_payloads: Sequence[bytes], min_support: float = 0.9) -> List[Dict[str, object]]:
    relations: List[Dict[str, object]] = []
    if not request_payloads or not response_payloads:
        return relations

    req_max_len = max((len(payload) for payload in request_payloads), default=0)
    resp_lengths = [len(payload) for payload in response_payloads]
    avg_resp_len = mean(resp_lengths) if resp_lengths else 0.0

    for width in (1, 2, 4):
        for start in range(0, max(0, req_max_len - width + 1)):
            for endian in ("big", "little"):
                usable = 0
                equals_response_length = 0
                equals_delta = 0
                for request, response in zip(request_payloads, response_payloads):
                    if len(request) < start + width:
                        continue
                    usable += 1
                    value = safe_int_from_bytes(request[start : start + width], endian=endian)
                    if value == len(response):
                        equals_response_length += 1
                    if value == max(0, len(response) - len(request)):
                        equals_delta += 1
                if usable == 0:
                    continue
                support_len = equals_response_length / usable
                support_delta = equals_delta / usable
                best_support = max(support_len, support_delta)
                if best_support >= min_support:
                    relation_type = "request_field_equals_response_length" if support_len >= support_delta else "request_field_equals_length_delta"
                    relations.append(
                        {
                            "request_offset": start,
                            "width": width,
                            "endian": endian,
                            "relation_type": relation_type,
                            "support": round(best_support, 4),
                            "usable_pairs": usable,
                            "avg_response_length": round(avg_resp_len, 2),
                        }
                    )
    relations.sort(key=lambda item: (-item["support"], item["request_offset"], item["width"]))
    return relations[:20]



def summarize_family_relations(
    records: Sequence[MessageRecord],
    pairs: Sequence[PairRecord],
    assignments: Sequence[FamilyAssignment],
    min_echo_support: float = 0.9,
    min_length_support: float = 0.9,
) -> Dict[str, object]:
    messages_by_id = _message_lookup(records)
    family_by_msg_id = _family_lookup(assignments)

    for pair in pairs:
        if pair.request_family_id is None:
            pair.request_family_id = family_by_msg_id.get(pair.request_msg_id)
        if pair.response_family_id is None:
            pair.response_family_id = family_by_msg_id.get(pair.response_msg_id)

    family_edges = []
    family_roles: Dict[str, Counter] = defaultdict(Counter)

    for (request_family, response_family), family_pairs in sorted(_pair_by_family(pairs).items()):
        request_payloads = []
        response_payloads = []
        scores = []
        latencies = []

        for pair in family_pairs:
            request = messages_by_id.get(pair.request_msg_id)
            response = messages_by_id.get(pair.response_msg_id)
            if request is None or response is None:
                continue
            request_payloads.append(hex_to_bytes(request.payload_hex))
            response_payloads.append(hex_to_bytes(response.payload_hex))
            scores.append(pair.score)
            if pair.latency_ms is not None:
                latencies.append(pair.latency_ms)

        if not request_payloads or not response_payloads:
            continue

        echo_candidates = _echo_candidates(request_payloads, response_payloads, min_support=min_echo_support)
        length_relations = _length_relations(request_payloads, response_payloads, min_support=min_length_support)
        family_roles[request_family]["request_like"] += len(family_pairs)
        family_roles[response_family]["response_like"] += len(family_pairs)

        family_edges.append(
            {
                "request_family_id": request_family,
                "response_family_id": response_family,
                "pair_count": len(family_pairs),
                "avg_pair_score": round(mean(scores), 4) if scores else 0.0,
                "avg_latency_ms": round(mean(latencies), 4) if latencies else None,
                "echo_fields": echo_candidates,
                "length_relations": length_relations,
            }
        )

    role_hints = {}
    for family_id, counts in family_roles.items():
        request_like = counts.get("request_like", 0)
        response_like = counts.get("response_like", 0)
        if request_like > response_like:
            hint = "request"
        elif response_like > request_like:
            hint = "response"
        else:
            hint = "unknown"
        role_hints[family_id] = {
            "role_hint": hint,
            "request_like_pairs": request_like,
            "response_like_pairs": response_like,
        }

    return {
        "family_edges": family_edges,
        "role_hints": role_hints,
    }
