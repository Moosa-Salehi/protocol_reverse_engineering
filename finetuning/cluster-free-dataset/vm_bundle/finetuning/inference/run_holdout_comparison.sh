#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -f ".venv/bin/activate" ]]; then
    echo "ERROR: Missing .venv - run 'bash training/setup_ubuntu.sh' first." >&2
    exit 1
fi

source .venv/bin/activate

DATA="${1:-data/split/test.jsonl}"
MODEL="${2:-Qwen/Qwen2.5-Coder-7B-Instruct}"
ADAPTER="${3:-output/qwen25-coder-7b-protocol-re/adapter}"
OUT_DIR="${4:-output/test}"

export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export HF_HUB_CACHE="${HF_HUB_CACHE:-$HF_HOME/hub}"

echo "== Holdout pre-flight =="
echo "Root:       $ROOT_DIR"
echo "Data:       $DATA"
echo "Model:      $MODEL"
echo "Adapter:    $ADAPTER"
echo "Output:     $OUT_DIR"
echo "HF_HOME:    $HF_HOME"
echo

echo "== GPU =="
if ! nvidia-smi; then
    echo "ERROR: nvidia-smi failed." >&2
    exit 1
fi

echo
echo "== Disk =="
df -h .

echo

if [[ ! -f "$DATA" ]]; then
    echo "ERROR: Missing evaluation data: $DATA" >&2
    exit 1
fi

if [[ ! -d "$ADAPTER" ]]; then
    echo "ERROR: Missing adapter directory: $ADAPTER" >&2
    exit 1
fi

if [[ ! -s "$ADAPTER/adapter_config.json" ]]; then
    echo "ERROR: Missing or empty adapter_config.json" >&2
    exit 1
fi

if [[ ! -s "$ADAPTER/adapter_model.safetensors" ]]; then
    echo "ERROR: Missing or empty adapter_model.safetensors" >&2
    exit 1
fi

if ! command -v python >/dev/null 2>&1; then
    echo "ERROR: python not found inside .venv." >&2
    exit 1
fi

mkdir -p "$OUT_DIR"

echo
echo "== STEP 1: Evaluate base model =="

python inference/evaluate_holdout.py \
    --data "$DATA" \
    --model "$MODEL" \
    --output "$OUT_DIR/base.json" \
    --dtype fp16

echo
echo "== STEP 2: Evaluate fine-tuned model =="

python inference/evaluate_holdout.py \
    --data "$DATA" \
    --model "$MODEL" \
    --adapter "$ADAPTER" \
    --output "$OUT_DIR/finetuned.json" \
    --dtype fp16

echo
echo "== STEP 3: Compare reports =="

python inference/compare_holdout_reports.py \
    --base "$OUT_DIR/base.json" \
    --finetuned "$OUT_DIR/finetuned.json" \
    --output "$OUT_DIR/comparison.json"

echo
echo "== Holdout evaluation complete =="
echo "Comparison written to: $OUT_DIR/comparison.json"

ls -lh \
    "$OUT_DIR/base.json" \
    "$OUT_DIR/finetuned.json" \
    "$OUT_DIR/comparison.json"
