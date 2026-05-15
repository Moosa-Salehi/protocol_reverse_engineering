# Protocol RE project

This project is a framework for reverse engineering industrial communication protocols from PCAP traffic. The system takes network captures and gradually infers the structure of an unknown protocol.

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
- `scripts/04_discover_families.py` discovers message families with DBSCAN, HDBSCAN, or a built-in heuristic fallback; it clusters a unique-message sample and propagates sampled labels to duplicate payloads across the corpus.
- `scripts/05_extract_features.py` writes reusable per-family feature artifacts.
- `scripts/06_infer_boundaries.py` infers templates, contiguous segments, and coarse field hypotheses; with `--features-json`, it uses family entropy/uniqueness/coverage vectors to refine segment confidence.
- `scripts/07_pair_requests_responses.py` emits candidate request/response pairs per session.
- `scripts/08_infer_keywords.py` finds candidate keyword bytes and keyword-based subformats.
- `scripts/10_infer_relations.py` summarizes family-to-family request/response relations, echo fields, and simple role hints.
- `scripts/11_infer_semantics.py` attaches semantic field labels using boundary hypotheses plus request/response evidence.
- `scripts/12_build_protocol_model.py` assembles a protocol-model JSON document matching `schema/protocol_model.schema.json`, including feature, keyword, relation, and semantic evidence when supplied.
- `scripts/13_evaluate_pipeline.py` writes pipeline quality metrics for corpus coverage, clustering, boundaries, pairing, relations, and semantic-label coverage when supplied.
- `scripts/14_export_llm_evidence.py` renders a schema-shaped compact per-family evidence bundle for downstream LLM analysis, including compact evaluation metrics when supplied.
- `scripts/15_analyze_with_llm.py` renders the protocol-analysis prompt and can call an OpenAI-compatible LLM API to write `data/13_llm_analysis.json`.
- `scripts/16_prepare_evaluation_data.py` prepares `data/14_evaluation_model_data.json` for final ground-truth evaluation.
- `scripts/17_evaluate_protocol_spec.py` compares `data/14_evaluation_model_data.json` against a ground-truth protocol JSON and writes `data/15_evaluation_result.json`.
- `scripts/18_export_markdown.py` renders a human-readable Markdown protocol specification with evaluation metrics when supplied.
- `scripts/19_export_html.py` renders a self-contained HTML protocol report with model, relation, feature, semantic, and evaluation evidence.

## Feature artifacts

- `family_features.json` contains per-family length statistics, entropy and uniqueness vectors by byte offset, aggregate byte histograms, motif/repetition summaries, top n-gram frequency tables, wider repeated motifs, trailing-block/padding hints, length profiles, and recurring fixed-position groups.
- `main.py` passes `data/03_family_features.json` into boundary inference and passes feature, keyword, relation, and semantic artifacts into the protocol-model builder so final models retain the evidence from upstream stages.
- Evaluation reports distinguish corpus assignment coverage from clustering sample ratio, so the configured 100K clustering sample is reported separately from propagated family assignment coverage.

## LLM evidence schema

`schema/llm_evidence.schema.json` defines the compact evidence bundle produced by `scripts/14_export_llm_evidence.py`. The bundle is protocol-agnostic and is organized for LLM analysis around source counts, coverage, evaluation quality signals, top global relations, global field candidates, compact family evidence, and open questions. Raw payloads are intentionally omitted. The exporter writes compact JSON by default; use `--pretty` only when human-readable formatting is needed. Use `--family-limit`, `--field-limit`, and `--relation-limit` to make smaller targeted bundles.

## LLM protocol analysis

`scripts/15_analyze_with_llm.py` reads `data/12_llm_evidence.json`, renders a protocol reverse-engineering prompt, and call an OpenAI-compatible API. Configure the API base URL and model in `LLM_config.json`; keep the API key only in an environment variable. When using `--render-only`, no config is needed.

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

Use `--render-only` to create the prompt without calling an API, or `--template custom_prompt.md` to replace the built-in analysis prompt. The runner exposes the same workflow with `--llm-config`, `--llm-template`, `--llm-render-only`, `--llm-temperature`, `--llm-max-tokens`.

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
python main.py <folder-containing-pcaps> --service-port <service-port>
```

This command treats the input folder as an existing normalized PCAP directory, extracts up to 200,000 TCP payload messages into `data/01_messages.jsonl`, runs all inference stages, writes `output/protocol_report.md` and `output/protocol_report.html`. Typical runtime for 200,000 messages: 6 minutes. (3 minutes for message extraction in stream mode, 2 minutes waiting for llm response).

Useful runner options:

```bash
python main.py files --collect
python main.py ../pcaps --service-port 502 --ground-truth-json ./truth-files/modbus.json
python main.py --use-existing-messages --ground-truth-json ./truth-files/modbus.json --llm-render-only
```

## Running step by step

Set imports first:

```bash
export PYTHONPATH=src
```
```powershell
$env:PYTHONPATH="src"
```

Build from an existing normalized PCAP directory, matching the default `python main.py pcaps` flow:

```bash
python3 scripts/03_extract_messages.py pcaps data/01_messages.jsonl --reassembly-mode stream --max-messages 200000
python3 scripts/04_discover_families.py data/01_messages.jsonl data/02_family_assignments.json --sample-size 100000
python3 scripts/05_extract_features.py data/01_messages.jsonl data/03_family_features.json --assignments-json data/02_family_assignments.json
python3 scripts/06_infer_boundaries.py data/01_messages.jsonl data/04_families.json --assignments-json data/02_family_assignments.json --features-json data/03_family_features.json
python3 scripts/07_pair_requests_responses.py data/01_messages.jsonl data/05_pairs.json --assignments-json data/02_family_assignments.json
python3 scripts/08_infer_keywords.py data/01_messages.jsonl data/06_keywords.json --assignments-json data/02_family_assignments.json
python3 scripts/10_infer_relations.py data/01_messages.jsonl data/02_family_assignments.json data/05_pairs.json data/08_relations.json
python3 scripts/11_infer_semantics.py data/04_families.json data/08_relations.json data/09_semantics.json
python3 scripts/12_build_protocol_model.py data/04_families.json data/10_protocol_model.json --features-json data/03_family_features.json --keywords-json data/06_keywords.json --relations-json data/08_relations.json --semantics-json data/09_semantics.json
python3 scripts/13_evaluate_pipeline.py data/01_messages.jsonl data/02_family_assignments.json data/04_families.json data/05_pairs.json data/08_relations.json data/11_evaluation.json --semantics-json data/09_semantics.json
python3 scripts/14_export_llm_evidence.py data/10_protocol_model.json data/12_llm_evidence.json --evaluation-json data/11_evaluation.json
python3 scripts/15_analyze_with_llm.py data/12_llm_evidence.json data/13_llm_analysis.json --config LLM_config.json --prompt-out data/13_llm_prompt.md
python3 scripts/16_prepare_evaluation_data.py data/10_protocol_model.json data/11_evaluation.json data/13_llm_analysis.json data/14_evaluation_model_data.json
python3 scripts/17_evaluate_protocol_spec.py data/14_evaluation_model_data.json truth-files/modbus.json data/15_evaluation_result.json
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