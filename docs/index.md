# Protocol Reverse Engineering

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A protocol-agnostic reverse engineering pipeline that analyzes binary protocol traffic from PCAP files and automatically infers protocol structure, message types, field boundaries, and semantic roles.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Analyze protocol traffic
python main.py pcaps/ --tshark-filter mbtcp --enhanced-boundaries

# View results
open output/protocol_report.html
```

**Output:** Comprehensive protocol specification with message families, field structures, and request/response relations.

## ✨ Features

- **Protocol-Agnostic Analysis** - Works with any binary protocol without prior knowledge
- **Automatic Message Clustering** - Discovers message families using advanced clustering (HDBSCAN/DBSCAN)
- **Field Boundary Detection** - Infers field boundaries with enhanced anti-fragmentation
- **Semantic Labeling** - Identifies opcodes, addresses, lengths, transaction IDs, and more
- **Request/Response Pairing** - Discovers protocol interactions and relations
- **Multi-Layer Detection** - Separates transport and application layers (experimental)
- **LLM-Assisted Refinement** - Optional LLM integration for improved semantic analysis
- **Comprehensive Reports** - Generates Markdown and interactive HTML specifications
- **Ground Truth Evaluation** - Validates results against known protocol specifications

## 📋 Requirements

- **Python 3.10+**
- **TShark** (Wireshark CLI) - for PCAP extraction
- **Dependencies:** numpy, scikit-learn, hdbscan, scapy, torch (optional)

## 📦 Installation

```bash
# Clone repository
git clone <repository-url>
cd protocol_re

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Usage

### Basic Analysis

```bash
# Analyze Modbus TCP traffic
python main.py pcaps/ --tshark-filter mbtcp

# Analyze unknown protocol on TCP port 502
python main.py pcaps/ --extraction-method tcp --service-port 502

# Use enhanced boundary detection (recommended)
python main.py pcaps/ --tshark-filter mbtcp --enhanced-boundaries
```

### Advanced Options

```bash
# With ground truth evaluation
python main.py pcaps/ --tshark-filter mbtcp \
    --ground-truth-json truth-files/modbus.json

# Custom LLM configuration (uses default if not specified)
python main.py pcaps/ --tshark-filter mbtcp \
    --llm-config LLM_config.json \
    --enhanced-boundaries

# Without LLM refinement (when API not available)
python main.py pcaps/ --tshark-filter mbtcp \
    --llm-render-only

# Multi-layer protocol detection
python main.py pcaps/ --tshark-filter mbtcp \
    --enable-layer-detection \
    --enhanced-boundaries

# Different feature modes
python main.py pcaps/ --tshark-filter mbtcp \
    --family-feature-mode raw_bytes  # raw_bytes (default), structural, neural, hybrid
```

### Feature Modes

- **raw_bytes** (recommended) - Padded byte vectors, 90%+ accuracy
- **structural** - Symbolic protocol features, interpretable
- **neural** (experimental) - VAE latent vectors, requires trained model
- **hybrid** - Combined neural + structural with adaptive fusion

## 📊 Pipeline Stages

The pipeline consists of 19 stages organized into phases:

1. **Collection & Extraction** (01-03)
   - Collect and deduplicate PCAPs
   - Extract protocol payloads

2. **Family Discovery** (04-06)
   - Cluster messages into families
   - Infer framing and headers
   - Extract statistical features

3. **Structure Inference** (07-09)
   - Detect field boundaries
   - Pair requests/responses
   - Discover discriminators/opcodes

4. **Semantic Analysis** (10-11)
   - Infer family relations
   - Assign semantic field labels

5. **Model Assembly** (12-13)
   - Build unified protocol model
   - Evaluate pipeline quality

6. **LLM Refinement** (14-15b, optional)
   - Export evidence for LLM
   - Apply evidence-gated patches

7. **Evaluation & Export** (16-19)
   - Compare against ground truth
   - Generate Markdown/HTML reports

## 📁 Project Structure

```
protocol_re/
├── src/protocol_re/          # Core library
│   ├── clustering/           # Message family discovery
│   ├── corpus/               # Message corpus management
│   ├── evaluation/           # Quality metrics
│   ├── export/               # Report generation
│   ├── features/             # Feature extraction
│   ├── inference/            # Structure inference
│   ├── llm/                  # LLM integration
│   └── model/                # Protocol model
├── scripts/                  # Pipeline stages (01-24)
├── docs/                     # Documentation
├── data/                     # Intermediate artifacts
├── output/                   # Final reports
├── pcaps/                    # Input PCAP files
├── truth-files/              # Ground truth protocols
├── schema/                   # JSON schemas
└── main.py                   # Pipeline runner
```

## 📖 Documentation

- **[Getting Started](docs/getting_started.md)** - Installation and first analysis
- **[How to Use](docs/how_to_use.md)** - Comprehensive usage guide
- **[Architecture](docs/architecture.md)** - System design and components
- **[API Reference](docs/api_reference.md)** - Module documentation
- **[Examples](docs/examples.md)** - Protocol-specific examples

