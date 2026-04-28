Protocol model artifacts

Core stages

- `scripts/01_collect_pcaps.py` collects PCAP files from a source tree into one normalized directory.
- `scripts/02_dedup_pcaps.py` finds duplicate PCAP files and can remove them.
- `scripts/03_extract_messages.py` extracts TCP payload messages from PCAPs directly into the canonical JSONL corpus.
- `scripts/04_build_corpus.py` builds the same canonical corpus from legacy extracted session JSON files.
- `scripts/05_discover_families.py` discovers message families with DBSCAN, HDBSCAN, or a built-in heuristic fallback.
- `scripts/06_infer_boundaries.py` infers templates, contiguous segments, and coarse field hypotheses.
- `scripts/07_pair_requests_responses.py` emits candidate request/response pairs per session.
- `scripts/08_infer_keywords.py` finds candidate keyword bytes and keyword-based subformats.
- `scripts/09_build_protocol_model.py` assembles a protocol-model JSON document matching `schema/protocol_model.schema.json`.
- `scripts/10_compare_subcluster_hypotheses.py` compares keyword-based and length-based subclustering strategies.
- `scripts/11_infer_relations.py` summarizes family-to-family request/response relations, echo fields, and simple role hints.
- `scripts/12_export_markdown.py` renders a human-readable Markdown protocol specification.
- `scripts/13_infer_semantics.py` attaches semantic field labels using boundary hypotheses plus request/response evidence.
- `scripts/14_extract_features.py` writes reusable per-message and per-family feature artifacts.

Feature artifacts

- `message_features.jsonl` contains per-message length, entropy, sparse byte histogram, top byte values, run-length statistics, and repeated n-gram motifs.
- `family_features.json` contains per-family length statistics, entropy and uniqueness vectors by byte offset, aggregate byte histograms, and motif/repetition summaries.
- `scripts/14_extract_features.py` streams `messages.jsonl` and writes message features line by line, so it should not load the whole corpus into memory.

Recommended flow from PCAPs

<div style="border: 1px solid #313131; padding: 17px; margin-bottom: 15px; border-radius: 4px; background: #2B2B2B; font-family: monospace; direction: ltr;">
  <div style="display: flex; justify-content: space-between;">
<span>$env:PYTHONPATH="src"</span>
<span style="color: #8C8C8C">powershell</span>
  </div>
</div>

<div style="border: 1px solid #313131; padding: 17px; margin-bottom: 15px; border-radius: 4px; background: #2B2B2B; font-family: monospace; direction: ltr;">
  <div style="display: flex; justify-content: space-between;">
<span>set PYTHONPATH=src</span>
<span style="color: #8C8C8C">cmd</span>
  </div>
</div>

<div style="border: 1px solid #313131; padding: 17px; margin-bottom: 15px; border-radius: 4px; background: #2B2B2B; font-family: monospace; direction: ltr;">
  <div style="display: flex; justify-content: space-between;">
<span>PYTHONPATH=src</span>
<span style="color: #8C8C8C">bash</span>
  </div>
</div>

```code
python scripts/01_collect_pcaps.py files pcaps
python scripts/02_dedup_pcaps.py pcaps --delete
python scripts/03_extract_messages.py pcaps data/messages.jsonl
python scripts/05_discover_families.py data/messages.jsonl data/family_assignments.json
python scripts/14_extract_features.py data/messages.jsonl data/features --assignments-json data/family_assignments.json
python scripts/06_infer_boundaries.py data/messages.jsonl data/families.json --assignments-json data/family_assignments.json
python scripts/07_pair_requests_responses.py data/messages.jsonl data/pairs.json --assignments-json data/family_assignments.json
python scripts/08_infer_keywords.py data/messages.jsonl data/keywords.json --assignments-json data/family_assignments.json
python scripts/10_compare_subcluster_hypotheses.py data/messages.jsonl data/subcluster_hypotheses.json --assignments-json data/family_assignments.json
python scripts/11_infer_relations.py data/messages.jsonl data/family_assignments.json data/pairs.json data/relations.json
python scripts/13_infer_semantics.py data/families.json data/relations.json data/semantics.json
python scripts/09_build_protocol_model.py data/families.json data/protocol_model.json --relations-json data/relations.json --semantics-json data/semantics.json
python scripts/12_export_markdown.py data/protocol_model.json data/protocol_spec.md
```

Compatibility note

- `scripts/04_build_corpus.py` exists so you can keep using the already extracted `modbus-payloads/*.json` dataset while migrating to the new structure.
- `scripts/03_extract_messages.py` is the preferred path for future runs because it preserves per-message direction and timestamps.
