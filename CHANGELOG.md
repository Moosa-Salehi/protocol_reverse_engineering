# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Zero-shot learned boundaries (`main.py --zeroshot-boundaries`, no labels): stage 04b runs the generic model
  trained on the shipped protocols at the threshold chosen leave-one-protocol-out (stored in the training set),
  with the label-free structural post-processors (`--zeroshot-posts`, default strings,ber,crc), and 07c gates
  the result with stage 07 (`--zeroshot-gate`, default on: stage-07 fields kept, predicted edges only split fields
  of >= 3 bytes and extend past the last field). Optional `--zeroshot-shared-layers` carries edges over from known
  protocols that share a lower layer (reference pool `assets/pre_trained/fewshot_reference_messages.jsonl.gz`).
  Truth files, 14 protocols, protocol left out: overall 0.357 (current defaults) -> 0.415, +0.068 vs the
  pre-anchor baseline [+0.030, +0.118], 12 up / 0 down; with shared layers 0.418 (11 up / 0 down).

- Few-shot field boundaries (`protocol_re.inference.fewshot_boundaries`, `FewShotBoundaries` thresholds;
  stages `04b_fewshot_boundaries` and `07c_apply_fewshot_edges`; `main.py --fewshot-labels` plus
  `--fewshot-training-set`, `--fewshot-exclude-protocol`, `--[no-]fewshot-split`; off unless labels are given).
  From a few labelled messages of the capture (boundaries in the truth-file convention), a learned boundary model
  trained on the shipped multi-protocol rows (`assets/pre_trained/fewshot_boundary_training.npz`, built by
  `scripts/diagnostics/32_build_fewshot_training_set.py`) is adapted to the protocol; every message gets edges
  from the model plus byte alignment with its most similar labelled message, with string / embedded-BER /
  CRC-16-block post-processing chosen by leave-one-out on the labels. Families whose messages disagree on their
  layout are split after stage 04 (signatures holding >= 10% of a family; BER families and homogeneous families
  are kept), and after stage 07 each family's fields become the majority of its messages' edges (TLV-tagged
  chains kept). `scripts/select_fewshot_messages.py` lists which messages to label. Validated through main.py on
  the 14 benchmark protocols with 50 labelled messages each and the protocol's own rows left out: truth-file
  overall 0.347 -> 0.503 (+0.155, 95% CI [+0.079, +0.235], 11 up / 2 down: Modbus 0.804 -> 0.756,
  EtherNet/IP 0.309 -> 0.288). Experiments: `dol/accuracy-push` (LOG.md).
- Stacked-header anchor in stage 05 (`framing._counted_region_start`, `_anchor_stacked_headers`;
  `FramingDetection.STACKED_HEADER_MIN_OVERSHOOT` / `COUNTED_LENGTH_*`; `05_infer_framing.py
  --[no-]stacked-header-anchor`, `main.py --[no-]stacked-header-anchor`, default on). A length field
  (1/2/4 bytes, optionally an 11/12-bit sub-field) whose value counts the bytes from offset c marks
  where the counted body begins; when a family's entropy layout puts the body start 4+ bytes past c
  (several stable datagram/item headers back to back) and the family's own messages satisfy the
  relation, a body-start-c hypothesis is put first. EtherCAT 30 -> 2 and CIP 32 -> 24 (both the
  truth-file header lengths). Truth files, current defaults, 14 protocols: overall 0.347 -> 0.357
  (EtherCAT 0.310 -> 0.369, DNP3 0.334 -> 0.398, IEC 104 0.068 -> 0.082, CIP 0.346 -> 0.333,
  9 unchanged). Experiments: `dol/accuracy-push` (LOG.md).
- Per-message TLV layout (`detect_tlv_message_layout`, `message_tlv_edges`, `message_layout_edges`
  in `protocol_re.inference.tlv`; `TlvFraming.MESSAGE_LAYOUT_*`). A family's fixed field list
  cannot follow a BER body whose element offsets shift with every variable-length value, so
  stage 07 (under `--tlv-boundaries`, default on) also records `message_layout`: the offset where
  a full-depth BER chain starts (constructed elements descended, multi-byte tags accepted).
  Per-message consumers take each message's own parse: edges at every element start and value
  start (tag + length as one header field). `field_hypotheses` are unchanged, so truth-file
  evaluations are unaffected. `31_benchmark_message_boundaries.py` applies the layouts
  (`--no-message-layouts` scores fixed edges only). On the 14-protocol benchmark, current stage-07
  defaults: macro per-message boundary F1 0.435 -> 0.485 (MMS 0.319 -> 0.652, GOOSE 0.301 -> 0.669;
  no other protocol detected). Experiments: `dol/per-message-segmentation`, `dol/tlv-integration-check`.
