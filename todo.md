### TODO 6. Neural-symbolic length-field identification

- Goal
    - Improve `scripts/05_infer_framing.py` and boundary inference so length fields are ranked by both symbolic consistency and learned structural context.
- Files
    - `src/protocol_re/inference/framing.py`
    - `src/protocol_re/inference/boundary_detection.py`
    - New: `src/protocol_re/inference/length_fields.py`
    - New: `src/protocol_re/neural/length_ranker.py`
    - New: `src/protocol_re/neural/features.py`
    - `src/protocol_re/model/schema.py`
    - `schema/protocol_model.schema.json`
    - `scripts/05_infer_framing.py`
    - `scripts/07_infer_boundaries.py`
- Tasks
    - Enumerate symbolic length candidates for widths 1, 2, 4, and optionally 8 bytes, with big/little endian variants.
    - Test each candidate against total message length, remaining length after the field, body length after inferred body start, and count-scaled forms such as `value * scale + constant`.
    - Add bit-level and byte-level correlation checks against segment sizes, body sizes, and family-specific length profiles.
    - Implement an optional neural ranker, preferably a small MLP, that consumes VAE latent vectors plus symbolic candidate features.
    - Score candidates with both `symbolic_confidence` and `neural_confidence`, then emit one combined `length_field_confidence`.
    - Keep the current heuristic path as the default fallback when neural weights are missing.
    - Store candidate evidence in framing output and propagate accepted fields into family field hypotheses.
- Output/schema changes
    - Add per-candidate evidence fields: `offset`, `width`, `endian`, `relation_type`, `scale`, `constant`, `symbolic_confidence`, `neural_confidence`, `confidence`, and `evidence`.
    - Valid `relation_type` values should include `total_length`, `remaining_length`, `body_length`, and `count_scaled_length`.
- Expected impact
    - Accuracy: ↑↑ for header interpretation and boundary placement.
    - Runtime: neutral when using cached latent vectors; fallback remains lightweight.
- Risk
    - Medium. Must avoid trusting neural scores unless symbolic checks also support the candidate.

### TODO 7. Contextual transaction-ID correlation

- Goal
    - Detect high-cardinality fields that are echoed across request/response pairs and use them to improve pairing and relation inference.
- Files
    - `src/protocol_re/inference/framing.py`
    - `src/protocol_re/corpus/request_response_pairing.py`
    - `src/protocol_re/inference/request_response_relations.py`
    - `src/protocol_re/inference/semantic_labeling.py`
    - New: `src/protocol_re/inference/correlation_fields.py`
    - New: `src/protocol_re/neural/field_embeddings.py`
    - `scripts/08_pair_requests_responses.py`
    - `scripts/10_infer_relations.py`
    - `scripts/11_infer_semantics.py`
- Tasks
    - Search fixed-offset field candidates with high cardinality, stable width, and low likelihood of being random payload tails.
    - Use existing candidate pairs plus a wider temporal search window to test request/response echo behavior.
    - Add embedding-based similarity for fields that may shift offsets across related families or occur inside variable headers.
    - Distinguish `transaction_id`, `correlation_id`, `sequence_number`, and `random_nonce` using echo rate, monotonicity, directionality, and reuse patterns.
    - Feed accepted correlation fields back into `_pair_score()` as strong evidence, not just a post-hoc relation label.
    - Emit field-level evidence and family-pair evidence for downstream semantic labeling and LLM evidence export.
- Output/schema changes
    - Add role labels `transaction_id` and `correlation_id` with evidence including `echo_rate`, `pair_support`, `offset_stability`, `cardinality`, and `confidence`.
- Expected impact
    - Accuracy: ↑↑ for request/response pairing and relation graphs.
    - Runtime: ↓ downstream after candidate pruning.
- Risk
    - Medium. Avoid mislabeling counters or timestamps as transaction IDs.

### TODO 8. Neural feature salience scoring

- Goal
    - Replace entropy-only discriminator discovery with learned salience scoring while preserving explainable symbolic evidence.
