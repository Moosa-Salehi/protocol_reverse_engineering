#!/usr/bin/env bash
# Merge the trained LoRA adapter into the base model, convert the merged model
# to an F16 GGUF, and quantize it for llama.cpp inference.
#
# Run from the transferred finetuning bundle root (next to data/, training/,
# inference/) after training has produced an adapter.
#
# Usage:
#   bash inference/gguf_export_ubuntu.sh [ADAPTER] [OUT_DIR]
#
# Arguments:
#   ADAPTER   trained LoRA adapter directory   (default output/qwen25-coder-7b-protocol-re/adapter)
#   OUT_DIR   run output directory             (default output/qwen25-coder-7b-protocol-re)
#
# Environment overrides:
#   BASE_MODEL     base model repo       (default Qwen/Qwen2.5-Coder-7B-Instruct)
#   QUANT          llama.cpp quant type  (default Q4_K_M)
#   LLAMA_CPP_DIR  llama.cpp checkout    (default ./llama.cpp, cloned on demand)
#   FORCE          set to 1 to redo merge/convert even if outputs already exist
#
# The merge reuses the Hugging Face cache from training (re-downloads ~15 GB
# only if the base model is absent). Only the small 'gguf' pip package is
# added to the training venv (required by convert_hf_to_gguf.py); the pinned
# stack in training/requirements-ubuntu.txt is never re-resolved.
set -euo pipefail

ADAPTER=${1:-output/qwen25-coder-7b-protocol-re/adapter}
OUT_DIR=${2:-output/qwen25-coder-7b-protocol-re}
BASE_MODEL=${BASE_MODEL:-Qwen/Qwen2.5-Coder-7B-Instruct}
QUANT=${QUANT:-Q4_K_M}
LLAMA_CPP_DIR=${LLAMA_CPP_DIR:-llama.cpp}
FORCE=${FORCE:-0}

if [ ! -f .venv/bin/activate ]; then
  echo "Missing .venv - run 'bash training/setup_ubuntu.sh' first." >&2
  exit 1
fi
# shellcheck source=/dev/null
source .venv/bin/activate

test -f "$ADAPTER/adapter_config.json" || { echo "Missing adapter config: $ADAPTER/adapter_config.json (train first, or pass the adapter path as the first argument)" >&2; exit 1; }
test -f "$ADAPTER/adapter_model.safetensors" || { echo "Missing adapter weights: $ADAPTER/adapter_model.safetensors" >&2; exit 1; }

MERGED_DIR="$OUT_DIR/merged"
GGUF_DIR="$OUT_DIR/gguf"
F16_GGUF="$GGUF_DIR/$(basename "$OUT_DIR")-f16.gguf"
QUANT_GGUF="$GGUF_DIR/$(basename "$OUT_DIR")-${QUANT}.gguf"
mkdir -p "$GGUF_DIR"

echo "== Stage 1/4: merge adapter into $BASE_MODEL =="
if [ "$FORCE" = "1" ] || [ ! -f "$MERGED_DIR/config.json" ]; then
  python inference/merge_adapter.py --model "$BASE_MODEL" --adapter "$ADAPTER" --output "$MERGED_DIR"
else
  echo "Already merged at $MERGED_DIR (set FORCE=1 to redo)"
fi
test -f "$MERGED_DIR/config.json" || { echo "Merge did not produce $MERGED_DIR/config.json" >&2; exit 1; }

echo "== Stage 2/4: prepare llama.cpp =="
if [ ! -d "$LLAMA_CPP_DIR" ]; then
  command -v git >/dev/null 2>&1 || { echo "git not found - install with: sudo apt install -y git" >&2; exit 1; }
  git clone --depth 1 https://github.com/ggml-org/llama.cpp "$LLAMA_CPP_DIR"
fi
QUANTIZE_BIN_CANDIDATES=("$LLAMA_CPP_DIR/build/bin/llama-quantize" "$LLAMA_CPP_DIR/build/bin/quantize" "$LLAMA_CPP_DIR/build/bin/llama-quantize-v2")
QUANTIZE_BIN=""
for c in "${QUANTIZE_BIN_CANDIDATES[@]}"; do if [ -x "$c" ]; then QUANTIZE_BIN="$c"; break; fi; done
if [ -z "$QUANTIZE_BIN" ]; then
  command -v cmake >/dev/null 2>&1 || { echo "cmake not found - install with: sudo apt install -y cmake" >&2; exit 1; }
  cmake -S "$LLAMA_CPP_DIR" -B "$LLAMA_CPP_DIR/build"
  # Use most cores but cap to avoid OOM on 48GB RAM box; llama.cpp build is memory-hungry
  JOBS=$(nproc); [ "$JOBS" -gt 12 ] && JOBS=12
  cmake --build "$LLAMA_CPP_DIR/build" --config Release -j "$JOBS"
  for c in "${QUANTIZE_BIN_CANDIDATES[@]}"; do if [ -x "$c" ]; then QUANTIZE_BIN="$c"; break; fi; done
fi
# fallback: search build tree
if [ -z "$QUANTIZE_BIN" ]; then QUANTIZE_BIN=$(find "$LLAMA_CPP_DIR/build" -maxdepth 4 -type f -name "llama-quantize*" -executable 2>/dev/null | head -n1 || true); fi
test -n "$QUANTIZE_BIN" && test -x "$QUANTIZE_BIN" || { echo "llama-quantize not found (searched $LLAMA_CPP_DIR/build). Try: ls $LLAMA_CPP_DIR/build/bin/" >&2; exit 1; }
echo "Using quantize bin: $QUANTIZE_BIN"
CONVERT_PY="$LLAMA_CPP_DIR/convert_hf_to_gguf.py"
test -f "$CONVERT_PY" || { echo "Missing $CONVERT_PY (llama.cpp checkout incomplete)" >&2; exit 1; }

if ! python -c "import gguf" >/dev/null 2>&1; then
  echo "Installing the 'gguf' package into the training venv (required by convert_hf_to_gguf.py)"
  python -m pip install gguf
fi

echo "== Stage 3/4: convert merged model to F16 GGUF =="
if [ "$FORCE" = "1" ] || [ ! -s "$F16_GGUF" ]; then
  rm -f "$F16_GGUF"
  python "$CONVERT_PY" "$MERGED_DIR" --outfile "$F16_GGUF" --outtype f16
else
  echo "Already converted: $F16_GGUF (set FORCE=1 to redo)"
fi
test -s "$F16_GGUF" || { echo "Conversion did not produce $F16_GGUF" >&2; exit 1; }

echo "== Stage 4/4: quantize to $QUANT =="
rm -f "$QUANT_GGUF"
"$QUANTIZE_BIN" "$F16_GGUF" "$QUANT_GGUF" "$QUANT"
test -s "$QUANT_GGUF" || { echo "Quantization did not produce $QUANT_GGUF" >&2; exit 1; }

echo "GGUF export complete:"
ls -lh "$F16_GGUF" "$QUANT_GGUF"
echo "Copy $QUANT_GGUF off the VM for llama.cpp inference; keep the adapter as the primary artifact."
