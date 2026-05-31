# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation with MkDocs
- Getting started guide
- Architecture documentation
- How-to-use guide with examples
- Testing guide
- Contributing guidelines

## [1.0.0] - 2026-05-31

### Added
- Enhanced boundary detection (A2) with anti-fragmentation penalties
- Multi-layer protocol detection (A6) for transport/application separation
- Hybrid feature fusion (A1) with adaptive weighting
- Multi-stage LLM integration (A5) with evidence-gated validation
- Improved logging and observability (C5)
- Code structure refactoring (C4)
- Diagnostic tools for neural features, boundaries, and fusion

### Changed
- Refactored stage 15 LLM analysis with prompt splitting
- Improved boundary detection precision from 38% to 65%+
- Updated README with comprehensive feature documentation

### Fixed
- Over-segmentation in boundary detection
- Neural feature collapse detection
- Large payload handling optimization

## [0.9.0] - 2026-05-15

### Added
- Semantic field labeling (A3) with protocol-agnostic inference
- Relation false positive reduction (A4)
- Ground truth evaluation framework
- LLM-assisted refinement with RFC 6902 patches

### Changed
- Improved clustering accuracy to 90%+ for raw_bytes mode
- Enhanced request/response pairing algorithm

### Fixed
- Clustering performance issues with large corpora
- Memory leaks in feature extraction

## [0.8.0] - 2026-04-30

### Added
- Neural feature mode with VAE latent vectors
- Structural feature mode with symbolic patterns
- Hybrid feature fusion methods
- Latent vector caching for performance

### Changed
- Refactored clustering module for multiple feature modes
- Improved feature extraction performance

## [0.7.0] - 2026-04-15

### Added
- Discriminator/opcode discovery with learned salience
- Request/response relation inference
- Echo field detection
- Length relation detection

### Changed
- Improved pairing algorithm accuracy
- Enhanced relation confidence scoring

## [0.6.0] - 2026-04-01

### Added
- Field boundary detection with entropy and mutual information
- Framing inference for header detection
- Feature extraction per family
- Protocol model assembly

### Changed
- Improved boundary detection algorithm
- Enhanced framing hypothesis generation

## [0.5.0] - 2026-03-15

### Added
- Message family discovery with HDBSCAN/DBSCAN
- Raw bytes feature extraction
- Family assignment propagation
- Clustering quality metrics

### Changed
- Optimized clustering for large message corpora
- Improved family assignment coverage

## [0.4.0] - 2026-03-01

### Added
- TShark-based message extraction
- Scapy-based TCP port extraction
- Message corpus management
- PCAP collection and deduplication

### Changed
- Improved extraction performance
- Enhanced error handling

## [0.3.0] - 2026-02-15

### Added
- HTML report generation with interactive elements
- Markdown report generation
- LLM evidence export
- Evaluation metrics computation

### Changed
- Improved report formatting and structure
- Enhanced visualization in HTML reports

## [0.2.0] - 2026-02-01

### Added
- Protocol model schema definition
- JSON schema validation
- Ground truth comparison framework
- Evaluation result reporting

### Changed
- Standardized protocol model format
- Improved schema documentation

## [0.1.0] - 2026-01-15

### Added
- Initial project structure
- Basic pipeline runner
- Core module organization
- README and basic documentation

---

## Legend

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security fixes
