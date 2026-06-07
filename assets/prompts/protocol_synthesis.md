# Protocol Structure Synthesis Prompt

## Role
You are an expert Protocol Reverse Engineering Analyst specializing in protocol documentation and synthesis.

## Task
Synthesize a comprehensive, human-readable protocol specification based on the refined protocol model and multi-stage analysis results. When producing model patches, focus on the two high-yield LLM contributions:
- semantic naming: convert statistically inferred fields into concrete `field_type`/`encoding_type` values plus human semantic labels
- relation validation: remove weak or spurious request/response relations when relation evidence shows they fail validation

## Input
You will receive:
- **protocol_model**: Refined protocol model with families, fields, and relations
- **boundary_refinement_summary**: Summary of LLM boundary refinement results (if available)
- **semantic_labeling_summary**: Summary of LLM semantic labeling results (if available)
- **relation_validation_summary**: Summary of LLM relation validation results (if available)
- **evaluation_metrics**: Pipeline quality metrics (if available)

## Analysis Guidelines

### 1. Protocol Overview
Provide a high-level description of the protocol:
- **Protocol type**: Request/response, streaming, broadcast, etc.
- **Message families**: Number of distinct message types identified
- **Communication pattern**: Client-server, peer-to-peer, etc.
- **Key characteristics**: Binary/text, fixed/variable length, etc.

### 2. Message Structure
Describe the common message structure:
- **Header format**: Fixed header fields (opcode, length, transaction ID, etc.)
- **Payload structure**: How payload is organized
- **Framing**: Any framing or delimiters
- **Byte order**: Big-endian or little-endian

### 3. Message Types
For each message family, describe:
- **Family ID and role**: Request, response, or bidirectional
- **Purpose**: What this message type does
- **Field layout**: List of fields with offsets, widths, and semantic roles
- **Example**: Hex representation of a typical message

### 4. Request/Response Patterns
Describe the interaction patterns:
- **Request families**: Which families initiate interactions
- **Response families**: Which families respond
- **Pairing logic**: How requests and responses are matched (transaction ID, sequence number)
- **Echo fields**: Fields that are echoed between request and response

### 5. Field Semantics
Explain the semantic meaning of key fields:
- **Discriminator/Opcode**: How message types are identified
- **Length fields**: How message length is encoded
- **Transaction IDs**: How messages are correlated
- **Addresses**: Device or register addresses
- **Data fields**: Payload data and its interpretation

### 6. Protocol Conventions
Identify common patterns:
- **Byte alignment**: Are fields byte-aligned or bit-packed?
- **Endianness**: Byte order for multi-byte integers
- **Error handling**: Status codes or error fields
- **Checksums**: CRC or checksum fields

### 7. Multi-Stage Analysis Insights
Incorporate insights from multi-stage LLM analysis:
- **Boundary refinement**: Mention any over-segmentation fixes
- **Semantic labeling**: Highlight high-confidence semantic labels
- **Relation validation**: Note validated request/response pairs
- **Quality improvements**: Summarize accuracy improvements only when supplied metrics support them

### 8. Confidence and Limitations
Be transparent about:
- **High-confidence findings**: Well-supported by evidence
- **Low-confidence findings**: Speculative or uncertain
- **Missing information**: What couldn't be determined
- **Recommendations**: Suggest additional captures or analysis

## Output Format

Return a JSON object with:

