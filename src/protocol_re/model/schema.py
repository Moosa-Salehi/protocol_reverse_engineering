from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MessageRecord:
    msg_id: int
    source_file: str
    session_id: str
    session_key: str
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    direction: str
    payload_hex: str
    payload_len: int
    timestamp: Optional[float] = None
    index_in_session: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if not data["metadata"]:
            data.pop("metadata")
        return data


@dataclass
class FamilyAssignment:
    msg_id: int
    family_id: str
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PairRecord:
    request_msg_id: int
    response_msg_id: int
    session_id: str
    score: float
    latency_ms: Optional[float] = None
    request_family_id: Optional[str] = None
    response_family_id: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Segment:
    start: int
    end: int
    kind: str = "unknown"
    confidence: float = 0.0
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FieldHypothesis:
    family_id: str
    start: int
    length: int
    field_type: str
    confidence: float
    endian: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FamilySemanticSummary:
    family_id: str
    role: str = "unknown"
    confidence: float = 0.0
    field_labels: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FamilyFeatureSummary:
    family_id: str
    message_count: int
    length_stats: Dict[str, Any] = field(default_factory=dict)
    position_stats: Dict[str, Any] = field(default_factory=dict)
    aggregate_byte_histogram: Dict[str, Any] = field(default_factory=dict)
    entropy_summary: Dict[str, Any] = field(default_factory=dict)
    unique_ratio_summary: Dict[str, Any] = field(default_factory=dict)
    run_length_summary: Dict[str, Any] = field(default_factory=dict)
    motif_stats: Dict[str, Any] = field(default_factory=dict)
    structure_stats: Dict[str, Any] = field(default_factory=dict)
    example_msg_ids: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FamilyModel:
    family_id: str
    role: str
    message_count: int
    template: str
    segments: List[Segment] = field(default_factory=list)
    field_hypotheses: List[FieldHypothesis] = field(default_factory=list)
    feature_summary: Optional[FamilyFeatureSummary] = None
    semantic_summary: Optional[FamilySemanticSummary] = None
    keyword_summary: Optional[Dict[str, Any]] = None
    framing_summary: Optional[Dict[str, Any]] = None
    related_families: List[str] = field(default_factory=list)
    examples: List[int] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["segments"] = [segment.to_dict() for segment in self.segments]
        data["field_hypotheses"] = [field.to_dict() for field in self.field_hypotheses]
        data["feature_summary"] = self.feature_summary.to_dict() if self.feature_summary else None
        data["semantic_summary"] = self.semantic_summary.to_dict() if self.semantic_summary else None
        return data


@dataclass
class FamilyRelation:
    request_family_id: str
    response_family_id: str
    pair_count: int
    avg_pair_score: float
    support_ratio: float = 0.0
    edge_lift: float = 0.0
    direction_consistency: float = 0.0
    dominant_direction: str = "unknown"
    temporal_order_consistency: float = 0.0
    order_usable_pairs: int = 0
    avg_latency_ms: Optional[float] = None
    relation_type: Optional[str] = None
    semantic_label: Optional[str] = None
    confidence: Optional[float] = None
    echo_fields: List[Dict[str, Any]] = field(default_factory=list)
    length_relations: List[Dict[str, Any]] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ProtocolModel:
    protocol_name: str = "unknown-industrial-protocol"
    version: str = "0.1"
    families: List[FamilyModel] = field(default_factory=list)
    relations: List[FamilyRelation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol_name": self.protocol_name,
            "version": self.version,
            "metadata": self.metadata,
            "families": [family.to_dict() for family in self.families],
            "relations": [relation.to_dict() for relation in self.relations],
        }
