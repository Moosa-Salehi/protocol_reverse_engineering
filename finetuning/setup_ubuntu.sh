#!/usr/bin/env bash
set -euo pipefail
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel
python -m pip install -r requirements-ubuntu.txt
python -c 'import torch; assert torch.cuda.is_available(), "CUDA is not visible"; print(torch.cuda.get_device_name(0))'
