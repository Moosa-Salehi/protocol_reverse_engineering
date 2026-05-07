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

## Architecture

The pipeline is intentionally protocol-agnostic. PCAP extraction creates a canonical message corpus, family discovery groups similar payloads, feature extraction builds reusable byte-level evidence, boundary inference proposes templates and fields, request/response pairing and relation inference connect families, semantic labeling adds role and field hints, and exporters turn the resulting protocol model into Markdown, HTML, evaluation metrics, and LLM evidence bundles.

The package code lives under `src/protocol_re/`; CLI stages live in `scripts/`; generated/intermediate artifacts live in `data/`; final specs go to `output/`.

## Core stages

- `scripts/01_collect_pcaps.py` collects PCAP files from a source tree into one normalized directory.
- `scripts/02_dedup_pcaps.py` finds duplicate PCAP files and can remove them.
- `scripts/03_extract_messages.py` extracts TCP payload messages from PCAPs directly into the canonical JSONL corpus.
- `scripts/03_alt_build_corpus.py` builds the same canonical corpus from legacy extracted `protocol-x-payloads/*.json` files.
- `scripts/04_discover_families.py` discovers message families with DBSCAN, HDBSCAN, or a built-in heuristic fallback; it clusters a unique-message sample and propagates sampled labels to duplicate payloads across the corpus.
- `scripts/05_extract_features.py` writes reusable per-message and per-family feature artifacts.
- `scripts/06_infer_boundaries.py` infers templates, contiguous segments, and coarse field hypotheses; with `--features-json`, it uses family entropy/uniqueness/coverage vectors to refine segment confidence.
- `scripts/07_pair_requests_responses.py` emits candidate request/response pairs per session.
- `scripts/08_infer_keywords.py` finds candidate keyword bytes and keyword-based subformats.
- `scripts/09_compare_subcluster_hypotheses.py` compares keyword-based and length-based subclustering strategies.
- `scripts/10_infer_relations.py` summarizes family-to-family request/response relations, echo fields, and simple role hints.
- `scripts/11_infer_semantics.py` attaches semantic field labels using boundary hypotheses plus request/response evidence.
- `scripts/12_build_protocol_model.py` assembles a protocol-model JSON document matching `schema/protocol_model.schema.json`, including feature, keyword, subcluster, relation, and semantic evidence when supplied.
- `scripts/13_evaluate_pipeline.py` writes pipeline quality metrics for corpus coverage, clustering, boundaries, pairing, relations, and semantic-label coverage when supplied.
- `scripts/14_export_llm_evidence.py` renders a schema-shaped compact per-family evidence bundle for downstream LLM analysis, including compact evaluation metrics when supplied.
- `scripts/15_analyze_with_llm.py` renders the protocol-analysis prompt and can call an OpenAI-compatible LLM API to write `data/13_llm_analysis.json`.
- `scripts/16_prepare_evaluation_data.py` prepares `data/14_evaluation_model_data.json` for final ground-truth evaluation.
- `scripts/17_evaluate_protocol_spec.py` compares `data/14_evaluation_model_data.json` against a ground-truth protocol JSON and writes `data/15_evaluation_result.json`.
- `scripts/18_export_markdown.py` renders a human-readable Markdown protocol specification with evaluation metrics when supplied.
- `scripts/19_export_html.py` renders a self-contained HTML protocol report with model, relation, feature, semantic, and evaluation evidence.

## Feature artifacts

- `message_features.jsonl` contains per-message length, entropy, sparse byte histogram, top byte values, run-length statistics, and repeated n-gram motifs.
- `family_features.json` contains per-family length statistics, entropy and uniqueness vectors by byte offset, aggregate byte histograms, motif/repetition summaries, top n-gram frequency tables, wider repeated motifs, trailing-block/padding hints, length profiles, and recurring fixed-position groups.
- `scripts/05_extract_features.py` streams `messages.jsonl` and writes message features line by line, so it should not load the whole corpus into memory.
- `main.py` passes `data/03_features/family_features.json` into boundary inference and passes feature, keyword, subcluster, relation, and semantic artifacts into the protocol-model builder so final models retain the evidence from upstream stages.
- Evaluation reports distinguish corpus assignment coverage from clustering sample ratio, so the configured 100K clustering sample is reported separately from propagated family assignment coverage.

## LLM evidence schema

