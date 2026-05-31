# Comprehensive TODO List for Protocol Reverse Engineering Pipeline

**Analysis Date:** 2026-05-30  
**Current Status:** Overall accuracy score: 0.4905 (FAIL) on test protocol evaluation  
**Priority Order:** 1. Accuracy → 2. Runtime → 3. Code Quality

---

## Executive Summary

Based on evaluation results (`data/15_evaluation_result.json`) using **raw_bytes clustering mode**, the pipeline shows:

### Strengths:
- **Message Type Matching:** 90.91% recall, 90.91% precision (10/11 types detected) ✅
- **Field Boundary Recall:** 88.57% (good detection) ✅
- **Relations Recall:** 100% (all relations found) ✅

### Critical Weaknesses:
- **Field Boundary Precision:** 38.27% (too many false positives - over-segmentation)
- **Field Semantics:** 0% accuracy (no correct semantic labels)
- **Relations Precision:** 35% (too many false positive relations)
- **Overall Score:** 0.4905 (below passing threshold)

### Key Insights:
1. **Neural mode fails catastrophically** (2 families, 0.16 score) vs **raw_bytes succeeds** (11 families, 0.49 score)
2. **Clustering works well** in raw_bytes mode (90.91% family detection)
3. **Main issues:** Over-segmentation, zero semantic labeling, noisy relations
4. **LLM integration is monolithic** - needs to be broken into smaller, stage-specific interactions

The pipeline has strong infrastructure but needs: (1) fix neural features, (2) reduce over-segmentation, (3) implement semantic labeling, (4) add multi-stage LLM integration.

---

## PRIORITY 1: ACCURACY IMPROVEMENTS (Critical)

### A1. Fix Neural Feature Mode (CRITICAL - Currently Broken)
**Priority:** P0 - Neural mode produces 2 families vs raw_bytes 11 families  
**Current Issue:** Neural features (32D latent) collapse all messages into one cluster  
**Impact:** Neural mode is unusable (0.16 score vs 0.49 for raw_bytes)

**Root Cause Analysis:**
- Neural VAE compresses 10-12 byte messages too aggressively
- 32D latent space loses discriminative information
- Transaction IDs and variable headers add noise
- Structural features in hybrid mode don't compensate enough

**Tasks:**
1. **Diagnose neural feature collapse:**
   - Visualize latent space distribution (t-SNE, UMAP)
   - Measure latent space variance and separation
   - Compare latent distances vs ground truth family distances
   - Identify which message types are being merged

2. **Improve neural feature extraction:**
   - Increase latent dimension (32D → 64D or 128D)
   - Train VAE with discriminative loss (not just reconstruction)
   - Add contrastive learning to separate different message types
   - Use attention mechanism to focus on discriminative bytes
   - Consider using pre-trained protocol embeddings

3. **Add protocol-agnostic preprocessing:**
   - Detect and mask variable fields (transaction IDs, counters, timestamps)
   - Normalize payload lengths (pad/truncate intelligently)
   - Extract stable prefix/suffix patterns before encoding
   - Use byte position embeddings (like positional encoding in transformers)

4. **Improve hybrid feature fusion:**
   - Balance neural vs structural feature weights
   - Use learned fusion (small MLP) instead of concatenation
   - Add feature importance analysis
   - Ensure structural features can override neural when confident

5. **Add fallback mechanism:**
   - Detect when neural features are failing (low variance, high compression)
   - Automatically fall back to raw_bytes or structural mode
   - Log warnings when neural mode is degraded

**Files:**
- `src/protocol_re/clustering/hybrid_features.py`
- `src/protocol_re/neural/model_loader.py`
- `pre_trained/industrial_VAE.pth` (may need retraining)
- `scripts/04_discover_families.py`

**Expected Impact:** Neural mode score 0.16 → 0.45+, comparable to raw_bytes

**Note:** This is protocol-agnostic - no protocol-specific logic, only generic pattern detection

---

### A2. Fix Over-Segmentation (CRITICAL - Precision Issue)
**Priority:** P0 - 88.57% recall but only 38.27% precision  
**Current Issue:** Too many false positive boundaries - splitting fields incorrectly  
**Impact:** 50 false positives vs 31 true positives (62% of boundaries are wrong)

