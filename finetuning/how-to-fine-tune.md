# How to fine-tune the protocol-re model

This guide covers the complete workflow: generate evidence and trusted targets on Windows, approve and split the dataset, train on Ubuntu with CUDA, evaluate unseen protocols, and export the model.

Run Windows commands from the repository root. Run Ubuntu commands from the `finetuning` directory unless a section says otherwise.

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

On the first run, candidate generation may be skipped because trusted target files do not exist yet. The pipeline evidence is still produced.

## 4. Configure trusted Wireshark targets

Create one file per protocol:

```text
finetuning/windows_data/wireshark_targets/<protocol>.json
```

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

After creating a target file, generate its JSONL directly without rerunning PCAP sampling:

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

Each JSONL has a sibling `.summary.json` containing written and skipped counts.

## 5. Promote approved data

Records generated from trusted Wireshark targets carry Wireshark approval metadata. Run the structural promotion gate for every file:

```powershell
py .\finetuning\dataset-generation\promote_reviewed.py `
  .\finetuning\windows_data\candidate_jsonl\train\cip.jsonl `
  .\finetuning\windows_data\approved\train\cip.jsonl

py .\finetuning\dataset-generation\promote_reviewed.py `
  .\finetuning\windows_data\candidate_jsonl\holdout\modbus.jsonl `
  .\finetuning\windows_data\approved\holdout\modbus.jsonl
```

If a target source is not trusted, set `reviewed` and `approved` to false until it has been checked. Do not bypass the promotion step.

## 6. Assemble files for Ubuntu

Copy the approved protocol JSONL files to the Ubuntu VM. Under `finetuning`, create:

```text
data/
├── approved/
│   └── <training protocol>.jsonl
└── holdout-approved/
    └── <holdout protocol>.jsonl
```

Concatenate them separately:

```bash
mkdir -p data/approved data/holdout-approved
cat data/approved/*.jsonl > data/raw.jsonl
cat data/holdout-approved/*.jsonl > data/holdout.jsonl
```

Never include a holdout file in `data/raw.jsonl`.

## 7. Set up Ubuntu and CUDA

Recommended for Qwen2.5-14B QLoRA:

- Ubuntu 24.04
- Python 3.11
- NVIDIA GPU with 24 GB VRAM, such as RTX 3090
- At least 32 GB system RAM for training
- More RAM for merging the full model

From the `finetuning` directory:

```bash
bash training/setup_ubuntu.sh
source .venv/bin/activate
```

The setup installs pinned versions from `training/requirements-ubuntu.txt`, verifies CUDA, and reports BF16 support.

## 8. Audit leakage

Run the audit before training:

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

## 9. Inspect dataset quality

Generate tokenizer-aware statistics:

```bash
python dataset-generation/summarize_dataset.py \
  data/raw.jsonl \
  --tokenizer Qwen/Qwen2.5-14B-Instruct \
  --output data/dataset_summary.json
```

Check protocol and task balance, family counts, prompt-token p95/max, target lengths, and target density. Prompts longer than the configured training context will be rejected later.

## 10. Split the training dataset

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

## 11. Run the smoke test

```bash
bash training/smoke_test_ubuntu.sh
```

It creates task-covering subsets, trains for two optimizer steps, evaluates, saves an adapter, and checks the expected files under `output/smoke`.

## 12. Train

The complete automated command is:

```bash
bash training/train_ubuntu.sh
```

It runs leakage auditing, dataset summarization, environment capture, splitting, the smoke test, and full training.

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

## 13. Evaluate base model versus adapter

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

## 14. Merge and convert to GGUF

Merging a 14B model can require substantially more than 32 GB of system RAM. Perform this step on a machine with sufficient CPU memory:

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

## 15. Run GGUF inference on Windows

Install a CUDA-enabled `llama.cpp` build and place `llama-cli.exe` on `PATH`:

```powershell
.\finetuning\inference\infer_windows.ps1 `
  -Model "D:\Models\protocol-re-Q4_K_M.gguf" `
  -PromptFile ".\data\rendered_boundary_prompt.txt" `
  -Seed 42 `
  -MaxTokens 512
```

The prompt file must contain the same `### TASK:` and `Evidence Bundle` structure used during training. Inference is deterministic by default.

## 16. Preserve artifacts

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