- Periodic-array boundaries (`protocol_re.inference.periodic_arrays`, `PeriodicArrays`
  thresholds): stage 07 `--periodic-arrays {off,strict,loose}` / `main.py
  --boundary-periodic-arrays` detects arrays of fixed-width elements inside varying regions
  (phase statistics repeating every 2/4/8 bytes, plus length-gcd or count-field evidence)
  and splits them per element. Default `loose` (`off` disables it). With `loose` over the 13 non-Modbus benchmark
  protocols: per-message boundary F1 0.323 -> 0.382, truth-file overall 0.300 -> 0.314; no
  region is detected on the Modbus and GOOSE truth corpora (scores unchanged).
- Truth files for bacnet, cip, dnp3, enip, ethercat, hart_ip, iec104, mms, opcua,
  powerlink, s7comm and zigbee, derived from the tshark dissection of the benchmark
  captures (`dol/truth-file-derivation/scripts/build_truth.py`): fixed-offset fields per
  message type, arrays and variable-position content as one bytes field.
- `scripts/diagnostics/31_benchmark_message_boundaries.py`: per-message field-boundary
  precision/recall/F1 against the tshark annotations for every protocol with a run under
  `finetuning/windows_data/runs`, printed as one table. `--families-file` selects which
  boundaries to score (e.g. `05_families_refined.json`).
- Ground-truth fields may declare `tlv_tag` (e.g. `"0x81"`). The evaluator matches such a
  field to the predicted element carrying the same tag instead of by byte offset, which is
  undefined for variable-offset elements. `truth_files/goose.json` now tags its PDU fields.
- Stage 17 `--messages-jsonl`: truth types are scoped by the discriminator values observed
  in the corpus (at least `FamilyRefinement.MIN_FAMILY_SIZE` messages each) rather than by
  the predicted families. `main.py` passes it for the main and the no-LLM evaluation, so
  both are scored against the same truth types.
- `LLMRefinement` thresholds in `config/thresholds.py`.
- `field_roles` evaluation metric: of the truth fields that declare a `semantic_role`, how
  many were located and given a role of the same class (`ROLE_CLASSES` in stage 17, e.g.
  `function_code`/`opcode`/`discriminator`). Reported next to the other metrics, in the
  `--compare-no-llm` table and in the HTML/Markdown reports; it is not part of
  `overall_score`. `truth_files/modbus.json` and `truth_files/goose.json` now declare roles
  on the fields where the role is unambiguous.
- TLV coincidence guard (`TlvFraming.MIN_VARIABLE_LENGTH_TAGS`,
  `MIN_FIXED_LAYOUT_VALUE_TAGS`, `MIN_FIXED_LAYOUT_SEQUENCE_SHARE`): a TLV verdict needs a
  value length that varies across messages, or a fixed layout with at least three
  value-carrying tags in one shared tag sequence.

- Session-bound exclusion in discriminator detection (`FamilyRefinement.SESSION_BOUND_*`):
  a candidate byte that varies across the corpus but is fixed inside each long session is
  an endpoint identifier, not a type code, and is dropped while another candidate remains.
- Stage 11 `--assignments-json`: the field at the corpus-wide discriminator that family
  refinement keyed the families on is labelled as the opcode/discriminator in every family
  (`FieldSemantics.GLOBAL_DISCRIMINATOR_CONFIDENCE`), instead of `constant`.
- Framing length regions carry `distinct_lengths` and `verified` evidence.
- Length-scaled field cap, off by default: stage 07 `--max-fields-per-byte` /
  `main.py --boundary-max-fields-per-byte` (`BoundaryDetection.MAX_FIELDS_PER_BYTE`).
  At 0.5 it raises macro per-message boundary F1 over 14 protocols from 0.365 to 0.442,
  but splits long arrays per element, which `truth_files/modbus.json` counts as one field
  (200K multi-device capture: overall 0.749 -> 0.580).
- `TlvFraming.MIN_CHAIN_ELEMENTS`: a TLV verdict needs at least two elements in the most
  common tag sequence. A one-element chain is only a length-prefixed message (the Modbus
  MBAP length field parsed that way).