**Root Cause Analysis:**
- Entropy-based scoring creates boundaries at every byte transition
- No penalty for excessive segmentation
- Single-byte fields are over-generated
- No validation against field width conventions

**Tasks:**
1. **Add anti-fragmentation penalties:**
   - Penalize 1-byte fields heavily unless strong evidence (flags, enum, opcode)
   - Require minimum segment width (default: 2 bytes)
   - Add smoothing to boundary scores (prefer fewer, stronger boundaries)
   - Implement maximum field count per family (e.g., 15 fields max)

2. **Improve boundary scoring algorithm:**
   - Reduce weight on entropy jumps (currently over-weighted)
   - Increase weight on mutual information drops (field independence)
   - Add field-width consistency across family (prefer aligned boundaries)
   - Reward boundaries at common widths (1, 2, 4, 8 bytes)
   - Add coverage consistency (boundaries should appear in most messages)

3. **Add boundary validation and merging:**
   - Merge adjacent constant fields into single field
   - Merge adjacent 1-byte variable fields if low cardinality
   - Validate field widths against typical protocol patterns
   - Check if fields align with length field values
   - Flag and merge suspicious single-byte sequences

4. **Add LLM-assisted boundary refinement:**
   - Export boundary candidates with scores to LLM
   - Ask LLM to identify likely over-segmentation
   - Let LLM suggest field merges based on patterns
   - Validate LLM suggestions against statistical evidence

5. **Implement boundary quality metrics:**
   - Track precision/recall during inference (if ground truth available)
   - Add over-segmentation ratio metric
   - Log boundary confidence distributions
   - Report average fields per family

**Files:**
- `src/protocol_re/inference/boundary_detection.py`
- `scripts/07_infer_boundaries.py`

**Expected Impact:** Boundary precision 38.27% → 70%+, F1 53.45% → 75%+

**Note:** All improvements are protocol-agnostic, based on statistical patterns only

---

### A3. Implement Semantic Field Labeling (CRITICAL - NEW)
**Priority:** P0 - Currently 0% accuracy  
**Current Issue:** No correct semantic labels detected - all fields labeled as generic types

**Root Cause Analysis:**
- Current semantic labeling is too weak (only uses basic field types)
- No inference of semantic roles (opcode, address, length, transaction_id, etc.)
- No use of cross-field relationships
- No pattern-based semantic inference

**Tasks:**
1. **Build protocol-agnostic semantic inference engine:**
   - Detect **discriminator/opcode fields:** byte 0-1, low cardinality (2-256), stable position, correlates with family
   - Detect **length fields:** 1/2/4 bytes, value matches message length or remaining length
   - Detect **counter/sequence fields:** high cardinality, monotonic or cycling values
   - Detect **transaction_id fields:** 2/4 bytes, echoed in paired messages, high cardinality
   - Detect **address fields:** 2/4 bytes, moderate cardinality, stable across similar messages
   - Detect **quantity/count fields:** 1/2 bytes, correlates with payload size
   - Detect **status/flags fields:** 1 byte, low cardinality, appears in responses
   - Detect **payload/data fields:** variable length, high entropy, after header
   - Detect **checksum/CRC fields:** last 1/2/4 bytes, appears to be calculated

2. **Add field type taxonomy (protocol-agnostic):**
   - **Encoding types:** uint8, uint16_be, uint16_le, uint32_be, uint32_le, bytes, bitfield
   - **Semantic roles:** discriminator, length, transaction_id, sequence_number, address, quantity, status, flags, payload, checksum, constant, reserved
   - Separate encoding from semantics in schema
   - Allow multiple semantic hypotheses per field with confidence scores

3. **Use relation evidence for semantic inference:**
   - Fields echoed in request/response pairs → transaction_id or correlation_id
   - Fields matching response length → length or byte_count
   - First field with low cardinality → discriminator or message_type
   - Fields that increment → counter or sequence_number
   - Fields that vary randomly → nonce or random_id

