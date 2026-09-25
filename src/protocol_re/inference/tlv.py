"""TLV/BER self-describing framing detection and field derivation.

Variable-offset, self-describing protocols (GOOSE/BER, SNMP/ASN.1,
DNS-style tag-length-value chains) defeat fixed-offset segmentation and
length-bucket clustering: entropy layouts land mid-header, every payload
length becomes its own family, and the deterministic tag structure that
actually defines the message type is never exposed as fields.

This module provides the deterministic core of the TLV framing mode:

* :func:`parse_tlv_message` parses one message as a strict chain of
  BER-style tag-length elements after a fixed header prefix.
* :func:`parse_tlv_tree` additionally descends into a single constructed
  wrapper element (e.g. the GOOSE ``0x61`` GoosePdu) so the inner chain
  becomes the field-bearing body.
* :func:`detect_tlv_framing` accepts the mode only when nearly every
  message parses exactly, the tag alphabet is plausible, and the tag
  sequences do not degenerate into one sequence per message.
* :func:`merge_families_by_tlv_signature` re-keys clustering families so
  messages sharing a tag sequence (the type identity of a self-describing
  protocol) land in one family instead of one family per length bucket.
* :func:`derive_tlv_field_hypotheses` converts a parsed family into field
  hypotheses with absolute wire offsets (the pipeline-wide convention).

Everything here is deterministic and gated: when the corpus does not parse
as TLV the functions return ``None`` / no-op metadata and the rest of the
pipeline behaves exactly as before.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from protocol_re.config.thresholds import TlvFraming as _TF
from protocol_re.model.schema import FamilyAssignment, FieldHypothesis, Segment
from protocol_re.utils.bytes import hex_to_bytes


@dataclass(frozen=True)
class TlvElement:
    """One tag-length-value element at an absolute wire offset."""

    tag: int
    start: int  # absolute offset of the tag byte
    length: int  # total element length (tag + length bytes + value)
    value_offset: int  # absolute offset of the first value byte
    value_length: int
    length_header_bytes: int  # bytes between the tag and the value


@dataclass
class TlvMessageView:
    """Parsed TLV structure of one message."""

    header_length: int
    elements: List[TlvElement]
    # When the top level is a single constructed wrapper (BER constructed
    # tag such as the GOOSE 0x61 GoosePdu), ``wrapper`` holds that element
    # and ``elements`` holds the parsed inner chain.
    wrapper: Optional[TlvElement] = None

    @property
    def body_start(self) -> int:
        first = self.elements[0] if self.elements else None
        return first.start if first is not None else self.header_length


@dataclass
class TlvFramingDetection:
    """Corpus- or family-level verdict that the TLV framing mode applies."""

    header_length: int
    parse_success_ratio: float
    messages_parsed: int
    tag_counts: Dict[int, int]
    distinct_tags: int
    sequence_count: int
    evidence: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        """Compact dict for embedding in framing / boundary artifacts."""
        return {
            "detected": True,
            "header_length": self.header_length,
            "parse_success_ratio": self.parse_success_ratio,
            "messages_parsed": self.messages_parsed,
            "distinct_tags": self.distinct_tags,
            "sequence_count": self.sequence_count,
            "tag_counts": {f"0x{tag:02x}": count for tag, count in sorted(self.tag_counts.items())},
            "evidence": self.evidence,
        }


def parse_tlv_message(
    payload: bytes,
    header_length: int = 0,
    *,
    base: int = 0,
    max_walk: int = _TF.MAX_CHAIN_WALK,
    length_slack: int = _TF.LENGTH_SLACK_BYTES,
) -> Optional[TlvMessageView]:
    """Parse ``payload`` as a strict BER-style TLV chain.

    ``base`` is the absolute offset of ``payload[0]`` within the original
    message (non-zero when parsing the value region of a wrapper element from
    a sliced buffer); all returned offsets are absolute with respect to that
    original message. Returns ``None`` on any structural violation: a length
    that exceeds the remaining bytes (beyond ``length_slack``), a BER
    long-form header wider than 4 bytes, a high-tag-number element, or an
    unterminated chain.
    """
    if header_length < 0 or len(payload) < header_length:
        return None
    chain_start = base + header_length
    pos = chain_start
    end = base + len(payload)
    elements: List[TlvElement] = []
    while pos < end:
        if pos - chain_start > max_walk:
            return None
        if pos + 2 > end:
            return None
        tag = payload[pos - base]
        if tag & 0x1F == 0x1F:
            return None  # high-tag-number form is not supported
        first_len = payload[pos - base + 1]
        if first_len & _TF.BER_LONG_FORM_MASK:
            count = first_len & 0x7F
            if count == 0 or count > 4:
                return None
            if pos + 2 + count > end:
                return None
            length = int.from_bytes(payload[pos - base + 2 : pos - base + 2 + count], "big")
            length_header_bytes = 2 + count
        else:
            length = first_len
            length_header_bytes = 2
        value_offset = pos + length_header_bytes
        if value_offset + length > end + length_slack:
            return None
        elements.append(
            TlvElement(
                tag=tag,
                start=pos,
                length=length_header_bytes + length,
                value_offset=value_offset,
                value_length=length,
                length_header_bytes=length_header_bytes,
            )
        )
        pos = value_offset + length
    if not elements:
        return None
    return TlvMessageView(header_length=header_length, elements=elements)


def parse_tlv_tree(
    payload: bytes,
    header_length: int = 0,
    *,
    max_walk: int = _TF.MAX_CHAIN_WALK,
    length_slack: int = _TF.LENGTH_SLACK_BYTES,
) -> Optional[TlvMessageView]:
    """Parse a message, descending into a single constructed wrapper.

    Self-describing industrial PDUs frequently wrap the whole body in one
    constructed element (GOOSE ``0x61``, SNMP ``0x30``). When the top level
    is exactly one element whose value region itself parses as a complete
    TLV chain, the inner chain becomes the element list and the wrapper is
    recorded separately so its constant tag can surface as a field.
    """
    top = parse_tlv_message(payload, header_length, max_walk=max_walk, length_slack=length_slack)
    if top is None:
        return None
    if len(top.elements) == 1:
        only = top.elements[0]
        if only.value_length >= 2 and only.value_offset + only.value_length <= len(payload):
            inner = parse_tlv_message(
                payload[only.value_offset : only.value_offset + only.value_length],
                0,
                base=only.value_offset,
                max_walk=max_walk,
                length_slack=length_slack,
            )
            if inner is not None and inner.elements:
                return TlvMessageView(header_length=header_length, elements=inner.elements, wrapper=only)
    return top


def _parse_ratio(messages: Sequence[bytes], header_length: int, limit: int) -> float:
    sample = messages[:limit]
    if not sample:
        return 0.0
    ok = sum(1 for payload in sample if parse_tlv_tree(payload, header_length) is not None)
    return ok / len(sample)


def _tree_stats(
    messages: Sequence[bytes], header_length: int, limit: int
) -> Tuple[Counter[int], Counter[Tuple[int, ...]], float, int]:
    """Tag/sequence statistics from tree parses, plus wrapper-descent ratio."""
    tag_counts: Counter[int] = Counter()
    sequences: Counter[Tuple[int, ...]] = Counter()
    parsed = 0
    wrapped = 0
    for payload in messages[:limit]:
        view = parse_tlv_tree(payload, header_length)
        if view is None:
            continue
        parsed += 1
        if view.wrapper is not None:
            wrapped += 1
        tag_counts.update(element.tag for element in view.elements)
        sequences.update(tuple(element.tag for element in view.elements))
    wrapper_ratio = wrapped / parsed if parsed else 0.0
    return tag_counts, sequences, wrapper_ratio, parsed


def detect_tlv_framing(
    messages: Sequence[bytes],
    *,
    quick_sample: int = 256,
    sample_cap: int = _TF.SIGNATURE_SAMPLE_CAP,
) -> Optional[TlvFramingDetection]:
    """Detect a fixed header prefix followed by a TLV chain.

    The candidate header length is scanned from 0 to ``TlvFraming.MAX_HEADER_SCAN``;
    candidates must parse ≥ ``MIN_PARSE_SUCCESS_RATIO`` of a quick sample before
    the ratio is confirmed on a larger sample. Candidates are ranked by parse
    ratio, then by how often the whole body is one constructed wrapper (a
    too-small header turns header bytes into degenerate top-level elements and
    blocks the descent), then by tag-vocabulary richness, then smallest header.
    The verdict additionally requires a plausible tag alphabet
    (``MIN_DISTINCT_TAGS``..``MAX_DISTINCT_TAGS``) and a non-degenerate sequence
    cardinality (a self-describing protocol repeats tag sequences; payload
    bytes do not).
    """
    cleaned = [bytes(message) for message in messages if message]
    if len(cleaned) < _TF.MIN_MESSAGES_FOR_TAG_VOCABULARY:
        return None

    candidates: List[Tuple[int, float]] = []
    for header_length in range(0, _TF.MAX_HEADER_SCAN + 1):
        if _parse_ratio(cleaned, header_length, quick_sample) < _TF.MIN_PARSE_SUCCESS_RATIO:
            continue
        ratio = _parse_ratio(cleaned, header_length, sample_cap)
        if ratio >= _TF.MIN_PARSE_SUCCESS_RATIO:
            candidates.append((header_length, ratio))
    if not candidates:
        return None

    scored: List[Tuple[float, float, int, int, Counter[int], Counter[Tuple[int, ...]], int]] = []
    for header_length, ratio in candidates:
        tag_counts, sequences, wrapper_ratio, parsed = _tree_stats(cleaned, header_length, sample_cap)
        scored.append((ratio, wrapper_ratio, len(tag_counts), header_length, tag_counts, sequences, parsed))
    # Prefer: full parse, wrapper descent, richer tag vocabulary, smallest header.
    ratio, _wrapper_ratio, _tags, header_length, tag_counts, sequences, parsed = max(scored, key=lambda item: item[:4])

    distinct = len(tag_counts)
    if distinct < _TF.MIN_DISTINCT_TAGS or distinct > _TF.MAX_DISTINCT_TAGS:
        return None
    max_sequences = max(1, int(_TF.MAX_SEQUENCE_CARDINALITY_RATIO * max(parsed, 1)))
    if len(sequences) > max_sequences:
        return None

    return TlvFramingDetection(
        header_length=header_length,
        parse_success_ratio=round(ratio, 4),
        messages_parsed=parsed,
        tag_counts=dict(sorted(tag_counts.items())),
        distinct_tags=distinct,
        sequence_count=len(sequences),
        evidence={
            "candidate_header_lengths": sorted(header for header, _ in candidates),
            "wrapper_ratio": round(_wrapper_ratio, 4),
        },
    )


def merge_families_by_tlv_signature(
    records: Sequence[Any],
    assignments: Sequence[FamilyAssignment],
    detection: TlvFramingDetection,
) -> Tuple[List[FamilyAssignment], Dict[str, Any]]:
    """Re-key families so one TLV tag sequence = one family.

    Messages whose payload parses to the same tag sequence (and whose parse
    fails are kept in their original family) are grouped under a new stable
    family id; signatures are ordered by descending member count then lexicographic
    tag sequence, so identical inputs always yield identical ids.
    """
    family_by_msg_id = {assignment.msg_id: assignment.family_id for assignment in assignments}
    record_by_msg_id = {record.msg_id: record for record in records}

    members_by_signature: Dict[Tuple[int, ...], List[int]] = defaultdict(list)
    parse_failures = 0
    for assignment in assignments:
        record = record_by_msg_id.get(assignment.msg_id)
        if record is None:
            continue
        view = parse_tlv_tree(hex_to_bytes(record.payload_hex), detection.header_length)
        if view is None:
            parse_failures += 1
            continue
        members_by_signature[tuple(element.tag for element in view.elements)].append(assignment.msg_id)

    if not members_by_signature:
        return list(assignments), {
            "applied": False,
            "reason": "no_messages_parsed_with_detected_header",
            "header_length": detection.header_length,
        }

    ordered = sorted(members_by_signature.items(), key=lambda item: (-len(item[1]), item[0]))
    family_count_before = len({assignment.family_id for assignment in assignments})

    new_assignments: List[FamilyAssignment] = []
    signature_to_family: Dict[Tuple[int, ...], str] = {}
    for index, (signature, _members) in enumerate(ordered):
        signature_to_family[signature] = f"family_{index}"
    for assignment in assignments:
        record = record_by_msg_id.get(assignment.msg_id)
        signature = None
        if record is not None:
            view = parse_tlv_tree(hex_to_bytes(record.payload_hex), detection.header_length)
            if view is not None:
                signature = tuple(element.tag for element in view.elements)
        if signature is None:
            new_assignments.append(assignment)  # keep pre-existing family
            continue
        new_assignments.append(
            FamilyAssignment(msg_id=assignment.msg_id, family_id=signature_to_family[signature], confidence=assignment.confidence)
        )

    family_count_after = len({assignment.family_id for assignment in new_assignments})
    metadata = {
        "applied": True,
        "reason": "tlv_signature_merge",
        "header_length": detection.header_length,
        "distinct_tags": detection.distinct_tags,
        "sequence_count": detection.sequence_count,
        "parse_success_ratio": detection.parse_success_ratio,
        "parse_failures": parse_failures,
        "family_count_before": family_count_before,
        "family_count_after": family_count_after,
        "signatures": [
            {"family_id": signature_to_family[signature], "member_count": len(members), "tags": [f"0x{tag:02x}" for tag in signature]}
            for signature, members in ordered
        ],
    }
    return new_assignments, metadata


def header_field_runs(messages: Sequence[bytes], header_length: int) -> List[Dict[str, Any]]:
    """Group fixed-header bytes into constant / variable runs.

    Returns dicts with ``start``, ``length``, ``constant`` and (for constant
    runs) ``value_hex`` — the raw material for header field hypotheses.
    """
    if header_length <= 0:
        return []
    usable = [message for message in messages if len(message) >= header_length]
    if not usable:
        return []
    constant: List[bool] = []
    for offset in range(header_length):
        values = {message[offset] for message in usable}
        constant.append(len(values) == 1)
    runs: List[Dict[str, Any]] = []
    start = 0
    while start < header_length:
        end = start + 1
        while end < header_length and constant[end] == constant[start]:
            end += 1
        run: Dict[str, Any] = {"start": start, "length": end - start, "constant": constant[start]}
        if constant[start]:
            run["value_hex"] = bytes(usable[0][start:end]).hex()
        runs.append(run)
        start = end
    return runs


_WIDTH_TYPE: Dict[int, str] = {1: "uint8", 2: "uint16", 4: "uint32", 8: "uint64"}


def _header_field_chunks(messages: Sequence[bytes], header_length: int) -> List[Dict[str, Any]]:
    """Turn fixed-header bytes into register-sized field chunks.

    Constant/variable runs are first split at 2-byte granularity (1-byte
    remainder), then a trailing constant chunk is merged with an adjacent
    variable chunk into one register when the pair totals ≤2 bytes — a
    uint16 whose high byte is always 0x00 but whose low byte varies is one
    length field, not a constant plus a counter.
    """
    chunks: List[Dict[str, Any]] = []
    for run in header_field_runs(messages, header_length):
        offset, remaining = run["start"], run["length"]
        while remaining > 0:
            chunk_length = 2 if remaining >= 2 else 1
            chunk: Dict[str, Any] = {"start": offset, "length": chunk_length, "constant": run["constant"]}
            if run["constant"]:
                slice_at = 2 * (offset - run["start"])
                chunk["value_hex"] = run["value_hex"][slice_at : slice_at + 2 * chunk_length]
            chunks.append(chunk)
            offset += chunk_length
            remaining -= chunk_length
    merged: List[Dict[str, Any]] = []
    index = 0
    while index < len(chunks):
        chunk = chunks[index]
        nxt = chunks[index + 1] if index + 1 < len(chunks) else None
        if (
            chunk["constant"]
            and nxt is not None
            and not nxt["constant"]
            and chunk["start"] + chunk["length"] == nxt["start"]
            and chunk["length"] + nxt["length"] <= 2
        ):
            merged.append({"start": chunk["start"], "length": chunk["length"] + nxt["length"], "constant": False})
            index += 2
            continue
        merged.append(chunk)
        index += 1
    return merged


def _value_field_type(values: Sequence[bytes], value_length: int) -> Tuple[str, Optional[str], float]:
    """Classify a TLV value region: (field_type, endian, confidence)."""
    if not values:
        return "bytes", None, 0.4
    unique = set(values)
    if len(unique) == 1:
        return "constant", None, 0.99
    if value_length in _WIDTH_TYPE:
        return _WIDTH_TYPE[value_length], "big", 0.8
    printable = sum(1 for value in values if all(0x20 <= byte < 0x7F for byte in value))
    if printable / len(values) >= 0.9 and value_length >= 2:
        return "string", None, 0.75
    return "bytes", None, 0.5


def derive_tlv_field_hypotheses(
    family_id: str,
    messages_hex: Sequence[str],
    detection: TlvFramingDetection,
) -> Tuple[List[FieldHypothesis], List[Segment], Dict[str, Any]]:
    """Derive field hypotheses (absolute offsets) from a parsed TLV family.

    Header runs become fixed-offset fields; each distinct body tag becomes one
    field spanning its full element. A constant wrapper tag (e.g. the GOOSE
    ``0x61``) becomes a 1-byte constant field at the body start so downstream
    discriminator logic sees it.
    """
    messages = [hex_to_bytes(item) for item in messages_hex if item]
    parsed_pairs: List[Tuple[bytes, TlvMessageView]] = []
    for payload in messages:
        view = parse_tlv_tree(payload, detection.header_length)
        if view is not None:
            parsed_pairs.append((payload, view))
    views = [view for _payload, view in parsed_pairs]
    parsed_ratio = len(views) / len(messages) if messages else 0.0

    hypotheses: List[FieldHypothesis] = []
    segments: List[Segment] = []

    for chunk in _header_field_chunks(messages, detection.header_length):
        attributes: Dict[str, Any] = {"tlv_region": "header", "tlv_run": "constant" if chunk["constant"] else "variable"}
        if chunk["constant"]:
            attributes["value_hex"] = chunk["value_hex"]
            field_type = "constant"
            confidence = 0.99
        else:
            field_type = _WIDTH_TYPE.get(chunk["length"], "bytes")
            confidence = 0.7
        hypotheses.append(
            FieldHypothesis(
                family_id=family_id,
                start=chunk["start"],
                length=chunk["length"],
                field_type=field_type,
                confidence=confidence,
                endian=None,
                evidence={"source": "tlv_header_run"},
                attributes=attributes,
            )
        )
        segments.append(
            Segment(start=chunk["start"], end=chunk["start"] + chunk["length"], kind="header", confidence=confidence)
        )

    # Constant wrapper tag surfaces as its own 1-byte field at body start.
    wrapper = views[0].wrapper if views else None
    if wrapper is not None:
        wrapper_tags = {view.wrapper.tag for view in views if view.wrapper is not None}
        if len(wrapper_tags) == 1:
            hypotheses.append(
                FieldHypothesis(
                    family_id=family_id,
                    start=wrapper.start,
                    length=1,
                    field_type="constant",
                    confidence=0.99,
                    endian=None,
                    evidence={"source": "tlv_wrapper_tag", "parse_success_ratio": round(parsed_ratio, 4)},
                    attributes={"value_hex": f"{wrapper.tag:02x}", "tlv_region": "wrapper_tag"},
                )
            )
            segments.append(Segment(start=wrapper.start, end=wrapper.start + 1, kind="tlv_tag", confidence=0.99))

    # Per-tag observations, kept aligned with parsed messages so value
    # classification always sees the bytes behind each element. Element
    # offsets are absolute, so slicing the original payload is exact.
    values_by_tag: Dict[int, List[bytes]] = defaultdict(list)
    starts_by_tag: Dict[int, List[int]] = defaultdict(list)
    lengths_by_tag: Dict[int, List[int]] = defaultdict(list)
    for payload, view in parsed_pairs:
        for element in view.elements:
            values_by_tag[element.tag].append(payload[element.value_offset : element.value_offset + element.value_length])
            starts_by_tag[element.tag].append(element.start)
            lengths_by_tag[element.tag].append(element.length)

    for tag in sorted(values_by_tag):
        values = values_by_tag[tag]
        start = Counter(starts_by_tag[tag]).most_common(1)[0][0]
        length = Counter(lengths_by_tag[tag]).most_common(1)[0][0]
        presence_ratio = len(values) / len(messages) if messages else 0.0
        value_length = max((len(value) for value in values), default=0)
        field_type, endian, confidence = _value_field_type(values, value_length)
        attributes = {
            "tlv_tag": str(tag),
            "tlv_tag_hex": f"0x{tag:02x}",
            "tlv_pdu_offset": str(start - detection.header_length),
            "tlv_optional": presence_ratio < 0.99,
            "tlv_occurrences": len(values),
        }
        if field_type == "constant" and values:
            attributes["value_hex"] = values[0].hex()
        hypotheses.append(
            FieldHypothesis(
                family_id=family_id,
                start=start,
                length=length,
                field_type=field_type,
                confidence=round(min(0.99, confidence + 0.15 * presence_ratio), 4),
                endian=endian,
                evidence={"source": "tlv_element", "presence_ratio": round(presence_ratio, 4)},
                attributes=attributes,
            )
        )
        segments.append(Segment(start=start, end=start + length, kind="tlv", confidence=confidence))

    metadata = {
        "mode": "tlv_ber",
        "header_length": detection.header_length,
        "parsed_ratio": round(parsed_ratio, 4),
        "distinct_tags": len(values_by_tag),
    }
    return hypotheses, segments, metadata
