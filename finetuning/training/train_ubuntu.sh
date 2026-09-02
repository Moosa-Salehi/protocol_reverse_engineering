#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
test -f data/split/train.jsonl || { echo "Copy the Windows-prepared data/split/train.jsonl to the VM first"; exit 1; }
test -f data/split/validation.jsonl || { echo "Copy the Windows-prepared data/split/validation.jsonl to the VM first"; exit 1; }
python training/capture_environment.py --output output/qwen25-coder-7b-protocol-re/environment.json
bash training/smoke_test_ubuntu.sh
python training/train_unsloth.py --model Qwen/Qwen2.5-Coder-7B-Instruct --train data/split/train.jsonl --validation data/split/validation.jsonl --output output/qwen25-coder-7b-protocol-re --max-seq-length 4096 --rank 16 --gradient-accumulation 16 --epochs 2
