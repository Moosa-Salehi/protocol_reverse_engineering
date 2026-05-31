# Protocol Reverse Engineering

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

## ✨ Key Features

- **Protocol-Agnostic** - Works with any binary protocol
- **Automatic Clustering** - Discovers message families
- **Field Detection** - Infers boundaries and structure
- **Semantic Analysis** - Labels opcodes, addresses, lengths
- **LLM Integration** - Optional AI-assisted refinement
- **Comprehensive Reports** - Markdown and HTML output

## 📖 Documentation

- **[Getting Started](docs/getting_started.md)** - Installation and first analysis
- **[How to Use](docs/how_to_use.md)** - Comprehensive usage guide
- **[Architecture](docs/architecture.md)** - System design
- **[Roadmap](TODO_COMPREHENSIVE.md)** - Development roadmap

## 🎯 Use Cases

- **Industrial Protocol Analysis** - Modbus, S7comm, DNP3, IEC 104
- **SCADA Security** - Understand proprietary protocols
- **IoT Research** - Analyze device communication
- **Network Forensics** - Reverse engineer unknown protocols
- **Protocol Documentation** - Generate specifications from traffic

## 📊 Pipeline Overview

```
PCAP Files → Extract Messages → Cluster Families → Infer Structure
    ↓
Detect Boundaries → Pair Requests/Responses → Label Semantics
    ↓
Build Protocol Model → LLM Refinement → Generate Reports
```

## 🔧 Requirements

- Python 3.10+
- TShark (Wireshark CLI)
- Dependencies: numpy, scikit-learn, hdbscan

## 📈 Performance

- **Runtime:** ~6 minutes for 200K messages
- **Accuracy:** 90%+ message type detection
- **Scalability:** Handles up to 200K messages by default

## 🛠️ Advanced Features

- **Enhanced Boundary Detection** - Reduces over-segmentation
- **Multi-Layer Detection** - Separates transport/application layers
- **Hybrid Clustering** - Neural + structural features
- **Ground Truth Evaluation** - Validates against known protocols

## 📝 Example Usage

```bash
# Basic analysis
python main.py pcaps/ --tshark-filter mbtcp

# With enhanced features
python main.py pcaps/ --tshark-filter mbtcp \
    --enhanced-boundaries \
    --enable-layer-detection

# With LLM refinement
python main.py pcaps/ --tshark-filter mbtcp \
    --llm-config LLM_config.json \
    --enhanced-boundaries

# With ground truth evaluation
python main.py pcaps/ --tshark-filter mbtcp \
    --ground-truth-json truth-files/modbus.json \
    --enhanced-boundaries
```

## 🗺️ Project Status

**Current Version:** 1.0.0

**Recent Improvements:**
- ✅ Enhanced boundary detection (A2)
- ✅ Multi-layer protocol detection (A6)
- ✅ Hybrid feature fusion (A1)
- ✅ Multi-stage LLM integration (A5)
- ✅ Improved documentation (C3)
- ✅ Logging and observability (C5)

**In Progress:**
- 🔄 Improved semantic labeling (A3)
- 🔄 Comprehensive unit tests (C1)

See [TODO_COMPREHENSIVE.md](TODO_COMPREHENSIVE.md) for full roadmap.

## 📄 License

MIT License - See LICENSE file for details.

---

**Get Started:** [Installation Guide](docs/getting_started.md) | [Usage Guide](docs/how_to_use.md) | [Architecture](docs/architecture.md)
