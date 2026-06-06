# Architecture

This document describes the technical architecture, design principles, and implementation details of the Protocol Reverse Engineering pipeline.

## Design Principles

1. **Protocol-Agnostic**: All inference is based on statistical patterns and structural analysis, not protocol-specific knowledge
2. **Evidence-Preserving**: Each stage retains upstream evidence in the protocol model rather than discarding it
3. **Modular**: Stages can be run independently or as part of the full pipeline
4. **Deterministic with ML**: Core functionality uses deterministic algorithms; ML features (neural clustering, LLM refinement) are added as enhancements

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Input: PCAP/PCAPNG Files                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 01-02: Collection & Deduplication (Optional)             │
│  - Collect PCAPs from source tree                               │
│  - Remove duplicate captures                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 03: Message Extraction                                   │
│  - Extract payloads using TShark or Scapy                       │
│  - Create canonical message corpus (JSONL)                      │
│  Output: data/01_messages.jsonl                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 04: Family Discovery                                     │
│  - Cluster messages into families using HDBSCAN/DBSCAN          │
│  - Support multiple feature modes (raw_bytes, structural,       │
│    neural, hybrid)                                              │
│  Output: data/02_family_assignments.json                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 05: Framing Inference                                    │
│  - Detect stable prefixes and header patterns                   │
│  - Identify length fields, counters, discriminators             │
│  - Optional: Multi-layer protocol detection                     │
│  Output: data/04_framing.json                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 06: Feature Extraction                                   │
│  - Extract per-family statistical features                      │
│  - Entropy, uniqueness, byte histograms, n-grams                │
│  Output: data/03_family_features.json                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 07: Boundary Detection                                   │
│  - Infer field boundaries within messages                       │
│  - Enhanced mode: reduce over-segmentation                      │
│  - LLM-assisted boundary refinement                             │
│  Output: data/05_families.json                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 08: Request/Response Pairing                             │
│  - Pair likely requests and responses within sessions           │
│  Output: data/06_pairs.json                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 09: Discriminator/Opcode Discovery                       │
│  - Identify discriminator bytes using learned salience          │
│  - Detect opcode candidates and subformats                      │
│  Output: data/07_keywords.json                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 10: Relation Inference                                   │
│  - Infer family-to-family relations                             │
│  - Detect echo fields, length relations                         │
│  - LLM-assisted relation validation                             │
│  Output: data/08_relations.json                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 11: Semantic Labeling                                    │
│  - Assign semantic roles to fields                              │
│  - LLM-assisted semantic labeling                               │
│  Output: data/09_semantics.json                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 12: Protocol Model Assembly                              │
│  - Combine all evidence into unified protocol model             │
│  Output: data/10_protocol_model.json                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 13: Pipeline Evaluation                                  │
│  - Compute quality metrics                                      │
│  Output: data/11_evaluation.json                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 14-15b: LLM Analysis & Refinement                        │
│  - Export compact evidence for LLM                              │
│  - Call LLM API for analysis                                    │
│  - Validate and apply evidence-gated patches                    │
│  Output: data/10_protocol_model.refined.json                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 16-17: Ground Truth Evaluation (Optional)                │
│  - Compare against ground truth protocol                        │
│  Output: data/15_evaluation_result.json                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Stage 18-19: Report Generation                                 │
│  - Export Markdown and HTML reports                             │
│  Output: output/protocol_report.md, output/protocol_report.html │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Message Corpus (`src/protocol_re/corpus/`)

The canonical message representation used throughout the pipeline. Each message contains:
- Payload hex data
- Source file and session information
- Timestamp and metadata
- Extraction method details

### 2. Clustering (`src/protocol_re/clustering/`)

Message family discovery using multiple feature extraction modes:

- **raw_bytes**: Padded byte vectors with volatile offset downweighting
- **structural**: 35-dimensional symbolic protocol features (length buckets, stable prefixes, discriminators, entropy, direction)
- **neural**: 32D VAE latent vectors
- **hybrid**: Combined neural + structural features with adaptive/learned fusion

Supports HDBSCAN, DBSCAN, and heuristic fallback clustering.

### 3. Inference (`src/protocol_re/inference/`)

Protocol structure inference modules:

- **Framing**: Detect headers, length fields, counters, discriminators
- **Boundary Detection**: Infer field boundaries using entropy, mutual information, and variability
- **Semantic Labeling**: Assign semantic roles
- **Relations**: Discover request/response pairs and field correlations
- **Layer Detection**: Identify multi-layer protocols (transport + application)

### 4. Features (`src/protocol_re/features/`)

Statistical feature extraction per family:
- Length profiles and statistics
- Entropy and uniqueness by byte offset
- Byte histograms and n-gram frequencies
- Motif repetition and padding detection
- Fixed-position field groups

### 5. LLM Integration (`src/protocol_re/llm/`)

LLM-assisted refinement with evidence gating:
- Stage-specific LLM interactions (boundaries, semantics, relations)
- RFC 6902 JSON patch validation
- Evidence-based patch acceptance/rejection

### 6. Evaluation (`src/protocol_re/evaluation/`)

Quality metrics and ground truth comparison:
- Clustering quality (silhouette score, coverage)
- Boundary detection precision/recall
- Semantic labeling accuracy
- Relation detection F1 score
- Overall protocol model score

