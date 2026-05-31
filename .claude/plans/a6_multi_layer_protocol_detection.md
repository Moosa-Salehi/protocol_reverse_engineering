# Implementation Plan: A6. Multi-Layer Protocol Detection

## Overview
Implement protocol-agnostic multi-layer detection to separate transport headers from application payloads. Many real-world protocols (Modbus TCP, S7comm, etc.) have stable outer headers with transaction IDs and length fields, followed by variable application payloads. Currently, the pipeline treats messages as flat, which introduces noise in clustering and mixes transport/application fields in boundary detection.

## Problem Analysis
- **Current behavior**: Clustering uses full message including transport headers
- **Issue**: Transport headers (transaction IDs, length fields) add noise to clustering
- **Impact**: Families mix transport and application logic, boundaries are less precise
- **Goal**: Detect layer boundaries automatically, cluster on inner protocol only

## Architecture Design

### 1. Layer Detection Module (`src/protocol_re/inference/layer_detection.py`)
**Purpose**: Protocol-agnostic detection of layered structure within messages

**Key Functions**:
- `detect_layer_boundary(messages)` - Find split between outer header and inner payload
- `analyze_layer_structure(family_messages)` - Per-family layer analysis
- Uses existing framing evidence (stable prefixes, length fields) to identify layers

**Detection Strategy**:
1. Leverage existing framing analysis (stage 05) which already detects:
   - Stable prefixes (constant bytes)
   - Length fields pointing to payload regions
   - Header/body boundaries
2. Add layer-specific heuristics:
   - Length field pointing past its own position = likely transport header
   - Stable prefix + variable suffix = potential layer boundary
   - Transaction/counter fields in header region = transport layer marker
3. Confidence scoring based on:
   - Strength of framing evidence
   - Consistency across family messages
   - Presence of multiple layer indicators

### 2. Integration Points

#### Stage 04 - Family Discovery (Clustering)
**File**: `scripts/04_discover_families.py`, `src/protocol_re/clustering/family_discovery.py`
- **Before clustering**: Detect layers, extract inner protocol only
- **Fallback**: If no clear layer boundary, use full message (current behavior)
- **Metadata**: Record layer information in assignments JSON

#### Stage 05 - Framing Inference
**File**: `scripts/05_infer_framing.py`, `src/protocol_re/inference/framing.py`
- **Enhancement**: Add layer boundary detection to framing output
- **Output**: Mark field regions as "transport_layer" vs "application_layer"
- **Backward compatible**: Existing framing output structure preserved

#### Stage 06 - Feature Extraction
**File**: `scripts/06_extract_features.py`, `src/protocol_re/features/extraction.py`
- Extract features from inner protocol only (if layer detected)
- Keep outer header stats separately for pairing/relation analysis

#### Stage 07 - Boundary Detection
**File**: `scripts/07_infer_boundaries.py`, `src/protocol_re/inference/boundary_detection.py`
- Apply boundary detection to inner protocol only
- Outer header fields marked separately as transport layer

#### Stage 12 - Protocol Model
**File**: `scripts/12_build_protocol_model.py`
- Add layer metadata to families
- Mark fields with layer attribution ("transport" vs "application")

### 3. Schema Extensions

**Protocol Model Schema** (`schema/protocol_model.schema.json`):
```json
{
  "family": {
    "layer_info": {
      "has_layers": boolean,
      "outer_header_end": integer,
      "inner_payload_start": integer,
      "confidence": number,
      "evidence": object
    }
  },
  "field_hypothesis": {
    "layer": "transport" | "application" | "unknown"
  }
}
```

**Framing Output** (`data/04_framing.json`):
```json
{
  "families": {
    "family_X": {
      "layer_boundary": {
        "detected": boolean,
        "boundary_offset": integer,
        "confidence": number,
        "evidence": {...}
      }
    }
  }
}
```

## Implementation Steps

### Step 1: Create Layer Detection Module
- Create `src/protocol_re/inference/layer_detection.py`
- Implement `detect_layer_boundary()` using framing evidence
- Implement `analyze_family_layers()` for per-family analysis
- Add confidence scoring logic

### Step 2: Enhance Framing Inference (Stage 05)
- Modify `src/protocol_re/inference/framing.py`:
  - Add layer boundary detection to `infer_family_framing()`
  - Use existing field regions (length, counter, constant) as layer indicators
  - Add layer boundary to output structure
- Update `scripts/05_infer_framing.py` to include layer info in output

### Step 3: Update Family Discovery (Stage 04)
- Modify `scripts/04_discover_families.py`:
  - Add `--enable-layer-detection` flag (default: False for backward compatibility)
  - Load framing JSON if layer detection enabled
  - Extract inner protocol before clustering
- Modify `src/protocol_re/clustering/family_discovery.py`:
  - Add `layer_aware_clustering()` function
  - Strip outer headers before vectorization
  - Record layer info in metadata

### Step 4: Update Feature Extraction (Stage 06)
- Modify `src/protocol_re/features/extraction.py`:
  - Extract features from inner protocol when layers detected
  - Keep separate stats for outer header (for pairing)

### Step 5: Update Boundary Detection (Stage 07)
- Modify `src/protocol_re/inference/boundary_detection.py`:
  - Apply boundary detection to inner protocol only
  - Mark outer header fields with layer="transport"

### Step 6: Update Protocol Model Builder (Stage 12)
- Add layer metadata to families
- Add layer attribution to fields
- Ensure schema validation passes

### Step 7: Update Main Runner
- Add `--enable-layer-detection` flag to `main.py`
- Pass flag through pipeline
- Update README with usage examples

### Step 8: Testing & Documentation
- Test with Modbus TCP (has clear MBAP header)
- Test with S7comm (has TPKT/COTP layers)
- Add documentation to README
- Create `docs/LAYER_DETECTION_GUIDE.md`

## Backward Compatibility
- Layer detection is **opt-in** via `--enable-layer-detection` flag
- Default behavior unchanged (treats messages as flat)
- All outputs remain valid when layer detection disabled
- Schema extensions are optional fields

## Expected Impact
- **Clustering accuracy**: +10-15% for layered protocols (Modbus TCP, S7comm)
- **Boundary precision**: Cleaner field boundaries in application layer
- **Semantic labeling**: Better role detection without transport noise
- **No impact**: Flat protocols (no layers) work as before

## Files to Create
1. `src/protocol_re/inference/layer_detection.py` - Core layer detection logic

## Files to Modify
1. `src/protocol_re/inference/framing.py` - Add layer boundary detection
2. `scripts/05_infer_framing.py` - Output layer info
3. `scripts/04_discover_families.py` - Add layer-aware clustering flag
4. `src/protocol_re/clustering/family_discovery.py` - Implement layer-aware clustering
5. `src/protocol_re/features/extraction.py` - Layer-aware feature extraction
6. `scripts/06_extract_features.py` - Pass layer info
7. `src/protocol_re/inference/boundary_detection.py` - Layer-aware boundaries
8. `scripts/07_infer_boundaries.py` - Pass layer info
9. `scripts/12_build_protocol_model.py` - Add layer metadata
10. `schema/protocol_model.schema.json` - Add layer fields
11. `main.py` - Add CLI flag
12. `README.md` - Document feature

## Testing Strategy
- Unit tests for layer detection logic
- Integration test with Modbus TCP captures (clear MBAP header)
- Regression test: ensure flat protocols unchanged
- Evaluation: compare accuracy with/without layer detection

## Open Questions for User
None - implementation approach is clear based on existing architecture.
