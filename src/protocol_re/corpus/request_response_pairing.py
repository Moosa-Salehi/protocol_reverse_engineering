from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from protocol_re.model.schema import FamilyAssignment, MessageRecord, PairRecord
from protocol_re.config.thresholds import RequestResponsePairing as _RRP

from protocol_re.utils.bytes import hex_to_bytes


REQUEST_DIRECTIONS = {"client_to_server", "initiator_to_responder"}
RESPONSE_DIRECTIONS = {"server_to_client", "responder_to_initiator"}


def _family_lookup(assignments: Sequence[FamilyAssignment]) -> Dict[int, str]:
    return {assignment.msg_id: assignment.family_id for assignment in assignments}


def _endpoint(record: MessageRecord, side: str) -> Tuple[str, int]:
    if side == "src":
        return (record.src_ip, int(record.src_port or 0))
    return (record.dst_ip, int(record.dst_port or 0))


def _infer_server_endpoint(session_records: Sequence[MessageRecord]) -> Optional[Tuple[str, int]]:
    if not session_records:
        return None
    endpoint_counts: Counter[Tuple[str, int]] = Counter()
    port_peer_counts: Dict[int, set[Tuple[str, int]]] = defaultdict(set)
    for record in session_records:
        src = _endpoint(record, "src")
        dst = _endpoint(record, "dst")
        if src[1] > 0:
            endpoint_counts[src] += 1
            port_peer_counts[src[1]].add(dst)
        if dst[1] > 0:
            endpoint_counts[dst] += 1
            port_peer_counts[dst[1]].add(src)

    if endpoint_counts:
        scored = []
        for endpoint, count in endpoint_counts.items():
            port = endpoint[1]
            peer_cardinality = len(port_peer_counts.get(port, set()))
            stable_port_bonus = 1 if peer_cardinality > 1 else 0
            low_port_bonus = 1 if 0 < port < 49152 else 0
            scored.append((stable_port_bonus, peer_cardinality, low_port_bonus, count, -port, endpoint))
        scored.sort(reverse=True)
        if scored[0][0] or scored[0][1] or scored[0][2]:
            return scored[0][-1]

    first = min(
        session_records,
        key=lambda record: (
            record.timestamp if record.timestamp is not None else float("inf"),
            record.index_in_session,
        ),
    )
    return _endpoint(first, "dst")


def _with_inferred_directions(session_records: Sequence[MessageRecord]) -> List[MessageRecord]:
    if any(record.direction != "unknown" for record in session_records):
        return list(session_records)
    server = _infer_server_endpoint(session_records)
    if server is None:
        return list(session_records)
    inferred = []
    for record in session_records:
        if _endpoint(record, "dst") == server and _endpoint(record, "src") != server:
            record.direction = "client_to_server"
            record.metadata.setdefault("direction_inference", "server_endpoint")
        elif _endpoint(record, "src") == server and _endpoint(record, "dst") != server:
            record.direction = "server_to_client"
            record.metadata.setdefault("direction_inference", "server_endpoint")
        inferred.append(record)
    return inferred


def infer_missing_directions(records: Sequence[MessageRecord]) -> List[MessageRecord]:
    sessions: Dict[str, List[MessageRecord]] = defaultdict(list)
    for record in records:
        sessions[record.session_id].append(record)
    inferred_records: List[MessageRecord] = []
    for session_records in sessions.values():
        session_records.sort(key=lambda record: record.index_in_session)
        inferred_records.extend(_with_inferred_directions(session_records))
    return inferred_records


