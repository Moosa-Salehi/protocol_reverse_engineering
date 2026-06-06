from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, stdev
from typing import Dict, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilyAssignment, MessageRecord, PairRecord
from protocol_re.corpus.request_response_pairing import infer_missing_directions
from protocol_re.utils.bytes import hex_to_bytes, safe_int_from_bytes


MAX_ECHO_WIDTH = 4
DEFAULT_MIN_EDGE_PAIRS = 2
DEFAULT_MIN_EDGE_LIFT = 1.0
DEFAULT_MAX_RESPONSE_FAMILIES_PER_REQUEST = 5

# A4: Tightened performance limits for echo/length field detection
MAX_ECHO_SEARCH_LENGTH = 64  # Reduced from 256 to focus on header regions (first 64 bytes)
MAX_LENGTH_FIELD_SEARCH_LENGTH = 64  # Reduced from 128 to focus on header regions
ECHO_SEARCH_STRIDE = 1
MAX_EVIDENCE_PAIRS_PER_EDGE = 500

# A4: Stricter thresholds for relation detection
DEFAULT_MIN_ECHO_SUPPORT = 0.8
DEFAULT_MIN_LENGTH_SUPPORT = 0.75
MIN_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence to keep a relation



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


def _sample_pairs(items: Sequence[Tuple[bytes, bytes]], max_items: int = MAX_EVIDENCE_PAIRS_PER_EDGE) -> List[Tuple[bytes, bytes]]:
    if len(items) <= max_items:
        return list(items)
    step = len(items) / max_items
    return [items[min(int(index * step), len(items) - 1)] for index in range(max_items)]


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


# A4: Helper function to detect if a field is likely a counter or timestamp
def _is_likely_counter_or_timestamp(values: List[int]) -> bool:
    """
    Detect if a sequence of values is likely a counter or timestamp.
    Counters: monotonically increasing or cycling with small deltas
    Timestamps: large values with small deltas
    """
    if len(values) < 3:
        return False

    # Check for monotonic increase (counter)
    increasing = sum(1 for i in range(len(values) - 1) if values[i + 1] > values[i])
    if increasing / (len(values) - 1) > 0.8:  # 80% increasing
        return True

    # Check for cycling pattern (counter wrapping)
    deltas = [abs(values[i + 1] - values[i]) for i in range(len(values) - 1)]
    if deltas:
        avg_delta = mean(deltas)
        if avg_delta < 10:  # Small deltas suggest counter
            return True

    # Check for timestamp-like values (large numbers with small relative changes)
    if values:
        avg_value = mean(values)
        if avg_value > 1000000 and deltas:  # Large values
            relative_deltas = [d / avg_value for d in deltas if avg_value > 0]
            if relative_deltas and mean(relative_deltas) < 0.01:  # Small relative change
                return True

    return False


# A4: Helper function to calculate confidence score for echo fields
def _calculate_echo_confidence(
    width: int,
    support: float,
    usable_pairs: int,
    request_offset: int,
    response_offset: int,
    request_values: List[int],
    response_values: List[int],
) -> float:
    """
    Calculate confidence score for an echo field candidate.
    Higher confidence for:
    - Wider fields (2-4 bytes preferred over 1 byte)
    - Higher support (>95%)
    - More usable pairs
    - Header region (first 32 bytes)
    - Not a counter or timestamp
    """
    confidence = 0.0

    # Base confidence from support
    confidence += support * 0.4  # Max 0.4

    # Width bonus: prioritize 2-byte and 4-byte fields (typical transaction IDs)
    if width == 2:
        confidence += 0.25
    elif width == 4:
        confidence += 0.25
    elif width == 1:
        confidence += 0.05  # Low confidence for single-byte echoes
    else:
        confidence += 0.15

    # Position bonus: prefer header regions (first 32 bytes)
    if request_offset < 32 and response_offset < 32:
        confidence += 0.15
    elif request_offset < 64 and response_offset < 64:
        confidence += 0.10
    else:
        confidence += 0.05

    # Sample size bonus
    if usable_pairs >= 10:
        confidence += 0.10
    elif usable_pairs >= 5:
        confidence += 0.05

    same_series = request_values == response_values
    # Penalize counter-like echoes only when they are not exact request/response echoes;
    # exact 2/4-byte echoes are common transaction identifiers.
    if not same_series and (
        _is_likely_counter_or_timestamp(request_values) or _is_likely_counter_or_timestamp(response_values)
    ):
        confidence *= 0.3
    if same_series and width in (2, 4):
        confidence += 0.1

    return min(1.0, confidence)


