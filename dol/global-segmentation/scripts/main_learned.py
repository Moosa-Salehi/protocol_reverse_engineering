"""main.py with the learned-edge rebuild inserted after stage 07 (experiment only).

Usage: LEARNED_EXCLUDE=<protocol> [LEARNED_PERIODIC=1] [LEARNED_GATE=wide [LEARNED_MAX_WIDTH=8]] main_learned.py <main.py arguments>
LEARNED_PERIODIC=1 runs the periodic post-process (loose) after the rebuild, because the
rebuild replaces the array splits stage 07 made.
"""
import os
import sys
from pathlib import Path

ROOT = Path('/mnt/d/tez/practical/protocol_re')
sys.path.insert(0, str(ROOT))
import main as pipeline  # noqa: E402

APPLY = str(Path(__file__).resolve().parent / 'apply_learned.py')
PERIODIC = str(ROOT / 'dol/periodic-array-experiments/scripts/apply_periodic.py')
_build = pipeline.build_pipeline


def build_pipeline(args):
    steps = _build(args)
    d = args.data_dir
    for i, (name, _) in enumerate(steps):
        if name == '07_infer_boundaries':
            extra = [('07l_learned_edges', [APPLY, str(d), '--exclude', os.environ['LEARNED_EXCLUDE'], '--gate', os.environ.get('LEARNED_GATE', 'off')]
                     + (['--max-width', os.environ['LEARNED_MAX_WIDTH']] if os.environ.get('LEARNED_MAX_WIDTH') else []))]
            if os.environ.get('LEARNED_PERIODIC'):
                extra.append(('07p_periodic_arrays', [PERIODIC, str(d / '01_messages.jsonl'), str(d / '02_family_assignments.json'),
                                                      str(d / '05_families.json'), '--mode', 'loose']))
            steps[i + 1:i + 1] = extra
            break
    return steps


pipeline.build_pipeline = build_pipeline
pipeline.main()
