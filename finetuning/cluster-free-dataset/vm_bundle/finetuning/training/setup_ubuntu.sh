#!/usr/bin/env bash
set -euo pipefail

# Quadro RTX 8000 (48 GB, Turing TU102, sm_75) aware setup for Ubuntu 24.04.
# - picks python3.11 if present, else python3.12 / python3 (24.04 default is 3.12)
# - verifies nvidia-smi + ~80 GB free before creating the venv
# - Quadro 8000 does NOT support BF16 -> training will use FP16 (handled in train_unsloth.py)

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "== nvidia-smi =="; nvidia-smi || true
else
  echo "WARNING: nvidia-smi not found - did the driver install + reboot complete?" >&2
fi

echo "== disk =="; df -h .; echo
# warn if <80 GB free (need ~50 GB for model/cache/gguf + headroom)
FREE_GB=$(df -BG . | awk 'NR==2{gsub(/G/,"",$4); print $4+0}')
if [ "${FREE_GB:-0}" -lt 80 ]; then
  echo "WARNING: only ${FREE_GB}GB free on $(pwd) - want ~100 GB free (200 GB disk)." >&2
  echo "If this is a cloud VM, expand the partition: sudo growpart /dev/sda 1 && sudo resize2fs /dev/sda1" >&2
fi

# pick python interpreter
if command -v python3.11 >/dev/null 2>&1; then PYTHON=python3.11
elif command -v python3.12 >/dev/null 2>&1; then PYTHON=python3.12
elif command -v python3 >/dev/null 2>&1; then PYTHON=python3
else echo "No python3 found" >&2; exit 1; fi
echo "Using $PYTHON ($($PYTHON --version 2>&1))"
if ! $PYTHON -m venv --help >/dev/null 2>&1; then
  echo "python venv module missing - install: sudo apt install -y ${PYTHON}-venv python3-venv" >&2; exit 1
fi

if [ -d .venv ]; then echo "Reusing existing .venv (rm -rf .venv to recreate)"; else $PYTHON -m venv .venv; fi
# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r training/requirements-ubuntu.txt
# CUDA sanity check - Quadro 8000 is Turing, so BF16 will be False and training uses FP16
python -c 'import torch; assert torch.cuda.is_available(), "CUDA is not visible (driver not loaded?)"; print("GPU:", torch.cuda.get_device_name(0)); print("CUDA:", torch.version.cuda); print("BF16 supported:", torch.cuda.is_bf16_supported(), "(False is expected on Quadro RTX 8000 - will use FP16)")'
python -c 'import unsloth, trl, transformers, peft, datasets; print("unsloth", getattr(unsloth, "__version__", "unknown"), "trl", trl.__version__, "transformers", transformers.__version__, "peft", peft.__version__)'
echo "Setup complete. Activate with: source .venv/bin/activate"
