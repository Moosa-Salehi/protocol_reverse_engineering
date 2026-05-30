# Comprehensive TODO List for Protocol Reverse Engineering Pipeline

**Analysis Date:** 2026-05-30  
**Current Status:** Overall accuracy score: 0.158741 (FAIL) on Modbus evaluation  
**Priority Order:** 1. Accuracy → 2. Runtime → 3. Code Quality

---

## Executive Summary

Based on evaluation results (`data/15_evaluation_result.json`), the pipeline shows critical accuracy issues:
- **Message Type Matching:** 18.2% recall (2/11 types detected)
- **Field Boundaries:** 25.7% recall, 45% precision
- **Field Semantics:** 0% accuracy (no correct semantic labels)
- **Relations:** 0% accuracy (no correct request/response relations)

The pipeline has strong infrastructure (LLM integration, neural features, evaluation framework) but needs significant improvements in core inference algorithms.

---

## PRIORITY 1: ACCURACY IMPROVEMENTS (Critical)

### A1. Fix Family Discovery / Clustering (CRITICAL - Root Cause)
**Priority:** P0 - Blocking all downstream accuracy  
**Current Issue:** Only 2 families detected for Modbus (should be 11+ message types)  
**Impact:** Cascading failure - wrong clustering → wrong boundaries → wrong semantics

**Tasks:**
1. **Investigate clustering collapse:**
   - Analyze why 199,715/200,000 messages assigned to single family
   - Check if neural features (32D latent) are too compressed
   - Examine if structural features lack discriminative power
   - Review HDBSCAN/DBSCAN parameters (min_cluster_size, min_samples, eps)

2. **Add discriminator-aware clustering:**
   - Extract function code (byte 0) as strong clustering signal
   - Use stable prefix bytes as pre-clustering features
   - Add direction (client/server) as clustering constraint
   - Implement hierarchical clustering: coarse (by opcode) → fine (by structure)

3. **Improve feature engineering:**
   - Add position-weighted byte features (header bytes more important)
   - Include length bucket as explicit feature
   - Add byte histogram similarity
   - Use edit distance for similar-length messages
   - Combine multiple feature modes with learned weights

4. **Add clustering validation:**
   - Implement silhouette score monitoring
   - Add within-cluster variance checks
   - Detect over-clustering (too many 1-message families)
   - Detect under-clustering (families with high internal variance)
   - Auto-tune clustering parameters based on validation metrics

**Files:**
- `src/protocol_re/clustering/family_discovery.py`
- `src/protocol_re/clustering/hybrid_features.py`
- `src/protocol_re/clustering/structural_features.py`
- `scripts/04_discover_families.py`

**Expected Impact:** Recall 18% → 70%+, F1 0.31 → 0.75+

---

### A2. Improve Field Boundary Detection
**Priority:** P0 - Critical for semantic labeling  
**Current Issue:** 25.7% recall, many merged/split fields

**Tasks:**
1. **Add protocol-aware boundary hints:**
   - Detect common header patterns (1-byte opcode, 2-byte address, 2-byte quantity)
   - Use length field values to mark payload boundaries
   - Recognize fixed-width field patterns (2-byte, 4-byte alignment)
   - Add checksum/CRC detection at message end

2. **Improve boundary scoring:**
   - Reduce weight on entropy jumps (currently over-weighted)
   - Add field-width consistency across family
   - Penalize 1-byte fields unless strong evidence (enum/flags)
   - Reward boundaries that align with known field widths (1, 2, 4, 8)

3. **Add cross-family boundary consistency:**
   - If multiple families share prefix, align their boundaries
   - Use discriminator offsets as strong boundary signals
   - Propagate high-confidence boundaries across similar families

4. **Implement boundary validation:**
   - Check if inferred fields make semantic sense
   - Validate against length field values
   - Ensure no overlapping fields
   - Flag suspicious single-byte sequences

**Files:**
- `src/protocol_re/inference/boundary_detection.py`
- `scripts/07_infer_boundaries.py`

