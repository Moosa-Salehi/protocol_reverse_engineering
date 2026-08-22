#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
test -f data/raw.jsonl || { echo "Upload/concatenate reviewed protocol JSONL files into data/raw.jsonl first"; exit 1; }
if test -f data/holdout.jsonl; then
  python dataset-generation/audit_leakage.py --train data/raw.jsonl --holdout data/holdout.jsonl
else
  python dataset-generation/audit_leakage.py --train data/raw.jsonl
fi
python dataset-generation/summarize_dataset.py data/raw.jsonl --tokenizer Qwen/Qwen2.5-14B-Instruct --output data/dataset_summary.json
python dataset-generation/prepare_dataset.py data/raw.jsonl data/split
bash training/smoke_test_ubuntu.sh
python training/train_unsloth.py --model Qwen/Qwen2.5-14B-Instruct --train data/split/train.jsonl --validation data/split/validation.jsonl --output output/qwen25-14b-protocol-re --max-seq-length 4096 --rank 16 --gradient-accumulation 16 --epochs 2
