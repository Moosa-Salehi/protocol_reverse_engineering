from __future__ import annotations

from collections import Counter, defaultdict
from math import log2
from statistics import mean
from typing import Any, Dict, List, Optional, Sequence, Tuple

from protocol_re.config.thresholds import DiscriminatorDetection as _DD
from protocol_re.config.thresholds import FamilyRefinement as _FR
from protocol_re.inference.boundary_detection import infer_template
from protocol_re.model.schema import MessageRecord
from protocol_re.neural.salience import attention_offset_salience, encoder_gradient_salience, merge_salience_scores
from protocol_re.utils.bytes import hex_to_bytes

# Re-export for backward compatibility
SUPPRESSED_ROLE_TOKENS = _DD.SUPPRESSED_ROLE_TOKENS


def entropy(values: Sequence[Any]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    total = float(sum(counts.values()))
    return -sum((count / total) * log2(count / total) for count in counts.values())


def mutual_information(left: Sequence[Any], right: Sequence[Any]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    total = float(len(left))
    left_counts = Counter(left)
    right_counts = Counter(right)
    pair_counts = Counter(zip(left, right))
    value = 0.0
    for (lval, rval), count in pair_counts.items():
        pxy = count / total
        px = left_counts[lval] / total
        py = right_counts[rval] / total
        value += pxy * log2(pxy / (px * py))
    return value


def normalized_mi(left: Sequence[Any], right: Sequence[Any]) -> float:
    denom = max(entropy(left), entropy(right), 1e-9)
    return max(0.0, min(1.0, mutual_information(left, right) / denom))


def _offset_values(messages: Sequence[bytes], offset: int) -> Tuple[List[int], List[int]]:
    values: List[int] = []
    indexes: List[int] = []
    for index, message in enumerate(messages):
        if offset < len(message):
            values.append(message[offset])
            indexes.append(index)
    return values, indexes


def _offset_window_values(messages: Sequence[bytes], offset: int, width: int) -> Tuple[List[int], List[int]]:
    """Big-endian integer value of the ``width`` bytes at ``offset``.

    Only messages long enough to contain the full window contribute, so the
    returned ``indexes`` align with the contributing messages (mirroring
    :func:`_offset_values` for ``width == 1``)."""
    if width <= 1:
        return _offset_values(messages, offset)
    values: List[int] = []
    indexes: List[int] = []
    for index, message in enumerate(messages):
        if offset + width <= len(message):
            values.append(int.from_bytes(message[offset : offset + width], "big"))
            indexes.append(index)
    return values, indexes


def _length_field_match_ratio(messages: Sequence[bytes], offset: int, width: int) -> float:
    """Fraction of messages where the value at (offset, width) equals a length
    expression (payload_len, payload_len-offset, or payload_len-offset-width).
    A genuine length field matches in ~all messages; a type code only rarely."""
    values, indexes = _offset_window_values(messages, offset, width)
    if not values:
        return 0.0
    matches = 0
    for value, index in zip(values, indexes):
        length = len(messages[index])
        if value in (length, length - offset, length - offset - width):
            matches += 1
    return matches / len(values)


def detect_global_discriminator(
    records: Sequence[MessageRecord],
    family_by_msg_id: Dict[int, str],
    *,
    max_offset: int = _FR.MAX_OFFSET,
    widths: Sequence[int] = _FR.MULTI_BYTE_WIDTHS,
    min_global_mi: float = _FR.MIN_GLOBAL_MI,
    min_cardinality: int = _FR.MIN_CARDINALITY,
    max_cardinality: int = _FR.MAX_CARDINALITY,
    min_coverage: float = _FR.MIN_COVERAGE,
    max_stable_ratio: float = _FR.MAX_STABLE_RATIO,
    length_field_match_ratio: float = _FR.LENGTH_FIELD_MATCH_RATIO,
) -> Optional[Dict[str, Any]]:
    """Detect the corpus-wide type-discriminator (offset + width) label-free.

    A type/command code is a byte window that is present in (almost) every
    message, takes a small-to-moderate number of values, is neither constant nor
    a length field, and is not a high-cardinality address/counter/transaction id.
    Those structural gates alone reject the noise — crucially WITHOUT trusting
    the bootstrap clustering, which may not track message type at all.

    Selection between the survivors uses two modes:

    * **label-guided** — if some candidate's normalised mutual information with
      the bootstrap labels reaches ``min_global_mi`` (the bootstrap already
      separates by type), pick the highest-MI candidate. This matches the
      original intent and is best when clustering is good.
    * **structural fallback** — otherwise (a degraded bootstrap), pick the
      earliest qualifying window, i.e. the first type-like byte after the
      constant/length header. The opcode is conventionally the first body byte.

    Returns ``{offset, width, global_mi, cardinality}`` or ``None`` when nothing
    qualifies (text / unstructured corpora) so the caller passes assignments
    through unchanged.
    """
    messages: List[bytes] = []
    labels: List[str] = []
    for record in records:
        family_id = family_by_msg_id.get(record.msg_id)
        if family_id is None or family_id == "noise":
            continue
        messages.append(hex_to_bytes(record.payload_hex))
        labels.append(family_id)
    if len(messages) < 2 or len(set(labels)) < 2:
        return None

    scan_widths = sorted({int(width) for width in widths if int(width) >= 1})

    # Header bytes are the structural frame, never the type code: bytes that are
    # constant across the corpus (protocol-id, unit-id, ...) or that belong to a
    # length field. The discriminator must lie entirely outside them — this is
    # what stops a misaligned multi-byte window from straddling a length/constant
    # byte and masquerading as a low-cardinality candidate before the true opcode.
    header_offsets: set[int] = set()
    for offset in range(max_offset + max(scan_widths)):
        single, _single_idx = _offset_values(messages, offset)
        if single and len(set(single)) == 1:
            header_offsets.add(offset)
    for offset in range(max_offset + max(scan_widths)):
        for width in scan_widths:
            if _length_field_match_ratio(messages, offset, width) >= length_field_match_ratio:
                header_offsets.update(range(offset, offset + width))

    candidates: List[Dict[str, Any]] = []
    for offset in range(max_offset):
        for width in scan_widths:
            if header_offsets & set(range(offset, offset + width)):
                continue
            values, indexes = _offset_window_values(messages, offset, width)
            if len(values) < 2:
                continue
            coverage = len(values) / len(messages)
            if coverage < min_coverage:
                continue
            cardinality = len(set(values))
            if cardinality < min_cardinality or cardinality > max_cardinality:
                continue
            stable_ratio = Counter(values).most_common(1)[0][1] / len(values)
            if stable_ratio > max_stable_ratio:
                continue
            mi = normalized_mi(values, [labels[index] for index in indexes])
            candidates.append(
                {"offset": offset, "width": width, "global_mi": round(mi, 6), "cardinality": cardinality, "_mi": mi}
            )
    if not candidates:
        return None

    best_mi = max(candidate["_mi"] for candidate in candidates)
    if best_mi >= min_global_mi:
        # Label-guided: highest MI, ties broken toward the narrower, earlier window.
        chosen = min(
            candidates,
            key=lambda candidate: (-candidate["_mi"], candidate["width"], candidate["offset"]),
        )
    else:
        # Structural fallback: the first single-byte type-like field, widening only
        # when no single-byte window qualifies (genuine 16-bit opcode).
        chosen = min(candidates, key=lambda candidate: (candidate["width"], candidate["offset"]))
    return {key: value for key, value in chosen.items() if not key.startswith("_")}


def _contrastive_separation(values: Sequence[int], labels: Sequence[str]) -> float:
    if not values or len(values) != len(labels):
        return 0.0
    total = len(values)
    value_counts = Counter(values)
    dominant = 0
    for value, count in value_counts.items():
        label_counts = Counter(label for observed, label in zip(values, labels) if observed == value)
        dominant += label_counts.most_common(1)[0][1] if label_counts else 0
    purity = dominant / max(total, 1)
    balance = min(len(value_counts), int(_DD.CONTRASTIVE_BALANCE_DIVISOR)) / _DD.CONTRASTIVE_BALANCE_DIVISOR
    return max(0.0, min(1.0, (_DD.CONTRASTIVE_PURITY_WEIGHT * purity) + (_DD.CONTRASTIVE_BALANCE_WEIGHT * balance)))


def _excluded_roles(family_id: str, offset: int, family_features: Dict[str, Any], framing: Dict[str, Any]) -> List[str]:
    roles: List[str] = []
    family_framing = ((framing.get("families") or {}).get(family_id) or {}) if framing else {}
    for layout in family_framing.get("layout_hypotheses", []) or []:
        for field in layout.get("field_regions", []) or []:
            start = int(field.get("start", 0) or 0)
            end = int(field.get("end", start) or start)
            if start <= offset < end:
                field_type = str(field.get("field_type", "unknown"))
                if any(token in field_type for token in SUPPRESSED_ROLE_TOKENS):
                    roles.append(field_type)
    position_stats = (family_features.get("position_stats") or {}) if family_features else {}
    unique_ratios = position_stats.get("uniqueness_ratio_vector", []) or []
    coverage = position_stats.get("coverage_vector", []) or []
    if offset < len(unique_ratios) and offset < len(coverage):
        if float(unique_ratios[offset]) >= _DD.EXCLUDED_UNIQUE_RATIO_MIN and float(coverage[offset]) >= _DD.EXCLUDED_COVERAGE_MIN:
            roles.append("payload_blob")
    return sorted(set(roles))


def infer_discriminator_candidates(
    records: Sequence[MessageRecord],
    family_by_msg_id: Dict[int, str],
    features: Optional[Dict[str, Any]] = None,
    framing: Optional[Dict[str, Any]] = None,
    neural_model_path: Optional[str] = None,
    salience_cache_path: Optional[str] = None,
    max_offset: int = _DD.MAX_OFFSET,
    top_k: int = _DD.TOP_K,
) -> Dict[str, Any]:
    families: Dict[str, List[MessageRecord]] = defaultdict(list)
    labeled_payloads: List[bytes] = []
    labels: List[str] = []
    directions: List[str] = []
    for record in records:
        family_id = family_by_msg_id.get(record.msg_id)
        if family_id is None:
            continue
        families[family_id].append(record)
        labeled_payloads.append(hex_to_bytes(record.payload_hex))
        labels.append(family_id)
        directions.append(record.direction or "unknown")

    observed_max = min(max((len(payload) for payload in labeled_payloads), default=0), max_offset)
    attention = attention_offset_salience(labeled_payloads, labels, max_length=observed_max or 1, cache_path=salience_cache_path)
    gradient = encoder_gradient_salience(labeled_payloads, model_path=neural_model_path, max_length=observed_max or 1)
    salience = merge_salience_scores(attention, gradient, observed_max or 1)

    global_family_mi: Dict[int, float] = {}
    global_direction_mi: Dict[int, float] = {}
    for offset in range(observed_max):
        values, indexes = _offset_values(labeled_payloads, offset)
        global_family_mi[offset] = normalized_mi(values, [labels[index] for index in indexes])
        global_direction_mi[offset] = normalized_mi(values, [directions[index] for index in indexes])

    output: Dict[str, Any] = {}
    for family_id, family_records in sorted(families.items()):
        messages = [hex_to_bytes(record.payload_hex) for record in family_records]
        family_labels = [family_by_msg_id.get(record.msg_id, family_id) for record in family_records]
        family_directions = [record.direction or "unknown" for record in family_records]
        candidates: List[Dict[str, Any]] = []
        family_max = min(max((len(message) for message in messages), default=0), max_offset)
        for offset in range(family_max):
            values, indexes = _offset_values(messages, offset)
            if len(values) < 2:
                continue
            cardinality = len(set(values))
            coverage = len(values) / max(len(messages), 1)
            unique_ratio = cardinality / max(len(values), 1)
            stable_ratio = Counter(values).most_common(1)[0][1] / max(len(values), 1)
            if coverage < _DD.MIN_COVERAGE or cardinality <= _DD.MIN_CARDINALITY:
                continue
            # Evidence-gate learned salience with explainable symbolic constraints.
            cardinality_score = 1.0 - min(abs(cardinality - _DD.IDEAL_CARDINALITY) / _DD.CARDINALITY_RANGE_DIVISOR, 1.0) if cardinality <= _DD.MAX_SYMBOLIC_CARDINALITY else 0.0
            stability_score = max(0.0, min(1.0, 1.0 - stable_ratio))
            local_direction_mi = normalized_mi(values, [family_directions[index] for index in indexes])
            contrastive = _contrastive_separation(values, [family_labels[index] for index in indexes])
            learned = salience[offset] if offset < len(salience) else 0.0
            family_mi = global_family_mi.get(offset, 0.0)
            direction_mi = max(global_direction_mi.get(offset, 0.0), local_direction_mi)
            excluded = _excluded_roles(family_id, offset, (features or {}).get(family_id, {}) if features else {}, framing or {})
            if excluded:
                continue
            score = (
                (_DD.SCORE_LEARNED_WEIGHT * learned)
                + (_DD.SCORE_FAMILY_MI_WEIGHT * family_mi)
                + (_DD.SCORE_DIRECTION_MI_WEIGHT * direction_mi)
                + (_DD.SCORE_CARDINALITY_WEIGHT * cardinality_score)
                + (_DD.SCORE_CONTRASTIVE_WEIGHT * contrastive)
                + (_DD.SCORE_STABILITY_WEIGHT * stability_score)
            )
            if cardinality > max(_DD.MAX_SYMBOLIC_CARDINALITY, len(values) * _DD.HIGH_CARDINALITY_RATIO_THRESHOLD):
                score *= _DD.HIGH_CARDINALITY_PENALTY
            if score < _DD.MIN_SCORE:
                continue
            candidates.append(
                {
                    "family_id": family_id,
                    "start": offset,
                    "end": offset + 1,
                    "offset": float(offset),
                    "length": 1,
                    "field_type": "discriminator",
                    "cardinality": float(cardinality),
                    "coverage": round(coverage, 6),
                    "entropy": round(entropy(values), 6),
                    "salience_score": round(learned, 6),
                    "mutual_information": round(family_mi, 6),
                    "direction_mutual_information": round(direction_mi, 6),
                    "contrastive_separation": round(contrastive, 6),
                    "offset_stability": round(stable_ratio, 6),
                    "excluded_roles": [],
                    "confidence": round(max(0.0, min(1.0, score)), 6),
                    "evidence": {
                        "symbolic_cardinality_score": round(cardinality_score, 6),
                        "low_to_medium_cardinality": 1 < cardinality <= 32,
                        "learned_salience_available": bool(attention.get("available") or gradient.get("available")),
                    },
                }
            )
        candidates.sort(key=lambda item: (-float(item["confidence"]), int(item["start"])))
        output[family_id] = _family_discriminator_summary(family_id, messages, candidates[:top_k], attention, gradient)
    return output


def _family_discriminator_summary(
    family_id: str,
    messages: Sequence[bytes],
    candidates: Sequence[Dict[str, Any]],
    attention: Dict[str, Any],
    gradient: Dict[str, Any],
) -> Dict[str, Any]:
    keyword = dict(candidates[0]) if candidates else None
    if keyword is not None:
        keyword = {
            "offset": keyword["offset"],
            "entropy": keyword["entropy"],
            "cardinality": keyword["cardinality"],
            "salience_score": keyword["salience_score"],
            "mutual_information": keyword["mutual_information"],
            "contrastive_separation": keyword["contrastive_separation"],
            "excluded_roles": keyword["excluded_roles"],
            "confidence": keyword["confidence"],
        }
    if keyword is None:
        subclusters = {"format_0": {"message_count": len(messages), "template": infer_template([message.hex() for message in messages])}}
    else:
        offset = int(keyword["offset"])
        grouped: Dict[int, List[str]] = defaultdict(list)
        for message in messages:
            if offset < len(message):
                grouped[message[offset]].append(message.hex())
        subclusters = {
            f"format_{idx}": {
                "keyword_value": f"0x{value:02x}",
                "discriminator_value": f"0x{value:02x}",
                "message_count": len(members),
                "template": infer_template(members),
            }
            for idx, (value, members) in enumerate(sorted(grouped.items()))
        }
    return {
        "algorithm": "discriminator_candidate_discovery_v1",
        "family_id": family_id,
        "keyword": keyword,
        "discriminator_candidates": list(candidates),
        "opcode_candidates": list(candidates),
        "subclusters": subclusters,
        "salience_metadata": {
            "attention": {key: value for key, value in attention.items() if key != "offset_scores"},
            "gradient": {key: value for key, value in gradient.items() if key != "offset_scores"},
        },
    }


def split_messages_by_discriminator(messages_hex: Sequence[str], search_range: Optional[range] = None) -> Dict[str, Any]:
    records = [
        MessageRecord(
            msg_id=index,
            source_file="inline",
            session_id="inline",
            session_key="inline",
            src_ip="",
            src_port=0,
            dst_ip="",
            dst_port=0,
            direction="unknown",
            payload_hex=message_hex,
            payload_len=len(hex_to_bytes(message_hex)),
        )
        for index, message_hex in enumerate(messages_hex)
    ]
    max_offset = (max(search_range) + 1) if search_range else 128
    result = infer_discriminator_candidates(records, {record.msg_id: "family_0" for record in records}, max_offset=max_offset)
    return result.get("family_0", {"keyword": None, "subclusters": {"format_0": {"message_count": len(messages_hex), "template": infer_template(messages_hex)}}})