4. **Add cross-family semantic consistency:**
   - If multiple families have same field at same offset → shared header field
   - Propagate high-confidence semantic labels across similar families
   - Detect common protocol patterns (header + payload structure)

5. **Implement confidence-based labeling:**
   - Assign confidence scores to each semantic hypothesis
   - Require minimum confidence threshold (e.g., 0.6) for labeling
   - Report multiple hypotheses when uncertain
   - Flag fields with conflicting evidence

**Files:**
- `src/protocol_re/inference/semantic_labeling.py` (major rewrite)
- New: `src/protocol_re/inference/field_semantics.py`
- New: `src/protocol_re/inference/semantic_patterns.py`
- `scripts/11_infer_semantics.py`
- `src/protocol_re/model/schema.py` (add semantic role taxonomy)

**Expected Impact:** Semantic accuracy 0% → 40-60%

**Note:** All semantic inference is protocol-agnostic, based on statistical patterns and common protocol conventions

---

### A4. Reduce Relation False Positives
**Priority:** P1 - 100% recall but only 35% precision  
**Current Issue:** Too many false positive relations - 13 FP vs 7 TP

**Root Cause Analysis:**
- Echo field detection is too permissive (searches entire payload)
- Length relation detection generates spurious matches
- No validation of relation plausibility
- No filtering of weak relations

**Tasks:**
1. **Tighten echo field detection:**
   - Focus search on header regions only (first 32-64 bytes)
   - Require higher support threshold (>95% instead of 90%)
   - Prioritize 2-byte and 4-byte fields (typical transaction IDs)
   - Ignore single-byte echoes unless very high confidence
   - Validate that echoed fields are not counters or timestamps

2. **Improve length relation validation:**
   - Require high support (>95%) for length field claims
   - Validate that length field appears in consistent position
   - Check that length values are reasonable (not random)
   - Ensure length field is not a counter or address

3. **Add relation plausibility checks:**
   - Validate temporal ordering (response after request)
   - Check direction consistency (client→server, server→client)
   - Ensure paired families have compatible structures
   - Validate that relation makes semantic sense

4. **Implement relation confidence scoring:**
   - Score relations based on multiple evidence types
   - Require minimum confidence threshold (e.g., 0.7)
   - Report confidence for each relation
   - Filter low-confidence relations

5. **Add relation deduplication:**
   - Remove redundant relations (same evidence, different representation)
   - Merge similar relations
   - Keep only strongest relation per family pair

**Files:**
- `src/protocol_re/inference/request_response_relations.py`
- `scripts/10_infer_relations.py`

**Expected Impact:** Relation precision 35% → 70%+, F1 51.85% → 80%+

**Note:** All improvements are protocol-agnostic, based on statistical validation

---

### A5. Multi-Stage LLM Integration (CRITICAL - Architecture Change)
**Priority:** P0 - Current monolithic approach is ineffective  
**Current Issue:** Single massive evidence bundle sent to LLM - too much information, unclear goals

**Root Cause Analysis:**
- Current approach: collect ALL evidence → send to LLM in one shot → hope for good patches
- LLM gets overwhelmed with 10K+ lines of evidence
- No clear task decomposition
- No iterative refinement
- No validation between stages

**New Architecture: Multi-Stage LLM Pipeline**

**Stage 1: Clustering Validation (After Stage 04)**
- **Goal:** Validate family assignments, suggest splits/merges
- **Input:** Family statistics, sample messages per family, clustering diagnostics
- **Prompt:** "Review these message families. Identify families that should be split or merged based on structural patterns."
- **Output:** Family split/merge suggestions with evidence
- **Validation:** Check if suggestions improve silhouette score, validate against message samples
- **Apply:** Re-cluster with suggestions if validated

**Stage 2: Boundary Refinement (After Stage 07)**
- **Goal:** Fix over-segmentation, merge fields, validate boundaries
- **Input:** Per-family field boundaries, boundary scores, sample messages
- **Prompt:** "Review these field boundaries. Identify over-segmentation (too many 1-byte fields) and suggest field merges."
- **Output:** Boundary adjustment suggestions (merge fields, adjust offsets)
- **Validation:** Check if merges reduce false positives, validate against boundary scores
- **Apply:** Merge fields if validated