### Changed
- Zero-shot learned boundaries are now the default (`main.py --zeroshot-boundaries`, opt out with
  `--no-zeroshot-boundaries`); without the shipped training set the pipeline falls back to rule-based boundaries.
- The shipped boundary training set (`assets/pre_trained/fewshot_boundary_training.npz`, reference messages) is
  rebuilt from the families of the current clustering (global HDBSCAN setting; old files kept as `*.v1.*`).
  Leave-one-protocol-out per-message F1 (14 protocols, truth files): 0.608 -> 0.614.
- Zero-shot gating may merge away a stage-07 edge the model considers very unlikely (family-mean probability <
  `FewShotBoundaries.ZEROSHOT_VETO`), except the edges of confident length / keyword / opcode fields: 0.614 -> 0.620
  (OPC UA +0.066; none worse). Stage 04b exports the family-mean probabilities for stage 07c.
- Tried and not adopted (dol/improve): per-(family, length) message layouts for zero-shot edges (0.608 -> 0.606);
  change co-variation / bit-congruence features (`FewShotBoundaries.CHANGE_FEATURES`, 0.614 -> 0.610); request ->
  response consistency as a type signal (endpoint / transaction fields are echoed too; it would pick the Modbus
  unit id).

### Fixed
- Stages 04b and 07c did not receive the instance `--log-dir`.

- Few-shot boundaries: the family split is verified by the labelled messages (a family is split only into
  layouts its labels show, `--[no-]fewshot-split-verify`, `--fewshot-split-support`), and rebuilt fields end at
  the family's median length. Truth files: 12 up / 0 down (Modbus 0.756 -> 0.816, EtherNet/IP 0.288 -> 0.343),
  overall +0.142 vs +0.155 before.
- The per-message boundary benchmark skips `tshark-cache` fallback annotations by default
  (`--include-coarse` restores them): they hold a few coarse layer spans, about one edge
  per 100 bytes, and made up a fifth of the BACnet annotations.
- A metric with nothing predicted and nothing expected is reported with
  `"applicable": false` and left out of the overall score; the remaining weights are
  renormalised. Previously it contributed a full 1.0 (relations on GOOSE).
- LLM boundary lists can no longer remove an edge of a field stage 07 holds at
  `LLMRefinement.MERGE_PROTECT_CONFIDENCE` or above.
- The local backend reports the real consensus share as its boundary confidence instead of
  a constant 0.99.

### Changed
- Stage 04 no longer looks up HDBSCAN settings tuned per training protocol by the tshark filter name (a threat
  to validity: every benchmark protocol was clustered with settings tuned on its own labels, e.g. min_cluster_size
  = corpus size for ZigBee / POWERLINK); only the checkpoint's protocol-independent global setting is used. HDBSCAN
  noise is reassigned to the nearest clustered point (`Clustering.REASSIGN_NOISE_TO_NEAREST`; noise had reached
  97% / 86% / 42% on ZigBee / POWERLINK / EtherCAT with the global setting).
- Discriminator selection: label-guided "meaningful" candidates must explain some exact length
  (`FamilyRefinement.LABEL_GUIDED_MIN_LENGTH_MI`); windows present in >= `PARTIAL_MIN_COVERAGE` of the messages are
  eligible through the structure checks in both modes (short messages keep their own group).
- TLV detection samples messages evenly over the corpus instead of its head and accepts captures cut short by the
  snap length (`TlvFraming.TRUNCATED_MIN_COMPLETE_ELEMENTS`): 35% of the GOOSE corpus is truncated, which the head
  sample hid and a random sample exposed (GOOSE on 500 messages: 34 families for one message type).

### Fixed
- Session-order role inference labelled every message of a one-sender session a request: on the single-device Modbus
  capture (no direction, one session with one sender) each function code's requests and responses merged (10 -> 6
  families, overall 0.971 -> 0.696). Roles are now inferred only in sessions where both endpoints send; other
  messages keep the length bucket. Experiments: `dol/final-v2`, `dol/thesis-final`.