- Files
    - `src/protocol_re/features/extraction.py`
    - `src/protocol_re/inference/keyword_detection.py`
    - `src/protocol_re/inference/framing.py`
    - New: `src/protocol_re/neural/salience.py`
    - New: `src/protocol_re/inference/discriminator_fields.py`
    - `scripts/06_extract_features.py`
    - `scripts/09_infer_keywords.py`
    - `src/protocol_re/export/llm_evidence.py`
    - `schema/llm_evidence.schema.json`
- Tasks
    - Rename the internal concept from keyword-only detection to discriminator/opcode candidate discovery while keeping backward-compatible output names where needed.
    - Train or load an attention-based model that scores byte offsets and spans by contribution to family separation.
    - Add gradient-based salience support for neural encoders when model weights are available.
    - Combine learned salience with symbolic signals: low-to-medium cardinality, family mutual information, direction mutual information, length-profile separation, and offset stability.
    - Suppress fields already classified as length, transaction ID, counter, checksum, timestamp, or payload blob.
    - Search across all plausible header/body offsets instead of the current fixed offset window.
    - Export top discriminator candidates to LLM evidence with compact supporting statistics.
- Output/schema changes
    - Add candidate fields: `salience_score`, `mutual_information`, `contrastive_separation`, `excluded_roles`, and `confidence`.
- Expected impact
    - Accuracy: ↑ for message-type identification and family interpretation.
    - Runtime: neutral with cached salience; fallback stays heuristic.
- Risk
    - Medium. Learned salience must remain evidence-gated and explainable.

### TODO 9. Hybrid structural and neural feature encoding

- status: implemented. result: slight score decrease in raw_bytes mode, huge score decrease in structural mode.

### TODO 10. Neural clustering quality diagnostics

- Goal
    - Add diagnostics that identify over-split, under-split, noisy, or low-cohesion families using latent-space metrics and symbolic consistency.
- Files
    - `src/protocol_re/clustering/family_discovery.py`
    - `src/protocol_re/evaluation/reporting.py`
    - New: `src/protocol_re/clustering/diagnostics.py`
    - `scripts/04_discover_families.py`
    - `scripts/13_evaluate_pipeline.py`
    - `src/protocol_re/export/markdown.py`
    - `src/protocol_re/export/html.py`
- Tasks
    - Compute `latent_dispersion`, latent-space silhouette score, nearest-family distance, and density estimates when latent vectors exist.
    - Combine neural metrics with symbolic checks: length-profile consistency, discriminator consistency, direction consistency, field-layout consistency, and noise ratio.
    - Flag family merge candidates when latent distance is low and symbolic layouts are compatible.
    - Flag split candidates when latent dispersion is high, discriminator values are mixed, or field layouts are inconsistent.
    - Keep diagnostics advisory at first; do not automatically mutate family assignments until thresholds are validated.
    - Surface family-level warnings in evaluation JSON, Markdown, HTML, and LLM evidence.
- Output/schema changes
    - Add diagnostics: `latent_dispersion`, `latent_silhouette`, `merge_candidates`, `split_suspicion`, `under_split_score`, `over_split_score`, and `diagnostic_warnings`.
- Expected impact
    - Accuracy insight: ↑↑ for iterative tuning.
    - Runtime: neutral if computed from cached vectors.
- Risk
    - Low-medium. Automatic merge/split should remain disabled until proven reliable.

### TODO 11. Learned pairing and relation scorer

- Goal
    - Replace adjacency-first request/response pairing with an evidence-fusion scorer that can optionally use neural features.
- Files
    - `src/protocol_re/corpus/request_response_pairing.py`
    - `src/protocol_re/inference/request_response_relations.py`
    - New: `src/protocol_re/neural/pairing_model.py`
    - New: `src/protocol_re/inference/pairing_features.py`
    - `scripts/08_pair_requests_responses.py`
    - `scripts/10_infer_relations.py`
    - `src/protocol_re/model/schema.py`
    - `schema/protocol_model.schema.json`
