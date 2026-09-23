# Local Fine-Tuned Backend for Stages 07b / 11b

The fine-tuned Qwen2.5-Coder-7B adapter
(`finetuning/result/qwen25-coder-7b-protocol-re`) can now serve as the LLM
backend for the pipeline's boundary-refinement (07b) and semantic-labeling
(11b) stages, replacing the OpenAI-compatible API.

## How it works

The adapter was trained on **single-message** evidence in a fixed chat format
(`finetuning/cluster-free-dataset/build_payload_dataset.py`), not on the
family-level evidence bundles stages 07b/11b normally render. The new backend
(`src/protocol_re/llm/local_finetuned.py`) therefore:

1. picks up to `--local-max-samples` **structurally diverse** messages per
   family (length spread, duplicate-payload suppression),
2. renders one **training-format prompt per message**
   (`### TASK: ...` + single-message evidence bundle),
3. sends it to a llama.cpp `llama-server` hosting the Q4_K_M GGUF via its
   OpenAI-compatible endpoint,
4. aggregates per-message predictions into a family-level result:
   - boundaries: per-position consensus (`--local-min-support` of sampled
     messages must agree on an edge),
   - semantic labels: majority vote per (offset, width, role), vote share
     becomes the confidence, then labels are mapped onto the family's
     `field_hypotheses` by exact-then-containment span match,
5. returns a response whose shape the existing stage validators already accept,
   so merge application (07b) and label application (11b) work unchanged.

Per-message raw outputs are preserved in the stage result files
(`data/llm_stage_results/*_<family>.json` → `samples[].raw`) for auditing.

## 1. Start the inference server

```bash
llama-server \
  -m finetuning/result/qwen25-coder-7b-protocol-re/gguf/qwen25-coder-7b-protocol-re-Q4_K_M.gguf \
  --host 127.0.0.1 --port 8080 \
  -c 8192 --temp 0.0 -ngl 99
```

The model name the client sends defaults to `qwen25-coder-7b-protocol-re`;
llama.cpp ignores the name unless `--alias` enforcement is configured, but you
can align it with `--local-model` if your server checks it.

## 2. Run the pipeline stages

Standalone smoke of one family corpus:

```bash
python scripts/07b_refine_boundaries_llm.py \
  data/01_messages.jsonl data/05_families.json data/05_families_refined.json \
  --assignments-json data/02_family_assignments.json \
  --features-json data/03_family_features.json \
  --backend local-finetuned \
  --local-base-url http://127.0.0.1:8080 \
  --local-max-samples 5 --local-min-support 0.5
```

`11b_label_semantics_llm.py` takes the same backend flags.

Through `main.py`, pass the extra args straight through (they are forwarded to
both stages):

```bash
python main.py <pcaps> ... \
  --backend local-finetuned \
  --local-base-url http://127.0.0.1:8080
```

Note: `main.py` currently does not declare these flags; add them to
`parse_args()` (they are plain pass-through strings/floats) or invoke the stage
scripts directly. The stage flags are:

| Flag | Default | Meaning |
|---|---|---|
| `--backend` | `api` | `api` = OpenAI-compatible config; `local-finetuned` = local model |
| `--local-base-url` | `http://127.0.0.1:8080` | llama-server base URL |
| `--local-model` | `qwen25-coder-7b-protocol-re` | model name field |
| `--local-max-samples` | `5` | messages sampled per family |
| `--local-min-support` | `0.5` | consensus threshold (0–1] |
| `--local-timeout` | `300` | per-request timeout seconds |

## Design notes

- **Render-only / cached responses / user-provided responses** still work
  unchanged in `local-finetuned` mode: cached and user-provided responses take
  precedence over server calls (same precedence as the API backend).
- **Confidence gating**: the aggregated boundary response carries
  `confidence: 0.99` so it always passes the merge-suggestion gate; per-label
  confidence for semantics is the consensus vote share, gated by
  `--min-confidence` as usual.
- **Failure semantics**: server unreachable → `LocalBackendError` → stage
  result marked failed → family left unchanged (same warn/fail policy as the
  API backend via `warn_or_fail_stage_failures`).
- **API mode is untouched**: without `--backend local-finetuned`, everything
  behaves exactly as before (`llm_config=None` only occurs when the local
  backend is selected or render-only).

## Testing

- `tests/test_local_finetuned_backend.py` — unit tests: prompt rendering
  byte-matches the SFT format, JSON repair, prediction validation, consensus
  aggregation, and the `llm_call` integration hooks in both stages.
- `tests/mock_llama_server.py` — a mock llama-server for end-to-end smoke
  tests without a GPU:
  ```bash
  python tests/mock_llama_server.py 8901 &
  python scripts/07b_refine_boundaries_llm.py ... --backend local-finetuned \
      --local-base-url http://127.0.0.1:8901
  ```
