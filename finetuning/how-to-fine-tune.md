# How to fine-tune the protocol-re model

This guide covers the complete workflow: generate evidence and trusted targets on Windows, automatically approve/check/split the dataset, train on Ubuntu with CUDA, evaluate unseen protocols, and export the model.

Run Windows commands from the repository root. Run Ubuntu commands from the `finetuning` directory unless a section says otherwise.

## What is manual and what is automatic?

Only commands shown in a code block are commands for the user to run. Commands inside a script are run automatically by that script and must not also be run individually unless you are diagnosing a failed stage.

Manual decisions cannot safely be automated:

- Choose training versus holdout protocols (stage 1).
- Install Windows prerequisites and select the PCAP directory (stage 2).
- Create and verify trusted Wireshark target mappings (stage 4). This is the ground truth for training, so generating it from the pipeline's own predictions would invalidate the experiment.
- Copy the prepared bundle to the VM, because the VM address and transfer method are environment-specific.
- Review evaluation results and decide whether a model is acceptable.

User-run entry points:

1. `build_dataset_windows.ps1` generates samples, pipeline evidence, and candidate JSONL.
2. After trusted target review, rerun `build_dataset_windows.ps1`; it regenerates candidate JSONL for all configured protocols.
3. `prepare_dataset_windows.ps1` promotes approved records, assembles/audits/summarizes/splits the dataset, and creates the complete VM input bundle.
4. `setup_ubuntu.sh` creates the Ubuntu environment.
5. `smoke_test_ubuntu.sh` verifies the transferred dataset and GPU training environment.
6. `train_ubuntu.sh` captures the environment, runs another smoke test, and performs full training using the split prepared on Windows.
7. Evaluation, merge, conversion, and Windows inference remain explicit commands because they are separate decisions/artifact-producing operations.

## 1. Choose training and holdout protocols

Edit `dataset-generation/protocols.json` before generating data:

```json
{
  "train": {
    "cip": {"filter": "cip", "aliases": ["cip"]}
  },
  "holdout": {
    "modbus": {"filter": "mbtcp || modbus", "aliases": ["modbus", "mbtcp"]}
  }
}
```

- `filter` is a TShark display filter.
- `aliases` are used by the leakage audit.
- Holdout protocols must never be copied into the training JSONL.
- Keep at least one or two protocols completely unseen during training. Modbus and GOOSE are the current defaults.

## 2. Prepare Windows

Install:

- Python supported by the main repository.
- Wireshark, including `tshark.exe` and `mergecap.exe`.
- The normal `protocol_re` Python dependencies.

Verify the external commands:

```powershell
tshark --version
mergecap --version
py --version
```

Place PCAP, PCAPNG, or CAP files under one directory. The sampler searches it recursively.

## 3. Generate sampled PCAPs and pipeline evidence

From the repository root:

```powershell
.\finetuning\dataset-generation\build_dataset_windows.ps1 `
  -PcapDir "D:\traffic\pcaps" `
  -BudgetPerProtocol 20000 `
  -MaxMessages 20000 `
  -IncludeHoldout
```

Configuration:

- Omit `-IncludeHoldout` when generating only training protocols.
- `BudgetPerProtocol` controls the sampled packet budget for each protocol.
- `MaxMessages` limits messages processed by the main pipeline.
- Use `-Python "C:\path\to\python.exe"` if `py` is not the desired interpreter.

Important outputs:

```text
finetuning/windows_data/
├── sampled_pcaps/
│   └── sampling_report.json
├── runs/<protocol>/data/
│   ├── 10_protocol_model.json
│   └── 12_llm_evidence.json
└── candidate_jsonl/
    ├── train/
    └── holdout/
```

The first run generates conservative Wireshark target candidates and review reports. It deliberately waits for review before creating approved training JSONL.

## 4. Review automatically generated Wireshark targets

Stage 3 runs TShark's `jsonraw` export on each sampled capture and creates one target file per protocol:

```text
finetuning/windows_data/wireshark_targets/<protocol>.json
```