def _pair_score(request: MessageRecord, response: MessageRecord) -> Tuple[float, Dict[str, float]]:
    evidence: Dict[str, float] = {}
    score = 0.0

    index_gap = response.index_in_session - request.index_in_session
    if index_gap <= 0:
        return -1.0, {"invalid_order": 1.0}
    evidence["index_gap"] = float(index_gap)
    score += max(0.0, 2.0 - 0.25 * (index_gap - 1))

    if request.direction in REQUEST_DIRECTIONS and response.direction in RESPONSE_DIRECTIONS:
        evidence["opposite_direction"] = 1.0
        score += 1.5
    elif request.direction == "unknown" or response.direction == "unknown":
        evidence["direction_unknown"] = 1.0
        score += 0.5
    elif request.direction != response.direction:
        evidence["different_direction"] = 1.0
        score += 1.0

    if request.src_ip == response.dst_ip and request.dst_ip == response.src_ip:
        evidence["endpoint_reversal"] = 1.0
        score += 1.0

    length_delta = abs(request.payload_len - response.payload_len)
    evidence["length_delta"] = float(length_delta)
    score += max(0.0, 1.0 - min(length_delta, 32) / 32.0)

    if request.timestamp is not None and response.timestamp is not None:
        latency_ms = max(0.0, (response.timestamp - request.timestamp) * 1000.0)
        evidence["latency_ms"] = latency_ms
        score += max(0.0, 1.0 - min(latency_ms, 1000.0) / 1000.0)

    return score, evidence


def _field_value(payload: bytes, offset: int, width: int) -> Optional[bytes]:
    if len(payload) < offset + width:
        return None
    return payload[offset : offset + width]


def detect_correlation_field(
    session_records: Sequence[MessageRecord],
    window: int = _RRP.CORRELATION_WINDOW,
    max_offset: int = _RRP.CORRELATION_MAX_OFFSET,
    widths: Sequence[int] = _RRP.CORRELATION_WIDTHS,
    sample: int = _RRP.CORRELATION_DETECTION_SAMPLE,
    min_coverage: float = _RRP.CORRELATION_MIN_COVERAGE,
    min_distinct_ratio: float = _RRP.CORRELATION_MIN_DISTINCT_RATIO,
) -> Optional[Tuple[int, int]]:
    """Detect a transaction/correlation-id field (offset, width).

    A correlation id is a header field that (a) varies across messages (so a
    constant protocol-id is rejected) and (b) whose value matches a nearby
    message within ``window`` positions for most messages (request/response
    echo). Returns the best ``(offset, width)`` or ``None``.
    """
    payloads = [hex_to_bytes(record.payload_hex) for record in session_records[:sample]]
    n = len(payloads)
    if n < 4:
        return None

    best: Optional[Tuple[float, float, int, int]] = None  # (coverage, distinct_ratio, -offset, width)
    for width in sorted({int(w) for w in widths if int(w) > 0}):
        for offset in range(0, max_offset):
            values = [_field_value(payload, offset, width) for payload in payloads]
            present = [value for value in values if value is not None]
            if len(present) < 4:
                continue
            distinct_ratio = len(set(present)) / len(present)
            if distinct_ratio < min_distinct_ratio:
                continue  # constant / low-cardinality field is not a correlation id
            partnered = 0
            for i, value in enumerate(values):
                if value is None:
                    continue
                lo = max(0, i - window)
                hi = min(n, i + window + 1)
                if any(j != i and values[j] == value for j in range(lo, hi)):
                    partnered += 1
            coverage = partnered / len(present)
            if coverage < min_coverage:
                continue
            candidate = (coverage, distinct_ratio, -offset, width)
            if best is None or candidate > best:
                best = candidate

    if best is None:
        return None
    return (-best[2], best[3])


