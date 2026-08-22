#!/usr/bin/env bash
set -euo pipefail
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements-ubuntu.txt
python -c 'import torch; assert torch.cuda.is_available(), "CUDA is not visible"; print(torch.cuda.get_device_name(0)); print("BF16:", torch.cuda.is_bf16_supported())'
python -c 'import unsloth, trl, transformers, peft, datasets; print("unsloth", getattr(unsloth, "__version__", "unknown"), "trl", trl.__version__, "transformers", transformers.__version__, "peft", peft.__version__)'