- Tasks
    - Build a structured feature vector for candidate pairs using temporal proximity, index proximity, endpoint reversal, direction, length compatibility, discriminator compatibility, shared transaction ID evidence, echo fields, and latent similarity.
    - Implement a neural pairing scorer that fuses structural features and latent vectors, with a heuristic scorer as fallback.
    - Score multiple response candidates per request instead of only adjacent messages.
    - Emit confidence scores and evidence components for every accepted pair and family-level relation.
    - Use learned scores to filter false positives and classify relation types such as `request_response`, `command_ack`, `query_result`, and `error_response`.
    - Preserve existing behavior behind a compatibility flag until evaluation improves.
- Output/schema changes
    - Add pair evidence fields: `score`, `score_components`, `model_score`, `heuristic_score`, `shared_transaction_id`, `latent_similarity`, and `relation_confidence`.
- Expected impact
    - Accuracy: ↑↑ for relation extraction and semantic labels.
    - Runtime: ↓ after pruning candidate windows.
- Risk
    - Medium. Requires good negative sampling or conservative thresholds.

### TODO 12. Automated unsolicited event detection

- Goal
    - Stop forcing all traffic into request/response structure and classify spontaneous messages such as telemetry, events, notifications, and heartbeats.
- Files
    - `src/protocol_re/corpus/request_response_pairing.py`
    - `src/protocol_re/inference/request_response_relations.py`
    - `src/protocol_re/inference/semantic_labeling.py`
    - New: `src/protocol_re/inference/event_detection.py`
    - New: `src/protocol_re/neural/event_classifier.py`
    - `scripts/08_pair_requests_responses.py`
    - `scripts/10_infer_relations.py`
    - `scripts/11_infer_semantics.py`
- Tasks
    - Add message/family roles: `request`, `response`, `notification`, `event`, `heartbeat`, and `unknown`.
    - Detect families that frequently appear without matching responses but have stable direction, regular timing, and consistent structure.
    - Train or load an optional classifier using directionality, periodicity, structural regularity, payload length stability, discriminator values, and latent features.
    - Keep unpaired messages as first-class evidence instead of treating them only as pairing failures.
    - Feed event/heartbeat labels into relation inference and semantic labeling.
    - Render event families separately in Markdown and HTML reports.
- Output/schema changes
    - Add role evidence: `message_role`, `role_confidence`, `unpaired_rate`, `periodicity_score`, `direction_consistency`, and `event_classifier_score`.
- Expected impact
    - Accuracy: ↑ for industrial telemetry, alarms, and heartbeat protocols.
    - Runtime: neutral.
- Risk
    - Low-medium. Avoid overclassifying sparse request traffic as events.

### TODO 13. Deep boundary segmentation

- Goal
    - Replace statistical-only field segmentation with a neural boundary model that is constrained by symbolic protocol evidence.
- Files
    - `src/protocol_re/inference/boundary_detection.py`
    - New: `src/protocol_re/inference/field_candidates.py`
    - New: `src/protocol_re/neural/boundary_model.py`
    - New: `src/protocol_re/neural/reconstruction.py`
    - `scripts/07_infer_boundaries.py`
    - `src/protocol_re/model/schema.py`
    - `schema/protocol_model.schema.json`
- Tasks
    - Implement a Neural Boundary Detection Model, such as BiLSTM-CRF or a compact Transformer tagger, that predicts boundary probabilities per byte offset.
    - Use VAE reconstruction error as an anomaly or transition signal to highlight likely field boundaries.
    - Combine neural boundary probabilities with symbolic candidates: constant runs, numeric fields, length fields, discriminators, transaction IDs, counters, flags/status, payload tails, and checksum-like trailers.
    - Penalize excessive one-byte segmentation unless strong enum/flags/status evidence exists.
    - Prefer compact layouts with high role evidence and consistent boundaries across messages in the same family.
    - Keep entropy jumps as one weak signal, not the primary segmentation driver.
    - Add family-level max-field sanity checks and oversegmentation warnings.
- Output/schema changes
    - Add boundary evidence fields: `boundary_probability`, `reconstruction_error`, `symbolic_support`, `neural_support`, `segmentation_confidence`, and `oversegmentation_warning`.