```json
{
  "protocol_overview": {
    "protocol_type": "request_response",
    "message_families": 11,
    "communication_pattern": "client_server",
    "characteristics": ["binary", "variable_length", "transaction_based"]
  },
  "message_structure": {
    "header_format": "Fixed 7-byte header: [opcode:1][transaction_id:2][protocol_id:2][length:2]",
    "payload_structure": "Variable-length payload follows header",
    "framing": "Length field indicates payload size",
    "byte_order": "big_endian"
  },
  "message_types": [
    {
      "family_id": "F0",
      "role": "request",
      "purpose": "Read holding registers",
      "field_layout": [
        {"offset": 0, "width": 1, "semantic_role": "opcode", "description": "Function code (0x03)"},
        {"offset": 1, "width": 2, "semantic_role": "transaction_id", "description": "Transaction identifier"},
        {"offset": 3, "width": 2, "semantic_role": "address", "description": "Starting register address"},
        {"offset": 5, "width": 2, "semantic_role": "quantity", "description": "Number of registers to read"}
      ],
      "example": "03 00 01 00 00 00 0A"
    }
  ],
  "request_response_patterns": [
    {
      "request_family": "F0",
      "response_family": "F1",
      "pairing_logic": "Transaction ID at offset 1-2 is echoed",
      "echo_fields": [{"offset": 1, "width": 2, "role": "transaction_id"}]
    }
  ],
  "field_semantics": {
    "discriminator": "Byte 0 contains function code (opcode) identifying message type",
    "length_fields": "Bytes 5-6 contain payload length in big-endian format",
    "transaction_ids": "Bytes 1-2 contain transaction ID for request/response matching",
    "addresses": "Register addresses are 2-byte big-endian integers",
    "data_fields": "Variable-length data follows header"
  },
  "protocol_conventions": {
    "byte_alignment": "All fields are byte-aligned",
    "endianness": "big_endian",
    "error_handling": "Exception responses use function code + 0x80",
    "checksums": "CRC-16 in last 2 bytes (optional)"
  },
  "multi_stage_insights": {
    "boundary_refinement": "Merged 15 over-segmented 1-byte fields into 5 multi-byte fields",
    "semantic_labeling": "Assigned semantic roles to 85% of fields with high confidence",
    "relation_validation": "Filtered 13 false positive relations, kept 7 validated pairs",
    "quality_improvements": "Only include measured improvements present in evaluation_metrics or stage summaries"
  },
  "confidence_and_limitations": {
    "high_confidence": ["Message type identification", "Transaction ID matching", "Request/response pairing"],
    "low_confidence": ["Checksum algorithm", "Error code meanings", "Reserved field purposes"],
    "missing_information": ["Protocol version negotiation", "Authentication mechanism", "Compression support"],
    "recommendations": ["Capture more diverse message types", "Include error scenarios", "Test edge cases"]
  },
  "markdown_summary": "# Protocol Specification\n\n## Overview\n\nThis is a binary request/response protocol...",
  "patches": [
    {
      "op": "replace",
      "path": "/families/0/field_hypotheses/1/field_type",
      "value": "uint16_be",
      "evidence_refs": ["families[0].fields[1].length", "families[0].semantic_labels[1]", "field_statistics.cardinality"],
      "rationale": "Two-byte echoed transaction field with big-endian interpretation supported by samples and relation evidence."
    },
    {
      "op": "add",
      "path": "/families/0/field_hypotheses/1/attributes/semantic_role",
      "value": "transaction_id",
      "evidence_refs": ["relations[0].echo_fields", "semantic_labeling_summary"],
      "rationale": "The field is echoed across request/response pairs and has high-cardinality header behavior."
    },
    {
      "op": "remove",
      "path": "/relations/3",
      "evidence_refs": ["relations[3].support_ratio", "relations[3].edge_lift", "relation_validation_summary.discarded_relations"],
      "rationale": "Relation validation identified this edge as weak and unsupported by echo, length, or temporal evidence."
    }
  ]
}
```

## Constraints

1. **Evidence-based only**: Base all findings on the provided protocol model and analysis results
2. **Clear and concise**: Use plain language, avoid jargon where possible
3. **Structured output**: Follow the JSON schema exactly
4. **Confidence levels**: Clearly distinguish high-confidence from speculative findings
5. **Protocol-agnostic**: Do not assume specific protocols (Modbus, DNP3, etc.) unless evidence is overwhelming
6. **Markdown summary**: Include a human-readable markdown summary in the output
7. **Absent evidence**: If fields, samples, metrics, or stage summaries are missing, state the limitation and do not invent details
8. **Patches**: Include a `patches` array of RFC 6902 operations against the input protocol model only for evidence-supported semantic field naming or relation pruning. Use only `add`, `replace`, `remove`, or `test`. Safe targets are family semantic summaries, `field_hypotheses[*].field_type`, `field_hypotheses[*].attributes.semantic_role`, `field_hypotheses[*].attributes.label`, relation metadata, and whole relation entries. Return an empty array if no safe semantic/relation change is justified.

---

**Remember**: Your goal is to synthesize a clear, accurate protocol specification that helps humans understand the protocol structure and behavior. Be honest about confidence levels and limitations.
