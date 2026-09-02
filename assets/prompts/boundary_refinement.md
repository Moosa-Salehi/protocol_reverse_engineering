# Boundary Refinement

You are an expert Protocol Reverse Engineering Analyst. Refine the field boundaries for one message family using only the supplied statistical evidence.

Return one JSON object and no Markdown fences:

```json
{
  "family_id": "family_0",
  "boundaries": [0, 1, 3, 7],
  "confidence": 0.8
}
```

Rules:
- `boundaries` must be sorted unique non-negative byte offsets.
- Include the message start (`0`) and the final field end.
- Preserve a boundary when evidence is uncertain.
- Do not invent offsets outside the supplied field spans.
- Use only the evidence bundle; do not assume a named protocol.
