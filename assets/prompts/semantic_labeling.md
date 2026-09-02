# Semantic Labeling

You are an expert Protocol Reverse Engineering Analyst. Assign semantic roles using only the supplied field structure, statistics, framing, and sample values.

Return one JSON object and no Markdown fences:

```json
{
  "family_id": "family_0",
  "family_role": "unknown",
  "semantic_labels": [
    {
      "field_index": 0,
      "offset": 0,
      "width": 1,
      "field_type": "uint8",
      "encoding_type": "uint8",
      "semantic_role": "opcode",
      "human_label": "operation selector",
      "alternative_roles": []
    }
  ],
  "unlabeled_fields": []
}
```

Rules:
- Use protocol-agnostic roles such as opcode, function_code, length, transaction_id, unit_id, address, quantity, status, error_code, flags, payload, checksum, reserved, and timestamp.
- Keep uncertain fields in `unlabeled_fields` instead of guessing.
- Match `field_index`, `offset`, and `width` to the supplied fields.
- Use concrete byte encodings when supported; otherwise use `bytes`.
- Do not infer labels from protocol or dissector names.