`schema/llm_evidence.schema.json` defines the compact evidence bundle produced by `scripts/14_export_llm_evidence.py`. The bundle is protocol-agnostic and is organized for LLM analysis around source counts, coverage, evaluation quality signals, top global relations, global field candidates, compact family evidence, and open questions. Raw payloads are intentionally omitted. The exporter writes compact JSON by default; use `--pretty` only when human-readable formatting is needed. Use `--family-limit`, `--field-limit`, and `--relation-limit` to make smaller targeted bundles.

## LLM protocol analysis

`scripts/15_analyze_with_llm.py` reads `data/12_llm_evidence.json`, renders a protocol reverse-engineering prompt, and can call an OpenAI-compatible `/chat/completions` API. Configure the API base URL and model in `LLM_config.json`; keep the API key only in an environment variable:

```json
{
  "api_key_required": "yes",
  "openai_base_url": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "temperature": 0.1,
  "max_tokens": 6000,
  "timeout": 120
}
```

```bash
export OPENAI_API_KEY=<api-key>
python3 scripts/15_analyze_with_llm.py data/12_llm_evidence.json data/13_llm_analysis.json --prompt-out data/13_llm_prompt.md --config LLM_config.json
```

Use `--render-only` to create the prompt without calling an API, or `--template custom_prompt.md` to replace the built-in analysis prompt. The runner exposes the same workflow with `--llm-config`, `--llm-template`, `--llm-render-only`, `--llm-temperature`, `--llm-max-tokens`, and `--skip-llm`.

## Required system

a windows/linux system with python installed.

## Installing dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the pipeline

Default PCAP workflow:

```bash
python main.py <folder-containing-pcaps>
```

This command treats the input folder as an existing normalized PCAP directory, extracts up to 2,000,000 TCP payload messages into `data/01_messages.jsonl`, runs all inference stages, writes `data/13_llm_analysis.json`, `output/protocol_report.md`, and `output/protocol_report.html`, then prints total execution time and output file paths. Typical runtime for 2 million messages: 30 minutes.

Useful runner options:

```bash
python main.py <folder-containing-pcaps> --max-workers 4
python main.py <folder-containing-pcaps> --service-port <port>
python main.py <folder-containing-pcaps> --reassembly-mode stream
python main.py files --collect
python main.py pcaps --max-messages 5000000
python main.py pcaps --skip-llm
python main.py pcaps --ground-truth-json ground_truth/protocol.json
python main.py --legacy-json archive/protocol-x-payloads --deduplicate-payloads
python main.py --legacy-json archive/protocol-x-payloads --data-dir /tmp/protocol_re_data --output-dir /tmp/protocol_re_output --stop-after 03_alt_build_corpus
python main.py --legacy-json archive/protocol-x-payloads --deduplicate-payloads --llm-render-only --stop-after 15_analyze_with_llm
```

- `--legacy-json <dir>` uses already extracted archive JSON payloads instead of PCAPs.
- `--collect` collects PCAP/PCAPNG files into `pcaps/` and removes duplicate captures before extraction.
- `--max-messages <n>` limits extraction/corpus writing; default is 2,000,000.
- `--service-port` optionally filters extraction to one TCP port. If omitted, the PCAP extractor treats all TCP payloads as candidate unknown-protocol traffic.
- `--reassembly-mode packet` keeps the fast packet-payload extractor; `--reassembly-mode stream` reconstructs directional raw TCP byte streams without assuming any application protocol framing.
- `--data-dir`, `--pcap-dir`, and `--output-dir` override artifact locations.
- `--llm-config <file>` points stage 15 at an LLM config JSON; by default it uses `LLM_config.json`.
- `--llm-render-only` renders `data/13_llm_prompt.md` and `data/13_llm_analysis.json` metadata without calling an API.
- `--skip-llm` skips LLM evidence export and analysis stages.
- `--ground-truth-json <file>` runs final protocol-spec evaluation and writes `data/15_evaluation_result.json`.
- `--stop-after <step>` is useful for smoke tests and partial runs.

## Running step by step

Set imports first:

```bash
export PYTHONPATH=src
```

Build from an existing normalized PCAP directory, matching the default `python main.py pcaps` flow:

