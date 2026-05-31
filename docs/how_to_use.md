# How to Use

This guide covers common usage patterns for the Protocol Reverse Engineering pipeline.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Feature Modes](#feature-modes)
- [LLM Integration](#llm-integration)
- [Ground Truth Evaluation](#ground-truth-evaluation)
- [Diagnostic Tools](#diagnostic-tools)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

1. **Python 3.10+** installed
2. **TShark** (Wireshark CLI) installed and in PATH
3. PCAP/PCAPNG files containing protocol traffic

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd protocol_re

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set Python path (for step-by-step execution)
export PYTHONPATH=src  # On Windows PowerShell: $env:PYTHONPATH="src"
```

### Run the Pipeline

```bash
# Basic usage - analyze PCAP directory
python main.py pcaps/ --tshark-filter mbtcp

# With ground truth evaluation
python main.py pcaps/ --tshark-filter mbtcp --ground-truth-json truth-files/modbus.json

# Use existing messages (skip extraction)
python main.py --use-existing-messages
```

## Basic Usage

### 1. Prepare PCAP Files

Place your PCAP/PCAPNG files in a directory:

```
pcaps/
├── capture1.pcap
├── capture2.pcapng
└── session3.pcap
```

### 2. Run the Pipeline

```bash
python main.py pcaps/ --tshark-filter <filter>
```

**Common TShark filters:**
- `mbtcp` - Modbus TCP
- `s7comm` - Siemens S7
- `udp.port == 502` - UDP port 502
- `tcp.port == 102` - TCP port 102

### 3. View Results

After completion, check:
- `output/protocol_report.md` - Human-readable specification
- `output/protocol_report.html` - Interactive HTML report
- `data/10_protocol_model.refined.json` - Machine-readable protocol model

## Advanced Usage

### Collection and Deduplication

Collect PCAPs from a source tree and remove duplicates:

```bash
python main.py source_files/ --collect --tshark-filter mbtcp
```

This will:
1. Collect all PCAPs from `source_files/` into `pcaps/`
2. Remove duplicate captures
3. Run the full pipeline

### TCP Port Extraction (Alternative to TShark)

Use Scapy-based TCP port extraction instead of TShark:

```bash
python main.py pcaps/ --extraction-method tcp --service-port 502
```

**When to use:**
- TShark filter is not available for your protocol
- You want to extract by TCP/UDP port only
- TShark is not installed

### Enhanced Boundary Detection

Reduce over-segmentation (recommended):

```bash
python main.py pcaps/ --tshark-filter mbtcp --enhanced-boundaries
```

**Options:**
- `--enhanced-boundaries` - Enable enhanced mode
- `--boundary-max-fields 12` - Limit maximum fields per family (default: 15)
- `--enable-merging` - Enable multi-pass segment merging

**Impact:**
- Reduces false positive boundaries by ~50%
- Eliminates excessive 1-byte fields
- Improves boundary precision from 38% to 65-70%

### Multi-Layer Protocol Detection

Detect layered protocols (transport + application):

```bash
python main.py pcaps/ --tshark-filter mbtcp --enable-layer-detection
```

**Options:**
- `--enable-layer-detection` - Enable layer detection (experimental)
- `--layer-min-confidence 0.7` - Minimum confidence threshold

**Use cases:**
- Protocols with stable outer headers (Modbus TCP, S7comm)
- Transport framing + application payload
- Protocol tunneling scenarios

### Message Limits

Control the number of messages processed:

```bash
python main.py pcaps/ --tshark-filter mbtcp --max-messages 50000
```

**Default:** 200,000 messages

**When to adjust:**
- Small captures: reduce for faster processing
- Large captures: increase for better coverage
- Memory constraints: reduce to limit memory usage

## Feature Modes

### Raw Bytes Mode (Recommended)

Default mode using padded byte vectors:

```bash
python main.py pcaps/ --tshark-filter mbtcp --family-feature-mode raw_bytes
```

**Pros:**
- 90%+ accuracy on test protocols
- Fast and deterministic
- No external dependencies

**Use when:**
- You want reliable, production-ready results
- You don't have a trained neural model
- Protocol has clear structural patterns

### Structural Mode

Use symbolic protocol features:

```bash
python main.py pcaps/ --tshark-filter mbtcp --family-feature-mode structural
```

**Pros:**
- Protocol-agnostic feature extraction
- Interpretable features
- No ML dependencies

**Use when:**
- You want to understand feature importance
- Raw bytes mode is not working well
- You need explainable clustering

### Neural Mode (Experimental)

Use VAE latent vectors:

```bash
python main.py pcaps/ --tshark-filter mbtcp \
    --family-feature-mode neural \
    --family-neural-model-path industrial_VAE.pth
```

**Pros:**
- Can capture complex patterns
- Learned representations

**Cons:**
- May produce poor clustering (collapsed latent space)
- Requires PyTorch and trained model
- Currently not recommended for production

**Use when:**
- You have a well-trained VAE model
- Protocol has complex, non-obvious patterns
- You're experimenting with ML approaches

### Hybrid Mode

Combine neural and structural features:

```bash
# Adaptive fusion (recommended)
python main.py pcaps/ --tshark-filter mbtcp \
    --family-feature-mode hybrid \
    --fusion-method adaptive \
    --family-neural-model-path industrial_VAE.pth

# Learned fusion with MLP
python main.py pcaps/ --tshark-filter mbtcp \
    --family-feature-mode hybrid \
    --fusion-method learned \
    --family-neural-model-path industrial_VAE.pth

# Fixed weights
python main.py pcaps/ --tshark-filter mbtcp \
    --family-feature-mode hybrid \
    --fusion-method fixed \
    --fusion-neural-weight 0.3 \
    --fusion-structural-weight 0.7 \
    --family-neural-model-path industrial_VAE.pth
```

**Fusion methods:**
- `adaptive` - Quality-based automatic weighting (default)
- `learned` - MLP-based feature importance learning
- `fixed` - Manual weight specification
- `concat` - Simple concatenation

**Features:**
- Automatic neural collapse detection
- Fallback to structural features when neural fails
- Latent vector caching for speed

## LLM Integration

### Setup

1. Create `LLM_config.json`:

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

2. Set API key:

```bash
# Linux/Mac
export OPENAI_API_KEY=<your-api-key>

# Windows PowerShell
$env:OPENAI_API_KEY = "<your-api-key>"
```

### Run with LLM Refinement

```bash
python main.py pcaps/ --tshark-filter mbtcp --llm-config LLM_config.json
```

### LLM Options

```bash
# Custom prompt template
python main.py pcaps/ --tshark-filter mbtcp \
    --llm-config LLM_config.json \
    --llm-template custom_prompt.md

# Render prompt only (no API call)
python main.py pcaps/ --tshark-filter mbtcp --llm-render-only

# Adjust LLM parameters
python main.py pcaps/ --tshark-filter mbtcp \
    --llm-config LLM_config.json \
    --llm-temperature 0.2 \
    --llm-max-tokens 8000
```

### Stage-Specific LLM Refinement

Run individual LLM refinement stages:

```bash
# Boundary refinement
python scripts/07b_refine_boundaries_llm.py \
    data/05_families.json \
    data/05_families.refined.json \
    --config LLM_config.json

# Semantic labeling
python scripts/11b_label_semantics_llm.py \
    data/05_families.json \
    data/09_semantics.json \
    data/09_semantics.llm.json \
    --config LLM_config.json

# Relation validation
python scripts/10b_validate_relations_llm.py \
    data/08_relations.json \
    data/08_relations.validated.json \
    --config LLM_config.json
```

## Ground Truth Evaluation

### Prepare Ground Truth

Create a ground truth JSON file (see `truth-files/modbus.json` for example):

```json
{
  "protocol_name": "Modbus TCP",
  "families": [
    {
      "family_id": "read_coils",
      "fields": [
        {"name": "function_code", "offset": 0, "length": 1, "semantic_role": "opcode"},
        {"name": "start_address", "offset": 1, "length": 2, "semantic_role": "address"},
        {"name": "quantity", "offset": 3, "length": 2, "semantic_role": "quantity"}
      ]
    }
  ]
}
```

### Run with Evaluation

```bash
python main.py pcaps/ --tshark-filter mbtcp \
    --ground-truth-json truth-files/modbus.json
```

### View Evaluation Results

Check `data/15_evaluation_result.json` for detailed metrics:
- Message type matching (precision/recall)
- Field boundary detection (precision/recall)
- Semantic labeling accuracy
- Relation detection (precision/recall)
- Overall score

## Diagnostic Tools

### Diagnose Neural Features

Analyze neural feature quality and detect collapsed latent spaces:

```bash
python scripts/20_diagnose_neural_features.py data/01_messages.jsonl \
    --sample-size 5000 \
    --model-path pre_trained/industrial_VAE.pth \
    --latent-cache data/latent_cache.json
```

**Output:**
- Latent space variance analysis
- Separation metrics
- Comparison with structural features
- Recommendations

### Test Enhanced Neural Features

Compare original vs enhanced neural features:

```bash
python scripts/21_test_enhanced_neural.py data/01_messages.jsonl \
    --sample-size 5000 \
    --model-path pre_trained/industrial_VAE.pth
```

### Test Boundary Detection

Test boundary detection with different thresholds:

```bash
python scripts/22_test_boundary_detection.py data/01_messages.jsonl \
    --assignments-json data/02_family_assignments.json \
    --features-json data/03_family_features.json
```

### Test Learned Fusion

Test hybrid feature fusion methods:

```bash
python scripts/23_test_learned_fusion.py data/01_messages.jsonl \
    --model-path pre_trained/industrial_VAE.pth
```

### Test Boundary Refinement

Compute boundary quality metrics and test LLM refinement:

```bash
python scripts/24_test_boundary_refinement.py data/05_families.json \
    --messages-json data/01_messages.jsonl \
    --assignments-json data/02_family_assignments.json
```

## Step-by-Step Execution

For debugging or custom workflows, run stages individually:

```bash
# Set Python path
export PYTHONPATH=src  # Windows: $env:PYTHONPATH="src"

# Stage 03: Extract messages
python scripts/03_extract_messages.py pcaps data/01_messages.jsonl \
    --extraction-method tshark \
    --tshark-filter mbtcp \
    --max-messages 200000

# Stage 04: Discover families
python scripts/04_discover_families.py data/01_messages.jsonl \
    data/02_family_assignments.json \
    --sample-size 100000 \
    --feature-mode raw_bytes

# Stage 05: Infer framing
python scripts/05_infer_framing.py data/01_messages.jsonl \
    data/02_family_assignments.json \
    data/04_framing.json

# Stage 06: Extract features
python scripts/06_extract_features.py data/01_messages.jsonl \
    data/03_family_features.json \
    --assignments-json data/02_family_assignments.json

# Stage 07: Infer boundaries
python scripts/07_infer_boundaries.py data/01_messages.jsonl \
    data/05_families.json \
    --assignments-json data/02_family_assignments.json \
    --features-json data/03_family_features.json \
    --framing-json data/04_framing.json \
    --enhanced \
    --max-fields 15

# Stage 08: Pair requests/responses
python scripts/08_pair_requests_responses.py data/01_messages.jsonl \
    data/06_pairs.json \
    --assignments-json data/02_family_assignments.json

# Stage 09: Infer discriminators
python scripts/09_infer_keywords.py data/01_messages.jsonl \
    data/07_keywords.json \
    --assignments-json data/02_family_assignments.json \
    --features-json data/03_family_features.json \
    --framing-json data/04_framing.json

# Stage 10: Infer relations
python scripts/10_infer_relations.py data/01_messages.jsonl \
    data/02_family_assignments.json \
    data/06_pairs.json \
    data/08_relations.json

# Stage 11: Infer semantics
python scripts/11_infer_semantics.py data/05_families.json \
    data/08_relations.json \
    data/09_semantics.json

# Stage 12: Build protocol model
python scripts/12_build_protocol_model.py data/05_families.json \
    data/10_protocol_model.json \
    --features-json data/03_family_features.json \
    --keywords-json data/07_keywords.json \
    --relations-json data/08_relations.json \
    --semantics-json data/09_semantics.json \
    --framing-json data/04_framing.json

# Stage 13: Evaluate pipeline
python scripts/13_evaluate_pipeline.py data/01_messages.jsonl \
    data/02_family_assignments.json \
    data/05_families.json \
    data/06_pairs.json \
    data/08_relations.json \
    data/11_evaluation.json \
    --semantics-json data/09_semantics.json

# Stage 14: Export LLM evidence
python scripts/14_export_llm_evidence.py data/10_protocol_model.json \
    data/12_llm_evidence.json \
    --evaluation-json data/11_evaluation.json

# Stage 15: Analyze with LLM
python scripts/15_analyze_with_llm.py data/12_llm_evidence.json \
    data/13_llm_analysis.json \
    --config LLM_config.json \
    --prompt-out data/13_llm_prompt.md

# Stage 15b: Apply LLM refinement
python scripts/15b_apply_llm_refinement.py data/10_protocol_model.json \
    data/13_llm_analysis.json \
    data/10_protocol_model.refined.json \
    --evidence-json data/12_llm_evidence.json \
    --schema-json schema/protocol_model.schema.json \
    --patches-out data/13_llm_patches.json \
    --validation-out data/13_llm_patch_validation.json

# Stage 16: Prepare evaluation data
python scripts/16_prepare_evaluation_data.py data/10_protocol_model.json \
    data/11_evaluation.json \
    data/13_llm_analysis.json \
    data/14_evaluation_model_data.json \
    --refined-protocol-model-json data/10_protocol_model.refined.json \
    --patch-validation-json data/13_llm_patch_validation.json

# Stage 17: Evaluate against ground truth
python scripts/17_evaluate_protocol_spec.py data/14_evaluation_model_data.json \
    truth-files/modbus.json \
    data/15_evaluation_result.json

# Stage 18: Export Markdown
python scripts/18_export_markdown.py data/10_protocol_model.refined.json \
    output/protocol_report.md \
    --evaluation-json data/11_evaluation.json \
    --llm-analysis-json data/13_llm_analysis.json \
    --final-evaluation-json data/15_evaluation_result.json

# Stage 19: Export HTML
python scripts/19_export_html.py data/10_protocol_model.refined.json \
    output/protocol_report.html \
    --evaluation-json data/11_evaluation.json \
    --llm-analysis-json data/13_llm_analysis.json \
    --final-evaluation-json data/15_evaluation_result.json
```

## Troubleshooting

### TShark Not Found

**Error:** `tshark: command not found`

**Solution:**
1. Install Wireshark (includes TShark)
2. Add TShark to PATH
3. Verify: `tshark --version`

### No Messages Extracted

**Error:** `No messages found in corpus`

**Possible causes:**
- Incorrect TShark filter
- PCAP files don't contain matching traffic
- Extraction method mismatch

**Solutions:**
- Verify filter: `tshark -r capture.pcap -Y "mbtcp" -T fields -e data`
- Try alternative extraction: `--extraction-method tcp --service-port 502`
- Check PCAP contents: `tshark -r capture.pcap`

### Poor Clustering Results

**Symptoms:**
- Too few families (e.g., 2 instead of 11)
- All messages in one cluster
- Low silhouette score

**Solutions:**
1. Try different feature mode: `--family-feature-mode raw_bytes`
2. Diagnose neural features: `python scripts/20_diagnose_neural_features.py`
3. Adjust clustering parameters: `--sample-size 50000`
4. Check message diversity: ensure captures contain varied traffic

### Over-Segmentation

**Symptoms:**
- Too many 1-byte fields
- Low boundary precision (< 40%)
- Excessive field count (> 20 fields per family)

**Solutions:**
1. Enable enhanced boundaries: `--enhanced-boundaries`
2. Reduce field limit: `--boundary-max-fields 12`
3. Use LLM refinement: `--llm-config LLM_config.json`

### LLM API Errors

**Error:** `OpenAI API error: 401 Unauthorized`

**Solution:**
- Check API key: `echo $OPENAI_API_KEY`
- Verify config: `cat LLM_config.json`
- Test API: `curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models`

**Error:** `Timeout waiting for LLM response`

**Solution:**
- Increase timeout: `--llm-timeout 300`
- Reduce evidence size: `--family-limit 10`
- Use render-only mode: `--llm-render-only`

### Memory Issues

**Error:** `MemoryError` or system slowdown

**Solutions:**
1. Reduce message limit: `--max-messages 50000`
2. Reduce clustering sample: `--sample-size 10000`
3. Close other applications
4. Use 64-bit Python

### Slow Performance

**Symptoms:**
- Pipeline takes > 15 minutes for 200K messages
- Stages hang or appear frozen

**Solutions:**
1. Check TShark performance: time the extraction stage
2. Reduce sample size: `--sample-size 50000`
3. Skip LLM stages: `--llm-render-only`
4. Use raw_bytes mode (fastest): `--family-feature-mode raw_bytes`

## Best Practices

### 1. Start Simple

Begin with default settings:
```bash
python main.py pcaps/ --tshark-filter mbtcp
```

### 2. Use Enhanced Boundaries

Always enable for better results:
```bash
python main.py pcaps/ --tshark-filter mbtcp --enhanced-boundaries
```

### 3. Prefer Raw Bytes Mode

Use `raw_bytes` for production:
```bash
python main.py pcaps/ --tshark-filter mbtcp --family-feature-mode raw_bytes
```

### 4. Validate with Ground Truth

Create ground truth for your protocol and evaluate:
```bash
python main.py pcaps/ --tshark-filter mbtcp --ground-truth-json truth.json
```

### 5. Use LLM Refinement Selectively

LLM refinement helps but costs tokens:
- Use for final analysis
- Use `--llm-render-only` for testing
- Review patches before accepting

### 6. Save Intermediate Results

Keep `data/` directory for debugging and re-runs:
```bash
# Re-run from stage 10 onwards
python main.py --use-existing-messages
```

### 7. Monitor Quality Metrics

Check `data/11_evaluation.json` for quality signals:
- Silhouette score > 0.3 (good clustering)
- Coverage > 90% (good family assignment)
- Boundary confidence > 0.6 (good boundaries)

## Next Steps

- Read [Architecture](architecture.md) for system design details
- Check [API Reference](api_reference.md) for module documentation
- See [Examples](examples.md) for protocol-specific guides
- Review [TODO_COMPREHENSIVE.md](../TODO_COMPREHENSIVE.md) for roadmap
