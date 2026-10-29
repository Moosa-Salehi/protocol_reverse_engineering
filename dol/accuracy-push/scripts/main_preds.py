"""main.py with apply_preds.py inserted after stage 07 (experiment only); with SPLIT=1 also
split_by_layout.py after stage 04 (families split by predicted layout before framing).
Usage: PRED_PROTOCOL=<p> PRED_TAG=<tag> [SPLIT=1] main_preds.py <main.py arguments>"""
import os
import sys
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
sys.path.insert(0, str(ROOT))
import main as pipeline  # noqa: E402

APPLY = str(Path(__file__).resolve().parent / 'apply_preds.py')
SPLIT = str(Path(__file__).resolve().parent / 'split_by_layout.py')
_build = pipeline.build_pipeline


def build_pipeline(args):
    steps = _build(args)
    p, tag = os.environ['PRED_PROTOCOL'], os.environ['PRED_TAG']
    for i, (name, _) in enumerate(steps):
        if name == '07_infer_boundaries':
            steps.insert(i + 1, ('07x_predicted_edges', [APPLY, str(args.data_dir), p, tag]))
            break
    if os.environ.get('SPLIT'):
        for i, (name, _) in enumerate(steps):
            if name == '04_discover_families':
                steps.insert(i + 1, ('04x_split_by_layout', [SPLIT, str(args.data_dir), p, tag]))
                break
    return steps


pipeline.build_pipeline = build_pipeline
pipeline.main()
