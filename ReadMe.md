# Protocol Reverse Engineering

This project is a protocol-agnostic reverse-engineering pipeline for traffic captured in PCAP/PCAPNG files. It turns packet captures into a canonical message corpus, groups similar payloads into message families, infers framing/header clues, field boundaries, discriminator/opcode subformats, request/response relations, and semantic hints, then assembles those signals into a structured protocol model plus Markdown/HTML reports and optional LLM/evaluation artifacts. It is designed for industrial and other binary protocols where the analyst has traffic captures but not a formal specification.

The pipeline is:

1. Optionally collect PCAP/PCAPNG files from an arbitrary source tree into a normalized `pcaps/` directory and remove duplicate captures.
2. Extract payloads into `data/01_messages.jsonl` Using TShark with user filter. Each message records source file, session key, payload hex, length, timestamp and extraction metadata.
3. Discover message families in `data/02_family_assignments.json` by clustering unique payload vectors with HDBSCAN or DBSCAN after optional PCA. Feature modes include raw bytes, symbolic structural features, optional 32D neural latents from `industrial_VAE.pth`, or hybrid structural+neural vectors. When dependencies or the neural model are unavailable, deterministic fallback paths are used; sampled labels are propagated to duplicate payloads and centroid-nearest unsampled unique payloads.
4. Infer protocol-agnostic framing hypotheses in `data/04_framing.json`, including stable prefixes and likely header fields such as length, counter, discriminator, and body/tail variability hints.
5. Extract reusable per-family evidence in `data/03_family_features.json`: length profiles, entropy and uniqueness by offset, byte histograms, n-gram/motif repetition, trailing padding/suffix clues, recurring fixed-position groups, and example message ids.
6. Infer family templates, contiguous segments, and coarse field hypotheses in `data/05_families.json`. Boundary inference uses payload variability plus optional feature/framing evidence, including high-confidence body-start hints, without treating framing-only bytes as protocol fields.
7. Pair likely requests and responses within sessions, discover discriminator/opcode bytes and subformats with learned salience plus symbolic evidence, summarize family-to-family relations, echo fields, length relations, role hints, and semantic field labels.
8. Assemble `data/10_protocol_model.json` from family, feature, framing, discriminator/keyword, relation, and semantic evidence; write pipeline quality metrics to `data/11_evaluation.json`.
9. Export compact LLM evidence, render or call an OpenAI-compatible analysis step, prepare optional ground-truth evaluation input, and compare against a ground-truth protocol JSON when provided.
10. Render final human-readable Markdown and self-contained HTML reports, including evaluation, LLM analysis, and final ground-truth metrics when available.

## Architecture

The pipeline is intentionally protocol-agnostic and evidence-preserving. Extraction creates the canonical corpus consumed by every later stage. Family discovery assigns message ids to payload families so framing, feature extraction, boundary inference, discriminator/opcode discovery, pairing, relation inference, and semantic labeling all work from the same family map. The protocol-model builder then keeps the upstream evidence attached to each family instead of flattening it away, and exporters render the same model into Markdown, HTML, compact LLM evidence, and evaluation inputs.

The package code lives under `src/protocol_re/`; CLI stages live in `scripts/`; generated/intermediate artifacts live in `data/`; final specs go to `output/`.

## Core stages