- Expected impact
    - Accuracy: ↑↑ for field boundaries and semantic labeling.
    - Runtime: neutral to slower depending on model size; cache per-family predictions.
- Risk
    - Medium-high. Needs strict fallback and strong oversegmentation controls.

### TODO 14. Semantic role and encoding taxonomy

- Goal
    - Standardize the protocol model so field encoding types are separate from semantic roles and all LLM/evaluation outputs use the same taxonomy.
- Files
    - `src/protocol_re/model/schema.py`
    - `schema/protocol_model.schema.json`
    - `schema/llm_evidence.schema.json`
    - `schema/evaluation_input.schema.json`
    - `src/protocol_re/inference/semantic_labeling.py`
    - `src/protocol_re/export/llm_evidence.py`
    - `src/protocol_re/export/markdown.py`
    - `src/protocol_re/export/html.py`
    - `scripts/11_infer_semantics.py`
    - `scripts/12_build_protocol_model.py`
    - `scripts/14_export_llm_evidence.py`
- Tasks
    - Extend field hypotheses with `encoding_type`, `semantic_role`, `role_confidence`, and `role_evidence` while preserving `field_type` for backward compatibility.
    - Define encoding types such as `uint8`, `uint16`, `uint32`, `uint64`, `int`, `float`, `bytes`, `bitfield`, `enum`, `ascii`, `utf8`, `bcd`, and `unknown`.
    - Define semantic roles such as `constant`, `reserved`, `version`, `message_type`, `function_code`, `length`, `transaction_id`, `correlation_id`, `sequence_number`, `counter`, `unit_id`, `device_id`, `address`, `quantity`, `status`, `error_code`, `flags`, `timestamp`, `payload`, `checksum`, and `unknown`.
    - Add strict schema validation for LLM-ready evidence bundles so prompts and JSON patch workflows use stable field names.
    - Update exporters to display encoding type and semantic role separately.
    - Update evaluation to score encoding-type matches separately from semantic-role matches.
- Output/schema changes
    - Add taxonomy definitions to model and LLM evidence schemas.
- Expected impact
    - Accuracy: ↑ for semantic evaluation and LLM refinement.
    - Runtime: neutral.
- Risk
    - Medium due to schema compatibility.

### TODO 15. LLM-driven protocol hinting

- Goal
    - Add an evidence-gated plugin system where LLMs can propose protocol-family hints without controlling the core generic pipeline.
- Files
    - `src/protocol_re/llm/analyze.py`
    - `src/protocol_re/export/llm_evidence.py`
    - New package: `src/protocol_re/protocol_hints/`
    - New: `src/protocol_re/protocol_hints/base.py`
    - New: `src/protocol_re/protocol_hints/llm_hinting.py`
    - Optional: `src/protocol_re/protocol_hints/modbus_like.py`
    - Optional: `src/protocol_re/protocol_hints/dnp3_like.py`
    - Optional: `src/protocol_re/protocol_hints/iec104_like.py`
    - Optional: `src/protocol_re/protocol_hints/s7_like.py`
    - `scripts/14_export_llm_evidence.py`
    - `scripts/15_analyze_with_llm.py`
- Tasks
    - Define a plugin interface where input is the generic protocol model plus compact evidence, and output is a protocol-family hint with confidence and evidence references.
    - Let LLM hinting compare evidence bundles against external specs, RFCs, or user-provided protocol notes when explicitly enabled.
    - Require every hint to cite local evidence fields such as stable prefixes, discriminators, length fields, function-code patterns, relation shapes, and known port information.
    - Keep hints advisory and separate from the core protocol model unless later accepted by a validated refinement step.
    - Add confidence thresholds and report known-protocol similarity separately from generic inference.
    - Support `--llm-render-only` so hints can be reviewed without API calls.
- Output/schema changes
    - Add optional `protocol_hints` section with `candidate_protocol`, `confidence`, `matched_evidence`, `missing_evidence`, `source`, and `limitations`.
- Expected impact
    - Accuracy: ↑ for known protocols and analyst productivity.
    - Runtime: neutral unless external LLM/spec lookup is enabled.