def _echo_candidates(request_payloads: Sequence[bytes], response_payloads: Sequence[bytes], min_support: float = DEFAULT_MIN_ECHO_SUPPORT) -> List[Dict[str, object]]:
    candidates: List[Dict[str, object]] = []
    if not request_payloads or not response_payloads:
        return candidates

    req_max_len = max((len(payload) for payload in request_payloads), default=0)
    resp_max_len = max((len(payload) for payload in response_payloads), default=0)

    # A4: Limit search space to header regions only (first 64 bytes)
    req_search_len = min(req_max_len, MAX_ECHO_SEARCH_LENGTH)
    resp_search_len = min(resp_max_len, MAX_ECHO_SEARCH_LENGTH)

    for width in range(1, MAX_ECHO_WIDTH + 1):
        for req_start in range(0, max(0, req_search_len - width + 1), ECHO_SEARCH_STRIDE):
            for resp_start in range(0, max(0, resp_search_len - width + 1), ECHO_SEARCH_STRIDE):
                usable = 0
                matches = 0
                request_values = []
                response_values = []

                for request, response in zip(request_payloads, response_payloads):
                    if len(request) < req_start + width or len(response) < resp_start + width:
                        continue
                    usable += 1
                    req_chunk = request[req_start : req_start + width]
                    resp_chunk = response[resp_start : resp_start + width]

                    if req_chunk == resp_chunk:
                        matches += 1

                    # Collect values for counter/timestamp detection (for 1-4 byte fields)
                    if width <= 4:
                        req_val = safe_int_from_bytes(req_chunk, endian="big")
                        resp_val = safe_int_from_bytes(resp_chunk, endian="big")
                        request_values.append(req_val)
                        response_values.append(resp_val)

                if usable == 0:
                    continue
                support = matches / usable
                if support >= min_support:
                    # A4: Calculate confidence score
                    confidence = _calculate_echo_confidence(
                        width, support, usable, req_start, resp_start,
                        request_values, response_values
                    )

                    candidates.append(
                        {
                            "request_offset": req_start,
                            "response_offset": resp_start,
                            "width": width,
                            "support": round(support, 4),
                            "usable_pairs": usable,
                            "confidence": round(confidence, 4),
                        }
                    )

    # A4: Sort by confidence first, then support, then width
    candidates.sort(key=lambda item: (-item["confidence"], -item["support"], -item["width"], item["request_offset"], item["response_offset"]))

    # A4: Filter by minimum confidence threshold and deduplicate
    filtered_candidates = []
    seen_positions = set()

    for candidate in candidates:
        if candidate["confidence"] < MIN_CONFIDENCE_THRESHOLD:
            continue

        # Deduplicate: skip if we already have an overlapping echo field with higher confidence
        position_key = (candidate["request_offset"], candidate["response_offset"], candidate["width"])
        if position_key in seen_positions:
            continue

        # Check for overlapping fields
        overlaps = False
        for seen_req_off, seen_resp_off, seen_width in seen_positions:
            req_overlap = (
                candidate["request_offset"] < seen_req_off + seen_width and
                candidate["request_offset"] + candidate["width"] > seen_req_off
            )
            resp_overlap = (
                candidate["response_offset"] < seen_resp_off + seen_width and
                candidate["response_offset"] + candidate["width"] > seen_resp_off
            )
            if req_overlap and resp_overlap:
                overlaps = True
                break

        if not overlaps:
            filtered_candidates.append(candidate)
            seen_positions.add(position_key)

    return filtered_candidates[:10]  # Return top 10 instead of 20


