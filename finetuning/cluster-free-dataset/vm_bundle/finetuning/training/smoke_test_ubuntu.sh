#!/usr/bin/env bash
set -Eeuo pipefail

cd /home/user01/finetuning
source .venv/bin/activate

echo "=== STEP 1: GPU ==="
nvidia-smi | sed -n '1,12p'

echo "=== STEP 2: DISK ==="
df -h . | sed -n '1,3p'

echo "=== STEP 3: CHECK TEST SPLIT ==="
test -f data/split/test.jsonl || {
    echo "Missing preserved test split: data/split/test.jsonl"
    exit 1
}

echo "=== STEP 4: MAKE SMOKE DATASET ==="
python -u dataset-generation/make_smoke_dataset.py \
    --train data/split/train.jsonl \
    --validation data/split/validation.jsonl \
    --output-dir data/smoke

echo "=== STEP 5: CLEAN OUTPUT ==="
rm -rf output/smoke

echo "=== STEP 6: TRAIN ==="
python -u training/train_unsloth.py \
    --model Qwen/Qwen2.5-Coder-7B-Instruct \
    --train data/smoke/train.jsonl \
    --validation data/smoke/validation.jsonl \
    --output output/smoke \
    --max-seq-length 4096 \
    --rank 32 \
    --per-device-batch-size 2 \
    --gradient-accumulation 1 \
    --max-steps 2

echo "=== STEP 7: CHECK ADAPTER ==="
test -s output/smoke/adapter/adapter_config.json
test -s output/smoke/adapter/adapter_model.safetensors
test -s output/smoke/config.json

echo "Smoke test passed: CUDA training, evaluation, and adapter saving succeeded."