- Risk
    - Medium-high. Must avoid overfitting unknown traffic to familiar protocols.

### TODO 16. Layered neuro-symbolic evaluation

- Goal
    - Evaluate the pipeline at separate layers so neural clustering, boundary segmentation, semantic roles, pairing, and LLM refinement can be improved independently.
- Files
    - `scripts/13_evaluate_pipeline.py`
    - `scripts/16_prepare_evaluation_data.py`
    - `scripts/17_evaluate_protocol_spec.py`
    - `src/protocol_re/evaluation/reporting.py`
    - `schema/evaluation_input.schema.json`
    - `schema/evaluation_output.schema.json`
    - `src/protocol_re/export/markdown.py`
    - `src/protocol_re/export/html.py`
- Tasks
    - Add neural clustering metrics: latent silhouette, latent dispersion, nearest-family margin, neural cluster precision proxy, and neural/symbolic disagreement rate.
    - Add boundary metrics: segment boundary overlap, boundary precision/recall, IoU against ground truth when available, oversegmentation ratio, and undersegmentation ratio.
    - Add semantic metrics: encoding-type accuracy, semantic-role accuracy, role confidence calibration, and evidence coverage.
    - Add pairing/relation metrics: pair precision/recall when ground truth exists, transaction-ID support rate, false-positive relation proxy, and unpaired-event classification rate.
    - Add LLM/refinement metrics: patch acceptance rate, schema-valid patch rate, evidence-supported patch rate, and refined-vs-base evaluation delta.
    - Keep legacy summary metrics for compatibility but group new metrics by layer.
- Output/schema changes
    - Add top-level metric groups: `clustering`, `boundaries`, `semantics`, `pairing`, `relations`, `neural`, and `llm_refinement`.
- Expected impact
    - Accuracy metric quality: ↑↑ and easier regression tracking.
    - Runtime: neutral.
- Risk
    - Low-medium. Requires careful handling when ground truth is absent.

### TODO 17. Structured LLM refinement engine

- Goal
    - Convert LLM output from freeform analysis into validated semantic patches that can refine the protocol model without hallucinating unsupported changes.
- Files
    - `src/protocol_re/llm/analyze.py`
    - New: `src/protocol_re/llm/patches.py`
    - New: `src/protocol_re/llm/patch_validation.py`
    - New: `src/protocol_re/llm/refinement.py`
    - `src/protocol_re/export/llm_evidence.py`
    - `src/protocol_re/model/schema.py`
    - `schema/protocol_model.schema.json`
    - `schema/llm_evidence.schema.json`
    - `scripts/15_analyze_with_llm.py`
    - New: `scripts/15b_apply_llm_refinement.py`
    - `scripts/16_prepare_evaluation_data.py`
    - `scripts/17_evaluate_protocol_spec.py`
- Tasks
    - Change the LLM contract so the model can emit RFC 6902 JSON patches against `data/10_protocol_model.json`.
    - Include neural context in the evidence bundle: latent diagnostics, salience scores, boundary probabilities, reconstruction error, and neural pairing scores.
    - Validate every patch against the protocol model schema before applying it.
    - Add an evidence gate that rejects patches lacking support from statistical, symbolic, or neural evidence.
    - Restrict allowed patch targets at first to semantic roles, encoding types, confidence adjustments, relation labels, and protocol hints.
    - Write rejected patches with rejection reasons for auditability.
    - Produce both base and refined protocol models so evaluation can compare refined vs unrefined output.
    - Add a safe CLI workflow: render prompt, collect LLM patches, validate patches, apply accepted patches, then evaluate deltas.
- Output/schema changes
    - Add refinement artifacts: `data/13_llm_analysis.json`, `data/13_llm_patches.json`, `data/13_llm_patch_validation.json`, and `data/10_protocol_model.refined.json`.
- Expected impact
    - Analyst productivity: ↑↑ with controlled LLM assistance.
    - Accuracy: ↑ when patches are evidence-supported.
    - Runtime: neutral except LLM latency.
- Risk
    - High. Strict validation is mandatory to prevent hallucinated model changes.