### 7. Export (`src/protocol_re/export/`)

Report generation:
- Markdown protocol specifications
- Self-contained HTML reports with interactive elements
- Compact LLM evidence bundles
- Evaluation data for ground truth comparison

## Data Flow

### Intermediate Artifacts

All intermediate artifacts are stored in the `data/` directory:

| File | Stage | Description |
|------|-------|-------------|
| `01_messages.jsonl` | 03 | Canonical message corpus |
| `02_family_assignments.json` | 04 | Message-to-family mappings |
| `03_family_features.json` | 06 | Per-family statistical features |
| `04_framing.json` | 05 | Framing and header hypotheses |
| `05_families.json` | 07 | Field boundaries and templates |
| `06_pairs.json` | 08 | Request/response pairs |
| `07_keywords.json` | 09 | Discriminator/opcode candidates |
| `08_relations.json` | 10 | Family-to-family relations |
| `09_semantics.json` | 11 | Semantic field labels |
| `10_protocol_model.json` | 12 | Base protocol model |
| `10_protocol_model.refined.json` | 15b | LLM-refined protocol model |
| `11_evaluation.json` | 13 | Pipeline quality metrics |
| `12_llm_evidence.json` | 14 | Compact LLM evidence bundle |
| `13_llm_analysis.json` | 15 | LLM analysis and patches |
| `14_evaluation_model_data.json` | 16 | Prepared evaluation data |
| `15_evaluation_result.json` | 17 | Ground truth comparison results |

### Final Outputs

Final reports are stored in the `output/` directory:
- `protocol_report.md`: Human-readable Markdown specification
- `protocol_report.html`: Self-contained HTML report with visualizations

## Feature Modes

### Raw Bytes Mode

Uses padded byte vectors with downweighting of volatile offsets. Achieved 90%+ accuracy on tested protocol.

Implementation:
- Pad messages to fixed length (default: 512 bytes)
- Extract byte values as features
- Downweight positions with high variance
- Use cosine similarity for clustering

### Structural Mode

Uses 35-dimensional symbolic protocol features:
- Length features: log bucket, mod 2/4/8 patterns (4 dims)
- Direction: client-to-server, server-to-client, unknown (3 dims)
- Entropy and uniqueness ratio (2 dims)
- Body start and length field evidence (2 dims)
- Stable prefix mask: 16-byte stability scores (16 dims)
- Discriminator bytes: first 8 bytes normalized (8 dims)

Implementation:
- Extract length distribution features
- Compute stable byte positions across corpus
- Identify discriminator candidates
- Combine into 35-dim feature vector

### Neural Mode

Uses 32D VAE latent vectors from `assets/pre_trained/industrial_VAE.pth`.

Implementation:
- Load pre-trained VAE model
- Encode messages to latent space
- Use latent vectors as features
- Detect collapsed latent spaces

### Hybrid Mode

Combines neural and structural features with flexible fusion:
- **concat**: Simple concatenation (baseline)
- **adaptive**: Quality-based automatic weighting (recommended)
- **learned**: MLP-based feature importance learning
- **fixed**: Manual weight specification

Implementation:
- Extract both neural (32D) and structural (35D) features
- Detect neural collapse (low variance, poor separation)
- Automatically adjust fusion weights based on feature quality
- Cache latent vectors for performance
- Fallback to concat if learned fusion unavailable

## Enhanced Features

### Enhanced Boundary Detection

Reduces over-segmentation through:
- Anti-fragmentation penalties (penalize excessive 1-byte fields)
- Reduced entropy weight in scoring
- Multi-pass segment merging (up to 3 passes with 6 merging rules)
- Maximum field count limit (default: 15 fields per family)

Merging Rules:
1. Merge adjacent 1-byte fields
2. Merge low-entropy neighbors
3. Merge fields with similar byte distributions
4. Merge fields with correlated values
5. Merge constant fields
6. Merge fields below minimum length threshold

### Multi-Layer Protocol Detection

Detects layered protocols (transport framing + application payload) using:
- Length fields pointing past their position
- Stable prefix + variable suffix patterns
- Transaction/counter fields in header region
- Confidence scoring based on evidence strength

Detection Criteria:
- Length field at offset < 8 pointing to offset > 8
- Stable prefix (entropy < 0.5) for first N bytes
- Variable suffix (entropy > 2.0) for remaining bytes
- Transaction ID or counter in header region

Implementation:
- `src/protocol_re/inference/layer_detection.py` - boundary detection logic
- `scripts/05_infer_framing.py` --detect-layers flag enables detection
- `scripts/04_discover_families.py` --layer-aware flag for layer-aware clustering
- Layer boundary stored in framing JSON for downstream stages
- Clustering can run on inner payload only (post-header bytes)

### LLM-Assisted Refinement

Stage-specific LLM interactions for:
- Boundary refinement (merge over-segmented fields)
- Semantic labeling (assign field roles)
- Relation validation (filter false positives)

Evidence Gating:
- All LLM suggestions validated against statistical evidence
- Patches rejected if they contradict strong evidence
- Confidence scores used to weight decisions
- Fallback to statistical inference if LLM unavailable

### Scalability

- Supports up to 200K messages by default (configurable)
- Clustering uses sampling for large corpora

## Next Step

- Read [Contribution](contributing.md) for contributing