It joins TShark packets to the pipeline corpus and family assignments, converts frame-relative offsets to pipeline-payload-relative offsets, and accepts only fields with an unambiguous semantic mapping and repeated packet support. It also creates:

```text
finetuning/windows_data/wireshark_target_reports/<protocol>.review.json
```

Review this report and the generated target file. Confirm the accepted mappings, correct any wrong mapping, and manually resolve only important fields listed under `ambiguous` or `unmatched`. This reduces stage 4 to exception review instead of entering every field manually.

The file maps pipeline family IDs to trusted Wireshark fields. It must follow `dataset-generation/wireshark_targets.schema.json`:

```json
{
  "family_0": [
    {
      "offset": 0,
      "width": 2,
      "wireshark_name": "Transaction identifier",
      "semantic_role": "transaction_id",
      "field_type": "integer",
      "encoding_type": "uint16_be"
    }
  ]
}
```

Requirements:

- `offset` is relative to the protocol payload used by the pipeline.
- `width` is in bytes and must match the corresponding pipeline field.
- `semantic_role` must be in the taxonomy accepted by `build_evidence_dataset.py`.
- Wireshark names are used only in targets/audit evidence; they are removed from prompts.

After making corrections, rerun stage 3 with `-SkipTargetGeneration` so it preserves the reviewed target files and regenerates candidate JSONL:

```powershell
.\finetuning\dataset-generation\build_dataset_windows.ps1 `
  -PcapDir "D:\traffic\pcaps" `
  -BudgetPerProtocol 20000 `
  -MaxMessages 20000 `
  -IncludeHoldout `
  -SkipTargetGeneration
```

To regenerate just one protocol's JSONL while correcting a target, use:

```powershell
py .\finetuning\dataset-generation\build_evidence_dataset.py `
  .\finetuning\windows_data\runs\cip\data\10_protocol_model.json `
  .\finetuning\windows_data\candidate_jsonl\train\cip.jsonl `
  --evidence-bundle .\finetuning\windows_data\runs\cip\data\12_llm_evidence.json `
  --wireshark-targets .\finetuning\windows_data\wireshark_targets\cip.json
```

For Modbus, GOOSE, or another holdout protocol, write the output under `candidate_jsonl\holdout`.

Optional builder arguments:

```text
--tasks boundary_refinement semantic_labeling
--max-families 20
```

Each JSONL has a sibling `.summary.json` containing written and skipped counts. `-MinimumTargetSupport` controls how many observations a mapping needs; the default is 2. Increasing it is more conservative.

## 5. Automatically approve, assemble, audit, summarize, and split

Records generated from trusted Wireshark targets carry Wireshark approval metadata. The following single command performs the former stages 5, 6, 8, 9, and 10 for every candidate file:

```powershell
.\finetuning\dataset-generation\prepare_dataset_windows.ps1
```

It automatically:

- Promotes all structurally valid `reviewed=true`, `approved=true` candidate records.
- Concatenates training protocols into `raw.jsonl` and holdouts into `holdout.jsonl` without mixing them.
- Runs leakage and shared-source-PCAP checks.
- Downloads/loads the Qwen tokenizer and writes tokenizer-aware dataset statistics.
- Creates the family-grouped training/validation split with seed 42.

The first tokenizer load may download files from Hugging Face. Use `-Python "C:\path\to\python.exe"` if needed. If a target source is not trusted, its records must remain unapproved; do not bypass the promotion gate.

Output:

```text
finetuning/windows_data/vm_bundle/finetuning/data/
├── raw.jsonl
├── holdout.jsonl
├── sampling_report.json       # when available
├── dataset_summary.json
└── split/
    ├── train.jsonl
    ├── validation.jsonl
    └── summary.json