**Stage 3: Semantic Labeling (After Stage 11)**
- **Goal:** Assign semantic roles to fields
- **Input:** Field hypotheses, relation evidence, family roles
- **Prompt:** "Assign semantic labels to these fields based on their characteristics: position, cardinality, echoing, length correlation."
- **Output:** Semantic label suggestions with confidence
- **Validation:** Check if labels are supported by statistical evidence
- **Apply:** Add semantic labels if validated

**Stage 4: Relation Validation (After Stage 10)**
- **Goal:** Validate request/response relations, filter false positives
- **Input:** Relation candidates, echo fields, pairing evidence
- **Prompt:** "Review these request/response relations. Identify false positives and validate true relations."
- **Output:** Relation validation (keep/discard) with reasoning
- **Validation:** Check if reasoning aligns with evidence
- **Apply:** Filter relations based on validation

**Stage 5: Protocol Structure Synthesis (Final)**
- **Goal:** Generate human-readable protocol description
- **Input:** Refined protocol model (after all stages)
- **Prompt:** "Synthesize a protocol specification describing the overall structure, message types, and field semantics."
- **Output:** Markdown protocol description
- **Validation:** Check for consistency with model
- **Apply:** Include in final report

**Implementation Tasks:**
1. **Create stage-specific prompt templates:**
   - One template per stage with clear goals
   - Focused evidence bundles (not everything)
   - Structured output schemas per stage

2. **Implement stage-specific LLM callers:**
   - `llm_validate_clustering(families, diagnostics) → split/merge suggestions`
   - `llm_refine_boundaries(family_id, fields, samples) → boundary adjustments`
   - `llm_label_semantics(family_id, fields, relations) → semantic labels`
   - `llm_validate_relations(relations, evidence) → relation validation`
   - `llm_synthesize_protocol(protocol_model) → markdown description`

3. **Add evidence-gated validation:**
   - Every LLM suggestion must cite specific evidence
   - Validate suggestions against statistical evidence
   - Reject suggestions without support
   - Log rejection reasons for auditability

4. **Implement iterative refinement:**
   - Allow multiple LLM calls per stage if needed
   - Support human-in-the-loop review
   - Enable checkpoint/resume between stages

5. **Add cost and token management:**
   - Track tokens per stage
   - Implement token budgets per stage
   - Support --llm-render-only for all stages
   - Cache LLM responses per stage

**Files:**
- New: `src/protocol_re/llm/multi_stage.py`
- New: `src/protocol_re/llm/stage_clustering.py`
- New: `src/protocol_re/llm/stage_boundaries.py`
- New: `src/protocol_re/llm/stage_semantics.py`
- New: `src/protocol_re/llm/stage_relations.py`
- New: `src/protocol_re/llm/stage_synthesis.py`
- New: `prompts/clustering_validation.md`
- New: `prompts/boundary_refinement.md`
- New: `prompts/semantic_labeling.md`
- New: `prompts/relation_validation.md`
- New: `prompts/protocol_synthesis.md`
- Refactor: `scripts/15_analyze_with_llm.py` → multi-stage orchestrator
- Refactor: `src/protocol_re/llm/analyze.py` → stage-specific modules

**Expected Impact:** 
- LLM effectiveness: significantly improved (focused tasks)
- Semantic accuracy: 0% → 40-60% (with LLM assistance)
- Boundary precision: 38% → 60%+ (with LLM merge suggestions)
- Overall score: 0.49 → 0.65-0.75

**Note:** All LLM interactions are protocol-agnostic, based on generic patterns

---

### A6. Add Multi-Layer Protocol Detection (Protocol-Agnostic)
**Priority:** P2 - Important for real-world protocols  
**Current Issue:** Many protocols have transport headers + application payload, pipeline treats as flat

**Root Cause Analysis:**
- Protocols often have stable outer headers (framing, transaction IDs, length fields)
- Inner protocol payload contains the actual message logic
- Clustering on full frame includes transport noise
- Boundaries mix transport and application fields