- Over-fragmented families when the capture gives no message direction (symmetric UDP ports: 94% of BACnet, 86% of
  EtherNet/IP): the refinement signature fell back to a length bucket. The role now comes from session order (first
  sender = client; `FamilyRefinement.INFER_ROLE_FROM_SESSION`) when at least `SESSION_ROLE_MIN_UNKNOWN_SHARE` of the
  corpus lacks a direction (HART-IP, 32% unknown, keeps the length bucket: its sessions start mid-conversation and
  the inferred roles were inverted). Truth files, 14 protocols, macro overall: rules 0.387 -> 0.406, zero-shot
  0.458 -> 0.478, few-shot 50 0.519 -> 0.545; only BACnet and EtherNet/IP change (e.g. rules 0.220 -> 0.366 and
  0.223 -> 0.344). On the 500-message samples BACnet drops (0.304 -> 0.195; sampled sessions are cut).
  Experiments: `dol/direction-fix`.
- TLV family merge: messages that do not parse kept their old family id, which could collide with the new
  tag-sequence ids (`family_<n>`) and merge unrelated messages; they now keep it as `<id>_unparsed`, and truncated
  messages join the most common tag sequence that starts with their complete elements.
  Effect of these changes (truth files, 14 protocols, macro overall): rules 0.380 -> 0.387, zero-shot 0.437 -> 0.458,
  shared layers 0.418 -> 0.461, few-shot 10 / 20 / 50 0.442 / 0.444 / 0.511 -> 0.494 / 0.505 / 0.519 (none of the
  paired bootstrap CIs excludes 0). BACnet (0.371 -> 0.220) and EtherNet/IP (0.309 -> 0.223) drop in every
  configuration: the new discriminator picks separate the types better (family/type NMI 0.10 -> 0.51 and
  0.51 -> 0.72) but over-fragment with length buckets (direction unknown), so message-type precision falls.
  Experiments: `dol/hdbscan-global`.

- Family refinement picked a sequence-number byte on IEC 104: the two bootstrap families split the corpus almost
  purely by length (H(family | length) = 0.016 bits), so the normalised I(value; family | length) was a ratio of
  near-zero numbers (~1.0 for nearly every byte) and "earliest meaningful" chose offset 5 (receive-sequence high
  byte); the type id at offset 6 was also excluded because the 6-byte S/U control frames lack it (coverage 0.64).
  A bootstrap with H(family | length) < `FamilyRefinement.MIN_BOOTSTRAP_CONDITIONAL_ENTROPY` now selects label-free
  like a single family (max NMI(value; length), same guards), may use a window present in >=
  `LABEL_FREE_MIN_COVERAGE` of the messages, and keeps the shorter messages as their own group (value
  `ABSENT_DISCRIMINATOR_VALUE`) instead of noise. IEC 104 overall 0.082 -> 0.415 (rule-based), 0.129 -> 0.435
  (zero-shot), 0.246 -> 0.548 (few-shot 50); the other 13 protocols and the Modbus slices are identical. Threshold
  chosen after measuring the 14 bootstraps (next lowest 0.22 bits). Experiments: `dol/iec104-discriminator`.
- Family refinement never ran when bootstrap clustering returned a single family (HDBSCAN can select the root
  cluster): `detect_global_discriminator` returned early with fewer than two labels, so the first 10K / 50K messages
  of the 200K multi-device Modbus capture scored 0.089 / 0.087 overall. With one bootstrap family and a known message
  direction (>= `FamilyRefinement.SINGLE_FAMILY_MIN_KNOWN_DIRECTION`), the detector now picks the candidate whose
  value best explains the exact message length (normalised MI >= `SINGLE_FAMILY_MIN_STRUCTURE_MI`), after dropping
  length fields counting from any constant offset and candidates that are a length field for >=
  `SINGLE_FAMILY_MAX_LENGTH_RELATION` of the messages; single-family TLV/BER corpora are skipped. Modbus slices
  0.600 / 0.603; truth files, 14 protocols: unchanged in the rule-based, zero-shot and few-shot-50 configurations.
  Without the direction guard the rule-based macro rose 0.357 -> 0.368 (EtherCAT, POWERLINK) but few-shot EtherCAT
  fell 0.605 -> 0.328 and zero-shot POWERLINK 0.498 -> 0.343 (length-bucket split of the one family); simply
  removing the early return cost 0.045. Rules chosen while looking at these cases (post hoc). Experiments:
  `dol/single-family-fix`.
- Family refinement keyed a multi-device Modbus capture on the Unit-Id (offset 6) instead
  of the function code (offset 7) once the bootstrap used neural features, because the
  selection floor depended on the bootstrap labels.