```

## 6. Copy the exact VM input files

Stage 5 automatically creates this exact bundle:

```text
finetuning/
├── dataset-generation/
├── inference/
├── training/
└── data/
```

It intentionally excludes `.venv`, `windows_data`, `output`, and `__pycache__`. Transfer only `finetuning/windows_data/vm_bundle/finetuning` by your normal shared-folder, SCP, or archive workflow. Place it anywhere in the Ubuntu user's writable storage, then enter that directory. Before the smoke test, the VM must have at least these files:

```text
finetuning/training/requirements-ubuntu.txt
finetuning/training/setup_ubuntu.sh
finetuning/training/smoke_test_ubuntu.sh
finetuning/training/train_unsloth.py
finetuning/dataset-generation/make_smoke_dataset.py
finetuning/data/raw.jsonl
finetuning/data/holdout.jsonl
finetuning/data/split/train.jsonl
finetuning/data/split/validation.jsonl
```

## 7. Set up Ubuntu and CUDA

Recommended for Qwen2.5-14B QLoRA:

- Ubuntu 24.04
- Python 3.11
- NVIDIA GPU with 24 GB VRAM, such as RTX 3090
- At least 32 GB system RAM for training
- 64 GB system RAM minimum for merging the full 14B model; 80-96 GB is recommended to avoid out-of-memory failures
- At least 80 GB free disk for the model cache, merged FP16 model, and temporary/output files (more if retaining multiple copies)

From the `finetuning` directory:

```bash
bash training/setup_ubuntu.sh
source .venv/bin/activate
```

The setup installs pinned versions from `training/requirements-ubuntu.txt`, verifies CUDA, and reports BF16 support.

## 8. Optional: rerun individual dataset checks on Ubuntu

The former stages 8-10 are dataset preparation and now run automatically on Windows in stage 5. They appear here only as optional diagnostic commands and are not rerun by `train_ubuntu.sh`.

Leakage audit:

```bash
python dataset-generation/audit_leakage.py \
  --train data/raw.jsonl \
  --holdout data/holdout.jsonl
```

If `sampling_report.json` was copied to the VM, also check whether the same source captures contributed to train and holdout:

```bash
python dataset-generation/audit_leakage.py \
  --train data/raw.jsonl \
  --holdout data/holdout.jsonl \
  --sampling-report data/sampling_report.json
```

The audit rejects prompt overlap, within-set duplicate prompts, protocol aliases in prompts, target markers in prompts, and optionally shared source PCAPs.

### Dataset quality

Generate tokenizer-aware statistics:

```bash
python dataset-generation/summarize_dataset.py \
  data/raw.jsonl \
  --tokenizer Qwen/Qwen2.5-14B-Instruct \
  --output data/dataset_summary.json
```

Check protocol and task balance, family counts, prompt-token p95/max, target lengths, and target density. Prompts longer than the configured training context will be rejected later.

### Training/validation split

```bash
python dataset-generation/prepare_dataset.py \
  data/raw.jsonl data/split \
  --validation-fraction 0.1 \
  --seed 42
```

The split is grouped by protocol and family, so a family cannot appear in both training and validation. Both tasks must occur in both subsets.

Outputs:

```text
data/split/train.jsonl
data/split/validation.jsonl
data/split/summary.json
```

This validation split measures performance on known training protocols. `data/holdout.jsonl` measures cross-protocol generalization and is never passed to the trainer.

## 9. Run the smoke test

```bash
bash training/smoke_test_ubuntu.sh
```

It creates task-covering subsets, trains for two optimizer steps, evaluates, saves an adapter, and checks the expected files under `output/smoke`.

## 10. Train

The complete automated command is:

```bash
bash training/train_ubuntu.sh
```

It verifies that the Windows-prepared split exists, captures the environment, runs the smoke test, and performs full training. It does not repeat leakage auditing, dataset summarization, or splitting.

Default full-training command:

```bash
python training/train_unsloth.py \
  --model Qwen/Qwen2.5-14B-Instruct \
  --train data/split/train.jsonl \
  --validation data/split/validation.jsonl \
  --output output/qwen25-14b-protocol-re \
  --max-seq-length 4096 \
  --rank 16 \
  --gradient-accumulation 16 \
  --learning-rate 1e-4 \
  --epochs 2