**Tasks:**
1. **Detect layered structure (protocol-agnostic):**
   - Identify stable prefix patterns (potential outer header)
   - Detect length fields that point to inner protocol start
   - Recognize protocol identifiers or version fields
   - Find boundary between stable header and variable payload

2. **Implement automatic layer separation:**
   - Extract outer header fields separately (mark as "transport layer")
   - Cluster inner protocol messages independently
   - Maintain layer relationships in protocol model
   - Report layers separately in output

3. **Add layer-aware feature extraction:**
   - Extract features from inner protocol only for clustering
   - Keep outer header for pairing
   - Separate boundary detection per layer

4. **Add layer-aware evaluation:**
   - Match fields at correct layer
   - Support hierarchical ground truth
   - Report accuracy per layer

**Files:**
- New: `src/protocol_re/inference/layer_detection.py`
- `src/protocol_re/inference/framing.py`
- `scripts/05_infer_framing.py`
- `scripts/04_discover_families.py` (add layer-aware clustering)

**Expected Impact:** Accuracy +10-15% for layered protocols, better clustering

**Note:** All layer detection is protocol-agnostic, based on statistical patterns

---

## PRIORITY 2: RUNTIME OPTIMIZATIONS (Important)

### B1. Optimize Large Payload Handling (COMPLETED)
**Status:** ✅ Completed in this session  
**Changes:** Added limits to stages 06, 07, 10 for payloads >512 bytes

---

### B2. Add Incremental/Streaming Processing
**Priority:** P2 - Scalability for large captures

**Tasks:**
1. **Implement streaming feature extraction:**
   - Process messages in batches
   - Update family statistics incrementally
   - Avoid loading entire corpus into memory

2. **Add checkpoint/resume support:**
   - Save intermediate results after each stage
   - Allow resuming from last checkpoint
   - Enable partial re-runs (e.g., only re-run stages 10+)

3. **Parallelize independent operations:**
   - Process families in parallel (stages 06, 07)
   - Parallelize feature extraction per family
   - Use multiprocessing for CPU-bound tasks

**Files:**
- `src/protocol_re/corpus/message_corpus.py`
- `src/protocol_re/features/extraction.py`
- `main.py`

**Expected Impact:** 2-5x speedup for large captures

---

### B3. Optimize Neural Model Inference
**Priority:** P3 - Minor impact

**Tasks:**
1. **Batch neural encoding:**
   - Process messages in larger batches (current: 256)
   - Use GPU if available
   - Cache latent vectors more aggressively

2. **Optimize model loading:**
   - Load neural models once, reuse across stages
   - Use quantized models for faster inference
   - Add model warm-up to avoid cold-start latency

**Files:**
- `src/protocol_re/neural/model_loader.py`
- `src/protocol_re/clustering/hybrid_features.py`

**Expected Impact:** 10-20% speedup when using neural features

---

### B4. Add Configurable Performance Limits
**Priority:** P2 - User control

**Tasks:**
1. **Make limits configurable:**
   - Add CLI args for max payload analysis length
   - Add family size limits (skip huge families)
   - Add timeout limits per stage

2. **Add performance profiling:**
   - Log time spent per stage
   - Identify bottleneck families
   - Report performance metrics in evaluation

**Files:**
- `main.py`
- All stage scripts

**Expected Impact:** Better user control, easier debugging

---

## PRIORITY 3: CODE QUALITY & MAINTAINABILITY

### C1. Add Comprehensive Unit Tests
**Priority:** P1 - Critical for refactoring  
**Current Status:** No visible test suite

**Tasks:**
1. **Add test infrastructure:**
   - Create `tests/` directory
   - Add pytest configuration
   - Add test fixtures for sample protocols

2. **Add unit tests for core modules:**
   - Clustering: test feature extraction, label propagation
   - Boundary detection: test scoring, segmentation
   - Semantic labeling: test field type inference
   - Relations: test pairing, echo detection

3. **Add integration tests:**
   - End-to-end pipeline tests with known protocols
   - Regression tests using evaluation results
   - Performance benchmarks

**Files:**
- New: `tests/` directory structure
- New: `tests/test_clustering.py`
- New: `tests/test_boundaries.py`
- New: `tests/test_semantics.py`
- New: `tests/test_relations.py`
- New: `tests/fixtures/` (sample PCAPs, ground truth)

