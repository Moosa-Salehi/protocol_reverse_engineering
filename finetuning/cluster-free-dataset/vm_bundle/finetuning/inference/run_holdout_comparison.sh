#!/usr/bin/env bash
set -euo pipefail
# Tuned for Quadro RTX 8000 48GB - full 7B eval fits in FP16; pre-flight prints GPU/disk.
if [ ! -f .venv/bin/activate ]; then echo "Missing .venv - run 'bash training/setup_ubuntu.sh' first." >&2; exit 1; fi
# shellcheck source=/dev/null
source .venv/bin/activate
echo "== holdout pre-flight =="; nvidia-smi 2>&1 | head -n 12; df -h . | head -n 3; echo
DATA=${1:-data/split/test.jsonl}
MODEL=${2:-Qwen/Qwen2.5-Coder-7B-Instruct}
ADAPTER=${3:-output/qwen25-coder-7b-protocol-re/adapter}
OUT_DIR=${4:-output/test}
mkdir -p "$OUT_DIR"
test -f "$DATA" || { echo "Missing eval data: $DATA" >&2; exit 1; }
python inference/evaluate_holdout.py --data "$DATA" --model "$MODEL" --output "$OUT_DIR/base.json"
python inference/evaluate_holdout.py --data "$DATA" --model "$MODEL" --adapter "$ADAPTER" --output "$OUT_DIR/finetuned.json"
python inference/compare_holdout_reports.py --base "$OUT_DIR/base.json" --finetuned "$OUT_DIR/finetuned.json" --output "$OUT_DIR/comparison.json"
echo "Test comparison written to $OUT_DIR/comparison.json"
ls -lh "$OUT_DIR"/{base,finetuned,comparison}.json
