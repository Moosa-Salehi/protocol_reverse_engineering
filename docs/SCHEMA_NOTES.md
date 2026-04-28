Protocol model artifacts

Core stages

- `scripts/01_collect_pcaps.py` collects PCAP files from a source tree into one normalized directory.
- `scripts/02_dedup_pcaps.py` finds duplicate PCAP files and can remove them.
- `scripts/03_extract_messages.py` extracts TCP payload messages from PCAPs directly into the canonical JSONL corpus.
- `scripts/04_discover_families.py` discovers message families with DBSCAN, HDBSCAN, or a built-in heuristic fallback.
- `scripts/05_extract_features.py` writes reusable per-message and per-family feature artifacts.
- `scripts/06_infer_boundaries.py` infers templates, contiguous segments, and coarse field hypotheses.
- `scripts/07_pair_requests_responses.py` emits candidate request/response pairs per session.
- `scripts/08_infer_keywords.py` finds candidate keyword bytes and keyword-based subformats.
- `scripts/09_compare_subcluster_hypotheses.py` compares keyword-based and length-based subclustering strategies.
- `scripts/10_infer_relations.py` summarizes family-to-family request/response relations, echo fields, and simple role hints.
- `scripts/11_infer_semantics.py` attaches semantic field labels using boundary hypotheses plus request/response evidence.
- `scripts/12_build_protocol_model.py` assembles a protocol-model JSON document matching `schema/protocol_model.schema.json`.
- `scripts/13_export_markdown.py` renders a human-readable Markdown protocol specification.

Feature artifacts

- `message_features.jsonl` contains per-message length, entropy, sparse byte histogram, top byte values, run-length statistics, and repeated n-gram motifs.
- `family_features.json` contains per-family length statistics, entropy and uniqueness vectors by byte offset, aggregate byte histograms, and motif/repetition summaries.
- `scripts/05_extract_features.py` streams `messages.jsonl` and writes message features line by line, so it should not load the whole corpus into memory.

Recommended flow from PCAPs

<div style="border: 1px solid #313131; padding: 8px 12px; margin-bottom: 15px; border-radius: 4px; background: #2B2B2B; font-family: monospace;">
  <div style="display: flex; justify-content: space-between;">
    <span>set PYTHONPATH=src</span>
    <span style="color: #8C8C8C">cmd</span>
  </div>
  <div style="display: flex; justify-content: space-between;">
    <span>$env:PYTHONPATH=&quot;src&quot;</span>
    <span style="color: #8C8C8C">powershell</span>
  </div>

  <div style="white-space: pre; overflow-x: auto;">
python.exe .\scripts\01_collect_pcaps.py files pcaps
python.exe .\scripts\02_dedup_pcaps.py pcaps --delete
python.exe .\scripts\03_extract_messages.py pcaps data\01_messages.jsonl
python.exe .\scripts\04_discover_families.py data\01_messages.jsonl data\02_family_assignments.json
python.exe .\scripts\05_extract_features.py data\01_messages.jsonl data\03_features --assignments-json data\02_family_assignments.json
python.exe .\scripts\06_infer_boundaries.py data\01_messages.jsonl data\04_families.json --assignments-json data\02_family_assignments.json
python.exe .\scripts\07_pair_requests_responses.py data\01_messages.jsonl data\05_pairs.json --assignments-json data\02_family_assignments.json
python.exe .\scripts\08_infer_keywords.py data\01_messages.jsonl data\06_keywords.json --assignments-json data\02_family_assignments.json
python.exe .\scripts\09_compare_subcluster_hypotheses.py data\01_messages.jsonl data\07_subcluster_hypotheses.json --assignments-json data\02_family_assignments.json
python.exe .\scripts\10_infer_relations.py data\01_messages.jsonl data\02_family_assignments.json data\05_pairs.json data\08_relations.json
python.exe .\scripts\11_infer_semantics.py data\04_families.json data\08_relations.json data\09_semantics.json
python.exe .\scripts\12_build_protocol_model.py data\04_families.json data\10_protocol_model.json --relations-json data\08_relations.json --semantics-json data\09_semantics.json
python.exe .\scripts\13_export_markdown.py data\10_protocol_model.json output\protocol_spec.md
  </div>
</div>


<div style="border: 1px solid #313131; padding: 8px 12px; margin-bottom: 15px; border-radius: 4px; background: #2B2B2B; font-family: monospace;">
  <div style="display: flex; justify-content: space-between;">
    <span>PYTHONPATH=src</span>
    <span style="color: #8C8C8C">bash</span>
  </div>
  <div style="white-space: pre; overflow-x: auto;">
python3 scripts/01_collect_pcaps.py files pcaps
python3 scripts/02_dedup_pcaps.py pcaps --delete
python3 scripts/03_extract_messages.py pcaps data/01_messages.jsonl
python3 scripts/04_discover_families.py data/01_messages.jsonl data/02_family_assignments.json
python3 scripts/05_extract_features.py data/01_messages.jsonl data/03_features --assignments-json data/02_family_assignments.json
python3 scripts/06_infer_boundaries.py data/01_messages.jsonl data/04_families.json --assignments-json data/02_family_assignments.json
python3 scripts/07_pair_requests_responses.py data/01_messages.jsonl data/05_pairs.json --assignments-json data/02_family_assignments.json
python3 scripts/08_infer_keywords.py data/01_messages.jsonl data/06_keywords.json --assignments-json data/02_family_assignments.json
python3 scripts/09_compare_subcluster_hypotheses.py data/01_messages.jsonl data/07_subcluster_hypotheses.json --assignments-json data/02_family_assignments.json
python3 scripts/10_infer_relations.py data/01_messages.jsonl data/02_family_assignments.json data/05_pairs.json data/08_relations.json
python3 scripts/11_infer_semantics.py data/04_families.json data/08_relations.json data/09_semantics.json
python3 scripts/12_build_protocol_model.py data/04_families.json data/10_protocol_model.json --relations-json data/08_relations.json --semantics-json data/09_semantics.json
python3 scripts/13_export_markdown.py data/10_protocol_model.json output/protocol_spec.md
  </div>
</div>

Compatibility note

- `scripts/03_alt_build_corpus.py` exists so you can keep using the already extracted `modbus-payloads/*.json` dataset while migrating to the new structure.
- `scripts/03_extract_messages.py` is the preferred path for future runs because it preserves per-message direction and timestamps.