**Expected Impact:** Safer refactoring, faster debugging

---

### C2. Improve Error Handling and Validation
**Priority:** P2 - Robustness

**Tasks:**
1. **Add input validation:**
   - Validate PCAP files before processing
   - Check for empty/corrupt message corpus
   - Validate ground truth schema

2. **Add graceful degradation:**
   - Continue pipeline if optional stages fail
   - Provide meaningful error messages
   - Log warnings for suspicious data

3. **Add data quality checks:**
   - Detect duplicate messages
   - Flag sessions with unusual patterns
   - Warn about insufficient data for clustering

**Files:**
- All stage scripts
- `src/protocol_re/corpus/message_corpus.py`

**Expected Impact:** Better user experience, easier debugging

---

### C3. Improve Documentation
**Priority:** P2 - Usability

**Tasks:**
1. **Add API documentation:**
   - Docstrings for all public functions
   - Type hints for all functions
   - Generate Sphinx/MkDocs documentation

2. **Add architecture documentation:**
   - Document pipeline stages and data flow
   - Explain clustering algorithms and parameters
   - Document neural model architecture

3. **Add usage examples:**
   - Tutorial for common protocols (Modbus, DNP3, S7)
   - Guide for adding new neural models
   - Guide for creating ground truth files

**Files:**
- New: `docs/` directory
- New: `docs/architecture.md`
- New: `docs/tutorial.md`
- New: `docs/api/` (auto-generated)

**Expected Impact:** Easier onboarding, better adoption

---

### C4. Refactor Code Structure
**Priority:** P3 - Long-term maintainability

**Tasks:**
1. **Manage duplicate/unused codes**
   - in some stages, multiple codes/functions exist with same purpose, remove the old ones.
   - remove any unused files/codes throughout the project.

2. **Separate concerns:**
   - Split large modules
   - Extract reusable utilities
   - Create clear interfaces between stages

3. **Improve naming:**
   - Rename "keywords" to "discriminators" consistently
   - Use semantic names for field types
   - Standardize function naming conventions

4. **Add configuration management:**
   - Centralize magic numbers and thresholds
   - Create config file for pipeline parameters

**Files:**
- All source files (gradual refactoring)
- New: `src/protocol_re/config.py`

**Expected Impact:** Easier maintenance, clearer code

---

### C5. Add Logging and Observability
**Priority:** P2 - Debugging and monitoring

**Tasks:**
1. **Improve logging:**
   - Use structured logging (JSON logs)
   - Add log levels (DEBUG, INFO, WARNING, ERROR)
   - Log key decisions (why family was assigned, why boundary was placed)

2. **Add progress tracking:**
   - Show progress bars for long operations
   - Estimate remaining time
   - Report intermediate results

3. **Add debugging tools:**
   - Visualize clustering results
   - Plot boundary scores
   - Show field hypothesis evolution

**Files:**
- All stage scripts
- New: `src/protocol_re/utils/logging.py`
- New: `src/protocol_re/visualization/` (optional)

**Expected Impact:** Easier debugging, better user feedback

---

## PRIORITY 4: ADVANCED FEATURES (Future)

### D1. Active Learning for Ground Truth Generation
**Priority:** P3 - Research feature

**Tasks:**
1. **Implement uncertainty sampling:**
   - Identify messages with low clustering confidence
   - Identify fields with conflicting semantic labels
   - Prioritize samples for human labeling

2. **Add interactive labeling tool:**
   - Web UI for reviewing and correcting inferences
   - Export corrected labels as ground truth
   - Retrain models with human feedback

**Expected Impact:** Faster ground truth creation, improved accuracy

---

### D2. Transfer Learning from Known Protocols
**Priority:** P3 - Research feature

**Tasks:**
1. **Build protocol knowledge base:**
   - Collect ground truth for common protocols (Modbus, DNP3, S7, IEC 104)
   - Train protocol-specific models
   - Create protocol fingerprints

2. **Add protocol recognition:**
   - Match unknown traffic against known protocols
   - Transfer learned features to similar protocols
   - Bootstrap clustering with protocol hints

