# Protocol Reverse Engineering

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A protocol-agnostic reverse engineering pipeline that analyzes binary protocol traffic from PCAP files and automatically infers protocol structure, message types, field boundaries, and semantic roles.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Analyze protocol traffic
python main.py pcaps/ --tshark-filter mbtcp --enhanced-boundaries

# View results
open output/protocol_report.html
```

## Key Features

- **Protocol-Agnostic Analysis** - Works with any binary protocol without prior knowledge
- **Automatic Message Clustering** - Discovers message families using advanced clustering
- **Field Boundary Detection** - Infers field boundaries with enhanced anti-fragmentation
- **Semantic Labeling** - Identifies opcodes, addresses, lengths, transaction IDs
- **Request/Response Pairing** - Discovers protocol interactions and relations
- **LLM-Assisted Refinement** - Optional LLM integration for improved analysis
- **Comprehensive Reports** - Generates Markdown and interactive HTML specifications
- **Ground Truth Evaluation** - Validates results against known protocol specifications

## Documentation

- **[Getting Started](docs/getting_started.md)** - Installation, first analysis, and basic usage
- **[Architecture](docs/architecture.md)** - System design and technical details
- **[Testing](docs/testing.md)** - Testing guide and diagnostic tools
- **[Documentation Guide](docs/Readme.md)** - How to build and contribute to docs

## Requirements

- Python 3.10+
- TShark (Wireshark CLI)
- Dependencies: numpy, scikit-learn, hdbscan, scapy, torch (optional)

## Basic Usage

```bash
# Analyze Modbus TCP traffic
python main.py pcaps/ --tshark-filter mbtcp

# With enhanced boundary detection (recommended)
python main.py pcaps/ --tshark-filter mbtcp --enhanced-boundaries

# With ground truth evaluation
python main.py pcaps/ --tshark-filter mbtcp --ground-truth-json truth-files/modbus.json
```

## Project Structure

```
protocol_re/
├── src/protocol_re/          # Core library
├── scripts/                  # Pipeline stages (01-24)
├── docs/                     # Documentation
├── data/                     # Intermediate artifacts
├── output/                   # Final reports
├── pcaps/                    # Input PCAP files
└── main.py                   # Pipeline runner
```

## Supported Protocols

The pipeline is protocol-agnostic and has been tested with:
- Modbus TCP, S7comm, DNP3, IEC 60870-5-104, and custom protocols

## Performance

Typical runtime for 200K messages: ~6 minutes

Accuracy on Modbus TCP:
- Message type detection: 90%+ precision/recall
- Field boundary recall: 88%+
- Field boundary precision: 65%+ (with enhanced mode)

## License

MIT License - See LICENSE file for details.

## Contact

For questions or issues, please open an issue on GitHub.