# A4: Helper function to calculate confidence score for length relations
def _calculate_length_confidence(
    width: int,
    support: float,
    usable_pairs: int,
    request_offset: int,
    relation_type: str,
    field_values: List[int],
    avg_response_length: float,
) -> float:
    """
    Calculate confidence score for a length relation candidate.
    Higher confidence for:
    - Higher support (>95%)
    - Consistent position (header region)
    - Reasonable length values (not random)
    - Not a counter or address
    """
    confidence = 0.0

    # Base confidence from support
    confidence += support * 0.5  # Max 0.5

    # Width bonus: prefer 1, 2, or 4 byte length fields
    if width in (1, 2, 4):
        confidence += 0.2
    else:
        confidence += 0.1

    # Position bonus: prefer header regions (first 32 bytes)
    if request_offset < 32:
        confidence += 0.15
    elif request_offset < 64:
        confidence += 0.10
    else:
        confidence += 0.05

    # Sample size bonus
    if usable_pairs >= 10:
        confidence += 0.10
    elif usable_pairs >= 5:
        confidence += 0.05

    # Monotonic request count/quantity fields are valid length predictors; penalize
    # counter-like fields only for exact length rules where no correlation is shown.
    if relation_type != "request_field_correlates_response_length" and _is_likely_counter_or_timestamp(field_values):
        confidence *= 0.2

    # Penalty for unreasonable length values (too large or too small)
    if field_values:
        avg_value = mean(field_values)
        if avg_value < 1 or avg_value > 65535:  # Unreasonable length
            confidence *= 0.5

        # Check if values are consistent with actual response lengths
        if avg_response_length > 0:
            ratio = avg_value / avg_response_length
            if relation_type == "request_field_equals_response_length":
                if 0.8 <= ratio <= 1.2:  # Within 20% of actual length
                    confidence += 0.05
            elif relation_type == "request_field_equals_length_delta":
                if ratio < 2.0:  # Delta should be smaller than full length
                    confidence += 0.05

    return min(1.0, confidence)


def _length_relations(request_payloads: Sequence[bytes], response_payloads: Sequence[bytes], min_support: float = DEFAULT_MIN_LENGTH_SUPPORT) -> List[Dict[str, object]]:
    relations: List[Dict[str, object]] = []
    if not request_payloads or not response_payloads:
        return relations

    req_max_len = max((len(payload) for payload in request_payloads), default=0)
    resp_lengths = [len(payload) for payload in response_payloads]
    avg_resp_len = mean(resp_lengths) if resp_lengths else 0.0

    # A4: Limit search space to header regions only (first 64 bytes)
    req_search_len = min(req_max_len, MAX_LENGTH_FIELD_SEARCH_LENGTH)

    for width in (1, 2, 4):
        for start in range(0, max(0, req_search_len - width + 1)):
            for endian in ("big", "little"):
                usable = 0
                equals_response_length = 0
                equals_delta = 0
                field_values = []

                for request, response in zip(request_payloads, response_payloads):
                    if len(request) < start + width:
                        continue
                    usable += 1
                    value = safe_int_from_bytes(request[start : start + width], endian=endian)
                    field_values.append(value)

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

                    # A4: Calculate confidence score
                    confidence = _calculate_length_confidence(
                        width, best_support, usable, start, relation_type,
                        field_values, avg_resp_len
                    )

                    relations.append(
                        {
                            "request_offset": start,
                            "width": width,
                            "endian": endian,
                            "relation_type": relation_type,
                            "support": round(best_support, 4),
                            "usable_pairs": usable,
                            "avg_response_length": round(avg_resp_len, 2),
                            "confidence": round(confidence, 4),
                        }
                    )

    # A4: Sort by confidence first, then support
    relations.sort(key=lambda item: (-item["confidence"], -item["support"], item["request_offset"], item["width"]))

    # A4: Filter by minimum confidence threshold and deduplicate
    filtered_relations = []
    seen_positions = set()

    for relation in relations:
        if relation["confidence"] < MIN_CONFIDENCE_THRESHOLD:
            continue

        # Deduplicate: keep only one relation per position (prefer higher confidence)
        position_key = (relation["request_offset"], relation["width"])
        if position_key in seen_positions:
            continue

        filtered_relations.append(relation)
        seen_positions.add(position_key)

    return filtered_relations[:10]  # Return top 10 instead of 20


