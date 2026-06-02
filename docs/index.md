# Protocol Reverse Engineering Documentation

Welcome to the Protocol Reverse Engineering pipeline documentation.

## Overview

This pipeline analyzes binary protocol traffic from PCAP files and automatically infers protocol structure, message types, field boundaries, and semantic roles without requiring prior protocol knowledge.

## Documentation

### Getting Started
- **[Getting Started Guide](getting_started.md)** - Installation, prerequisites, first analysis, basic and advanced usage

### Technical Documentation
- **[Architecture](architecture.md)** - System design, components, and data flow

### Contributing
- **[Contribution Guide](contributing.md)** - How to contribute to this project

## Quick Links

- [Installation](getting_started.md#installation)
- [First Analysis](getting_started.md#your-first-analysis)
- [Usage Guide](getting_started.md#usage-guide)
- [Troubleshooting](getting_started.md#troubleshooting)
- [Pipeline Architecture](architecture.md#pipeline-architecture)
- [Feature Modes](getting_started.md#feature-modes)
- [LLM Integration](getting_started.md#llm-integration)
- [Ground Truth Evaluation](getting_started.md#ground-truth-evaluation)

## Building Documentation

This project uses [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/).

### Install MkDocs

```bash
pip install mkdocs mkdocs-material mkdocstrings mkdocstrings-python
``` 

### Serve Locally

```bash
# From project root
mkdocs serve

# Open browser to http://127.0.0.1:8000
``` 

### Build Static Site

```bash
# From project root
mkdocs build

# Output in site/ directory
```

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

## Support

For issues or questions, please refer to the [Troubleshooting](getting_started.md#troubleshooting) section or open an issue on GitHub.