## 🔧 Diagnostic Tools

```bash
# Diagnose neural feature quality
python scripts/20_diagnose_neural_features.py data/01_messages.jsonl

# Test enhanced neural features
python scripts/21_test_enhanced_neural.py data/01_messages.jsonl

# Test boundary detection
python scripts/22_test_boundary_detection.py data/01_messages.jsonl

# Test hybrid feature fusion
python scripts/23_test_learned_fusion.py data/01_messages.jsonl

# Test boundary refinement
python scripts/24_test_boundary_refinement.py data/05_families.json
```

## 📈 Performance

**Typical runtime for 200K messages:** ~6 minutes
- Message extraction: ~3 minutes
- Clustering & inference: ~2 minutes
- LLM refinement: ~2 minutes (depends on API)

**Accuracy (Modbus TCP with hybrid mode + LLM refinement):**
- Message type detection: 90.91% precision/recall
- Field boundary recall: 88.57%
- Field boundary precision: 65%+ with enhanced mode and LLM refinement
- Semantic labeling: 40-60% accuracy with LLM assistance

## 🎓 Supported Protocols

The pipeline is **protocol-agnostic** and has been tested with:

- **Modbus TCP** - Industrial automation
- **S7comm** - Siemens PLC communication
- **DNP3** - SCADA protocol
- **IEC 60870-5-104** - Power system automation
- **Custom protocols** - Any binary protocol over TCP/UDP

## 🔬 Research Features

### Enhanced Boundary Detection (A2)
Reduces over-segmentation through anti-fragmentation penalties and multi-pass merging.

### Multi-Layer Protocol Detection (A6)
Automatically detects and separates transport and application layers.

### Hybrid Feature Fusion (A1)
Combines neural and structural features with adaptive weighting and collapse detection.

### LLM-Assisted Refinement (A5)
Stage-specific LLM interactions with evidence-gated validation.

## 🛠️ Development

### Running Tests

```bash
# Set Python path
export PYTHONPATH=src  # Windows: $env:PYTHONPATH="src"

# Run tests (when available)
pytest tests/
```

### Step-by-Step Execution

```bash
# Set Python path
export PYTHONPATH=src

# Run individual stages
python scripts/03_extract_messages.py pcaps data/01_messages.jsonl --tshark-filter mbtcp
python scripts/04_discover_families.py data/01_messages.jsonl data/02_family_assignments.json
python scripts/07_infer_boundaries.py data/01_messages.jsonl data/05_families.json --enhanced
# ... (see docs/how_to_use.md for complete sequence)
```

## 📝 Configuration

### LLM Configuration (Optional)

Create `LLM_config.json`:

```json
{
  "api_key_required": "yes",
  "openai_base_url": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "temperature": 0.1,
  "max_tokens": 4000,
  "timeout": 180
}
```

Set API key:
```bash
export OPENAI_API_KEY=<your-api-key>  # Linux/Mac
$env:OPENAI_API_KEY = "<your-api-key>"  # Windows PowerShell
```

## 🐛 Troubleshooting

### TShark Not Found
Install Wireshark (includes TShark) and add to PATH.

### No Messages Extracted
- Verify TShark filter: `tshark -r capture.pcap -Y "mbtcp"`
- Try TCP extraction: `--extraction-method tcp --service-port 502`

### Poor Clustering
- Use `raw_bytes` mode: `--family-feature-mode raw_bytes`
- Diagnose: `python scripts/20_diagnose_neural_features.py data/01_messages.jsonl`

### Over-Segmentation
- Enable enhanced boundaries: `--enhanced-boundaries`
- Reduce field limit: `--boundary-max-fields 12`

See [How to Use](docs/how_to_use.md#troubleshooting) for more solutions.

## 🗺️ Roadmap

See [TODO_COMPREHENSIVE.md](TODO_COMPREHENSIVE.md) for detailed roadmap.

**Priority 1: Accuracy Improvements**
- ✅ Enhanced boundary detection (A2)
- ✅ Multi-layer protocol detection (A6)
- ✅ Hybrid feature fusion (A1)
- ✅ Multi-stage LLM integration (A5)
- 🔄 Improved semantic labeling (A3)
- 🔄 Relation false positive reduction (A4)

**Priority 2: Runtime Optimizations**
- ✅ Large payload handling (B1)
- 🔄 Incremental processing (B2)
- 🔄 Neural model optimization (B3)

**Priority 3: Code Quality**
- 🔄 Comprehensive unit tests (C1)
- ✅ Improved documentation (C3)
- ✅ Logging and observability (C5)
- ✅ Code structure refactoring (C4)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- TShark/Wireshark for packet analysis
- HDBSCAN for density-based clustering
- scikit-learn for machine learning utilities
- PyTorch for neural feature extraction

## 📧 Contact

For questions, issues, or contributions, please open an issue on GitHub.

---

**Note:** This is a research tool for protocol analysis and reverse engineering. Use responsibly and in accordance with applicable laws and regulations.
