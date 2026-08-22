#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
python dataset-generation/make_smoke_dataset.py \
  --train data/split/train.jsonl \
  --validation data/split/validation.jsonl \
  --output-dir data/smoke
rm -rf output/smoke
python training/train_unsloth.py \
  --model Qwen/Qwen2.5-14B-Instruct \
  --train data/smoke/train.jsonl \
  --validation data/smoke/validation.jsonl \
  --output output/smoke \
  --max-seq-length 4096 \
  --rank 16 \
  --gradient-accumulation 1 \
  --max-steps 2
test -s output/smoke/adapter/adapter_config.json
test -s output/smoke/adapter/adapter_model.safetensors
test -s output/smoke/config.json
echo "Smoke test passed: CUDA training, evaluation, and adapter saving succeeded."