**Expected Impact:** Boundary recall 25.7% → 60%+, precision 45% → 70%+

---

### A3. Implement Semantic Field Labeling (NEW)
**Priority:** P0 - Currently 0% accuracy  
**Current Issue:** No correct semantic labels detected

**Tasks:**
1. **Build semantic inference engine:**
   - Create rule-based classifier for common field types
   - Detect function_code: byte 0, low cardinality (1-256), stable
   - Detect address fields: bytes 1-2, 2-byte width, big-endian
   - Detect quantity/count: bytes 3-4, 2-byte width, correlates with payload
   - Detect byte_count: 1-byte, value matches remaining length
   - Detect transaction_id: 2-byte, echoed in request/response
   - Detect payload: variable length, high entropy, after header

2. **Add field type taxonomy:**
   - Separate encoding (uint8, uint16, bytes) from semantics (function_code, address)
   - Define semantic roles: function_code, address, quantity, byte_count, transaction_id, unit_id, payload, checksum
   - Map field_type → semantic_role with confidence scores

3. **Use relation evidence:**
   - Fields echoed in responses → transaction_id
   - Fields matching response length → byte_count or quantity
   - First byte with low cardinality → function_code or message_type
   - Last bytes with fixed patterns → checksum or padding

4. **Add LLM-assisted semantic refinement:**
   - Export field candidates with evidence to LLM
   - Let LLM suggest semantic labels based on patterns
   - Validate LLM suggestions against evidence
   - Apply only evidence-supported labels

**Files:**
- `src/protocol_re/inference/semantic_labeling.py` (major rewrite)
- New: `src/protocol_re/inference/field_semantics.py`
- `scripts/11_infer_semantics.py`

**Expected Impact:** Semantic accuracy 0% → 40%+

---

### A4. Fix Request/Response Pairing and Relations
**Priority:** P1 - Currently 0% accuracy  
**Current Issue:** No correct relations detected

**Tasks:**
1. **Improve pairing algorithm:**
   - Use function code matching (request/response should have related opcodes)
   - Add transaction ID matching (if detected)
   - Consider temporal proximity + direction reversal
   - Handle multiple responses per request
   - Detect error responses (exception codes)

2. **Add relation type classification:**
   - Distinguish: request_response, command_ack, query_result, error_response
   - Use payload length patterns (query=short, result=long)
   - Use discriminator patterns (error codes vs normal codes)

3. **Improve echo field detection:**
   - Focus on header regions (first 32 bytes) not entire payload
   - Prioritize 2-byte and 4-byte fields (transaction IDs)
   - Require high support (>90%) for echo claims

4. **Add relation validation:**
   - Check if paired families have compatible structures
   - Validate temporal ordering (response after request)
   - Ensure direction consistency (client→server, server→client)

**Files:**
- `src/protocol_re/corpus/request_response_pairing.py`
- `src/protocol_re/inference/request_response_relations.py`
- `scripts/08_pair_requests_responses.py`
- `scripts/10_infer_relations.py`

**Expected Impact:** Relation recall 0% → 50%+

---

### A5. Add Multi-Layer Protocol Support
**Priority:** P2 - Important for real protocols  
**Current Issue:** Modbus TCP has MBAP header + PDU, pipeline treats as flat

**Tasks:**
1. **Detect layered structure:**
   - Identify stable outer headers (MBAP: 7 bytes for Modbus TCP)
   - Detect length fields that point to inner protocol start
   - Recognize protocol identifiers (MBAP protocol_id = 0x0000)

2. **Implement layer separation:**
   - Extract outer header fields separately
   - Cluster inner protocol messages independently
   - Maintain layer relationships in protocol model

3. **Add layer-aware evaluation:**
   - Match fields at correct layer
   - Support hierarchical ground truth (MBAP + Modbus PDU)

**Files:**
- New: `src/protocol_re/inference/layer_detection.py`
- `src/protocol_re/inference/framing.py`
- `scripts/05_infer_framing.py`

