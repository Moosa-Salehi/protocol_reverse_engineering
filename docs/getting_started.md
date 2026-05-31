# Getting Started

This guide will help you get up and running with the Protocol Reverse Engineering pipeline in minutes.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.10 or higher** installed
   - Check: `python --version` or `python3 --version`
   - Download: https://www.python.org/downloads/

2. **TShark (Wireshark CLI)** installed
   - Check: `tshark --version`
   - Download: https://www.wireshark.org/download.html
   - Note: Install Wireshark, which includes TShark

3. **PCAP files** containing protocol traffic you want to analyze

## Installation

### Step 1: Clone or Download the Repository

```bash
git clone <repository-url>
cd protocol_re
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate

# On Windows (PowerShell):
venv\Scripts\activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning and clustering
- `hdbscan` - Hierarchical density-based clustering
- `scapy` - Packet manipulation (optional extraction method)
- `torch` - PyTorch for neural features (optional)
- `colorama` - Colored terminal output

## Your First Analysis

### Example 1: Analyze Modbus TCP Traffic

If you have Modbus TCP PCAP files:

```bash
# Place your PCAP files in a directory
mkdir pcaps
cp /path/to/your/*.pcap pcaps/

# Run the pipeline
python main.py pcaps --tshark-filter mbtcp

# Wait 5-10 minutes for completion
```

**What happens:**
1. Extracts Modbus TCP payloads from PCAPs
2. Discovers message families (message types)
3. Infers field boundaries and structure
4. Detects request/response pairs
5. Generates protocol specification

**Output:**
- `output/protocol_report.md` - Human-readable specification
- `output/protocol_report.html` - Interactive HTML report
- `data/10_protocol_model.refined.json` - Machine-readable model

### Example 2: Analyze Unknown Protocol on TCP Port 502

If you don't know the protocol but know the port:

```bash
python main.py pcaps --extraction-method tcp --service-port 502
```

### Example 3: Analyze with Enhanced Boundary Detection

For better field boundary detection:

```bash
python main.py pcaps --tshark-filter mbtcp --enhanced-boundaries
```

**Recommended:** Always use `--enhanced-boundaries` for better results.

## Understanding the Output

### Protocol Report (Markdown)

Open `output/protocol_report.md` to see:

```markdown
# Protocol Specification

## Overview
- Total messages: 150,000
- Message families: 11
- Sessions analyzed: 45

## Message Families

### Family 0: Read Coils Request
- **Count:** 12,500 messages
- **Direction:** Client → Server
- **Length:** 12 bytes

**Fields:**
1. Transaction ID (offset 0, length 2) - uint16_be
2. Protocol ID (offset 2, length 2) - constant 0x0000
3. Length (offset 4, length 2) - uint16_be
4. Unit ID (offset 6, length 1) - uint8
5. Function Code (offset 7, length 1) - opcode (0x01)
6. Start Address (offset 8, length 2) - uint16_be
7. Quantity (offset 10, length 2) - uint16_be
...
```

### Protocol Report (HTML)

Open `output/protocol_report.html` in a browser to see:
- Interactive family explorer
- Field visualizations
- Request/response relation graphs
- Statistical evidence
- Evaluation metrics (if ground truth provided)

### Protocol Model (JSON)

`data/10_protocol_model.refined.json` contains machine-readable protocol structure:

```json
{
  "protocol_name": "Unknown Protocol",
  "families": [
    {
      "family_id": "0",
      "count": 12500,
      "direction": "client_to_server",
      "fields": [
        {
          "name": "field_0",
          "offset": 0,
          "length": 2,
          "type": "uint16_be",
          "semantic_role": "transaction_id"
        }
      ]
    }
  ]
}
```

## Common TShark Filters

Use these filters with `--tshark-filter`:

| Protocol | Filter | Description |
|----------|--------|-------------|
| Modbus TCP | `mbtcp` | Modbus TCP protocol |
| S7comm | `s7comm` | Siemens S7 communication |
| DNP3 | `dnp3` | DNP3 SCADA protocol |
| IEC 60870-5-104 | `iec104` | IEC 104 protocol |
| Custom TCP | `tcp.port == 502` | TCP port 502 |
| Custom UDP | `udp.port == 2222` | UDP port 2222 |
| IP address | `ip.addr == 192.168.1.10` | Specific IP address |
| Combined | `mbtcp and ip.addr == 192.168.1.10` | Multiple conditions |

**Find available filters:**
```bash
tshark -G protocols | grep -i modbus
```

## Next Steps

### 1. Improve Results with Enhanced Features

```bash
# Use enhanced boundary detection (recommended)
python main.py pcaps --tshark-filter mbtcp --enhanced-boundaries

# Enable multi-layer protocol detection (experimental)
python main.py pcaps --tshark-filter mbtcp --enable-layer-detection
```

### 2. Evaluate Against Ground Truth

If you know the protocol structure, create a ground truth file and evaluate:

```bash
python main.py pcaps --tshark-filter mbtcp \
    --ground-truth-json truth-files/modbus.json
```

See `truth-files/modbus.json` for ground truth format.

### 3. Use LLM Refinement

For better semantic labeling, use LLM-assisted refinement:

```bash
# Create LLM_config.json (see below)
# Set API key: export OPENAI_API_KEY=<your-key>

python main.py pcaps --tshark-filter mbtcp \
    --llm-config LLM_config.json
```

**LLM_config.json:**
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

### 4. Try Different Feature Modes

```bash
# Raw bytes (recommended, default)
python main.py pcaps --tshark-filter mbtcp --family-feature-mode raw_bytes

# Structural features
python main.py pcaps --tshark-filter mbtcp --family-feature-mode structural

# Hybrid (neural + structural, requires PyTorch and model)
python main.py pcaps --tshark-filter mbtcp \
    --family-feature-mode hybrid \
    --family-neural-model-path industrial_VAE.pth
```

## Troubleshooting

### Problem: "tshark: command not found"

**Solution:**
1. Install Wireshark from https://www.wireshark.org/download.html
2. Add TShark to PATH:
   - Windows: Add `C:\Program Files\Wireshark` to PATH
   - Linux: `sudo apt install tshark` or `sudo yum install wireshark`
   - Mac: `brew install wireshark`
3. Verify: `tshark --version`

### Problem: "No messages found in corpus"

**Possible causes:**
- Wrong TShark filter
- PCAP files don't contain matching traffic
- PCAP files are empty or corrupted

**Solutions:**
1. Test filter manually:
   ```bash
   tshark -r pcaps/capture.pcap -Y "mbtcp" -T fields -e data | head
   ```
2. Try TCP port extraction:
   ```bash
   python main.py pcaps --extraction-method tcp --service-port 502
   ```
3. Check PCAP contents:
   ```bash
   tshark -r pcaps/capture.pcap -c 10
   ```

### Problem: "ModuleNotFoundError: No module named 'protocol_re'"

**Solution:**
Set Python path before running individual scripts:
```bash
# Linux/Mac
export PYTHONPATH=src

# Windows PowerShell
$env:PYTHONPATH="src"

# Windows Command Prompt
set PYTHONPATH=src
```

Note: `main.py` sets this automatically; only needed for individual scripts.

### Problem: Pipeline is very slow

**Solutions:**
1. Reduce message limit:
   ```bash
   python main.py pcaps --tshark-filter mbtcp --max-messages 50000
   ```
2. Use raw_bytes mode (fastest):
   ```bash
   python main.py pcaps --tshark-filter mbtcp --family-feature-mode raw_bytes
   ```
3. Skip LLM stages:
   ```bash
   python main.py pcaps --tshark-filter mbtcp --llm-render-only
   ```

### Problem: Poor clustering results (too few families)

**Solutions:**
1. Use raw_bytes mode:
   ```bash
   python main.py pcaps --tshark-filter mbtcp --family-feature-mode raw_bytes
   ```
2. Diagnose the issue:
   ```bash
   python scripts/20_diagnose_neural_features.py data/01_messages.jsonl
   ```
3. Ensure diverse traffic in PCAPs (multiple message types)

## Understanding Pipeline Stages

The pipeline runs these stages automatically:

1. **Message Extraction** (Stage 03)
   - Extracts protocol payloads from PCAPs
   - Creates canonical message corpus
   - Output: `data/01_messages.jsonl`

2. **Family Discovery** (Stage 04)
   - Clusters similar messages into families
   - Uses HDBSCAN or DBSCAN clustering
   - Output: `data/02_family_assignments.json`

3. **Framing Inference** (Stage 05)
   - Detects headers and framing patterns
   - Identifies length fields, counters
   - Output: `data/04_framing.json`

4. **Feature Extraction** (Stage 06)
   - Extracts statistical features per family
   - Entropy, uniqueness, byte histograms
   - Output: `data/03_family_features.json`

5. **Boundary Detection** (Stage 07)
   - Infers field boundaries
   - Segments messages into fields
   - Output: `data/05_families.json`

6. **Request/Response Pairing** (Stage 08)
   - Pairs requests with responses
   - Analyzes session patterns
   - Output: `data/06_pairs.json`

7. **Discriminator Discovery** (Stage 09)
   - Identifies opcode/discriminator bytes
   - Detects message type indicators
   - Output: `data/07_keywords.json`

8. **Relation Inference** (Stage 10)
   - Discovers family-to-family relations
   - Detects echo fields, length relations
   - Output: `data/08_relations.json`

9. **Semantic Labeling** (Stage 11)
   - Assigns semantic roles to fields
   - Labels opcodes, addresses, lengths, etc.
   - Output: `data/09_semantics.json`

10. **Protocol Model Assembly** (Stage 12)
    - Combines all evidence into unified model
    - Output: `data/10_protocol_model.json`

11. **LLM Refinement** (Stages 14-15b, optional)
    - LLM-assisted semantic refinement
    - Evidence-gated patch validation
    - Output: `data/10_protocol_model.refined.json`

12. **Report Generation** (Stages 18-19)
    - Generates Markdown and HTML reports
    - Output: `output/protocol_report.md`, `output/protocol_report.html`

## Configuration Options

### Main Pipeline Options

```bash
python main.py <pcap-dir> [OPTIONS]

Required (one of):
  --tshark-filter FILTER        TShark display filter (e.g., mbtcp)
  --extraction-method tcp       Use TCP port extraction
  --use-existing-messages       Skip extraction, use existing data/01_messages.jsonl

Extraction:
  --max-messages N              Maximum messages to extract (default: 200000)
  --service-port PORT           TCP/UDP port for extraction (with --extraction-method tcp)

Clustering:
  --family-feature-mode MODE    Feature mode: raw_bytes, structural, neural, hybrid
  --sample-size N               Clustering sample size (default: 100000)
  --family-neural-model-path    Path to neural model (for neural/hybrid modes)

Boundaries:
  --enhanced-boundaries         Enable enhanced boundary detection (recommended)
  --boundary-max-fields N       Maximum fields per family (default: 15)

Layer Detection:
  --enable-layer-detection      Enable multi-layer protocol detection (experimental)
  --layer-min-confidence N      Minimum confidence for layer detection (default: 0.6)

LLM:
  --llm-config FILE             LLM configuration file
  --llm-render-only             Render prompts without calling API
  --llm-temperature N           LLM temperature (default: 0.1)
  --llm-max-tokens N            LLM max tokens (default: 4000)

Evaluation:
  --ground-truth-json FILE      Ground truth protocol for evaluation

Other:
  --collect                     Collect PCAPs from source tree first
```

## Learning Resources

- **[How to Use](how_to_use.md)** - Comprehensive usage guide
- **[Architecture](architecture.md)** - System design and components
- **[API Reference](api_reference.md)** - Module documentation
- **[Examples](examples.md)** - Protocol-specific examples
- **[TODO_COMPREHENSIVE.md](../TODO_COMPREHENSIVE.md)** - Roadmap and known issues

## Getting Help

1. Check the troubleshooting section above
2. Review the [How to Use](how_to_use.md) guide
3. Check `data/11_evaluation.json` for quality metrics
4. Run diagnostic tools (see [How to Use](how_to_use.md#diagnostic-tools))
5. Review intermediate outputs in `data/` directory

## What's Next?

Now that you've run your first analysis:

1. **Review the output reports** to understand what was discovered
2. **Try enhanced features** like `--enhanced-boundaries` for better results
3. **Create ground truth** for your protocol and evaluate accuracy
4. **Experiment with feature modes** to find what works best
5. **Use LLM refinement** for better semantic labeling

Happy protocol reverse engineering! 🔍