- `scripts/01_collect_pcaps.py` collects PCAP files from a source tree into one normalized directory.
- `scripts/02_dedup_pcaps.py` finds duplicate PCAP files and can remove them.
- `scripts/03_extract_messages.py` extracts protocol payload messages into the canonical JSONL corpus, using TShark display-filter extraction by default or the Scapy TCP port extractor for compatibility.
- `scripts/04_discover_families.py` discovers message families with DBSCAN, HDBSCAN, or a built-in heuristic fallback; it supports `raw_bytes`, `structural`, `neural`, and `hybrid` feature modes, caches neural latents by payload hash, clusters a unique-message sample, and propagates labels to duplicate payloads across the corpus.
- `scripts/05_infer_framing.py` infers protocol-agnostic framing/header hypotheses from discovered families using stable prefixes, length/correlation/counter/discriminator candidates, and body-tail variability.
- `scripts/06_extract_features.py` writes reusable per-family feature artifacts.
- `scripts/07_infer_boundaries.py` infers templates, contiguous segments, and coarse field hypotheses; with `--features-json` and `--framing-json`, it uses family feature vectors and high-confidence framing body-start hints to refine segment boundaries without adding framing fields as protocol fields.
- `scripts/08_pair_requests_responses.py` emits candidate request/response pairs per session.
- `scripts/09_infer_keywords.py` discovers discriminator/opcode candidates and subformats while preserving backward-compatible keyword output names; it combines learned salience, optional encoder gradients, family/direction mutual information, cardinality, stability, and framing/feature suppression evidence.
- `scripts/10_infer_relations.py` summarizes family-to-family request/response relations, echo fields, and simple role hints.
- `scripts/11_infer_semantics.py` attaches semantic field labels using boundary hypotheses plus request/response evidence.
- `scripts/12_build_protocol_model.py` assembles a protocol-model JSON document matching `schema/protocol_model.schema.json`, including feature, discriminator/keyword, relation, and semantic evidence when supplied.
- `scripts/13_evaluate_pipeline.py` writes pipeline quality metrics for corpus coverage, clustering, boundaries, pairing, relations, and semantic-label coverage when supplied.
- `scripts/14_export_llm_evidence.py` renders a schema-shaped compact per-family evidence bundle for downstream LLM analysis, including compact evaluation metrics when supplied.
- `scripts/15_analyze_with_llm.py` renders the protocol-analysis prompt and can call an OpenAI-compatible LLM API to write `data/13_llm_analysis.json`.
- `scripts/16_prepare_evaluation_data.py` prepares `data/14_evaluation_model_data.json` for final ground-truth evaluation.
- `scripts/17_evaluate_protocol_spec.py` compares `data/14_evaluation_model_data.json` against a ground-truth protocol JSON and writes `data/15_evaluation_result.json`.
- `scripts/18_export_markdown.py` renders a human-readable Markdown protocol specification with evaluation metrics when supplied.
- `scripts/19_export_html.py` renders a self-contained HTML protocol report with model, relation, feature, semantic, and evaluation evidence.

## Feature artifacts

- `family_features.json` contains per-family length statistics, entropy and uniqueness vectors by byte offset, aggregate byte histograms, motif/repetition summaries, top n-gram frequency tables, wider repeated motifs, trailing-block/padding hints, length profiles, and recurring fixed-position groups.
- `main.py` passes `data/03_family_features.json` into boundary inference and passes framing, feature, discriminator/keyword, relation, and semantic artifacts into the protocol-model builder so final models retain the evidence from upstream stages.
- Evaluation reports distinguish corpus assignment coverage from clustering sample ratio, so the configured 100K clustering sample is reported separately from propagated family assignment coverage.

## Family discovery feature modes

Stage 04 accepts `--feature-mode raw_bytes|structural|neural|hybrid`.

- `raw_bytes` preserves the previous padded-byte vector behavior and downweights volatile byte offsets.
- `structural` uses symbolic protocol features such as length buckets, stable prefix masks, discriminator-like bytes, direction, header/body split hints, and length-field evidence.
- `neural` loads `industrial_VAE.pth` when available and encodes each unique payload as a 32D latent vector.
- `hybrid` concatenates the neural 32D latent vector with the structural feature vector.

Neural modes are optional. If PyTorch, the model file, or a compatible encoder object is unavailable, family discovery falls back to symbolic structural features or the existing heuristic path. Latents are cached by payload hash with `--latent-cache-path` to speed repeated runs. The assignment JSON records clustering metadata under `metadata`, including `feature_mode`, `neural_model`, `latent_dim`, `latent_cache`, and `symbolic_feature_count`.

## Discriminator salience

Stage 09 now treats the legacy keyword step as discriminator/opcode candidate discovery. It keeps `data/07_keywords.json` and the `keyword` field for compatibility, but also emits `discriminator_candidates`/`opcode_candidates` with `salience_score`, `mutual_information`, `contrastive_separation`, `excluded_roles`, and `confidence`. Learned salience uses a small cached attention classifier over byte offsets, optional gradient salience from `--neural-model-path` when a compatible PyTorch encoder is available, and symbolic gates for cardinality, offset stability, family/direction mutual information, length-profile separation, and known framing roles. Fields already classified as length, transaction/counter, checksum, timestamp, or payload blob are suppressed.

The runner writes learned salience cache entries to `data/07_salience_cache.json` by default; override with `--discriminator-salience-cache-path`.

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

## Requirements

- Python 3.10+
- Wireshark/TShark installed and available as `tshark` in PATH

This project used `TShark 4.2.2` and `Python 3.12`.

## Installing dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the pipeline