- A constant byte in a fixed-length family was labelled `length` whenever its value
  happened to equal a length expression for that one message size (the Modbus function
  code 0x04 in an 11-byte family). Such matches now need confirmation on a sample pooled
  across families.
- Stage 12 arbitrates LLM and heuristic labels by confidence, but a label stage 11b had
  already written onto the field was never replaced by the winner, so a weaker LLM label
  overrode a stronger heuristic one. The winner now replaces it.
- TLV mode misfired on fixed-layout Modbus response families (`04 02 xx xx` parses as tag 4,
  length 2), replacing correct boundaries with overlapping TLV fields: field-boundary F1
  1.00 -> 0.94 on one corpus and 0.89 -> 0.52 on another. Both are restored.
- TLV tag-sequence statistics counted individual tags instead of sequences, so
  `sequence_count` equalled the tag count and the sequence-cardinality gate never applied.
- Stage 11b did not write the merged semantics file when no LLM label was applied, and
  stage 12 then failed.
- Variable-offset truth fields (`start: null`) were compared as if they sat at offset 0, so
  correctly parsed TLV elements could never match.
- Semantic labels were validated without field statistics, so the cardinality checks never
  ran. They now use the statistics built for the prompt.
- An LLM label of type `bytes`, or an integer type wider than the field, no longer replaces
  the inferred field type.

## [1.1.0] - 2026-07-22

### Added
- Isolated pipeline instance paths with `--data-dir`, `--output-dir`, and `--log-dir`.
  The selected log directory is passed to every stage, and generated artifacts, caches,
  user-provided LLM response placeholders, reports, and logs stay within their instance
  directories so concurrent runs do not interfere with each other.
- Transaction/correlation-id request-response pairing in
  `corpus/request_response_pairing.py`: `detect_correlation_field()` finds a header field
  that varies across messages but matches a nearby message within a small window (rejecting
  constant fields such as a protocol-id), and pairing is performed on that id. This replaces
  fragile adjacency pairing, which broke whenever a capture started mid-stream with an orphan
  response (shifting every pair by one). On the Modbus corpus, pairs went from 0% to 100%
  transaction-id and function-code agreement; relations recall rose ~0.50→0.67. New
  `RequestResponsePairing` thresholds in `config/thresholds.py`.
- Opcode/command isolation in boundary detection: when a confident framing/body boundary is
  known and the leading body byte is constant or near-constant within a family, it is split
  into its own 1-byte field and protected from merging. Recovers the discriminator byte (e.g.
  the Modbus function code) instead of fusing it into a wider uint16/uint32. New thresholds
  `BoundaryDetection.ISOLATE_BODY_OPCODE` / `OPCODE_MAX_CARDINALITY_RATIO` and CLI flag
  `--no-opcode-isolation` on stage 07. On Modbus this lifts field-semantics F1 ~0.11→0.50 and
  field-boundary F1 ~0.66→0.70 (overall ~0.50→0.58).
- Rewrote `truth_files/modbus.json` into a capture-derived, tshark-validated evaluation oracle:
  concrete per-FC request/response types (FC01/02/03/04/05/06 only — matching the actual
  capture), a single shared MBAP header type, documented offset convention, and per-FC
  responses. Removed phantom FC15/FC16/exception types and added the previously missing FC02
  (Read Discrete Inputs).

### Changed
- `--llm-render-only` now renders only the stage 15 protocol-synthesis prompt. It skips LLM
  boundary refinement, semantic labeling, and relation validation, prevents stale stage
  summaries from being auto-loaded, and omits their sections from the HTML report.
- HTML family rulers now use the final `field_hypotheses` boundaries and semantic attributes
  instead of stale pre-refinement summaries.

### Fixed
- Family-card tooltips are rendered in a body-level overlay so they are not clipped by card
  or report wrappers.
- Serialized chat-completion response content is displayed in the HTML LLM Analysis section.
- Boundary and semantic refinement sections are hidden when their stage failed with an
  `llm_api` error.
- Boundary and semantic refinement applied/rejected counts and row statuses now reflect
  validation and final-model data instead of stale stage counters.

## [1.0.1] - 2026-06-07

### Added
- Centralized algorithmic thresholds in `src/protocol_re/config/thresholds.py` — all magic numbers
  (boundary anti-fragmentation, framing scoring weights, echo/length detection limits, relation
  confidence thresholds, field semantic scores, clustering batch sizes, etc.) moved from individual
  modules to a single documented config module organised by subsystem.  Module-level constants are
  re-exported for backward compatibility.
