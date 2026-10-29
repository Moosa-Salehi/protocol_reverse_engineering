"""main.py with the periodic-array post-process inserted after stage 07 (experiment only).

Usage: PERIODIC_MODE=loose main_periodic.py <main.py arguments>
"""
import os
import sys
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
sys.path.insert(0, str(ROOT))
import main as pipeline  # noqa: E402

APPLY = str(Path(__file__).resolve().parent / 'apply_periodic.py')
_build = pipeline.build_pipeline


def build_pipeline(args):
    steps = _build(args)
    d = args.data_dir
    for i, (name, _) in enumerate(steps):
        if name == '07_infer_boundaries':
            steps.insert(i + 1, ('07p_periodic_arrays', [APPLY, str(d / '01_messages.jsonl'), str(d / '02_family_assignments.json'),
                                                         str(d / '05_families.json'), '--mode', os.environ.get('PERIODIC_MODE', 'loose')]))
            break
    return steps


pipeline.build_pipeline = build_pipeline
pipeline.main()
