#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
test -f data/raw.jsonl || { echo "Upload/concatenate reviewed protocol JSONL files into data/raw.jsonl first"; exit 1; }
python prepare_dataset.py data/raw.jsonl data/split
python train_unsloth.py --train data/split/train.jsonl --validation data/split/validation.jsonl --output output/qwen-protocol-re --max-seq-length 4096
