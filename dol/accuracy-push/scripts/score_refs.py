"""Score reference families files against the active annotation set (ANNSET env).
Usage: [ANNSET=truthconv] score_refs.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import qh
REFS = {'rules (current stage 07)': lambda p: qh.GS / 'bench-current' / p / 'data' / '05_families.json',
        'gated (>2 B fields)': lambda p: qh.GS / 'families' / p / '05_families.exp-gated-stage1-msgsel.json',
        'learned-v2': lambda p: qh.B / p / 'data' / '05_families.exp-learned-v2.json'}
for name, path in REFS.items():
    res = {p: qh.score(qh.load(p), qh.family_file(qh.load(p), path(p))) for p in qh.PROTOS}
    print(qh.report(res, f'{name} vs annotations{qh.SUFFIX or " (original)"}'), flush=True)