```bash
python3 scripts/03_extract_messages.py pcaps data/01_messages.jsonl --max-workers 4 --reassembly-mode packet --max-messages 2000000
python3 scripts/04_discover_families.py data/01_messages.jsonl data/02_family_assignments.json --sample-size 100000
python3 scripts/05_extract_features.py data/01_messages.jsonl data/03_features --assignments-json data/02_family_assignments.json
python3 scripts/06_infer_boundaries.py data/01_messages.jsonl data/04_families.json --assignments-json data/02_family_assignments.json --features-json data/03_features/family_features.json
python3 scripts/07_pair_requests_responses.py data/01_messages.jsonl data/05_pairs.json --assignments-json data/02_family_assignments.json
python3 scripts/08_infer_keywords.py data/01_messages.jsonl data/06_keywords.json --assignments-json data/02_family_assignments.json
python3 scripts/09_compare_subcluster_hypotheses.py data/01_messages.jsonl data/07_subcluster_hypotheses.json --assignments-json data/02_family_assignments.json
python3 scripts/10_infer_relations.py data/01_messages.jsonl data/02_family_assignments.json data/05_pairs.json data/08_relations.json
python3 scripts/11_infer_semantics.py data/04_families.json data/08_relations.json data/09_semantics.json
python3 scripts/12_build_protocol_model.py data/04_families.json data/10_protocol_model.json --features-json data/03_features/family_features.json --keywords-json data/06_keywords.json --subclusters-json data/07_subcluster_hypotheses.json --relations-json data/08_relations.json --semantics-json data/09_semantics.json
python3 scripts/13_evaluate_pipeline.py data/01_messages.jsonl data/02_family_assignments.json data/04_families.json data/05_pairs.json data/08_relations.json data/11_evaluation.json --semantics-json data/09_semantics.json
python3 scripts/14_export_llm_evidence.py data/10_protocol_model.json data/12_llm_evidence.json --evaluation-json data/11_evaluation.json
python3 scripts/15_analyze_with_llm.py data/12_llm_evidence.json data/13_llm_analysis.json --config LLM_config.json --prompt-out data/13_llm_prompt.md
python3 scripts/16_prepare_evaluation_data.py data/10_protocol_model.json data/11_evaluation.json data/13_llm_analysis.json data/14_evaluation_model_data.json
python3 scripts/17_evaluate_protocol_spec.py data/14_evaluation_model_data.json ground_truth/protocol.json data/15_evaluation_result.json
python3 scripts/18_export_markdown.py data/10_protocol_model.json output/protocol_report.md --evaluation-json data/11_evaluation.json --llm-analysis-json data/13_llm_analysis.json
python3 scripts/19_export_html.py data/10_protocol_model.json output/protocol_report.html --evaluation-json data/11_evaluation.json --llm-analysis-json data/13_llm_analysis.json
```

If running with `--collect`, prepend these steps and use `pcaps` as the extraction input:

```bash
python3 scripts/01_collect_pcaps.py files pcaps
python3 scripts/02_dedup_pcaps.py pcaps --delete
```

If running with `--ground-truth-json ground_truth/protocol.json`, insert this after stage 16 and pass the final evaluation JSON to the exporters:

```bash
python3 scripts/17_evaluate_protocol_spec.py data/14_evaluation_model_data.json ground_truth/protocol.json data/15_evaluation_result.json
python3 scripts/18_export_markdown.py data/10_protocol_model.json output/protocol_report.md --evaluation-json data/11_evaluation.json --llm-analysis-json data/13_llm_analysis.json --final-evaluation-json data/15_evaluation_result.json
python3 scripts/19_export_html.py data/10_protocol_model.json output/protocol_report.html --evaluation-json data/11_evaluation.json --llm-analysis-json data/13_llm_analysis.json --final-evaluation-json data/15_evaluation_result.json
```

Build from legacy extracted JSON payloads:

```bash
python3 scripts/03_alt_build_corpus.py archive/protocol-x-payloads data/01_messages.jsonl --deduplicate-payloads --max-messages 2000000
(the rest is the same)
```

Windows PowerShell equivalent for imports:

```powershell
$env:PYTHONPATH="src"
```

## Compatibility note

- `scripts/03_alt_build_corpus.py` exists so you can keep using the already extracted `protocol-x-payloads/*.json` dataset while migrating to the PCAP workflow.
- `scripts/03_extract_messages.py` is the preferred path for future runs because it preserves per-message direction and timestamps.
- The PCAP extractor defaults to packet-level TCP payloads. Use `--reassembly-mode stream` for directional raw TCP stream reconstruction; this handles retransmission overlap and stream gaps without assuming a known protocol grammar.
