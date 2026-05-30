from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilyAssignment, MessageRecord, PairRecord
from protocol_re.utils.bytes import hex_to_bytes, safe_int_from_bytes


MAX_ECHO_WIDTH = 4
DEFAULT_MIN_EDGE_PAIRS = 2
DEFAULT_MIN_EDGE_LIFT = 1.0
DEFAULT_MAX_RESPONSE_FAMILIES_PER_REQUEST = 5

# Performance limits for large payloads
MAX_ECHO_SEARCH_LENGTH = 256  # Limit echo field search to first 256 bytes
MAX_LENGTH_FIELD_SEARCH_LENGTH = 128  # Limit length field search to first 128 bytes
ECHO_SEARCH_STRIDE = 1  # Can increase to 2 or 4 for even faster search on very large payloads



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


def _order_consistent(request: MessageRecord, response: MessageRecord) -> Optional[bool]:
    if request.timestamp is not None and response.timestamp is not None:
        return response.timestamp >= request.timestamp
    if request.session_id == response.session_id:
        return response.index_in_session >= request.index_in_session
    return None


def _edge_features(
    request_family: str,
    response_family: str,
    family_pairs: Sequence[PairRecord],
    messages_by_id: Dict[int, MessageRecord],
    request_totals: Counter[str],
    response_totals: Counter[str],
    total_pairs: int,
) -> Dict[str, object]:
    pair_count = len(family_pairs)
    request_total = request_totals.get(request_family, 0)
    response_total = response_totals.get(response_family, 0)
    support_ratio = pair_count / request_total if request_total else 0.0
    expected = (request_total / total_pairs) * (response_total / total_pairs) if total_pairs else 0.0
    observed = pair_count / total_pairs if total_pairs else 0.0
    edge_lift = observed / expected if expected > 0.0 else 0.0

    direction_transitions: Counter[str] = Counter()
    ordered = 0
    order_usable = 0
    for pair in family_pairs:
        request = messages_by_id.get(pair.request_msg_id)
        response = messages_by_id.get(pair.response_msg_id)
        if request is None or response is None:
            continue
        direction_transitions[f"{request.direction}->{response.direction}"] += 1
        order_value = _order_consistent(request, response)
        if order_value is None:
            continue
        order_usable += 1
        if order_value:
            ordered += 1

    dominant_transition, dominant_count = direction_transitions.most_common(1)[0] if direction_transitions else ("unknown", 0)
    direction_consistency = dominant_count / pair_count if pair_count else 0.0
    temporal_order_consistency = ordered / order_usable if order_usable else 0.0

    return {
        "pair_count": pair_count,
        "support_ratio": round(support_ratio, 6),
        "edge_lift": round(edge_lift, 6),
        "direction_consistency": round(direction_consistency, 6),
        "dominant_direction": dominant_transition,
        "temporal_order_consistency": round(temporal_order_consistency, 6),
        "order_usable_pairs": order_usable,
    }


def _strong_self_relation(features: Dict[str, object], min_edge_pairs: int, min_edge_lift: float) -> bool:
    return (
        int(features["pair_count"]) >= max(min_edge_pairs * 3, 10)
        and float(features["edge_lift"]) >= max(min_edge_lift * 2.0, min_edge_lift)
        and float(features["direction_consistency"]) >= 0.9
        and float(features["temporal_order_consistency"]) >= 0.9
    )


def _prune_family_edges(
    grouped_pairs: Dict[Tuple[str, str], List[PairRecord]],
    messages_by_id: Dict[int, MessageRecord],
    min_edge_pairs: int,
    min_edge_lift: float,
    max_response_families_per_request: int,
    allow_self_relations: bool,
) -> List[Tuple[str, str, List[PairRecord], Dict[str, object]]]:
    total_pairs = sum(len(family_pairs) for family_pairs in grouped_pairs.values())
    request_totals: Counter[str] = Counter()
    response_totals: Counter[str] = Counter()
    for (request_family, response_family), family_pairs in grouped_pairs.items():
        request_totals[request_family] += len(family_pairs)
        response_totals[response_family] += len(family_pairs)

    retained_by_request: Dict[str, List[Tuple[str, str, List[PairRecord], Dict[str, object]]]] = defaultdict(list)
    for (request_family, response_family), family_pairs in grouped_pairs.items():
        features = _edge_features(
            request_family,
            response_family,
            family_pairs,
            messages_by_id,
            request_totals,
            response_totals,
            total_pairs,
        )
        if int(features["pair_count"]) < min_edge_pairs:
            continue
        if float(features["edge_lift"]) < min_edge_lift:
            continue
        if request_family == response_family and not allow_self_relations:
            if not _strong_self_relation(features, min_edge_pairs, min_edge_lift):
                continue
        retained_by_request[request_family].append((request_family, response_family, family_pairs, features))

    retained: List[Tuple[str, str, List[PairRecord], Dict[str, object]]] = []
    for request_family in sorted(retained_by_request):
        candidates = sorted(
            retained_by_request[request_family],
            key=lambda item: (
                -int(item[3]["pair_count"]),
                -float(item[3]["support_ratio"]),
                -float(item[3]["edge_lift"]),
                item[1],
            ),
        )
        retained.extend(candidates[:max_response_families_per_request])
    return retained



def _echo_candidates(request_payloads: Sequence[bytes], response_payloads: Sequence[bytes], min_support: float = 0.9) -> List[Dict[str, object]]:
    candidates: List[Dict[str, object]] = []
    if not request_payloads or not response_payloads:
        return candidates

    req_max_len = max((len(payload) for payload in request_payloads), default=0)
    resp_max_len = max((len(payload) for payload in response_payloads), default=0)

    # Limit search space to avoid performance issues with large payloads
    req_search_len = min(req_max_len, MAX_ECHO_SEARCH_LENGTH)
    resp_search_len = min(resp_max_len, MAX_ECHO_SEARCH_LENGTH)

    for width in range(1, MAX_ECHO_WIDTH + 1):
        for req_start in range(0, max(0, req_search_len - width + 1), ECHO_SEARCH_STRIDE):
            for resp_start in range(0, max(0, resp_search_len - width + 1), ECHO_SEARCH_STRIDE):
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

    # Limit search space to avoid performance issues with large payloads
    req_search_len = min(req_max_len, MAX_LENGTH_FIELD_SEARCH_LENGTH)

    for width in (1, 2, 4):
        for start in range(0, max(0, req_search_len - width + 1)):
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
    min_edge_pairs: int = DEFAULT_MIN_EDGE_PAIRS,
    min_edge_lift: float = DEFAULT_MIN_EDGE_LIFT,
    max_response_families_per_request: int = DEFAULT_MAX_RESPONSE_FAMILIES_PER_REQUEST,
    allow_self_relations: bool = False,
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
    grouped_pairs = _pair_by_family(pairs)
    retained_edges = _prune_family_edges(
        grouped_pairs,
        messages_by_id,
        min_edge_pairs=max(1, min_edge_pairs),
        min_edge_lift=min_edge_lift,
        max_response_families_per_request=max(1, max_response_families_per_request),
        allow_self_relations=allow_self_relations,
    )

    for request_family, response_family, family_pairs, edge_features in retained_edges:
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
                **edge_features,
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
