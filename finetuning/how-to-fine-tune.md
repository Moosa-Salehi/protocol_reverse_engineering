# Fine-tune with the curated cluster-free dataset

This workflow trains the boundary-refinement and semantic-labeling adapter from
the curated cluster-free dataset. All available protocols, including Modbus and
GOOSE, are included before splitting. Every protocol is represented in train,
validation, and test.

Run Windows commands from the repository root. Run Ubuntu commands from the
transferred `finetuning` directory.

## 1. Build protocol records on Windows

The message and annotation layout is:

```text
finetuning/windows_data/runs/<protocol>/01_messages.jsonl
finetuning/cluster-free-dataset/annotations/<protocol>.jsonl
```

Build reviewed cluster-free records for every discovered protocol:

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\finetuning\cluster-free-dataset\build_all_windows.ps1 `
  -MessagesRoot .\finetuning\windows_data\runs `
  -AnnotationsRoot .\finetuning\cluster-free-dataset\annotations `
  -OutputRoot .\finetuning\cluster-free-dataset\data
```

Each annotation must be reviewed and approved. Empty protocol files are not
included in the curated result.

## 2. Curate boundary and semantic records

Create up to 1,000 records per task. The semantic file may contain fewer than
1,000 records when the available annotations do not pass the quality filters.

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\finetuning\cluster-free-dataset\curate_1000_windows.ps1 `
  -DataRoot .\finetuning\cluster-free-dataset\data `
  -Output .\finetuning\cluster-free-dataset\data\curated_1000.jsonl `
  -Tokenizer "Qwen/Qwen2.5-Coder-7B-Instruct" `
  -Count 1000 `
  -ProtocolCap 100
```

This writes the boundary and semantic JSONL files and their summary files.

## 3. Validate, split, and create the VM bundle

```powershell
powershell -ExecutionPolicy Bypass `
  -File .\finetuning\cluster-free-dataset\prepare_combined_windows.ps1 `
  -DataRoot .\finetuning\cluster-free-dataset\data `
  -OutputRoot .\finetuning\cluster-free-dataset\data\split `
  -Tokenizer "Qwen/Qwen2.5-Coder-7B-Instruct" `
  -ValidationFraction 0.1 `
  -TestFraction 0.1 `
  -Seed 42
```

The command validates approvals, chat structure, targets, prompt leakage, and
conflicting supervision. It creates deterministic protocol-stratified
partitions and fails if a protocol cannot occur in all three.

The local split is:

```text
finetuning/cluster-free-dataset/data/split/
├── train.jsonl
├── validation.jsonl
├── test.jsonl
└── summary.json
```

The same command creates:

```text
finetuning/cluster-free-dataset/vm_bundle/finetuning/
├── cluster-free-dataset/
├── dataset-generation/
├── inference/
├── training/
└── data/
    ├── curated.jsonl
    ├── dataset_summary.json
    ├── curated_1000_summary.json
    ├── curated_1000_semantic_summary.json
    └── split/
        ├── train.jsonl
        ├── validation.jsonl
        ├── test.jsonl
        └── summary.json
```

Copy the entire `vm_bundle\finetuning` directory to the Ubuntu VM. Preserve
`test.jsonl` for final evaluation and do not re-split on the VM.

## 4. Prepare the Ubuntu VM

Recommended for the default 7B QLoRA run:

- Ubuntu 24.04
- Python 3.12 (Ubuntu 24.04 default; verified with torch 2.6.0 / unsloth 2025.3.9)
- NVIDIA GPU with at least 16 GB VRAM; 24 GB provides more headroom
- At least 32 GB system RAM
- At least 50 GB free disk

From the transferred `finetuning` directory:

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv build-essential git cmake
bash training/setup_ubuntu.sh
source .venv/bin/activate
```

## 5. Run the smoke test

```bash
bash training/smoke_test_ubuntu.sh
```

The smoke test makes small task-covering train and validation subsets, performs
two optimizer steps, evaluates, verifies adapter saving, and checks that the
untouched test split is present.

## 6. Train

```bash
bash training/train_ubuntu.sh
```

This validates all three partitions, captures the environment, runs the smoke
test, then trains on `train.jsonl` using `validation.jsonl` for evaluation.
The trainer never loads `test.jsonl`.

The equivalent full command is:

```bash
python training/train_unsloth.py \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --train data/split/train.jsonl \
  --validation data/split/validation.jsonl \
  --output output/qwen25-coder-7b-protocol-re \
  --max-seq-length 4096 \
  --rank 16 \
  --gradient-accumulation 16 \
  --learning-rate 1e-4 \
  --epochs 2
```

The trainer uses assistant-response-only loss and rejects examples that exceed
the configured context. It writes:

```text
output/qwen25-coder-7b-protocol-re/
├── adapter/
├── config.json
└── environment.json
```

## 7. Evaluate the preserved test split

```bash
bash inference/run_holdout_comparison.sh \
  data/split/test.jsonl \
  Qwen/Qwen2.5-Coder-7B-Instruct \
  output/qwen25-coder-7b-protocol-re/adapter \
  output/test
```

This writes `base.json`, `finetuned.json`, and `comparison.json` under
`output/test`. Review JSON validity, exact match, precision, recall, and F1
overall and by protocol/task. These are held-out records from known protocols,
not unseen-protocol evaluation.

## 8. Merge and export

Keep the LoRA adapter as the primary artifact. To create a merged model:

```bash
python inference/merge_adapter.py \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --adapter output/qwen25-coder-7b-protocol-re/adapter \
  --output output/merged
```

For GGUF inference, run the scripted pipeline (merge if needed, convert to
F16 GGUF, quantize to Q4_K_M by default) from the bundle root on the VM:

```bash
bash inference/gguf_export_ubuntu.sh
```

The script clones and builds `llama.cpp` on demand (requires `git` and
`cmake`: `sudo apt install -y git cmake`) and writes GGUF files under
`output/qwen25-coder-7b-protocol-re/gguf/`. It accepts the adapter and output
directory as optional arguments and honors `BASE_MODEL`, `QUANT`,
`LLAMA_CPP_DIR`, and `FORCE=1` overrides; see the script header for details.

Preserve the dataset summaries, split summary, adapter, training configuration,
environment capture, and all three test reports with the model.