**Expected Impact:** Accuracy +15% for layered protocols

---

### A6. Improve Discriminator/Opcode Detection
**Priority:** P1 - Critical for clustering and semantics  
**Current Issue:** Function codes not reliably detected

**Tasks:**
1. **Strengthen discriminator detection:**
   - Prioritize byte 0 for function codes
   - Require low cardinality (2-256 unique values)
   - Check stability across family (>95% same position)
   - Validate against clustering (should separate families)

2. **Add discriminator validation:**
   - Check if discriminator values correlate with family assignments
   - Ensure discriminator has high mutual information with families
   - Validate that discriminator is not a counter or random field

3. **Use discriminators in clustering:**
   - Pre-cluster by discriminator value
   - Use discriminator as strong feature in hybrid mode
   - Ensure families don't span multiple discriminator values

**Files:**
- `src/protocol_re/inference/framing.py`
- `scripts/09_infer_keywords.py`
- `scripts/05_infer_framing.py`

**Expected Impact:** Clustering accuracy +20%, semantic accuracy +15%

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
1. **Separate concerns:**
   - Split large modules (boundary_detection.py: 336 lines)
   - Extract reusable utilities
   - Create clear interfaces between stages

2. **Improve naming:**
   - Rename "keywords" to "discriminators" consistently
   - Use semantic names for field types
   - Standardize function naming conventions

3. **Add configuration management:**
   - Centralize magic numbers and thresholds
   - Create config file for pipeline parameters
   - Allow per-protocol configuration overrides

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
**Goal:** Improve overall score from 0.16 to 0.50+

1. **Week 1:** Fix clustering (A1)
   - Investigate clustering collapse
   - Add discriminator-aware features
   - Tune HDBSCAN parameters
   - Target: 5+ families detected for Modbus

2. **Week 2:** Improve boundaries (A2) and discriminators (A6)
   - Add protocol-aware boundary hints
   - Strengthen discriminator detection
   - Target: 50%+ boundary recall

3. **Week 3:** Implement semantic labeling (A3)
   - Build semantic inference engine
   - Add field type taxonomy
   - Target: 30%+ semantic accuracy

4. **Week 4:** Fix relations (A4)
   - Improve pairing algorithm
   - Add relation validation
   - Target: 40%+ relation recall

**Milestone:** Overall score 0.50+, all metrics >30%

---

### Phase 2: Advanced Accuracy & Runtime (Weeks 5-8)

1. **Week 5:** Multi-layer protocol support (A5)
2. **Week 6:** LLM-assisted refinement improvements
3. **Week 7:** Runtime optimizations (B2, B3)
4. **Week 8:** Performance tuning and profiling

**Milestone:** Overall score 0.65+, 2x faster runtime

---

### Phase 3: Code Quality & Testing (Weeks 9-12)

1. **Week 9-10:** Add comprehensive tests (C1)
2. **Week 11:** Improve documentation (C3)
3. **Week 12:** Code refactoring (C4)

**Milestone:** 80%+ test coverage, complete documentation

---

### Phase 4: Advanced Features (Weeks 13+)

1. Research and implement advanced features (D1-D4)
2. Explore new neural architectures
3. Add protocol-specific optimizations

**Milestone:** State-of-the-art protocol RE system

---

## METRICS & SUCCESS CRITERIA

### Accuracy Targets (by Phase 1 end)
- Overall score: 0.16 → **0.50+**
- Message type recall: 18% → **70%+**
- Field boundary recall: 26% → **60%+**
- Field boundary precision: 45% → **70%+**
- Field semantics accuracy: 0% → **40%+**
- Relations recall: 0% → **50%+**

### Runtime Targets (by Phase 2 end)
- 200K messages: 6 min → **3 min**
- Large payloads (8KB): hours → **10-20 min**
- Memory usage: stable, no leaks

### Code Quality Targets (by Phase 3 end)
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
