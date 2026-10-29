"""Pipeline post-process after stage 07: split each family's fields at detected array edges.

Usage: apply_periodic.py <01_messages.jsonl> <02_family_assignments.json> <05_families.json> [--mode loose]
The families file is rewritten in place; the stage-07 original is kept as
05_families.pre-periodic.json and the detections as 05_periodic_detections.json.
"""
import argparse
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import periodic  # noqa: E402
from bench_periodic import add_edges  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('messages'); ap.add_argument('assignments'); ap.add_argument('families')
    ap.add_argument('--mode', default='loose', choices=['strict', 'length', 'loose'])
    a = ap.parse_args()
    fam_path = Path(a.families)
    assign = {int(x['msg_id']): str(x['family_id']) for x in json.load(open(a.assignments))['assignments']}
    by = defaultdict(list)
    with open(a.messages) as fh:
        for line in fh:
            if line.strip():
                m = json.loads(line)
                fam = assign.get(int(m['msg_id']))
                if fam and fam != 'noise':
                    by[fam].append(bytes.fromhex(m['payload_hex']))
    fams = json.load(open(fam_path))
    shutil.copy(fam_path, fam_path.with_name('05_families.pre-periodic.json'))
    det, total = {}, 0
    for fam, details in fams.items():
        det[fam] = periodic.detect_family(by.get(fam, []), a.mode)
        edges = {e for r in det[fam] for e in r['edges']}
        fams[fam], k = add_edges(details, edges, markers=False)
        total += k
        for r in det[fam]:
            print(f"[periodic] {fam}: region [{r['start']},{r['end']}) p={r['p']} phase={r['phase']} "
                  f"({r['evidence']}, phase from {r['phase_from']})")
    json.dump(fams, open(fam_path, 'w'), indent=2)
    json.dump(det, open(fam_path.with_name('05_periodic_detections.json'), 'w'), indent=1, default=str)
    print(f'[periodic] mode={a.mode}: {sum(map(len, det.values()))} array regions, {total} field splits')


if __name__ == '__main__':
    main()
