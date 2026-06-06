"""
Protocol-agnostic semantic field inference engine.

This module provides functions to infer semantic roles for protocol fields
based on statistical evidence from multiple sources: framing, features,
relations, and keyword/discriminator analysis.

All inference is protocol-agnostic and based on common patterns found in
industrial and binary protocols.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from protocol_re.utils.bytes import hex_to_bytes, safe_int_from_bytes


@dataclass
class SemanticHypothesis:
    """A semantic role hypothesis for a field with confidence and evidence."""
    field_start: int
    field_length: int
    semantic_role: str
    confidence: float
    evidence: Dict[str, Any] = field(default_factory=dict)
    encoding_type: Optional[str] = None  # uint8, uint16_be, uint16_le, uint32_be, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": self.field_start,
            "length": self.field_length,
            "label": self.semantic_role,
            "field_type": self.encoding_type,
            "confidence": round(self.confidence, 4),
            "evidence": self.evidence,
            "encoding_type": self.encoding_type,
        }


def infer_discriminator_fields(
    field_hypotheses: List[Dict[str, Any]],
    framing_summary: Optional[Dict[str, Any]],
    keyword_summary: Optional[Dict[str, Any]],
    feature_summary: Optional[Dict[str, Any]],
) -> List[SemanticHypothesis]:
    """
    Detect discriminator/opcode/message-type fields.

    Characteristics:
    - Position: typically byte 0-2 (or after transaction ID)
    - Cardinality: 2-256 unique values (low but not constant)
    - Stability: appears in same position across family
    - Evidence: high salience score from keyword detection
    - Evidence: discriminator field from framing
    """
    hypotheses: List[SemanticHypothesis] = []

    # Check framing discriminator fields
    framing_discriminators = set()
    if framing_summary:
        for layout in framing_summary.get("layout_hypotheses", []):
            for region in layout.get("field_regions", []):
                if region.get("field_type") == "discriminator":
                    framing_discriminators.add((region["start"], region["end"] - region["start"]))

    # Check keyword/discriminator candidates
    keyword_candidates = {}
    if keyword_summary:
        for candidate in keyword_summary.get("discriminator_candidates", []):
            offset = candidate.get("offset")
            width = candidate.get("width", 1)
            salience = candidate.get("salience_score", 0.0)
            mi = candidate.get("mutual_information", 0.0)
            keyword_candidates[(offset, width)] = {
                "salience": salience,
                "mutual_information": mi,
                "confidence": candidate.get("confidence", 0.0),
            }

    # Analyze field hypotheses
    for field in field_hypotheses:
        start = field.get("start", 0)
        length = field.get("length", 1)
        field_type = field.get("field_type", "")

        # Skip if already labeled as keyword (legacy name for discriminator)
        if field_type == "keyword":
            evidence = dict(field.get("evidence", {}))
            confidence = float(field.get("confidence", 0.0))

            # Boost confidence if we have additional evidence
            if (start, length) in framing_discriminators:
                confidence = min(0.95, confidence + 0.1)
                evidence["framing_discriminator"] = True

            if (start, length) in keyword_candidates:
                kw_info = keyword_candidates[(start, length)]
                confidence = min(0.95, confidence + 0.05)
                evidence["salience_score"] = kw_info["salience"]
                evidence["mutual_information"] = kw_info["mutual_information"]

            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="discriminator",
                confidence=confidence,
                evidence=evidence,
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

        # Check framing discriminator fields not already labeled
        elif (start, length) in framing_discriminators:
            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="discriminator",
                confidence=0.7,
                evidence={"source": "framing", "field_type": "discriminator"},
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

        # Check keyword candidates not already labeled
        elif (start, length) in keyword_candidates:
            kw_info = keyword_candidates[(start, length)]
            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="discriminator",
                confidence=max(0.6, kw_info["confidence"]),
                evidence={
                    "source": "keyword_detection",
                    "salience_score": kw_info["salience"],
                    "mutual_information": kw_info["mutual_information"],
                },
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

    return hypotheses


def infer_length_fields(
    field_hypotheses: List[Dict[str, Any]],
    framing_summary: Optional[Dict[str, Any]],
    messages_hex: Optional[List[str]] = None,
) -> List[SemanticHypothesis]:
    """
    Detect length/size fields.

    Characteristics:
    - Position: typically byte 2-6
    - Width: 1, 2, or 4 bytes
    - Evidence: value matches message length (from framing)
    - Evidence: value matches remaining length
    - Evidence: value matches payload length
    """
    hypotheses: List[SemanticHypothesis] = []

    # Check framing length fields
    framing_lengths = {}
    if framing_summary:
        for layout in framing_summary.get("layout_hypotheses", []):
            for region in layout.get("field_regions", []):
                if region.get("field_type") == "length":
                    key = (region["start"], region["end"] - region["start"])
                    framing_lengths[key] = {
                        "confidence": region.get("confidence", 0.0),
                        "match_score": region.get("evidence", {}).get("match_score", 0.0),
                        "relation": region.get("evidence", {}).get("relation", "unknown"),
                    }

    # Analyze field hypotheses
    for field in field_hypotheses:
        start = field.get("start", 0)
        length = field.get("length", 1)
        field_type = field.get("field_type", "")

        # Check if already labeled as length
        if field_type == "length":
            evidence = dict(field.get("evidence", {}))
            confidence = float(field.get("confidence", 0.0))

            # Boost confidence if framing also detected it
            if (start, length) in framing_lengths:
                framing_info = framing_lengths[(start, length)]
                confidence = max(confidence, framing_info["confidence"])
                evidence["framing_match_score"] = framing_info["match_score"]
                evidence["framing_relation"] = framing_info["relation"]

            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="length",
                confidence=confidence,
                evidence=evidence,
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

        # Check framing length fields not already labeled
        elif (start, length) in framing_lengths:
            framing_info = framing_lengths[(start, length)]
            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="length",
                confidence=framing_info["confidence"],
                evidence={
                    "source": "framing",
                    "match_score": framing_info["match_score"],
                    "relation": framing_info["relation"],
                },
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

    return hypotheses


def infer_transaction_id_fields(
    field_hypotheses: List[Dict[str, Any]],
    relation_edges: List[Dict[str, Any]],
    framing_summary: Optional[Dict[str, Any]],
    feature_summary: Optional[Dict[str, Any]],
) -> List[SemanticHypothesis]:
    """
    Detect transaction/correlation ID fields.

    Characteristics:
    - Position: typically byte 0-4 (first field in header)
    - Width: 2 or 4 bytes
    - Cardinality: high (>50% unique values)
    - Evidence: echoed in request/response pairs
    - Evidence: high cardinality counter from framing
    """
    hypotheses: List[SemanticHypothesis] = []

    # Collect echo evidence from relations
    echo_fields = {}
    for edge in relation_edges:
        for echo in edge.get("echo_fields", []):
            offset = echo.get("request_offset")
            width = echo.get("width")
            support = echo.get("support", 0.0)
            if width in (2, 4):  # Transaction IDs are typically 2 or 4 bytes
                key = (offset, width)
                if key not in echo_fields or support > echo_fields[key]["support"]:
                    echo_fields[key] = {
                        "support": support,
                        "response_family": edge.get("response_family_id"),
                        "response_offset": echo.get("response_offset"),
                    }

    # Collect high-cardinality counter fields from framing
    framing_counters = {}
    if framing_summary:
        for layout in framing_summary.get("layout_hypotheses", []):
            for region in layout.get("field_regions", []):
                if region.get("field_type") == "transaction_or_counter":
                    key = (region["start"], region["end"] - region["start"])
                    evidence = region.get("evidence", {})
                    unique_ratio = evidence.get("unique_ratio", 0.0)
                    if unique_ratio > 0.5:  # High cardinality suggests transaction ID
                        framing_counters[key] = {
                            "confidence": region.get("confidence", 0.0),
                            "unique_ratio": unique_ratio,
                        }

    # Analyze field hypotheses
    for field in field_hypotheses:
        start = field.get("start", 0)
        length = field.get("length", 1)
        field_type = field.get("field_type", "")

        # Check if already labeled as counter_or_transaction_id
        if field_type == "counter_or_transaction_id":
            evidence = dict(field.get("evidence", {}))
            confidence = float(field.get("confidence", 0.0))

            # Check if echoed (strong evidence for transaction ID)
            if (start, length) in echo_fields:
                echo_info = echo_fields[(start, length)]
                confidence = min(0.95, confidence + 0.2)
                evidence["echoed"] = True
                evidence["echo_support"] = echo_info["support"]
                evidence["response_family"] = echo_info["response_family"]

                hypotheses.append(SemanticHypothesis(
                    field_start=start,
                    field_length=length,
                    semantic_role="transaction_id",
                    confidence=confidence,
                    evidence=evidence,
                    encoding_type=_infer_encoding_type(length, field.get("endian")),
                ))

            # Check framing counter evidence
            elif (start, length) in framing_counters:
                framing_info = framing_counters[(start, length)]
                if framing_info["unique_ratio"] > 0.7:
                    # High unique ratio suggests transaction ID over sequence counter
                    hypotheses.append(SemanticHypothesis(
                        field_start=start,
                        field_length=length,
                        semantic_role="transaction_id",
                        confidence=min(0.85, confidence + 0.1),
                        evidence={**evidence, "unique_ratio": framing_info["unique_ratio"]},
                        encoding_type=_infer_encoding_type(length, field.get("endian")),
                    ))
                else:
                    # Lower unique ratio suggests sequence counter
                    hypotheses.append(SemanticHypothesis(
                        field_start=start,
                        field_length=length,
                        semantic_role="sequence_number",
                        confidence=confidence,
                        evidence=evidence,
                        encoding_type=_infer_encoding_type(length, field.get("endian")),
                    ))
            else:
                # Ambiguous - could be either
                hypotheses.append(SemanticHypothesis(
                    field_start=start,
                    field_length=length,
                    semantic_role="transaction_id",
                    confidence=confidence * 0.8,
                    evidence={**evidence, "ambiguous": True},
                    encoding_type=_infer_encoding_type(length, field.get("endian")),
                ))

        # Check echo fields not already labeled
        elif (start, length) in echo_fields:
            echo_info = echo_fields[(start, length)]
            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="transaction_id",
                confidence=min(0.9, 0.55 + 0.4 * echo_info["support"]),
                evidence={
                    "source": "echo_detection",
                    "echo_support": echo_info["support"],
                    "response_family": echo_info["response_family"],
                },
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

    return hypotheses


def infer_counter_fields(
    field_hypotheses: List[Dict[str, Any]],
    framing_summary: Optional[Dict[str, Any]],
    feature_summary: Optional[Dict[str, Any]],
) -> List[SemanticHypothesis]:
    """
    Detect counter/sequence number fields.

    Characteristics:
    - Width: 1, 2, or 4 bytes
    - Cardinality: high
    - Evidence: monotonic increasing values
    - Evidence: small deltas between consecutive messages
    """
    hypotheses: List[SemanticHypothesis] = []

    # Collect counter evidence from framing
    framing_counters = {}
    if framing_summary:
        for layout in framing_summary.get("layout_hypotheses", []):
            for region in layout.get("field_regions", []):
                if region.get("field_type") == "transaction_or_counter":
                    key = (region["start"], region["end"] - region["start"])
                    evidence = region.get("evidence", {})
                    monotonic_ratio = evidence.get("monotonic_ratio", 0.0)
                    small_delta_ratio = evidence.get("small_delta_ratio", 0.0)
                    unique_ratio = evidence.get("unique_ratio", 0.0)

                    # High monotonic + small deltas suggests counter
                    if monotonic_ratio > 0.8 and small_delta_ratio > 0.5:
                        framing_counters[key] = {
                            "confidence": region.get("confidence", 0.0),
                            "monotonic_ratio": monotonic_ratio,
                            "small_delta_ratio": small_delta_ratio,
                            "unique_ratio": unique_ratio,
                        }

    # Analyze field hypotheses
    for field in field_hypotheses:
        start = field.get("start", 0)
        length = field.get("length", 1)
        field_type = field.get("field_type", "")

        # Check framing counter fields
        if (start, length) in framing_counters:
            framing_info = framing_counters[(start, length)]

            # Distinguish between sequence counter and transaction ID
            if framing_info["unique_ratio"] < 0.5 and framing_info["small_delta_ratio"] > 0.7:
                # Low unique ratio + small deltas = sequence counter
                hypotheses.append(SemanticHypothesis(
                    field_start=start,
                    field_length=length,
                    semantic_role="sequence_number",
                    confidence=framing_info["confidence"],
                    evidence={
                        "source": "framing",
                        "monotonic_ratio": framing_info["monotonic_ratio"],
                        "small_delta_ratio": framing_info["small_delta_ratio"],
                        "unique_ratio": framing_info["unique_ratio"],
                    },
                    encoding_type=_infer_encoding_type(length, field.get("endian")),
                ))

    return hypotheses


def infer_address_fields(
    field_hypotheses: List[Dict[str, Any]],
    feature_summary: Optional[Dict[str, Any]],
) -> List[SemanticHypothesis]:
    """
    Detect address/unit ID fields.

    Characteristics:
    - Position: typically early in message
    - Width: 1, 2, or 4 bytes
    - Cardinality: moderate (2-100 unique values)
    - Evidence: stable within sessions
    - Evidence: not monotonic (unlike counters)
    """
    hypotheses: List[SemanticHypothesis] = []

    # Use feature summary to detect moderate cardinality fields
    if feature_summary:
        position_stats = feature_summary.get("position_stats", {})

        # Check if position_stats is a dict with per-offset data or vectors
        if isinstance(position_stats, dict):
            # Check if it has vector format (entropy_vector, etc.) or per-offset format
            if "entropy_vector" in position_stats:
                # Vector format - skip address detection (not enough per-offset detail)
                pass
            else:
                # Per-offset format - process each offset
                for offset_str, stats in position_stats.items():
                    try:
                        offset = int(offset_str)
                    except (ValueError, TypeError):
                        continue  # Skip non-numeric keys

                    cardinality = stats.get("cardinality", 0)
                    unique_ratio = stats.get("unique_ratio", 0.0)

                    # Moderate cardinality (2-100 unique values, 5-50% unique ratio)
                    if 2 <= cardinality <= 100 and 0.05 <= unique_ratio <= 0.5:
                        # Find matching field hypothesis
                        for field in field_hypotheses:
                            start = field.get("start", 0)
                            length = field.get("length", 1)
                            if start <= offset < start + length and length in (1, 2, 4):
                                hypotheses.append(SemanticHypothesis(
                                    field_start=start,
                                    field_length=length,
                                    semantic_role="address",
                                    confidence=0.6,
                                    evidence={
                                        "source": "feature_analysis",
                                        "cardinality": cardinality,
                                        "unique_ratio": unique_ratio,
                                    },
                                    encoding_type=_infer_encoding_type(length, field.get("endian")),
                                ))
                                break

    return hypotheses


def infer_status_fields(
    field_hypotheses: List[Dict[str, Any]],
    role_hint: str,
    feature_summary: Optional[Dict[str, Any]],
) -> List[SemanticHypothesis]:
    """
    Detect status/error code fields.

    Characteristics:
    - Position: typically early in response messages
    - Width: 1 or 2 bytes
    - Cardinality: low (2-20 unique values)
    - Evidence: appears primarily in responses
    """
    hypotheses: List[SemanticHypothesis] = []

    # Only look for status fields in response messages
    if role_hint != "response":
        return hypotheses

    # Use feature summary to detect low cardinality fields in responses
    if feature_summary:
        position_stats = feature_summary.get("position_stats", {})

        # Check if position_stats is a dict with per-offset data or vectors
        if isinstance(position_stats, dict):
            # Check if it has vector format (entropy_vector, etc.) or per-offset format
            if "entropy_vector" in position_stats:
                # Vector format - skip status detection (not enough per-offset detail)
                pass
            else:
                # Per-offset format - process each offset
                for offset_str, stats in position_stats.items():
                    try:
                        offset = int(offset_str)
                    except (ValueError, TypeError):
                        continue  # Skip non-numeric keys

                    cardinality = stats.get("cardinality", 0)

                    # Low cardinality (2-20 unique values) suggests status/error code
                    if 2 <= cardinality <= 20:
                        # Find matching field hypothesis
                        for field in field_hypotheses:
                            start = field.get("start", 0)
                            length = field.get("length", 1)
                            if start <= offset < start + length and length in (1, 2):
                                hypotheses.append(SemanticHypothesis(
                                    field_start=start,
                                    field_length=length,
                                    semantic_role="status",
                                    confidence=0.55,
                                    evidence={
                                        "source": "feature_analysis",
                                        "cardinality": cardinality,
                                        "role": "response",
                                    },
                                    encoding_type=_infer_encoding_type(length, field.get("endian")),
                                ))
                                break

    return hypotheses


def infer_payload_fields(
    field_hypotheses: List[Dict[str, Any]],
    framing_summary: Optional[Dict[str, Any]],
    feature_summary: Optional[Dict[str, Any]],
) -> List[SemanticHypothesis]:
    """
    Detect payload/data fields.

    Characteristics:
    - Position: after header (use framing body_start)
    - Width: variable
    - Evidence: high entropy
    - Evidence: high uniqueness ratio
    """
    hypotheses: List[SemanticHypothesis] = []

    # Get body_start from framing
    body_start = None
    if framing_summary:
        for layout in framing_summary.get("layout_hypotheses", []):
            body_start = layout.get("body_start")
            if body_start is not None:
                break

    if body_start is None:
        return hypotheses

    # Find fields that start at or after body_start
    for field in field_hypotheses:
        start = field.get("start", 0)
        length = field.get("length", 1)

        if start >= body_start and length > 2:  # Payload fields are typically larger
            # Check entropy/uniqueness from features
            high_entropy = False
            if feature_summary:
                position_stats = feature_summary.get("position_stats", {})

                # Check if position_stats has vector format or per-offset format
                if isinstance(position_stats, dict) and "entropy_vector" in position_stats:
                    # Vector format - check entropy_vector
                    entropy_vector = position_stats.get("entropy_vector", [])
                    uniqueness_vector = position_stats.get("uniqueness_ratio_vector", [])

                    for offset in range(start, min(start + length, start + 8)):
                        if offset < len(entropy_vector):
                            entropy = entropy_vector[offset]
                            unique_ratio = uniqueness_vector[offset] if offset < len(uniqueness_vector) else 0.0
                            if entropy > 3.0 or unique_ratio > 0.7:
                                high_entropy = True
                                break
                elif isinstance(position_stats, dict):
                    # Per-offset format
                    for offset in range(start, min(start + length, start + 8)):
                        stats = position_stats.get(str(offset), {})
                        entropy = stats.get("entropy", 0.0)
                        unique_ratio = stats.get("unique_ratio", 0.0)
                        if entropy > 3.0 or unique_ratio > 0.7:
                            high_entropy = True
                            break

            confidence = 0.7 if high_entropy else 0.6
            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="payload",
                confidence=confidence,
                evidence={
                    "source": "framing",
                    "body_start": body_start,
                    "high_entropy": high_entropy,
                },
                encoding_type="bytes",
            ))

    return hypotheses


def infer_checksum_fields(
    field_hypotheses: List[Dict[str, Any]],
    messages_hex: Optional[List[str]] = None,
) -> List[SemanticHypothesis]:
    """
    Detect checksum/CRC fields.

    Characteristics:
    - Position: last 1, 2, or 4 bytes
    - Width: 1, 2, or 4 bytes
    - Evidence: appears at end of message
    - Evidence: high cardinality (appears random)

    Note: Cannot verify calculation without protocol knowledge.
    """
    hypotheses: List[SemanticHypothesis] = []

    if not field_hypotheses:
        return hypotheses

    # Find the last field
    last_field = max(field_hypotheses, key=lambda f: f.get("start", 0) + f.get("length", 0))
    start = last_field.get("start", 0)
    length = last_field.get("length", 1)

    # Checksums are typically 1, 2, or 4 bytes at the end
    if length in (1, 2, 4):
        # Check if it has high cardinality (suggests calculated value)
        evidence = last_field.get("evidence", {})
        cardinality_ratio = evidence.get("cardinality_ratio", 0.0)

        if cardinality_ratio > 0.5:  # High cardinality
            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role="checksum",
                confidence=0.6,
                evidence={
                    "source": "position_analysis",
                    "position": "last_field",
                    "cardinality_ratio": cardinality_ratio,
                },
                encoding_type=_infer_encoding_type(length, last_field.get("endian")),
            ))

    return hypotheses


def infer_constant_fields(
    field_hypotheses: List[Dict[str, Any]],
    feature_summary: Optional[Dict[str, Any]],
) -> List[SemanticHypothesis]:
    """
    Detect constant/reserved fields.

    Characteristics:
    - Cardinality: 1 (all same value)
    - Evidence: stability ratio = 1.0
    - Evidence: constant segment from boundary detection
    - Label as "reserved" if value is 0x00, else "constant"
    """
    hypotheses: List[SemanticHypothesis] = []

    for field in field_hypotheses:
        start = field.get("start", 0)
        length = field.get("length", 1)
        field_type = field.get("field_type", "")

        if field_type == "constant":
            evidence = dict(field.get("evidence", {}))
            unique_values = evidence.get("unique_values", 0)

            # Check if it's all zeros (reserved) or other constant
            is_reserved = False
            if feature_summary:
                position_stats = feature_summary.get("position_stats", {})

                # Check if position_stats has vector format or per-offset format
                if isinstance(position_stats, dict) and "entropy_vector" not in position_stats:
                    # Per-offset format
                    all_zero = True
                    for offset in range(start, start + length):
                        stats = position_stats.get(str(offset), {})
                        dominant_value = stats.get("dominant_value_hex", "")
                        if dominant_value != "00":
                            all_zero = False
                            break
                    is_reserved = all_zero
                # For vector format, we can't easily check dominant values, so skip

            semantic_role = "reserved" if is_reserved else "constant"
            hypotheses.append(SemanticHypothesis(
                field_start=start,
                field_length=length,
                semantic_role=semantic_role,
                confidence=float(field.get("confidence", 0.9)),
                evidence=evidence,
                encoding_type=_infer_encoding_type(length, field.get("endian")),
            ))

    return hypotheses


def _infer_encoding_type(length: int, endian: Optional[str]) -> Optional[str]:
    """Infer encoding type from field length and endianness."""
    if length == 1:
        return "uint8"
    elif length == 2:
        if endian == "big":
            return "uint16_be"
        elif endian == "little":
            return "uint16_le"
        return "uint16"
    elif length == 4:
        if endian == "big":
            return "uint32_be"
        elif endian == "little":
            return "uint32_le"
        return "uint32"
    elif length > 4:
        return "bytes"
    return None
