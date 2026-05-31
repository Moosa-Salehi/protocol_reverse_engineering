# Testing Guide

This guide covers testing practices, tools, and evaluation methods for the Protocol Reverse Engineering pipeline.

## Overview

The project uses a combination of:
- **Unit tests** - Test individual functions and modules
- **Integration tests** - Test pipeline stages end-to-end
- **Diagnostic tools** - Analyze feature quality and performance
- **Ground truth evaluation** - Validate against known protocols

## Test Structure

```
tests/
├── fixtures/              # Test data and fixtures
│   ├── pcaps/            # Sample PCAP files
│   ├── messages/         # Sample message corpora
│   └── ground_truth/     # Known protocol specifications
├── unit/                 # Unit tests
│   ├── test_clustering.py
│   ├── test_boundaries.py
│   ├── test_semantics.py
│   └── test_relations.py
├── integration/          # Integration tests
│   ├── test_pipeline.py
│   └── test_stages.py
└── conftest.py          # Pytest configuration and fixtures
```

## Running Tests

### Setup

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Set Python path
export PYTHONPATH=src  # Windows: $env:PYTHONPATH="src"
```

### Run All Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=src/protocol_re --cov-report=html tests/

# Run specific test file
pytest tests/unit/test_clustering.py

# Run specific test function
pytest tests/unit/test_clustering.py::test_raw_bytes_clustering
```

### Test Markers

```bash
# Run only unit tests
pytest -m unit tests/

# Run only integration tests
pytest -m integration tests/

# Skip slow tests
pytest -m "not slow" tests/
```

## Unit Tests

### Clustering Tests

Test message family discovery:

```python
# tests/unit/test_clustering.py
import pytest
from protocol_re.clustering.feature_extraction import extract_raw_bytes_features

def test_raw_bytes_feature_extraction():
    """Test raw bytes feature extraction."""
    messages = [
        {"payload_hex": "010300000001"},
        {"payload_hex": "010300000002"},
    ]
    features = extract_raw_bytes_features(messages)
    assert features.shape[0] == 2
    assert features.shape[1] > 0

def test_clustering_with_hdbscan():
    """Test HDBSCAN clustering."""
    # Test implementation
    pass
```

### Boundary Detection Tests

Test field boundary inference:

```python
# tests/unit/test_boundaries.py
def test_boundary_detection_basic():
    """Test basic boundary detection."""
    messages = create_test_messages()
    boundaries = detect_boundaries(messages)
    assert len(boundaries) > 0

def test_enhanced_boundary_detection():
    """Test enhanced mode reduces over-segmentation."""
    messages = create_test_messages()
    basic_boundaries = detect_boundaries(messages, enhanced=False)
    enhanced_boundaries = detect_boundaries(messages, enhanced=True)
    assert len(enhanced_boundaries) < len(basic_boundaries)
```

### Semantic Labeling Tests

Test semantic role assignment:

```python
# tests/unit/test_semantics.py
def test_opcode_detection():
    """Test opcode field detection."""
    fields = create_test_fields()
    semantics = infer_semantics(fields)
    opcode_fields = [f for f in semantics if f.role == "opcode"]
    assert len(opcode_fields) > 0

def test_length_field_detection():
    """Test length field detection."""
    # Test implementation
    pass
```

### Relation Tests

Test request/response pairing:

```python
# tests/unit/test_relations.py
def test_request_response_pairing():
    """Test request/response pairing."""
    messages = create_test_session()
    pairs = pair_requests_responses(messages)
    assert len(pairs) > 0

def test_echo_field_detection():
    """Test echo field detection."""
    # Test implementation
    pass
```

## Integration Tests

### End-to-End Pipeline Test

```python
# tests/integration/test_pipeline.py
def test_full_pipeline_modbus():
    """Test full pipeline on Modbus TCP."""
    # Run pipeline
    result = run_pipeline(
        pcap_dir="tests/fixtures/pcaps/modbus",
        tshark_filter="mbtcp"
    )
    
    # Verify outputs
    assert result.families_count > 5
    assert result.overall_score > 0.4
    assert os.path.exists("output/protocol_report.md")
```

### Stage-by-Stage Tests

```python
def test_extraction_stage():
    """Test message extraction stage."""
    messages = extract_messages(
        pcap_dir="tests/fixtures/pcaps/modbus",
        tshark_filter="mbtcp"
    )
    assert len(messages) > 0

def test_clustering_stage():
    """Test clustering stage."""
    messages = load_test_messages()
    assignments = discover_families(messages)
    assert len(set(assignments.values())) > 1
```

## Ground Truth Evaluation

### Creating Ground Truth

Create a ground truth JSON file:

