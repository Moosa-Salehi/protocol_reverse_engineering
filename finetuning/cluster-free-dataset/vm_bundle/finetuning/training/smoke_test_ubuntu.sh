#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
nvidia-smi 2>&1 | head -n 12; df -h . | head -n 3; echo
test -f data/split/test.jsonl || { echo "Missing preserved test split: data/split/test.jsonl"; exit 1; }
python dataset-generation/make_smoke_dataset.py \
  --train data/split/train.jsonl \
  --validation data/split/validation.jsonl \
  --output-dir data/smoke
rm -rf output/smoke
python training/train_unsloth.py \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --train data/smoke/train.jsonl \
  --validation data/smoke/validation.jsonl \
  --output output/smoke \
  --max-seq-length 4096 \
  --rank 32 \
  --per-device-batch-size 2 \
  --gradient-accumulation 1 \
  --max-steps 2
test -s output/smoke/adapter/adapter_config.json
test -s output/smoke/adapter/adapter_model.safetensors
test -s output/smoke/config.json
echo "Smoke test passed: CUDA training, evaluation, and adapter saving succeeded."
