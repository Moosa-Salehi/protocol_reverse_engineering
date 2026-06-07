# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

## [1.0.0] - 2026-06-6

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