```json
{
  "protocol_name": "Modbus TCP",
  "families": [
    {
      "family_id": "read_coils_request",
      "message_type": "read_coils",
      "direction": "request",
      "fields": [
        {
          "name": "transaction_id",
          "offset": 0,
          "length": 2,
          "type": "uint16_be",
          "semantic_role": "transaction_id"
        },
        {
          "name": "protocol_id",
          "offset": 2,
          "length": 2,
          "type": "uint16_be",
          "semantic_role": "constant"
        },
        {
          "name": "length",
          "offset": 4,
          "length": 2,
          "type": "uint16_be",
          "semantic_role": "length"
        },
        {
          "name": "unit_id",
          "offset": 6,
          "length": 1,
          "type": "uint8",
          "semantic_role": "address"
        },
        {
          "name": "function_code",
          "offset": 7,
          "length": 1,
          "type": "uint8",
          "semantic_role": "opcode"
        },
        {
          "name": "start_address",
          "offset": 8,
          "length": 2,
          "type": "uint16_be",
          "semantic_role": "address"
        },
        {
          "name": "quantity",
          "offset": 10,
          "length": 2,
          "type": "uint16_be",
          "semantic_role": "quantity"
        }
      ]
    }
  ],
  "relations": [
    {
      "request_family": "read_coils_request",
      "response_family": "read_coils_response",
      "relation_type": "request_response"
    }
  ]
}
```

### Running Evaluation

```bash
python main.py pcaps/ --tshark-filter mbtcp \
    --ground-truth-json truth-files/modbus.json
```

### Evaluation Metrics

Check `data/15_evaluation_result.json`:

```json
{
  "overall_score": 0.75,
  "message_type_matching": {
    "precision": 0.91,
    "recall": 0.91,
    "f1": 0.91
  },
  "field_boundaries": {
    "precision": 0.65,
    "recall": 0.89,
    "f1": 0.75
  },
  "semantic_labels": {
    "accuracy": 0.45
  },
  "relations": {
    "precision": 0.70,
    "recall": 1.0,
    "f1": 0.82
  }
}
```

## Test Fixtures

### Creating Test Messages

```python
# tests/fixtures/messages.py
def create_test_messages():
    """Create sample messages for testing."""
    return [
        {
            "payload_hex": "000100000006010100000001",
            "length": 12,
            "direction": "client_to_server",
            "session_key": "192.168.1.1:502-192.168.1.10:12345"
        },
        # More messages...
    ]
```

### Creating Test Families

```python
def create_test_families():
    """Create sample family data for testing."""
    return {
        "families": [
            {
                "family_id": "0",
                "count": 100,
                "fields": [
                    {"offset": 0, "length": 2},
                    {"offset": 2, "length": 2},
                ]
            }
        ]
    }
```

## Performance Testing

### Benchmarking

```python
import time

def test_clustering_performance():
    """Test clustering performance."""
    messages = load_large_corpus(100000)
    
    start = time.time()
    assignments = discover_families(messages)
    duration = time.time() - start
    
    assert duration < 60  # Should complete in under 60 seconds
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python -m memory_profiler scripts/04_discover_families.py \
    data/01_messages.jsonl data/02_family_assignments.json
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        export PYTHONPATH=src
        pytest --cov=src/protocol_re tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Coverage

### Measuring Coverage

```bash
# Run with coverage
pytest --cov=src/protocol_re --cov-report=html tests/

# View HTML report
open htmlcov/index.html
```

### Coverage Goals

- **Overall:** 80%+ coverage
- **Core modules:** 90%+ coverage
- **Critical paths:** 100% coverage

## Best Practices

1. **Write tests first** - TDD approach when possible
2. **Test edge cases** - Empty inputs, large inputs, invalid data
3. **Use fixtures** - Reuse test data and setup
4. **Mock external dependencies** - TShark, LLM APIs, file I/O
5. **Keep tests fast** - Unit tests < 1s, integration tests < 10s
6. **Test one thing** - Each test should verify one behavior
7. **Use descriptive names** - Test names should explain what is tested
8. **Document test intent** - Add docstrings explaining the test

## Debugging Tests

### Running with Debug Output

```bash
# Verbose output
pytest -v tests/

# Show print statements
pytest -s tests/

# Stop on first failure
pytest -x tests/

# Drop into debugger on failure
pytest --pdb tests/
```

### Using pytest-mock

```python
def test_with_mock(mocker):
    """Test with mocked dependencies."""
    mock_tshark = mocker.patch('subprocess.run')
    mock_tshark.return_value.stdout = "test_output"
    
    result = extract_messages("test.pcap")
    assert mock_tshark.called
```

## Known Issues

See [TODO_COMPREHENSIVE.md](../TODO_COMPREHENSIVE.md) for known issues and planned improvements:

- Neural mode produces poor clustering (use raw_bytes)
- Over-segmentation in boundary detection (use --enhanced-boundaries)
- Semantic labeling needs improvement (A3 in progress)

## Contributing Tests

When contributing:
1. Add tests for new features
2. Update existing tests if behavior changes
3. Ensure all tests pass before submitting PR
4. Aim for 80%+ coverage on new code
5. Document test fixtures and helpers

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Python testing best practices](https://docs.python-guide.org/writing/tests/)