def _pair_session_by_correlation(
    session_records: Sequence[MessageRecord],
    field: Tuple[int, int],
    session_id: str,
    family_by_msg_id: Dict[int, str],
    min_score: float,
    window: int = _RRP.CORRELATION_WINDOW,
) -> List[PairRecord]:
    offset, width = field
    payloads = [hex_to_bytes(record.payload_hex) for record in session_records]
    values = [_field_value(payload, offset, width) for payload in payloads]
    used = [False] * len(session_records)
    pairs: List[PairRecord] = []

    for i, request in enumerate(session_records):
        if used[i] or values[i] is None:
            continue
        partner_index: Optional[int] = None
        for j in range(i + 1, min(len(session_records), i + 1 + window)):
            if not used[j] and values[j] == values[i]:
                partner_index = j
                break
        if partner_index is None:
            continue
        response = session_records[partner_index]
        score, evidence = _pair_score(request, response)
        if score < 0:
            continue
        # Matching correlation id is strong evidence on top of ordering/length.
        score += 1.5
        evidence["correlation_id_match"] = 1.0
        evidence["correlation_offset"] = float(offset)
        evidence["correlation_width"] = float(width)
        evidence["pairing_mode"] = "correlation_id"
        if score < min_score:
            continue
        used[i] = True
        used[partner_index] = True
        pairs.append(
            PairRecord(
                request_msg_id=request.msg_id,
                response_msg_id=response.msg_id,
                session_id=session_id,
                score=round(score, 4),
                latency_ms=evidence.get("latency_ms"),
                request_family_id=family_by_msg_id.get(request.msg_id),
                response_family_id=family_by_msg_id.get(response.msg_id),
                evidence=evidence,
            )
        )
    return pairs


def pair_request_response_messages(
    records: Sequence[MessageRecord],
    assignments: Optional[Sequence[FamilyAssignment]] = None,
    min_score: float = 1.5,
    max_index_gap: int = 3,
) -> List[PairRecord]:
    family_by_msg_id = _family_lookup(assignments or [])
    sessions: Dict[str, List[MessageRecord]] = defaultdict(list)
    for record in records:
        sessions[record.session_id].append(record)

    pairs: List[PairRecord] = []
    for session_id, session_records in sessions.items():
        session_records.sort(key=lambda record: record.index_in_session)
        session_records = _with_inferred_directions(session_records)
        known_directions = {record.direction for record in session_records if record.direction != "unknown"}

        # Preferred strategy: pair on a detected transaction/correlation-id field.
        # This is robust to captures that start mid-stream with an orphan response
        # (which globally shifts adjacency-based pairing by one).
        correlation_field = detect_correlation_field(session_records)
        if correlation_field is not None:
            correlation_pairs = _pair_session_by_correlation(
                session_records,
                correlation_field,
                session_id,
                family_by_msg_id,
                min_score=min_score,
            )
            if correlation_pairs:
                pairs.extend(correlation_pairs)
                continue

        if not known_directions:
            for request, response in zip(session_records[0::2], session_records[1::2]):
                score, evidence = _pair_score(request, response)
                if score < min_score:
                    continue
                pairs.append(
                    PairRecord(
                        request_msg_id=request.msg_id,
                        response_msg_id=response.msg_id,
                        session_id=session_id,
                        score=round(score, 4),
                        latency_ms=evidence.get("latency_ms"),
                        request_family_id=family_by_msg_id.get(request.msg_id),
                        response_family_id=family_by_msg_id.get(response.msg_id),
                        evidence={**evidence, "pairing_mode": "adjacent_unknown_direction"},
                    )
                )
            continue

        used_response_ids = set()

        for idx, request in enumerate(session_records):
            if request.direction in RESPONSE_DIRECTIONS:
                continue
            best_response: Optional[MessageRecord] = None
            best_score = -1.0
            best_evidence: Dict[str, float] = {}

            for response in session_records[idx + 1 : idx + 1 + max_index_gap]:
                if response.msg_id in used_response_ids:
                    continue
                if request.direction in REQUEST_DIRECTIONS and response.direction not in RESPONSE_DIRECTIONS:
                    continue
                score, evidence = _pair_score(request, response)
                if score > best_score:
                    best_score = score
                    best_response = response
                    best_evidence = evidence

            if best_response is None or best_score < min_score:
                continue

            used_response_ids.add(best_response.msg_id)
            latency_ms = best_evidence.get("latency_ms")
            pairs.append(
                PairRecord(
                    request_msg_id=request.msg_id,
                    response_msg_id=best_response.msg_id,
                    session_id=session_id,
                    score=round(best_score, 4),
                    latency_ms=latency_ms,
                    request_family_id=family_by_msg_id.get(request.msg_id),
                    response_family_id=family_by_msg_id.get(best_response.msg_id),
                    evidence=best_evidence,
                )
            )

    return pairs