def _correlation(xs: Sequence[float], ys: Sequence[float]) -> float:
    if len(xs) < 3 or len(xs) != len(ys):
        return 0.0
    mean_x = mean(xs)
    mean_y = mean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denom_x = sum((x - mean_x) ** 2 for x in xs)
    denom_y = sum((y - mean_y) ** 2 for y in ys)
    if denom_x <= 0.0 or denom_y <= 0.0:
        return 0.0
    return numerator / ((denom_x * denom_y) ** 0.5)


def _length_correlation_relations(
    request_payloads: Sequence[bytes],
    response_payloads: Sequence[bytes],
    min_support: float = DEFAULT_MIN_LENGTH_SUPPORT,
) -> List[Dict[str, object]]:
    relations: List[Dict[str, object]] = []
    if not request_payloads or not response_payloads:
        return relations
    req_max_len = max((len(payload) for payload in request_payloads), default=0)
    req_search_len = min(req_max_len, MAX_LENGTH_FIELD_SEARCH_LENGTH)
    response_lengths = [float(len(payload)) for payload in response_payloads]

    for width in (1, 2, 4):
        for start in range(0, max(0, req_search_len - width + 1)):
            for endian in ("big", "little"):
                usable_values = []
                usable_lengths = []
                for request, response in zip(request_payloads, response_payloads):
                    if len(request) < start + width:
                        continue
                    value = safe_int_from_bytes(request[start : start + width], endian=endian)
                    usable_values.append(float(value))
                    usable_lengths.append(float(len(response)))
                if len(usable_values) < 3 or len(set(usable_values)) < 2 or len(set(usable_lengths)) < 2:
                    continue
                corr = _correlation(usable_values, usable_lengths)
                support = max(0.0, corr)
                if support < min_support:
                    continue
                slope = 0.0
                var_x = sum((value - mean(usable_values)) ** 2 for value in usable_values)
                if var_x > 0:
                    slope = sum(
                        (x - mean(usable_values)) * (y - mean(usable_lengths))
                        for x, y in zip(usable_values, usable_lengths)
                    ) / var_x
                if slope <= 0:
                    continue
                confidence = _calculate_length_confidence(
                    width,
                    support,
                    len(usable_values),
                    start,
                    "request_field_correlates_response_length",
                    [int(value) for value in usable_values],
                    mean(response_lengths) if response_lengths else 0.0,
                )
                relations.append(
                    {
                        "request_offset": start,
                        "width": width,
                        "endian": endian,
                        "relation_type": "request_field_correlates_response_length",
                        "support": round(support, 4),
                        "usable_pairs": len(usable_values),
                        "avg_response_length": round(mean(response_lengths), 2) if response_lengths else 0.0,
                        "correlation": round(corr, 4),
                        "slope": round(slope, 4),
                        "confidence": round(confidence, 4),
                    }
                )

    relations.sort(key=lambda item: (-item["confidence"], -item["support"], item["request_offset"], item["width"]))
    filtered: List[Dict[str, object]] = []
    seen_positions = set()
    for relation in relations:
        if relation["confidence"] < MIN_CONFIDENCE_THRESHOLD:
            continue
        position_key = (relation["request_offset"], relation["width"])
        if position_key in seen_positions:
            continue
        filtered.append(relation)
        seen_positions.add(position_key)
    return filtered[:10]


