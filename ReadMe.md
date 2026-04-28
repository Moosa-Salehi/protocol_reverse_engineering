# Protocol RE project

This project is a framework for reverse engineering industrial communication protocols from PCAP traffic. The system takes network captures or legacy extracted payload JSON and gradually infers the structure of an unknown protocol.

The pipeline is:

1. Read PCAP files and reconstruct flows/messages.
2. Extract raw payloads and represent them as byte/hex sequences.
3. Compute basic features such as message length, byte statistics, entropy, repetition patterns, and motifs.
4. Cluster similar messages to identify message types/families.
5. Detect field boundaries inside messages using statistical differences between byte offsets.
6. Produce structured summaries of each message type: length patterns, field positions, statistics, relations, and semantic hints.
7. Prepare this structured information so it can later be analyzed by an LLM to infer field roles and generate a protocol specification.
8. Export a human-readable protocol specification.

The package code lives under `src/protocol_re/`; CLI stages live in `scripts/`; generated/intermediate artifacts live in `data/`; final specs go to `output/`.

## Core stages

- `scripts/01_collect_pcaps.py` collects PCAP files from a source tree into one normalized directory.
- `scripts/02_dedup_pcaps.py` finds duplicate PCAP files and can remove them.
- `scripts/03_extract_messages.py` extracts TCP payload messages from PCAPs directly into the canonical JSONL corpus.
- `scripts/03_alt_build_corpus.py` builds the same canonical corpus from legacy extracted `protocol-x-payloads/*.json` files.
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

## Feature artifacts

- `message_features.jsonl` contains per-message length, entropy, sparse byte histogram, top byte values, run-length statistics, and repeated n-gram motifs.
- `family_features.json` contains per-family length statistics, entropy and uniqueness vectors by byte offset, aggregate byte histograms, and motif/repetition summaries.
- `scripts/05_extract_features.py` streams `messages.jsonl` and writes message features line by line, so it should not load the whole corpus into memory.
- `main.py` passes `data/03_features/family_features.json` into the protocol-model builder so final models include feature summaries.

## Installing dependencies

```bash
pip install -r requirements.txt
```

## Running the pipeline

Default PCAP workflow:

```bash
python main.py <folder-containing-pcaps>
```

This command collects PCAP/PCAPNG files into `pcaps/`, removes duplicate captures, extracts TCP payload messages into `data/01_messages.jsonl`, runs all inference stages, and writes `output/protocol_spec.md`.

Useful runner options:

```bash
python main.py <folder-containing-pcaps> --service-port 502 --max-workers 4
python main.py pcaps --skip-collect
python main.py --legacy-json archive/protocol-x-payloads --deduplicate-payloads
python main.py --legacy-json archive/protocol-x-payloads --data-dir /tmp/protocol_re_data --output-dir /tmp/protocol_re_output --stop-after 03_alt_build_corpus
```

- `--legacy-json <dir>` uses already extracted archive JSON payloads instead of PCAPs.
- `--skip-collect` treats the positional input folder as an existing normalized PCAP directory and skips collect/dedup.
- `--service-port` selects the TCP service port to extract; the default is `502`.
- `--data-dir`, `--pcap-dir`, and `--output-dir` override artifact locations.
- `--stop-after <step>` is useful for smoke tests and partial runs.

## Running step by step

Set imports first:

```bash
export PYTHONPATH=src
```

Build from PCAPs:

```bash
python3 scripts/01_collect_pcaps.py files pcaps
python3 scripts/02_dedup_pcaps.py pcaps --delete
python3 scripts/03_extract_messages.py pcaps data/01_messages.jsonl --service-port 502 --max-workers 4
python3 scripts/04_discover_families.py data/01_messages.jsonl data/02_family_assignments.json
python3 scripts/05_extract_features.py data/01_messages.jsonl data/03_features --assignments-json data/02_family_assignments.json
python3 scripts/06_infer_boundaries.py data/01_messages.jsonl data/04_families.json --assignments-json data/02_family_assignments.json
python3 scripts/07_pair_requests_responses.py data/01_messages.jsonl data/05_pairs.json --assignments-json data/02_family_assignments.json
python3 scripts/08_infer_keywords.py data/01_messages.jsonl data/06_keywords.json --assignments-json data/02_family_assignments.json
python3 scripts/09_compare_subcluster_hypotheses.py data/01_messages.jsonl data/07_subcluster_hypotheses.json --assignments-json data/02_family_assignments.json
python3 scripts/10_infer_relations.py data/01_messages.jsonl data/02_family_assignments.json data/05_pairs.json data/08_relations.json
python3 scripts/11_infer_semantics.py data/04_families.json data/08_relations.json data/09_semantics.json
python3 scripts/12_build_protocol_model.py data/04_families.json data/10_protocol_model.json --features-json data/03_features/family_features.json --relations-json data/08_relations.json --semantics-json data/09_semantics.json
python3 scripts/13_export_markdown.py data/10_protocol_model.json output/protocol_spec.md
```

Build from legacy extracted JSON payloads:

```bash
python3 scripts/03_alt_build_corpus.py archive/protocol-x-payloads data/01_messages.jsonl --deduplicate-payloads
python3 scripts/04_discover_families.py data/01_messages.jsonl data/02_family_assignments.json
python3 scripts/05_extract_features.py data/01_messages.jsonl data/03_features --assignments-json data/02_family_assignments.json
python3 scripts/06_infer_boundaries.py data/01_messages.jsonl data/04_families.json --assignments-json data/02_family_assignments.json
python3 scripts/07_pair_requests_responses.py data/01_messages.jsonl data/05_pairs.json --assignments-json data/02_family_assignments.json
python3 scripts/08_infer_keywords.py data/01_messages.jsonl data/06_keywords.json --assignments-json data/02_family_assignments.json
python3 scripts/09_compare_subcluster_hypotheses.py data/01_messages.jsonl data/07_subcluster_hypotheses.json --assignments-json data/02_family_assignments.json
python3 scripts/10_infer_relations.py data/01_messages.jsonl data/02_family_assignments.json data/05_pairs.json data/08_relations.json
python3 scripts/11_infer_semantics.py data/04_families.json data/08_relations.json data/09_semantics.json
python3 scripts/12_build_protocol_model.py data/04_families.json data/10_protocol_model.json --features-json data/03_features/family_features.json --relations-json data/08_relations.json --semantics-json data/09_semantics.json
python3 scripts/13_export_markdown.py data/10_protocol_model.json output/protocol_spec.md
```

Windows PowerShell equivalent for imports:

```powershell
$env:PYTHONPATH="src"
```

## Compatibility note

- `scripts/03_alt_build_corpus.py` exists so you can keep using the already extracted `protocol-x-payloads/*.json` dataset while migrating to the PCAP workflow.
- `scripts/03_extract_messages.py` is the preferred path for future runs because it preserves per-message direction and timestamps.
- The current PCAP extractor reads packet-level TCP payloads. True TCP stream reassembly is a planned improvement.