Default PCAP workflow:

```bash
python main.py <folder-containing-pcaps> --tshark-filter <tshark-filter>
```

This command treats the input folder as an existing normalized PCAP directory, extracts up to 200,000 TShark-filtered packet payloads into `data/01_messages.jsonl`, writes intermediate packet metadata to `data/payload_extraction/packets` and carved payloads to `data/payload_extraction/payloads`, runs all inference stages, writes `output/protocol_report.md` and `output/protocol_report.html`. Typical runtime for 200,000 messages: 6 minutes. (3 minutes for message extraction, 2 minutes waiting for llm response).

Useful runner options:

```bash
python main.py files --collect --tshark-filter "udp.srcport == 49152"
python main.py ../pcaps --tshark-filter mbtcp --ground-truth-json ./truth-files/modbus.json
python main.py ../pcaps --extraction-method tcp --service-port 502 --ground-truth-json ./truth-files/modbus.json
python main.py --use-existing-messages --ground-truth-json ./truth-files/modbus.json --llm-render-only
python main.py ../pcaps --tshark-filter s7comm --family-feature-mode hybrid --family-neural-model-path industrial_VAE.pth
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
python3 scripts/03_extract_messages.py pcaps data/01_messages.jsonl --extraction-method tshark --tshark-filter mbtcp --max-messages 200000
python3 scripts/04_discover_families.py data/01_messages.jsonl data/02_family_assignments.json --sample-size 100000 --feature-mode raw_bytes
python3 scripts/05_infer_framing.py data/01_messages.jsonl data/02_family_assignments.json data/04_framing.json
python3 scripts/06_extract_features.py data/01_messages.jsonl data/03_family_features.json --assignments-json data/02_family_assignments.json
python3 scripts/07_infer_boundaries.py data/01_messages.jsonl data/05_families.json --assignments-json data/02_family_assignments.json --features-json data/03_family_features.json --framing-json data/04_framing.json
python3 scripts/08_pair_requests_responses.py data/01_messages.jsonl data/06_pairs.json --assignments-json data/02_family_assignments.json
python3 scripts/09_infer_keywords.py data/01_messages.jsonl data/07_keywords.json --assignments-json data/02_family_assignments.json --features-json data/03_family_features.json --framing-json data/04_framing.json --neural-model-path industrial_VAE.pth --salience-cache-path data/salience_cache.json
python3 scripts/10_infer_relations.py data/01_messages.jsonl data/02_family_assignments.json data/06_pairs.json data/08_relations.json
python3 scripts/11_infer_semantics.py data/05_families.json data/08_relations.json data/09_semantics.json
python3 scripts/12_build_protocol_model.py data/05_families.json data/10_protocol_model.json --features-json data/03_family_features.json --keywords-json data/07_keywords.json --relations-json data/08_relations.json --semantics-json data/09_semantics.json --framing-json data/04_framing.json
python3 scripts/13_evaluate_pipeline.py data/01_messages.jsonl data/02_family_assignments.json data/05_families.json data/06_pairs.json data/08_relations.json data/11_evaluation.json --semantics-json data/09_semantics.json
python3 scripts/14_export_llm_evidence.py data/10_protocol_model.json data/12_llm_evidence.json --evaluation-json data/11_evaluation.json
python3 scripts/15_analyze_with_llm.py data/12_llm_evidence.json data/13_llm_analysis.json --config LLM_config.json --prompt-out data/13_llm_prompt.md
python3 scripts/16_prepare_evaluation_data.py data/10_protocol_model.json data/11_evaluation.json data/13_llm_analysis.json data/14_evaluation_model_data.json
python3 scripts/17_evaluate_protocol_spec.py data/14_evaluation_model_data.json truth-files/modbus.json data/15_evaluation_result.json
python3 scripts/18_export_markdown.py data/10_protocol_model.json output/protocol_report.md --evaluation-json data/11_evaluation.json --llm-analysis-json data/13_llm_analysis.json
python3 scripts/19_export_html.py data/10_protocol_model.json output/protocol_report.html --evaluation-json data/11_evaluation.json --llm-analysis-json data/13_llm_analysis.json
```

To use hybrid structural/neural clustering in the step-by-step flow:

```bash
python3 scripts/04_discover_families.py data/01_messages.jsonl data/02_family_assignments.json --sample-size 100000 --feature-mode hybrid --neural-model-path industrial_VAE.pth --latent-cache-path data/latent_cache.json --neural-batch-size 256
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
