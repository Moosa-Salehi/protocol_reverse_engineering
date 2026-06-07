from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from protocol_re.config.thresholds import LayerDetection as _LD
from protocol_re.utils.bytes import hex_to_bytes


@dataclass
class LayerBoundary:
    """Represents a detected boundary between protocol layers."""
    offset: int
    confidence: float
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "offset": self.offset,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class LayerInfo:
    """Layer structure information for a message family."""
    has_layers: bool
    outer_header_end: int
    inner_payload_start: int
    confidence: float
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_layers": self.has_layers,
            "outer_header_end": self.outer_header_end,
            "inner_payload_start": self.inner_payload_start,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


def detect_layer_boundary_from_framing(
    framing_result: Dict[str, Any],
    min_confidence: float = _LD.MIN_CONFIDENCE,
) -> Optional[LayerBoundary]:
    """
    Detect layer boundary from framing analysis results.

    Uses framing evidence to identify potential transport/application layer split:
    - Length fields pointing past their position suggest transport header
    - Stable prefix + variable suffix suggests layer boundary
    - Transaction/counter fields in header region suggest transport layer

    Args:
        framing_result: Framing analysis result for a single family
        min_confidence: Minimum confidence threshold for layer detection

    Returns:
        LayerBoundary if detected, None otherwise
    """
    layout_hypotheses = framing_result.get("layout_hypotheses", [])
    if not layout_hypotheses:
        return None

    # Use best layout hypothesis
    best_layout = layout_hypotheses[0]
    header_end = best_layout.get("header_end", 0)

    if header_end == 0:
        return None

    field_regions = best_layout.get("field_regions", [])
    if not field_regions:
        return None

    # Analyze field regions for layer indicators
    layer_indicators = []
    length_field_found = False
    counter_field_found = False
    constant_prefix_len = 0

    for region in field_regions:
        field_type = region.get("field_type", "")
        start = region.get("start", 0)
        end = region.get("end", 0)
        region_confidence = region.get("confidence", 0.0)

        if field_type == "length":
            length_field_found = True
            evidence = region.get("evidence", {})
            relation = evidence.get("relation", "")

            # Length field pointing to body after field suggests transport header
            if relation in ("body_after_field", "remaining_from_field"):
                layer_indicators.append({
                    "type": "length_field_to_body",
                    "offset": end,
                    "confidence": region_confidence,
                    "weight": _LD.INDICATOR_WEIGHT_LENGTH_TO_BODY,
                })

        elif field_type == "transaction_or_counter":
            counter_field_found = True
            layer_indicators.append({
                "type": "transaction_counter",
                "offset": end,
                "confidence": region_confidence,
                "weight": _LD.INDICATOR_WEIGHT_TRANSACTION_COUNTER,
            })

        elif field_type == "constant":
            if start == 0:
                constant_prefix_len = end
                layer_indicators.append({
                    "type": "constant_prefix",
                    "offset": end,
                    "confidence": region_confidence,
                    "weight": _LD.INDICATOR_WEIGHT_CONSTANT_PREFIX,
                })

    if not layer_indicators:
        return None

    # Score potential layer boundaries
    boundary_scores: Dict[int, float] = {}
    boundary_evidence: Dict[int, List[str]] = {}

    for indicator in layer_indicators:
        offset = indicator["offset"]
        score = indicator["confidence"] * indicator["weight"]
        boundary_scores[offset] = boundary_scores.get(offset, 0.0) + score
        boundary_evidence.setdefault(offset, []).append(indicator["type"])

    # Find best boundary
    if not boundary_scores:
        return None

    best_offset = max(boundary_scores.keys(), key=lambda k: boundary_scores[k])
    best_score = boundary_scores[best_offset]

    # Normalize confidence (max possible score ~3.5 with all indicators)
    confidence = min(best_score / _LD.MAX_POSSIBLE_RAW_SCORE, 1.0)

    if confidence < min_confidence:
        return None

    # Additional confidence boost if multiple indicators agree
    if len(boundary_evidence[best_offset]) >= 2:
        confidence = min(confidence * _LD.MULTI_INDICATOR_BOOST, 1.0)

    return LayerBoundary(
        offset=best_offset,
        confidence=round(confidence, 4),
        evidence={
            "indicators": boundary_evidence[best_offset],
            "indicator_count": len(boundary_evidence[best_offset]),
            "length_field_found": length_field_found,
            "counter_field_found": counter_field_found,
            "constant_prefix_len": constant_prefix_len,
            "header_end": header_end,
        },
    )