# A4: Calculate overall relation confidence based on multiple evidence types
def _calculate_relation_confidence(
    edge_features: Dict[str, object],
    echo_fields: List[Dict[str, object]],
    length_relations: List[Dict[str, object]],
) -> float:
    """
    Calculate overall confidence for a family relation based on:
    - Edge features (pair count, lift, direction consistency, temporal ordering)
    - Echo field evidence (high-confidence echoes)
    - Length relation evidence (high-confidence length fields)
    """
    confidence = 0.0

    # Base confidence from edge features
    pair_count = int(edge_features.get("pair_count", 0))
    edge_lift = float(edge_features.get("edge_lift", 0.0))
    direction_consistency = float(edge_features.get("direction_consistency", 0.0))
    temporal_order_consistency = float(edge_features.get("temporal_order_consistency", 0.0))

    # Pair count contribution (max 0.2)
    if pair_count >= 10:
        confidence += 0.2
    elif pair_count >= 5:
        confidence += 0.15
    elif pair_count >= 2:
        confidence += 0.10

    # Edge lift contribution (max 0.2)
    if edge_lift >= 2.0:
        confidence += 0.2
    elif edge_lift >= 1.5:
        confidence += 0.15
    elif edge_lift >= 1.0:
        confidence += 0.10

    # Direction consistency contribution (max 0.2)
    confidence += direction_consistency * 0.2

    # Temporal ordering contribution (max 0.2)
    confidence += temporal_order_consistency * 0.2

    # Echo field evidence (max 0.1)
    if echo_fields:
        max_echo_confidence = max(e.get("confidence", 0.0) for e in echo_fields)
        confidence += max_echo_confidence * 0.1

    # Length relation evidence (max 0.1)
    if length_relations:
        max_length_confidence = max(r.get("confidence", 0.0) for r in length_relations)
        confidence += max_length_confidence * 0.1

    return min(1.0, confidence)



def summarize_family_relations(
    records: Sequence[MessageRecord],
    pairs: Sequence[PairRecord],
    assignments: Sequence[FamilyAssignment],
    min_echo_support: float = DEFAULT_MIN_ECHO_SUPPORT,
    min_length_support: float = DEFAULT_MIN_LENGTH_SUPPORT,
    min_edge_pairs: int = DEFAULT_MIN_EDGE_PAIRS,
    min_edge_lift: float = DEFAULT_MIN_EDGE_LIFT,
    max_response_families_per_request: int = DEFAULT_MAX_RESPONSE_FAMILIES_PER_REQUEST,
    allow_self_relations: bool = False,
    min_relation_confidence: float = MIN_CONFIDENCE_THRESHOLD,
) -> Dict[str, object]:
    records = infer_missing_directions(records)
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
        payload_pairs = []
        scores = []
        latencies = []

        for pair in family_pairs:
            request = messages_by_id.get(pair.request_msg_id)
            response = messages_by_id.get(pair.response_msg_id)
            if request is None or response is None:
                continue
            payload_pairs.append((hex_to_bytes(request.payload_hex), hex_to_bytes(response.payload_hex)))
            scores.append(pair.score)
            if pair.latency_ms is not None:
                latencies.append(pair.latency_ms)

        if not payload_pairs:
            continue
        evidence_payload_pairs = _sample_pairs(payload_pairs)
        request_payloads = [request for request, _response in evidence_payload_pairs]
        response_payloads = [response for _request, response in evidence_payload_pairs]

        echo_candidates = _echo_candidates(request_payloads, response_payloads, min_support=min_echo_support)
        length_relations = _length_relations(request_payloads, response_payloads, min_support=min_length_support)
        existing_length_keys = {
            (existing["request_offset"], existing["width"], existing["relation_type"])
            for existing in length_relations
        }
        for relation in _length_correlation_relations(
            request_payloads,
            response_payloads,
            min_support=min_length_support,
        ):
            key = (relation["request_offset"], relation["width"], relation["relation_type"])
            if key in existing_length_keys:
                continue
            length_relations.append(relation)
            existing_length_keys.add(key)

        # A4: Calculate overall relation confidence
        relation_confidence = _calculate_relation_confidence(edge_features, echo_candidates, length_relations)

        # A4: Filter out low-confidence relations
        if relation_confidence < min_relation_confidence:
            continue

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
                "relation_confidence": round(relation_confidence, 4),  # A4: Add overall confidence
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
