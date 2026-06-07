# Protocol Reverse Engineering

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A protocol-agnostic reverse engineering pipeline that analyzes binary protocol traffic from PCAP files and automatically infers protocol structure, message types, field boundaries, and semantic roles.

## Key Features

- **Protocol-Agnostic Analysis** - Works with any binary protocol without prior knowledge
- **Automatic Message Clustering** - Discovers message families using advanced clustering
- **Field Boundary Detection** - Infers field boundaries with enhanced anti-fragmentation
- **Semantic Labeling** - Identifies field labels
- **Request/Response Pairing** - Discovers protocol interactions and relations
- **LLM-Assisted Refinement** - LLM integration for improved analysis
- **Comprehensive Reports** - Generates Markdown and interactive HTML specifications
- **Ground Truth Evaluation** - Validates results against known protocol specifications

## Documentation

- **[Getting Started](docs/getting_started.md)** - Installation, prerequisites, first analysis, basic and advanced usage
- **[Architecture](docs/architecture.md)** - System design, components, data flow and technical details
- **[Contribution Guide](docs/contributing.md)** - How to contribute to this project

## Requirements

- Python 3.10+
- TShark (Wireshark CLI)
- Dependencies: numpy, scikit-learn, hdbscan, scapy, torch

## Project Structure

```
protocol_re/
├── src/protocol_re/          # Core library
│   └── config/               # Centralized thresholds (thresholds.py)
├── scripts/                  # Pipeline stages (01-19)
│   └── diagnostics/          # Standalone diagnostic/test scripts (20-24)
├── docs/                     # Documentation
├── logs/                     # Pipeline logs and per stage logs
├── data/                     # Intermediate artifacts
├── output/                   # Final reports
├── assets/                   # Static runtime resources
│   ├── pre_trained/          # Trained neural models
│   ├── prompts/              # Prompts used in LLM assisted stages
│   └── schema/               # protocol model, evaluation schema
├── config/                   # Config (e.g. llm_config.json)
├── tests/                    # test modules
├── truth_files/              # Real protocol specification, used for evaluation
└── main.py                   # Pipeline runner
```

## Supported Protocols

The pipeline is protocol-agnostic and has been tested with:
- Modbus TCP

## Performance

Typical runtime for 200K Modbus messages: ~6 minutes

Accuracy on Modbus TCP:
- Message type detection: 90%+ precision/recall
- Field boundary recall: 60%+
- Field boundary precision: 40%+

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please open an issue on GitHub.