def analyze_family_layers(
    family_id: str,
    framing_result: Dict[str, Any],
    min_confidence: float = _LD.MIN_CONFIDENCE,
) -> LayerInfo:
    """
    Analyze layer structure for a message family.

    Args:
        family_id: Family identifier
        framing_result: Framing analysis result for this family
        min_confidence: Minimum confidence for layer detection

    Returns:
        LayerInfo with layer structure information
    """
    boundary = detect_layer_boundary_from_framing(framing_result, min_confidence)

    if boundary is None:
        # No layers detected - treat as flat protocol
        return LayerInfo(
            has_layers=False,
            outer_header_end=0,
            inner_payload_start=0,
            confidence=0.0,
            evidence={"reason": "no_layer_boundary_detected"},
        )

    return LayerInfo(
        has_layers=True,
        outer_header_end=boundary.offset,
        inner_payload_start=boundary.offset,
        confidence=boundary.confidence,
        evidence=boundary.evidence,
    )


def extract_inner_protocol(
    messages_hex: Sequence[str],
    layer_info: LayerInfo,
) -> List[str]:
    """
    Extract inner protocol payloads from messages.

    Args:
        messages_hex: List of message payloads in hex format
        layer_info: Layer structure information

    Returns:
        List of inner protocol payloads (hex), or original messages if no layers
    """
    if not layer_info.has_layers:
        return list(messages_hex)

    inner_payloads = []
    offset = layer_info.inner_payload_start

    for msg_hex in messages_hex:
        msg_bytes = hex_to_bytes(msg_hex)
        if len(msg_bytes) <= offset:
            # Message too short, keep as-is
            inner_payloads.append(msg_hex)
        else:
            # Extract inner protocol
            inner_bytes = msg_bytes[offset:]
            inner_hex = inner_bytes.hex()
            inner_payloads.append(inner_hex)

    return inner_payloads


def analyze_all_families(
    framing_data: Dict[str, Any],
    min_confidence: float = _LD.MIN_CONFIDENCE,
) -> Dict[str, LayerInfo]:
    """
    Analyze layer structure for all families in framing data.

    Args:
        framing_data: Complete framing analysis output
        min_confidence: Minimum confidence for layer detection

    Returns:
        Dictionary mapping family_id to LayerInfo
    """
    families = framing_data.get("families", {})
    layer_info_by_family: Dict[str, LayerInfo] = {}

    for family_id, framing_result in families.items():
        layer_info = analyze_family_layers(family_id, framing_result, min_confidence)
        layer_info_by_family[family_id] = layer_info

    return layer_info_by_family


def get_layer_statistics(layer_info_map: Dict[str, LayerInfo]) -> Dict[str, Any]:
    """
    Compute statistics about layer detection across families.

    Args:
        layer_info_map: Dictionary mapping family_id to LayerInfo

    Returns:
        Statistics dictionary
    """
    total_families = len(layer_info_map)
    layered_families = sum(1 for info in layer_info_map.values() if info.has_layers)

    if layered_families == 0:
        return {
            "total_families": total_families,
            "layered_families": 0,
            "layered_ratio": 0.0,
            "avg_confidence": 0.0,
            "avg_header_size": 0.0,
        }

    confidences = [info.confidence for info in layer_info_map.values() if info.has_layers]
    header_sizes = [info.outer_header_end for info in layer_info_map.values() if info.has_layers]

    return {
        "total_families": total_families,
        "layered_families": layered_families,
        "layered_ratio": round(layered_families / total_families, 4),
        "avg_confidence": round(sum(confidences) / len(confidences), 4),
        "avg_header_size": round(sum(header_sizes) / len(header_sizes), 2),
        "min_header_size": min(header_sizes),
        "max_header_size": max(header_sizes),
    }