```

Useful options:

- `--rank`: LoRA rank. Higher values increase capacity and memory use.
- `--gradient-accumulation`: effective batch accumulation.
- `--learning-rate`: defaults to `1e-4`.
- `--epochs`: defaults to `2`.
- `--max-steps`: overrides epochs and is intended for tests.
- `--max-seq-length`: examples longer than this cause a hard failure and an `oversized_examples.json` report.

Artifacts include:

```text
output/qwen25-14b-protocol-re/
├── adapter/
├── config.json
└── environment.json
```

## 11. Evaluate base model versus adapter

Run both models on the identical holdout file:

```bash
bash inference/run_holdout_comparison.sh \
  data/holdout.jsonl \
  Qwen/Qwen2.5-14B-Instruct \
  output/qwen25-14b-protocol-re/adapter \
  output/holdout
```

Outputs:

```text
output/holdout/base.json
output/holdout/finetuned.json
output/holdout/comparison.json
```

Review overall, per-protocol, and per-family JSON validity, exact match, precision, recall, F1, and metric deltas. Positive deltas are improvements; negative deltas are regressions.

To run a single evaluation with custom limits:

```bash
python inference/evaluate_holdout.py \
  --data data/holdout.jsonl \
  --model Qwen/Qwen2.5-14B-Instruct \
  --adapter output/qwen25-14b-protocol-re/adapter \
  --output output/holdout/custom.json \
  --max-input-tokens 4096 \
  --max-new-tokens 512 \
  --seed 42
```

## 12. Merge and convert to GGUF

Qwen2.5-14B has roughly 28 GB of FP16 weights. Loading, merging, and serializing require additional working memory, so use 64 GB RAM as the practical minimum and 80-96 GB when possible. Close other memory-heavy programs before merging:

```bash
python inference/merge_adapter.py \
  --model Qwen/Qwen2.5-14B-Instruct \
  --adapter output/qwen25-14b-protocol-re/adapter \
  --output output/merged
```

Convert and quantize with `llama.cpp`:

```bash
python /path/to/llama.cpp/convert_hf_to_gguf.py \
  output/merged \
  --outfile output/protocol-re-f16.gguf \
  --outtype f16

/path/to/llama.cpp/build/bin/llama-quantize \
  output/protocol-re-f16.gguf \
  output/protocol-re-Q4_K_M.gguf \
  Q4_K_M
```

## 13. Copy results back to Windows and run GGUF inference

Copy these result paths from the VM back to Windows after training/evaluation:

```text
finetuning/output/qwen25-14b-protocol-re/adapter/
finetuning/output/qwen25-14b-protocol-re/config.json
finetuning/output/qwen25-14b-protocol-re/environment.json
finetuning/output/holdout/base.json
finetuning/output/holdout/finetuned.json
finetuning/output/holdout/comparison.json
```

If merge/conversion ran on the VM, also copy:

```text
finetuning/output/merged/                    # optional; large HF model
finetuning/output/protocol-re-f16.gguf       # optional; very large
finetuning/output/protocol-re-Q4_K_M.gguf    # required for the Windows command below
```

Install a CUDA-enabled `llama.cpp` build and place `llama-cli.exe` on `PATH`:

```powershell
.\finetuning\inference\infer_windows.ps1 `
  -Model "D:\Models\protocol-re-Q4_K_M.gguf" `
  -PromptFile ".\data\rendered_boundary_prompt.txt" `
  -Seed 42 `
  -MaxTokens 512
```

The prompt file must contain the same `### TASK:` and `Evidence Bundle` structure used during training. Inference is deterministic by default.

## 14. Preserve artifacts

Keep these files with every experiment:

- Approved training and holdout JSONL.
- `sampling_report.json`.
- Per-protocol dataset summaries.
- `data/dataset_summary.json`.
- `data/split/summary.json`.
- Adapter directory and training `config.json`.
- `environment.json`.
- Base, fine-tuned, and comparison holdout reports.
- Merged model and GGUF files, if produced.

These artifacts are required to reproduce the run and determine whether fine-tuning improved unseen-protocol performance.
