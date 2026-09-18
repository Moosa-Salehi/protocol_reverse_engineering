#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
echo "== pre-flight: GPU / disk =="; nvidia-smi 2>&1 | head -n 20; df -h . | head -n 5; echo
test -f data/split/train.jsonl || { echo "Copy the Windows-prepared data/split/train.jsonl to the VM first"; exit 1; }
test -f data/split/validation.jsonl || { echo "Copy the Windows-prepared data/split/validation.jsonl to the VM first"; exit 1; }
test -f data/split/test.jsonl || { echo "Copy the Windows-prepared data/split/test.jsonl to the VM first"; exit 1; }
python cluster-free-dataset/validate_dataset.py data/split/train.jsonl
python cluster-free-dataset/validate_dataset.py data/split/validation.jsonl
python cluster-free-dataset/validate_dataset.py data/split/test.jsonl
python training/capture_environment.py --output output/qwen25-coder-7b-protocol-re/environment.json
bash training/smoke_test_ubuntu.sh
python training/train_unsloth.py --model Qwen/Qwen2.5-Coder-7B-Instruct --train data/split/train.jsonl --validation data/split/validation.jsonl --output output/qwen25-coder-7b-protocol-re --max-seq-length 4096 --rank 32 --per-device-batch-size 2 --gradient-accumulation 8 --epochs 2