**Expected Impact:** Faster convergence, higher accuracy for known protocols

---

### D3. Anomaly Detection for Protocol Deviations
**Priority:** P3 - Security feature

**Tasks:**
1. **Detect protocol violations:**
   - Flag messages that don't match inferred structure
   - Detect unusual field values
   - Identify malformed messages

2. **Add security analysis:**
   - Detect potential attacks (fuzzing, injection)
   - Flag suspicious patterns
   - Generate security reports

**Expected Impact:** Security value-add, protocol compliance checking

---

### D4. Multi-Protocol Session Analysis
**Priority:** P3 - Advanced feature

**Tasks:**
1. **Detect protocol switching:**
   - Identify sessions using multiple protocols
   - Detect protocol negotiation
   - Handle protocol tunneling

2. **Add cross-protocol analysis:**
   - Correlate events across protocols
   - Build multi-protocol state machines
   - Generate cross-protocol reports

**Expected Impact:** Better analysis of complex systems

---

## IMPLEMENTATION ROADMAP

### Phase 1: Critical Accuracy Fixes (Weeks 1-4)
**Goal:** Improve overall score from 0.49 to 0.70+

**Week 1: Fix Neural Features (A1)**
- Diagnose neural feature collapse (visualize latent space)
- Increase latent dimension or add discriminative loss
- Add protocol-agnostic preprocessing (mask variable fields)
- Implement fallback mechanism
- **Target:** Neural mode score 0.16 → 0.45+

**Week 2: Reduce Over-Segmentation (A2)**
- Add anti-fragmentation penalties
- Improve boundary scoring (reduce entropy weight)
- Implement boundary merging logic
- Add maximum field count limits
- **Target:** Boundary precision 38% → 65%+

**Week 3: Implement Semantic Labeling (A3)**
- Build protocol-agnostic semantic inference engine
- Add field type taxonomy (encoding + semantic roles)
- Use relation evidence for semantic inference
- Implement confidence-based labeling
- **Target:** Semantic accuracy 0% → 40%+

**Week 4: Reduce Relation False Positives (A4)**
- Tighten echo field detection (header regions only)
- Improve length relation validation
- Add relation plausibility checks
- Implement confidence scoring and filtering
- **Target:** Relation precision 35% → 70%+

**Milestone:** Overall score 0.70+, all metrics >60%

---

### Phase 2: Multi-Stage LLM Integration (Weeks 5-6)
**Goal:** Replace monolithic LLM with focused stage-specific interactions

**Week 5: Design and Implement Multi-Stage Architecture (A5)**
- Create stage-specific prompt templates
- Implement stage-specific LLM callers
- Add evidence-gated validation
- Build orchestration framework

**Week 6: Deploy and Test Multi-Stage LLM**
- Test each stage independently
- Validate evidence gating
- Measure token usage per stage
- Compare vs monolithic approach
- **Target:** Semantic accuracy 40% → 55%+, boundary precision 65% → 75%+

**Milestone:** Overall score 0.75+, LLM integration effective

---

### Phase 3: Advanced Features & Layer Detection (Weeks 7-8)

**Week 7: Multi-Layer Protocol Detection (A6)**
- Implement protocol-agnostic layer detection
- Add automatic layer separation
- Update clustering to use inner protocol only
- **Target:** Accuracy +10% for layered protocols

**Week 8: Performance Tuning and Optimization**
- Profile and optimize bottlenecks
- Add incremental processing (B2)
- Optimize neural inference (B3)
- Add configurable limits (B4)
- **Target:** 2x speedup for large captures

**Milestone:** Overall score 0.80+, 2x faster runtime

---

### Phase 4: Code Quality & Testing (Weeks 9-12)

**Week 9-10: Add Comprehensive Tests (C1)**
- Create test infrastructure
- Add unit tests for core modules
- Add integration tests
- Add regression tests

**Week 11: Improve Documentation (C3)**
- Add API documentation
- Add architecture documentation
- Add usage examples and tutorials

**Week 12: Code Refactoring (C4)**
- Separate concerns
- Improve naming consistency
- Add configuration management
- Clean up technical debt