- Documented multi-layer protocol detection implementation
- Documented hybrid fusion design (concat, adaptive, learned, fixed)
- Updated README accuracy metrics to reflect actual performance

### Fixed
- Field semantics labeling
- Coordinate/layering header split logic

## [1.0.0] - 2026-06-06

### Added
- Reorganize project structure
- Comprehensive documentation with MkDocs
- Getting started guide
- Architecture documentation
- Contributing guidelines
- `--use-user-provided-response` flag for LLM stages
- `--reuse-llm-responses` flag to skip successful API calls on re-runs
- LLM response caching in `data/llm_stage_results/`
- LLM request retries with exponential backoff
- Sequential LLM requests to avoid rate limits
- Framing summary block and LLM refinement block in HTML reports
- Stage timing logs printed in runner as they complete

### Changed
- LLM options moved to config file only (`config/llm_config.json`)
- Increased LLM prompt token limit to 10k
- Disabled JSON logs by default; logs now override
- Removed unnecessary data from HTML reports

### Fixed
- Field semantics labeling
- Coordinate/layering header split logic
- Crash in build protocol model due to key mismatch
- Pipeline continues when LLM API fails
- Prompts lacking proper evidence
- Ignored errors in LLM stages
- Empty prompt files bug
- Over-printing in main runner
- Multiple bug fixes in LLM integration stages

## [0.9.0] - 2026-05-31

### Added
- Enhanced boundary detection with anti-fragmentation penalties
- Multi-layer protocol detection for transport/application separation
- Hybrid feature fusion with adaptive weighting
- Multi-stage LLM integration with evidence-gated validation
- Improved logging and observability
- Code structure refactoring
- Diagnostic tools for neural features, boundaries, and fusion

### Changed
- Refactored stage 15 LLM analysis with prompt splitting
- Updated README with comprehensive feature documentation

### Fixed
- Over-segmentation in boundary detection
- Neural feature collapse detection
- Large payload handling optimization

## [0.8.0] - 2026-05-15

### Added
- Semantic field labeling with protocol-agnostic inference
- Relation false positive reduction
- Ground truth evaluation framework
- LLM-assisted refinement with RFC 6902 patches

### Changed
- Improved clustering accuracy to 90%+ for raw_bytes mode
- Enhanced request/response pairing algorithm

### Fixed
- Clustering performance issues with large corpora
- Memory leaks in feature extraction

## [0.7.0] - 2026-04-30

### Added
- Neural feature mode with VAE latent vectors
- Structural feature mode with symbolic patterns
- Hybrid feature fusion methods
- Latent vector caching for performance

### Changed
- Refactored clustering module for multiple feature modes
- Improved feature extraction performance

## [0.6.0] - 2026-04-15

### Added
- Discriminator/opcode discovery with learned salience
- Request/response relation inference
- Echo field detection
- Length relation detection

### Changed
- Improved pairing algorithm accuracy
- Enhanced relation confidence scoring

## [0.5.0] - 2026-04-01

### Added
- Field boundary detection with entropy and mutual information
- Framing inference for header detection
- Feature extraction per family
- Protocol model assembly

### Changed
- Improved boundary detection algorithm
- Enhanced framing hypothesis generation

## [0.4.0] - 2026-03-15

### Added
- Message family discovery with HDBSCAN/DBSCAN
- Raw bytes feature extraction
- Family assignment propagation
- Clustering quality metrics

### Changed
- Optimized clustering for large message corpora
- Improved family assignment coverage

## [0.3.0] - 2026-03-01

### Added
- TShark-based message extraction
- Scapy-based TCP port extraction
- Message corpus management
- PCAP collection and deduplication

### Changed
- Improved extraction performance
- Enhanced error handling

## [0.2.0] - 2026-02-15

### Added
- HTML report generation with interactive elements
- Markdown report generation
- LLM evidence export
- Evaluation metrics computation

### Changed
- Improved report formatting and structure
- Enhanced visualization in HTML reports

## [0.1.0] - 2026-02-01

### Added
- Initial project structure
- Basic pipeline runner
- Core module organization
- README and basic documentation
- Protocol model schema definition
- JSON schema validation
- Ground truth comparison framework
- Evaluation result reporting
- Standardized protocol model format
- Improved schema documentation

---

## Legend

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security fixes
