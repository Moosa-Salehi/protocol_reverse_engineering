#!/usr/bin/env bash
set -euo pipefail
DATA=${1:-data/holdout.jsonl}
MODEL=${2:-Qwen/Qwen2.5-Coder-7B-Instruct}
ADAPTER=${3:-output/qwen25-coder-7b-protocol-re/adapter}
OUT_DIR=${4:-output/holdout}
mkdir -p "$OUT_DIR"
python inference/evaluate_holdout.py --data "$DATA" --model "$MODEL" --output "$OUT_DIR/base.json"
python inference/evaluate_holdout.py --data "$DATA" --model "$MODEL" --adapter "$ADAPTER" --output "$OUT_DIR/finetuned.json"
python inference/compare_holdout_reports.py --base "$OUT_DIR/base.json" --finetuned "$OUT_DIR/finetuned.json" --output "$OUT_DIR/comparison.json"
echo "Holdout comparison written to $OUT_DIR/comparison.json"
