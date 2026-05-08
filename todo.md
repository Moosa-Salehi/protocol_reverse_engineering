  ### TODO 2. Stop writing per-message feature JSON

  - Files
      - scripts/05_extract_features.py
      - src/protocol_re/features/extraction.py

  ### TODO 3. Add relation graph pruning before expensive echo analysis

  - Files
      - src/protocol_re/inference/request_response_relations.py
      - scripts/10_infer_relations.py
  - Tasks
      - Compute edge-level features before echo detection:
          - pair_count
          - support ratio
          - edge lift over request/response family base rates
          - direction consistency
          - temporal/order consistency
      - Drop edges below minimum support/lift.
      - Drop self-edges unless strong evidence supports same-family request/response behavior.
      - Keep top K candidate response families per request family.
      - Run _echo_candidates() and _length_relations() only on retained edges.
      - Add CLI thresholds:
          - --min-edge-pairs
          - --min-edge-lift
          - --max-response-families-per-request
          - --allow-self-relations

  ### TODO 4. Preserve or infer direction in legacy JSON mode

  - Files
      - src/protocol_re/corpus/message_corpus.py
      - scripts/03_alt_build_corpus.py
      - main.py
  - Current issue
      - Legacy mode forces direction="unknown" even when source/destination ports are available.

  ### TODO 5. Add protocol-agnostic framing hypothesis module

  - Files
      - New: src/protocol_re/inference/framing.py
      - New optional script: scripts/04_infer_framing.py
      - Integrate with other files
      - update script's number accordingly
        
  - Current issue
      - The pipeline assumes each payload is already the semantic protocol body.
  - Tasks
      - Infer candidate common header regions using:
          - stable prefixes
          - recurring constants
          - length fields
          - transaction/correlation fields
          - sequence/counter-like fields
          - low-cardinality discriminator fields
          - payload-tail variability
      - Emit multiple scored layout hypotheses:
          - header start/end
          - body start/end
          - candidate field regions
          - confidence
          - supporting evidence
      - Do not hard-code any protocol.
      - Store hypothesis metadata per family and globally.
  - Expected impact
      - Accuracy: ↑↑
      - Runtime: neutral initially, ↓ downstream after pruning
  - Risk
      - Medium-high. Needs robust scoring and fallback behavior.

  ### TODO 6. Add generic length-field detection

  - Files
      - src/protocol_re/inference/framing.py
      - src/protocol_re/inference/boundary_detection.py
  - Tasks
      - For widths 1, 2, 4, and possibly 8:
          - Test big/little endian values.
          - Test value equals total message length.
          - Test value equals remaining length after the field.
          - Test value equals payload/body length.
          - Test value equals count-scaled payload length, e.g. value * 2, value + constant.
      - Store role hypothesis length.
      - Store relation type:
          - total_length
          - remaining_length
          - body_length
          - count_scaled_length

  ### TODO 7. Add transaction/correlation-field detection

  - Files
      - src/protocol_re/inference/framing.py
      - src/protocol_re/corpus/request_response_pairing.py
      - src/protocol_re/inference/request_response_relations.py
  - Tasks
      - Search candidate fields that:
          - have high cardinality
          - are often echoed between temporally close request/response candidates
          - are not random payload tails
          - have stable offsets across families
      - Label role as transaction_id or correlation_id.
      - Use these candidates to improve pairing.
  - Expected impact
      - Accuracy: ↑↑ for relations
      - Runtime: ↓ downstream

  ### TODO 8. Add discriminator/opcode candidate discovery

  - Files
      - New or existing:
          - src/protocol_re/inference/keyword_detection.py
          - src/protocol_re/inference/framing.py
  - Current issue
      - Current keyword detection selects max-entropy bytes in offsets 4-19.
  - Tasks
      - Replace max-entropy selection with discriminator scoring.
      - Score fields by:
          - low-to-medium cardinality
          - high mutual information with family assignment
          - high mutual information with role/direction
          - explains length/profile differences
          - stable offset
          - not length-like
          - not counter-like
          - not transaction-like
      - Search across all plausible offsets, not fixed range 4-19.
      - Rename output concept from keyword to discriminator_candidates.
  - Expected impact
      - Accuracy: ↑
      - Runtime: neutral or ↓
  - Risk
      - Medium.

  ### TODO 9. Add structural feature vectors for clustering

  - Files
      - src/protocol_re/clustering/family_discovery.py
      - New helper: src/protocol_re/clustering/structural_features.py
  - Current issue
      - vectorize_messages() clusters padded raw bytes, overweighting counters, transaction IDs, payload data, and random values.
  - Tasks
      - Add a new clustering feature mode:
          - raw_bytes
          - structural
          - hybrid
      - Structural features should include:
          - payload length bucket
          - candidate discriminator values
          - stable prefix mask
          - common header/body split
          - direction or endpoint role
          - length-field pattern
          - constant field pattern
          - entropy profile summary
      - Downweight fields classified as:
          - transaction/correlation ID
          - sequence number
          - timestamp
          - checksum
          - payload blob
      - Keep raw-byte fallback when structural evidence is weak.
  - Expected impact
      - Accuracy: ↑↑
      - Runtime: ↓ or neutral

  ### TODO 10. Add clustering quality diagnostics

  - Files
      - src/protocol_re/evaluation/reporting.py
      - scripts/13_evaluate_pipeline.py
  - Tasks
      - Report:
          - cluster purity proxy by discriminator candidates
          - length-profile consistency
          - direction consistency
          - field-layout consistency
          - noise ratio
          - over-split suspicion
          - under-split suspicion
      - Flag families that should likely merge or split.

  ### TODO 11. Replace adjacency-first pairing with scored evidence model

  - Files
      - src/protocol_re/corpus/request_response_pairing.py
  - Tasks
      - Update _pair_score() to include:
          - opposite direction
          - endpoint reversal
          - temporal proximity when timestamps exist
          - index proximity
          - shared transaction/correlation field
          - compatible discriminator/opcode relationship
          - request field explains response length
          - response status/error pattern
      - Keep adjacent pairing as a fallback feature, not primary evidence.
      - Emit evidence fields in a structured schema.
  - Expected impact
      - Accuracy: ↑↑
      - Runtime: ↓ after pruning
  - Risk
      - Medium.

  ### TODO 12. Support unsolicited/event messages

  - Files
      - src/protocol_re/corpus/request_response_pairing.py
      - src/protocol_re/inference/semantic_labeling.py
  - Tasks
      - Do not force every message into a request/response pair.
      - Add possible roles:
          - request
          - response
          - notification
          - event
          - heartbeat
          - unknown
      - If a family frequently has no response but consistent direction and structure, classify as notification/event candidate.
  - Expected impact
      - Accuracy: ↑ for industrial protocols with telemetry/events
      - Runtime: neutral
  - Risk
      - Low-medium.

  ### TODO 13. Replace entropy-only segmentation with candidate field search

  - Files
      - src/protocol_re/inference/boundary_detection.py
  - Current issue
      - Current segmentation overproduces fields: 285 predicted vs 35 truth fields in current evaluation.
  - Tasks
      - Keep entropy jumps as one signal.
      - Add field candidates from:
          - constant runs
          - numeric fields
          - length fields
          - discriminator fields
          - transaction/correlation fields
          - counter/sequence fields
          - flags/status fields
          - payload tails
          - checksum-like trailing fields
      - Prefer compact layouts with strong role evidence.
      - Penalize excessive one-byte segmentation unless supported as enum/flags/status.
      - Add family-level max-field sanity checks and oversegmentation warnings.
  - Expected impact
      - Accuracy: ↑↑
      - Runtime: ↓ after sampling
  - Risk
      - Medium-high.

  ### TODO 14. Add numeric field behavior tests

  - Files
      - src/protocol_re/inference/boundary_detection.py
      - New helper: src/protocol_re/inference/numeric_fields.py
  - Tasks
      - Test widths 1/2/4/8 with big/little endian.
      - Classify candidates as:
          - length
          - counter
          - sequence_number
          - address
          - quantity
          - status
          - enum
          - flags
          - unknown_numeric
      - Use monotonicity, cardinality, range, alignment, and relation evidence.
  - Expected impact
      - Accuracy: ↑
      - Runtime: neutral
  - Risk
      - Medium.

  ### TODO 15. Add checksum/trailer detection

  - Files
      - New: src/protocol_re/inference/checksum_detection.py
      - Integrate with boundary inference.
  - Tasks
      - Detect stable-size trailing fields.
      - Test simple checksum/CRC-like behavior heuristically:
          - high entropy
          - fixed final offset
          - changes when earlier bytes change
          - low direct semantic relation to payload length/opcode
      - Do not attempt full CRC polynomial brute force by default.
  - Expected impact
      - Accuracy: ↑ for protocols with checksums
      - Runtime: neutral if lightweight
  - Risk
      - Medium.

  ### TODO 16. Separate field encoding type from semantic role

  - Files
      - src/protocol_re/model/schema.py
      - schema/protocol_model.schema.json
      - src/protocol_re/inference/semantic_labeling.py
      - scripts/12_build_protocol_model.py
  - Current issue
      - Current field output conflates field_type and semantic meaning.
  - Tasks
      - Extend FieldHypothesis with:
          - encoding_type: e.g. uint8, uint16, uint32, bytes, bitfield, string, unknown
          - semantic_role: e.g. length, transaction_id, message_type, payload
          - role_confidence
      - Keep backward compatibility by preserving field_type for now.
      - Update exporters to display both type and role.
  - Expected impact
      - Accuracy: ↑ for semantic evaluation
      - Runtime: neutral
  - Risk
      - Medium due to schema compatibility.

  ### TODO 17. Implement generic semantic role labels

  - Files
      - src/protocol_re/inference/semantic_labeling.py
  - Tasks
      - Support roles:
          - constant
          - reserved
          - version
          - message_type
          - function_code
          - transaction_id
          - correlation_id
          - sequence_number
          - length
          - unit_id
          - device_id
          - address
          - quantity
          - status
          - error_code
          - flags
          - payload
          - checksum
          - timestamp
          - unknown
      - Label only when evidence supports the role.
      - Store evidence for every label.
  - Expected impact
      - Accuracy: ↑↑
      - Runtime: neutral
  - Risk
      - Low-medium.

  ### TODO 18. Add optional evidence-gated protocol hint system

  - Files
      - New package: src/protocol_re/protocol_hints/
      - New interface: src/protocol_re/protocol_hints/base.py
      - Optional hint modules:
          - modbus_like.py
          - dnp3_like.py
          - iec104_like.py
          - s7_like.py
  - Important constraint
      - Plugins must not drive the core pipeline by default.
      - Plugins may only attach an interpretation when generic evidence already supports it.
  - Tasks
      - Define plugin interface:
          - input: generic model + evidence
          - output: optional protocol-family hypothesis with confidence
      - Add confidence threshold.
      - Report known-protocol similarity separately from generic model.
  - Expected impact
      - Accuracy: ↑ for known protocols
      - Runtime: neutral
  - Risk
      - Medium. Avoid overfitting unknown protocols to known patterns.

  ### TODO 19. Add layered evaluation metrics

  - Files
      - scripts/17_evaluate_protocol_spec.py
      - src/protocol_re/evaluation/reporting.py
  - Current issue
      - Evaluation mixes generic RE quality with protocol-specific name matching.
  - Tasks
      - Add metrics for:
          - family/message-type matching
          - header/body split correctness
          - boundary overlap
          - encoding type match
          - generic semantic role match
          - protocol-specific label match
          - relation graph precision/recall
          - pairing precision proxy when ground truth is available
      - Keep old summary for compatibility.
  - Expected impact
      - Accuracy metric quality: ↑
      - Runtime: neutral
  - Risk
      - Low.

  ### TODO 20. structured LLM refinement

  - Files
      - src/protocol_re/llm/analyze.py
      - scripts/15_analyze_with_llm.py
      - New: scripts/15b_apply_llm_refinement.py
  - Tasks
      - Require LLM to emit JSON patches against the protocol model schema.
      - Compare refined vs unrefined evaluation.
  - Risk
    - High. Must validate strictly to avoid hallucinated model changes.
