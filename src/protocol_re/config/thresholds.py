"""
Centralized thresholds and tuning parameters for the protocol RE pipeline.

All magic numbers that affect algorithm behaviour live here, organised by
subsystem.  Each group is a plain namespace class so that values are
accessible as ``Group.NAME`` and can be imported directly.

When adding a new threshold:
    1. Place it in the appropriate group (or create one if needed).
    2. Give it a descriptive UPPER_CASE name.
    3. Add a docstring or inline comment explaining what it controls and why
       the current value was chosen.
    4. Re-export it from the originating module for backward compatibility,
       e.g. ``from protocol_re.config.thresholds import BoundaryDetection;
       MAX_FIELDS_PER_FAMILY = BoundaryDetection.MAX_FIELDS_PER_FAMILY``.
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# Feature Extraction
# ═══════════════════════════════════════════════════════════════════════════════


class FeatureExtraction:
    """Thresholds for :mod:`protocol_re.features.extraction`."""

    # Sizes of byte n-grams used for frequency profiling.
    NGRAM_SIZES: tuple[int, ...] = (2, 3)

    # Sizes of structural motifs (repeating byte patterns).
    STRUCTURAL_MOTIF_SIZES: tuple[int, ...] = (4, 5, 6, 8)

    # Maximum number of top byte-values to retain per offset in position stats.
    TOP_VALUES_LIMIT: int = 8

    # Maximum number of top motifs to retain per family.
    TOP_MOTIFS_LIMIT: int = 10

    # Maximum number of top n-gram frequencies to retain per family.
    TOP_NGRAM_FREQUENCIES_LIMIT: int = 20

    # Maximum number of top structural motifs to retain per family.
    TOP_STRUCTURAL_MOTIFS_LIMIT: int = 15

    # Sizes of trailing suffix bytes to extract for structural features.
    TRAILING_SUFFIX_SIZES: tuple[int, ...] = (1, 2, 4, 8)

    # Maximum bytes analysed for per-offset position statistics.
    MAX_POSITION_STATS_LENGTH: int = 512

    # Maximum bytes analysed for n-gram frequency extraction.
    MAX_NGRAM_ANALYSIS_LENGTH: int = 1024


# ═══════════════════════════════════════════════════════════════════════════════
# Boundary Detection
# ═══════════════════════════════════════════════════════════════════════════════


class BoundaryDetection:
    """Thresholds for :mod:`protocol_re.inference.boundary_detection`."""

    # Maximum message length (bytes) analysed during boundary detection.
    MAX_BOUNDARY_DETECTION_LENGTH: int = 512

    # Hard cap on the number of field segments per message family.
    # Prevents over-segmentation / fragmentation.
    MAX_FIELDS_PER_FAMILY: int = 15

    # Default minimum field width (bytes). 1 = no minimum beyond single byte.
    MIN_FIELD_WIDTH_DEFAULT: int = 1

    # Confidence penalty multiplier applied to 1-byte variable fields
    # unless backed by strong evidence (confidence >= 0.9).
    SINGLE_BYTE_PENALTY: float = 0.5

    # Weight assigned to the entropy-jump term when scoring field boundaries.
    # Reduced from the original 1.2 to avoid over-weighting entropy changes.
    ENTROPY_WEIGHT_REDUCED: float = 0.6

    # Target field widths (bytes) that the segment merger prefers when
    # combining adjacent small fields.
    MERGE_WIDTH_TARGETS_DEFAULT: tuple[int, ...] = (2, 4)

    # Widths (bytes) to scan when searching for length-field candidates.
    LENGTH_FIELD_WIDTHS_DEFAULT: tuple[int, ...] = (2, 4)

    # Minimum fraction of messages where a candidate field's numeric value
    # must match the remaining message length to be considered a length field.
    LENGTH_MATCH_THRESHOLD_DEFAULT: float = 0.8

    # Weight given to boundary-support evidence when computing overall
    # segment confidence (0–1). Higher values make the segmenter more
    # sensitive to detected boundary jumps.
    BOUNDARY_CONFIDENCE_WEIGHT_DEFAULT: float = 0.45

    # Opcode/command isolation: when a confident framing/body boundary is
    # known, the first byte of the application body is very often a message
    # type / function / command code. If that leading body byte is constant
    # or near-constant within the family, force a 1-byte boundary right after
    # it and protect it from being merged into the following field. This keeps
    # the discriminator byte (e.g. a Modbus function code) as its own field
    # instead of being fused into a wider uint16/uint32 chunk.
    ISOLATE_BODY_OPCODE: bool = True

    # Maximum cardinality ratio (distinct values / observations) for the
    # leading body byte to be treated as an opcode/command and isolated.
    # A true opcode is constant within a single-message-type family (ratio
    # ~0); the small allowance tolerates families that mix a few codes.
    OPCODE_MAX_CARDINALITY_RATIO: float = 0.05


# ═══════════════════════════════════════════════════════════════════════════════
# Request-Response Relations
# ═══════════════════════════════════════════════════════════════════════════════


class RequestResponseRelations:
    """Thresholds for :mod:`protocol_re.inference.request_response_relations`."""

    # Maximum width (bytes) of an echo field candidate.
    MAX_ECHO_WIDTH: int = 4

    # Minimum number of request-response pairs required to retain a family
    # edge during pruning.
    DEFAULT_MIN_EDGE_PAIRS: int = 2

    # Minimum edge lift required to retain a family edge.
    # Lift = observed co-occurrence / expected co-occurrence.
    DEFAULT_MIN_EDGE_LIFT: float = 1.0

    # Maximum number of response families allowed per request family after
    # pruning.
    DEFAULT_MAX_RESPONSE_FAMILIES_PER_REQUEST: int = 5

    # Maximum prefix bytes scanned for echo-field candidates.
    # Reduced from 256 to focus on header regions.
    MAX_ECHO_SEARCH_LENGTH: int = 64

    # Maximum prefix bytes scanned for length-relation candidates.
    # Reduced from 128 to focus on header regions.
    MAX_LENGTH_FIELD_SEARCH_LENGTH: int = 64

    # Step size (bytes) when scanning for echo-field positions.
    ECHO_SEARCH_STRIDE: int = 1

    # Maximum number of evidence payload pairs to sample per family edge.
    MAX_EVIDENCE_PAIRS_PER_EDGE: int = 500

    # Minimum support (fraction of pairs that match) for echo-field detection.
    DEFAULT_MIN_ECHO_SUPPORT: float = 0.8

    # Minimum support for length-relation detection.
    DEFAULT_MIN_LENGTH_SUPPORT: float = 0.75

    # Minimum overall confidence required to retain a detected relation.
    MIN_CONFIDENCE_THRESHOLD: float = 0.7


# ═══════════════════════════════════════════════════════════════════════════════
# Framing Detection
# ═══════════════════════════════════════════════════════════════════════════════


class FramingDetection:
    """Thresholds for :mod:`protocol_re.inference.framing`."""

    # Default maximum number of prefix bytes scanned for framing fields.
    MAX_HEADER_BYTES: int = 32

    # Maximum number of layout hypotheses retained per family.
    MAX_HYPOTHESES_PER_FAMILY: int = 3

    # Minimum number of messages required for non-fallback family inference.
    MIN_MESSAGES: int = 3

    # Divisor used to normalise raw boundary scores into [0, 1] confidence.
    # Confidence = min(1.0, max(0.0, raw_score / NORMALISER)).
    CONFIDENCE_SCORE_NORMALISER: float = 6.0

    # --- Field candidate thresholds ---

    # Minimum stable ratio for a byte position to be considered constant.
    CONSTANT_STABLE_RATIO: float = 0.95
    CONSTANT_COVERAGE: float = 0.9

    # Minimum match ratio for a candidate length field.
    LENGTH_MATCH_RATIO: float = 0.65

    # Counter / transaction-id field detection thresholds.
    COUNTER_UNIQUE_RATIO_MIN: float = 0.45
    COUNTER_SCORE_MIN: float = 0.62
    COUNTER_UNIQUE_WEIGHT: float = 0.35
    COUNTER_SEQUENCE_WEIGHT: float = 0.45
    COUNTER_MONOTONIC_WEIGHT: float = 0.20

    # Low-cardinality (discriminator) field detection.
    DISCRIMINATOR_COVERAGE_MIN: float = 0.9
    DISCRIMINATOR_CARDINALITY_MIN: int = 2
    DISCRIMINATOR_CARDINALITY_MAX: int = 16
    DISCRIMINATOR_STABLE_RATIO_MAX: float = 0.95
    DISCRIMINATOR_UNIQUE_RATIO_MAX: float = 0.35
    DISCRIMINATOR_COVERAGE_WEIGHT: float = 0.45
    DISCRIMINATOR_UNIQUE_WEIGHT: float = 0.35
    DISCRIMINATOR_CARDINALITY_WEIGHT: float = 0.20
    DISCRIMINATOR_CONFIDENCE_CAP: float = 0.9

    # --- Header boundary scoring weights ---

    # Weights applied to each field type when scoring boundary candidates.
    FIELD_WEIGHT_LENGTH: float = 1.25
    FIELD_WEIGHT_TRANSACTION_OR_COUNTER: float = 0.95
    FIELD_WEIGHT_DISCRIMINATOR: float = 0.75
    FIELD_WEIGHT_CONSTANT: float = 0.55
    FIELD_WEIGHT_UNKNOWN: float = 0.4

    # Boundary scoring term weights.
    BOUNDARY_FIELD_SCORE_WEIGHT: float = 1.0
    BOUNDARY_COVERAGE_WEIGHT: float = 0.8
    BOUNDARY_STABILITY_WEIGHT: float = 0.7
    BOUNDARY_TAIL_JUMP_WEIGHT: float = 0.9
    BOUNDARY_TAIL_JUMP_DIVISOR: float = 3.0
    BOUNDARY_SIZE_PENALTY_THRESHOLD: int = 16
    BOUNDARY_SIZE_PENALTY_DIVISOR: int = 32

    # Boost/penalty for preferred layer-aligned boundaries.
    PREFERRED_BOUNDARY_BOOST: float = 0.75
    PREFERRED_BOUNDARY_BEYOND_PENALTY: float = 0.75
    PREFERRED_BOUNDARY_BEFORE_PENALTY: float = 0.2

    # Baseline score for a zero-width header (no framing detected).
    ZERO_BOUNDARY_SCORE: float = 0.15

    # Minimum confidence for length-field layer-boundary hints.
    LENGTH_LAYER_MIN_CONFIDENCE: float = 0.65

    # Additional byte added to boundary when the next byte looks like a
    # selector/discriminator field.
    SELECTOR_LIKE_COVERAGE_MIN: float = 0.9
    SELECTOR_LIKE_STABLE_RATIO_MIN: float = 0.8
    SELECTOR_LIKE_UNIQUE_RATIO_MAX: float = 0.35
    SELECTOR_LIKE_CARDINALITY_MIN: int = 1
    SELECTOR_LIKE_CARDINALITY_MAX: int = 16

    # Minimum confidence for a header candidate to be counted in global stats.
    GLOBAL_HEADER_MIN_CONFIDENCE: float = 0.45

    # --- Position evidence compaction ---

    # Maximum number of position-evidence entries included in compact output.
    COMPACT_POSITION_EVIDENCE_LIMIT: int = 16

    # Tail window size (bytes) used for variability jump calculation.
    TAIL_VARIABILITY_WINDOW: int = 8


# ═══════════════════════════════════════════════════════════════════════════════
# Layer Detection
# ═══════════════════════════════════════════════════════════════════════════════


class LayerDetection:
    """Thresholds for :mod:`protocol_re.inference.layer_detection`."""

    # Default minimum confidence to report a detected layer boundary.
    MIN_CONFIDENCE: float = 0.6

    # Maximum possible raw score used to normalise confidence to [0, 1].
    MAX_POSSIBLE_RAW_SCORE: float = 3.5

    # Multiplicative confidence boost when multiple indicators agree on the
    # same boundary offset.
    MULTI_INDICATOR_BOOST: float = 1.2

    # Indicator type weights for scoring potential boundary offsets.
    INDICATOR_WEIGHT_LENGTH_TO_BODY: float = 1.5
    INDICATOR_WEIGHT_TRANSACTION_COUNTER: float = 1.0
    INDICATOR_WEIGHT_CONSTANT_PREFIX: float = 0.8


# ═══════════════════════════════════════════════════════════════════════════════
# Discriminator Detection
# ═══════════════════════════════════════════════════════════════════════════════


class DiscriminatorDetection:
    """Thresholds for :mod:`protocol_re.inference.discriminator_fields`."""

    # Role tokens that suppress a byte position from being considered a
    # discriminator candidate (these fields already have a known role).
    SUPPRESSED_ROLE_TOKENS: tuple[str, ...] = (
        "length",
        "transaction",
        "counter",
        "checksum",
        "timestamp",
        "blob",
    )

    # Default maximum byte offset scanned for discriminator candidates.
    MAX_OFFSET: int = 128

    # Number of top-scoring candidates retained per family.
    TOP_K: int = 5

    # --- Candidate filtering thresholds ---

    MIN_COVERAGE: float = 0.5
    MIN_CARDINALITY: int = 2

    # Ideal cardinality for a discriminator (peak of the scoring curve).
    IDEAL_CARDINALITY: int = 4
    CARDINALITY_RANGE_DIVISOR: float = 16.0

    # Maximum cardinality for the symbolic cardinality score to be non-zero.
    MAX_SYMBOLIC_CARDINALITY: int = 32

    # High-cardinality penalty: if cardinality exceeds this fraction of
    # distinct values the score is multiplied by the penalty factor.
    HIGH_CARDINALITY_RATIO_THRESHOLD: float = 0.45
    HIGH_CARDINALITY_PENALTY: float = 0.35

    # Minimum combined score for a candidate to be retained.
    MIN_SCORE: float = 0.08

    # --- Composite score weights ---

    SCORE_LEARNED_WEIGHT: float = 0.30
    SCORE_FAMILY_MI_WEIGHT: float = 0.24
    SCORE_DIRECTION_MI_WEIGHT: float = 0.16
    SCORE_CARDINALITY_WEIGHT: float = 0.14
    SCORE_CONTRASTIVE_WEIGHT: float = 0.10
    SCORE_STABILITY_WEIGHT: float = 0.06

    # --- Contrastive separation ---

    CONTRASTIVE_PURITY_WEIGHT: float = 0.75
    CONTRASTIVE_BALANCE_WEIGHT: float = 0.25
    CONTRASTIVE_BALANCE_DIVISOR: float = 16.0

    # --- Excluded role detection ---

    EXCLUDED_UNIQUE_RATIO_MIN: float = 0.8
    EXCLUDED_COVERAGE_MIN: float = 0.8


# ═══════════════════════════════════════════════════════════════════════════════
# Keyword Detection
# ═══════════════════════════════════════════════════════════════════════════════


class KeywordDetection:
    """Thresholds for :mod:`protocol_re.inference.keyword_detection`."""

    # Default search range for keyword/discriminator byte discovery
    # (start offset, end offset).
    SEARCH_RANGE_START: int = 4
    SEARCH_RANGE_END: int = 20


# ═══════════════════════════════════════════════════════════════════════════════
# Field Semantics
# ═══════════════════════════════════════════════════════════════════════════════


class FieldSemantics:
    """Thresholds for :mod:`protocol_re.inference.field_semantics` and
    :mod:`protocol_re.inference.semantic_labeling`."""

    # --- Discriminator ---

    DISCRIMINATOR_FRAMING_BOOST: float = 0.1
    DISCRIMINATOR_KEYWORD_BOOST: float = 0.05
    DISCRIMINATOR_MAX_CONFIDENCE: float = 0.95
    DISCRIMINATOR_FRAMING_BASE_CONFIDENCE: float = 0.7
    DISCRIMINATOR_KEYWORD_BASE_CONFIDENCE: float = 0.6

    # --- Transaction ID ---

    TRANSACTION_ID_ECHO_BOOST: float = 0.2
    TRANSACTION_ID_ECHO_MAX_CONFIDENCE: float = 0.95
    TRANSACTION_ID_HIGH_UNIQUE_CONFIDENCE: float = 0.85
    TRANSACTION_ID_COUNTER_BOOST: float = 0.1
    TRANSACTION_ID_AMBIGUOUS_FACTOR: float = 0.8
    TRANSACTION_ID_HIGH_UNIQUE_RATIO: float = 0.7
    TRANSACTION_ID_MEDIUM_UNIQUE_RATIO: float = 0.5
    TRANSACTION_ID_ECHO_BASE: float = 0.55
    TRANSACTION_ID_ECHO_SUPPORT_WEIGHT: float = 0.4
    TRANSACTION_ID_ECHO_MAX: float = 0.9

    # --- Counter / Sequence Number ---

    COUNTER_MONOTONIC_MIN: float = 0.8
    COUNTER_SMALL_DELTA_MIN: float = 0.5
    COUNTER_UNIQUE_RATIO_LOW: float = 0.5
    COUNTER_SMALL_DELTA_HIGH: float = 0.7

    # --- Address ---

    ADDRESS_CARDINALITY_MIN: int = 2
    ADDRESS_CARDINALITY_MAX: int = 100
    ADDRESS_UNIQUE_RATIO_MIN: float = 0.05
    ADDRESS_UNIQUE_RATIO_MAX: float = 0.5
    ADDRESS_BASE_CONFIDENCE: float = 0.6

    # --- Status ---

    STATUS_CARDINALITY_MIN: int = 2
    STATUS_CARDINALITY_MAX: int = 20
    STATUS_BASE_CONFIDENCE: float = 0.55

    # --- Payload ---

    PAYLOAD_MIN_LENGTH: int = 2  # fields shorter than this are not payload
    PAYLOAD_HIGH_ENTROPY_THRESHOLD: float = 3.0
    PAYLOAD_HIGH_UNIQUENESS_THRESHOLD: float = 0.7
    PAYLOAD_CONFIDENCE_HIGH: float = 0.7
    PAYLOAD_CONFIDENCE_LOW: float = 0.6
    PAYLOAD_ENTROPY_CHECK_WINDOW: int = 8

    # --- Checksum ---

    CHECKSUM_CARDINALITY_MIN: float = 0.5
    CHECKSUM_BASE_CONFIDENCE: float = 0.6

    # --- Constant ---

    CONSTANT_BASE_CONFIDENCE: float = 0.99
    FLAGS_OR_STATUS_MAX_CARDINALITY: int = 8
    FLAGS_OR_STATUS_BASE_CONFIDENCE: float = 0.7

    # --- Length field ---

    LENGTH_MATCH_THRESHOLD: float = 0.8
    KEYWORD_CARDINALITY_MAX: float = 0.2
    COUNTER_CARDINALITY_MIN: float = 0.8


# ═══════════════════════════════════════════════════════════════════════════════
# LLM Evidence
# ═══════════════════════════════════════════════════════════════════════════════


class LLMEvidence:
    """Thresholds for :mod:`protocol_re.llm.evidence_builders`."""

    # Maximum number of hex characters included in a prompt evidence snippet.
    MAX_PROMPT_HEX_CHARS: int = 100


# ═══════════════════════════════════════════════════════════════════════════════
# Neural Model
# ═══════════════════════════════════════════════════════════════════════════════


class NeuralModel:
    """Thresholds for :mod:`protocol_re.neural.model_loader`."""

    # Default filename for the pre-trained VAE encoder weights.
    DEFAULT_MODEL_PATH: str = "industrial_VAE.pth"


# ═══════════════════════════════════════════════════════════════════════════════
# Clustering
# ═══════════════════════════════════════════════════════════════════════════════


class Clustering:
    """Thresholds for :mod:`protocol_re.clustering`."""

    # Batch size used for centroid-based assignment of messages to clusters.
    CENTROID_ASSIGNMENT_BATCH_SIZE: int = 10000

    # Field types that are intrinsically high-volatility (not useful for
    # structural fingerprinting).  These are excluded from structural feature
    # vectors.
    HIGH_VOLATILITY_FIELD_TYPES: frozenset[str] = frozenset(
        {
            "transaction_id",
            "transaction-id",
            "sequence",
            "sequence_number",
            "seq",
            "timestamp",
            "checksum",
            "crc",
            "nonce",
            "random_nonce",
            "payload_blob",
            "blob",
        }
    )
