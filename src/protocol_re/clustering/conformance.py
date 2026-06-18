"""Framing-conformance filter for the message corpus.

A capture taken with a coarse display filter (e.g. tshark ``mbtcp``) or carved
mid-stream can include a small number of payloads that are not actually the
target protocol — a different service on the same port, or a mis-aligned
fragment. These form spurious low-count families (one per junk "opcode") that
pollute the protocol model and are scored as false positives.

Rather than delete families by size — which would also discard rare-but-real
message types such as exception responses — we drop the *messages* that violate
an invariant the corpus itself reveals: a high-confidence CONSTANT framing field.
Modbus TCP, for instance, has a protocol-identifier field that is 0x0000 in every
conforming message; the junk payloads carry other values there. The constant set
is detected label-free and length-field offsets are excluded first, so a byte
that is only coincidentally constant (a length high-byte that happens never to be
exercised) is not mistaken for an invariant.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Sequence, Tuple

from protocol_re.config.thresholds import ConformanceFilter as _CF
from protocol_re.inference.discriminator_fields import _length_field_match_ratio
from protocol_re.model.schema import MessageRecord
from protocol_re.utils.bytes import hex_to_bytes


def detect_framing_constants(
    records: Sequence[MessageRecord],
    *,
    max_offset: int = _CF.MAX_OFFSET,
    min_coverage: float = _CF.MIN_COVERAGE,
    constant_ratio: float = _CF.CONSTANT_RATIO,
    length_field_match_ratio: float = _CF.LENGTH_FIELD_MATCH_RATIO,
    length_field_widths: Sequence[int] = _CF.LENGTH_FIELD_WIDTHS,
) -> Dict[int, int]:
    """Detect header byte offsets that hold a single constant value corpus-wide.

    Returns ``{offset: value}``. An offset qualifies when it is present in at least
    ``min_coverage`` of messages and a single byte value covers at least
    ``constant_ratio`` of those, AND it is not part of a length field (whose value
    is constant only because longer messages happen to be absent from the capture).
    """
    payloads = [hex_to_bytes(record.payload_hex) for record in records]
    total = len(payloads)
    if total == 0:
        return {}

    # Offsets covered by a detected length field are excluded: their dominant value
    # can be near-constant simply because the capture lacks messages long enough to
    # exercise the high-order bytes, which is a property of the sample, not the wire
    # format.
    length_offsets: set[int] = set()
    for offset in range(max_offset):
        for width in length_field_widths:
            if _length_field_match_ratio(payloads, offset, width) >= length_field_match_ratio:
                length_offsets.update(range(offset, offset + width))

    counts: Dict[int, Counter] = defaultdict(Counter)
    present: Dict[int, int] = defaultdict(int)
    for payload in payloads:
        for offset in range(min(len(payload), max_offset)):
            counts[offset][payload[offset]] += 1
            present[offset] += 1

    constants: Dict[int, int] = {}
    for offset, counter in counts.items():
        if offset in length_offsets:
            continue
        if present[offset] / total < min_coverage:
            continue
        value, count = counter.most_common(1)[0]
        if count / present[offset] >= constant_ratio:
            constants[offset] = value
    return constants


def partition_by_conformance(
    records: Sequence[MessageRecord], constants: Dict[int, int]
) -> Tuple[List[MessageRecord], List[MessageRecord]]:
    """Split records into (conforming, non-conforming) by the constant invariants.

    A record is non-conforming when it contains a constant offset but carries a
    different value there. A record too short to reach an offset does not violate
    it (the field is simply absent)."""
    if not constants:
        return list(records), []
    conforming: List[MessageRecord] = []
    nonconforming: List[MessageRecord] = []
    for record in records:
        payload = hex_to_bytes(record.payload_hex)
        violates = any(
            offset < len(payload) and payload[offset] != value
            for offset, value in constants.items()
        )
        (nonconforming if violates else conforming).append(record)
    return conforming, nonconforming


def filter_nonconforming(
    records: Sequence[MessageRecord], **kwargs: Any
) -> Tuple[List[MessageRecord], List[MessageRecord], Dict[int, int]]:
    """Convenience wrapper: detect constants then partition. Returns
    ``(conforming, nonconforming, constants)``."""
    constants = detect_framing_constants(records, **kwargs)
    conforming, nonconforming = partition_by_conformance(records, constants)
    return conforming, nonconforming, constants