**Milestone:** 80%+ test coverage, complete documentation

---

### Phase 5: Advanced Research Features (Weeks 13+)

1. Active learning for ground truth generation (D1)
2. Transfer learning from known protocols (D2)
3. Anomaly detection for protocol deviations (D3)
4. Multi-protocol session analysis (D4)

**Milestone:** State-of-the-art protocol RE system

---

## METRICS & SUCCESS CRITERIA

### Current Baseline (raw_bytes mode)
- Overall score: **0.4905**
- Message type recall: **90.91%** ✅
- Message type precision: **90.91%** ✅
- Field boundary recall: **88.57%** ✅
- Field boundary precision: **38.27%** ❌
- Field semantics accuracy: **0%** ❌
- Relations recall: **100%** ✅
- Relations precision: **35%** ❌

### Accuracy Targets (by Phase 1 end)
- Overall score: 0.49 → **0.70+**
- Message type: maintain 90%+ (already good)
- Field boundary recall: maintain 88%+ (already good)
- Field boundary precision: 38% → **65%+**
- Field semantics accuracy: 0% → **40%+**
- Relations recall: maintain 100% (already good)
- Relations precision: 35% → **70%+**

### Accuracy Targets (by Phase 2 end)
- Overall score: 0.70 → **0.75+**
- Field boundary precision: 65% → **75%+**
- Field semantics accuracy: 40% → **55%+**
- Relations precision: 70% → **75%+**

### Accuracy Targets (by Phase 3 end)
- Overall score: 0.75 → **0.80+**
- All metrics: **>70%**

### Neural Mode Targets
- Current: 2 families, 0.16 score (broken)
- Phase 1 end: 10+ families, **0.45+ score**
- Phase 2 end: comparable to raw_bytes (**0.70+ score**)

### Runtime Targets (by Phase 3 end)
- 200K messages: 6 min → **3 min**
- Large payloads (8KB): 10-20 min → **5-10 min** (already improved)
- Memory usage: stable, no leaks

### Code Quality Targets (by Phase 4 end)
- Test coverage: 0% → **80%+**
- Documentation: minimal → **complete**
- Code complexity: reduce by 30%
- Type coverage: 50% → **95%+**

---

## RISK ASSESSMENT

### High Risk Items
1. **Clustering refactor (A1):** Core algorithm change, could break everything
   - Mitigation: Extensive testing, gradual rollout, keep old algorithm as fallback

2. **Semantic labeling (A3):** New complex module
   - Mitigation: Start with rule-based approach, add ML gradually

3. **Multi-layer support (A5):** Significant architecture change
   - Mitigation: Make optional, add feature flag

### Medium Risk Items
1. **Boundary detection changes (A2):** Could affect downstream stages
2. **Relation improvements (A4):** Complex logic, many edge cases
3. **Performance optimizations (B2):** Could introduce bugs

### Low Risk Items
1. **Documentation (C3):** No functional changes
2. **Logging improvements (C5):** Additive only
3. **Configuration management (C4):** Gradual refactoring

---

## DEPENDENCIES & PREREQUISITES

### Required for Phase 1
- Access to more ground truth protocols (DNP3, S7, IEC 104)
- Modbus PCAP with diverse function codes
- Validation dataset separate from test set

### Required for Phase 2
- GPU for neural model training (optional but recommended)
- Larger compute resources for parallel processing
- More diverse protocol captures

### Required for Phase 3
- CI/CD infrastructure for automated testing
- Documentation hosting (ReadTheDocs, GitHub Pages)
- Code review process

---

## CONCLUSION

The pipeline has excellent infrastructure but critical accuracy issues stemming from clustering collapse. The roadmap prioritizes fixing core inference algorithms (clustering, boundaries, semantics) before optimizing runtime or adding advanced features.

**Immediate Next Steps:**
1. Debug why clustering produces only 2 families for Modbus
2. Add discriminator-aware clustering features
3. Implement basic semantic field labeling
4. Add comprehensive unit tests

**Success Metric:** Achieve 0.50+ overall score on Modbus evaluation within 4 weeks.
