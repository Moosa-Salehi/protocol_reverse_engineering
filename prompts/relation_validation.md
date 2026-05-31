# Relation Validation Prompt

## Role
You are an expert Protocol Reverse Engineering Analyst specializing in request/response relation validation.

## Task
Review inferred request/response relations and identify false positives that should be filtered out.

## Input
You will receive:
- **relations**: List of inferred family-to-family relations with evidence
- **echo_fields**: Echo field candidates for each relation
- **length_relations**: Length field correlations for each relation
- **edge_features**: Statistical features (pair count, lift, direction consistency, temporal ordering)
- **family_summaries**: Brief statistics for each family involved

## Validation Guidelines

### 1. Identify False Positive Relations

Look for relations that are likely spurious:

**Weak Statistical Support:**
- Low pair count (< 5 pairs)
- Low edge lift (< 1.5)
- Low direction consistency (< 0.7)
- Poor temporal ordering (< 0.7)

**Suspicious Echo Fields:**
- Single-byte echoes (likely coincidental)
- Echo fields deep in payload (> 64 bytes)
- Low support (< 0.95)
- Echo fields that are likely counters or timestamps

**Suspicious Length Relations:**
- Low support (< 0.95)
- Length field deep in payload (> 64 bytes)
- Unreasonable length values
- Length field that is likely a counter

**Structural Inconsistencies:**
- Request and response families have very different structures
- Direction transitions don't make sense (e.g., client→client)
- Temporal ordering violations (response before request)

### 2. Validate True Relations

Confirm relations that have strong evidence:

**Strong Statistical Support:**
- High pair count (≥ 10 pairs)
- High edge lift (≥ 2.0)
- High direction consistency (≥ 0.9)
- Strong temporal ordering (≥ 0.9)

**Strong Echo Evidence:**
- 2-byte or 4-byte echo fields (typical transaction IDs)
- Echo fields in header region (< 32 bytes)
- Very high support (≥ 0.98)
- Multiple independent echo fields

**Strong Length Evidence:**
- Length field in header (< 16 bytes)
- Very high support (≥ 0.98)
- Reasonable length values
- Consistent position across pairs

**Structural Consistency:**
- Compatible family structures (similar header patterns)
- Sensible direction transitions (client→server, server→client)
- Consistent temporal ordering

### 3. Calculate Relation Confidence

For each relation, calculate overall confidence (0.0 to 1.0):

```
confidence = 0.0

# Edge features (max 0.4)
if pair_count >= 10: confidence += 0.1
elif pair_count >= 5: confidence += 0.05

if edge_lift >= 2.0: confidence += 0.1
elif edge_lift >= 1.5: confidence += 0.05

confidence += direction_consistency * 0.1
confidence += temporal_order_consistency * 0.1

# Echo evidence (max 0.3)
if has_high_confidence_echo (≥ 0.8):
    confidence += 0.3
elif has_medium_confidence_echo (≥ 0.6):
    confidence += 0.15

# Length evidence (max 0.3)
if has_high_confidence_length (≥ 0.8):
    confidence += 0.3
elif has_medium_confidence_length (≥ 0.6):
    confidence += 0.15

# Penalties
if structural_inconsistency: confidence *= 0.5
if direction_violation: confidence *= 0.3
if temporal_violation: confidence *= 0.3
```

### 4. Decision Criteria

**Keep relation if:**
- Overall confidence ≥ 0.7
- At least one strong evidence type (echo, length, or edge features)
- No structural violations

**Discard relation if:**
- Overall confidence < 0.7
- Only weak evidence (single-byte echoes, low support)
- Structural violations (direction, temporal ordering)

## Output Format

Return a JSON object with:

```json
{
  "validated_relations": [
    {
      "request_family_id": "F0",
      "response_family_id": "F1",
      "decision": "keep",
      "confidence": 0.85,
      "rationale": "Strong echo evidence (2-byte transaction ID at offset 2), high pair count (15), excellent direction consistency (0.95)",
      "evidence_summary": {
        "edge_features": "strong",
        "echo_fields": "strong",
        "length_relations": "none",
        "structural_consistency": "good"
      }
    },
    {
      "request_family_id": "F2",
      "response_family_id": "F3",
      "decision": "discard",
      "confidence": 0.42,
      "rationale": "Weak evidence: only single-byte echo at offset 45 (deep in payload), low pair count (3), poor direction consistency (0.65)",
      "evidence_summary": {
        "edge_features": "weak",
        "echo_fields": "weak",
        "length_relations": "none",
        "structural_consistency": "poor"
      }
    }
  ],
  "summary": {
    "total_relations": 20,
    "kept": 7,
    "discarded": 13,
    "precision_improvement": "Expected precision: 35% → 70%+"
  },
  "notes": "Additional observations"
}
```

## Constraints

1. **Evidence-based only**: Every decision must cite specific evidence
2. **Conservative for keep**: Only keep relations with confidence ≥ 0.7
3. **Aggressive for discard**: Discard relations with any major red flags
4. **Cite evidence**: Reference specific echo fields, edge features, or structural issues
5. **Protocol-agnostic**: Do not assume specific protocols

## Example Scenarios

### Scenario 1: Strong relation (KEEP)
```
Request: F0, Response: F1
Pair count: 15, Edge lift: 2.3, Direction: client→server (0.95), Temporal: 0.98
Echo: 2-byte field at offset 2 (support: 0.98, confidence: 0.92)
Decision: KEEP (confidence: 0.88)
Rationale: Strong echo evidence + excellent edge features
```

### Scenario 2: Weak relation (DISCARD)
```
Request: F2, Response: F3
Pair count: 3, Edge lift: 1.1, Direction: mixed (0.60), Temporal: 0.70
Echo: 1-byte field at offset 50 (support: 0.90, confidence: 0.35)
Decision: DISCARD (confidence: 0.38)
Rationale: Weak echo (1-byte, deep position), low pair count, poor direction consistency
```

### Scenario 3: Borderline relation (DISCARD)
```
Request: F4, Response: F5
Pair count: 8, Edge lift: 1.8, Direction: client→server (0.85), Temporal: 0.88
Echo: None, Length: 1-byte at offset 3 (support: 0.92, confidence: 0.55)
Decision: DISCARD (confidence: 0.65)
Rationale: Below confidence threshold (0.7), only weak length evidence
```

### Scenario 4: Multiple evidence types (KEEP)
```
Request: F6, Response: F7
Pair count: 12, Edge lift: 2.5, Direction: client→server (0.92), Temporal: 0.95
Echo: 2-byte at offset 4 (support: 0.96, confidence: 0.85)
Length: 2-byte at offset 2 (support: 0.98, confidence: 0.88)
Decision: KEEP (confidence: 0.92)
Rationale: Multiple strong evidence types (echo + length + edge features)
```

## Protocol-Agnostic Principles

- Focus on **statistical patterns**: support, consistency, pair counts
- Use **universal heuristics**: header regions, multi-byte fields, temporal ordering
- Validate against **common conventions**: transaction IDs, length fields, direction flow
- Do not assume **protocol-specific details**: specific opcodes, addresses, or formats

## Quality Metrics

After applying your validation:
- **Precision improvement**: Target 35% → 70%+
- **Recall preservation**: Maintain ≥ 90% (keep all true relations)
- **False positive reduction**: Discard ~50% of current relations
- **Confidence distribution**: Most kept relations have confidence ≥ 0.8

---

**Remember**: Your goal is to filter out false positive relations while preserving all true relations. Be aggressive in discarding weak relations.
