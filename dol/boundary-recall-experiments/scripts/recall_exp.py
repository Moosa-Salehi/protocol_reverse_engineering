"""Boundary-recall experiment: rerun stage 07 with different settings on the
benchmark runs and score each variant per message. Family files are written
next to the baseline as 05_families.exp-<variant>.json."""
import importlib.util, json, subprocess, sys, os
from collections import Counter, defaultdict
from pathlib import Path
ROOT=Path('/mnt/d/tez/practical/protocol_re'); B=ROOT/'dol/benchmark-14-protocols'; ANN=ROOT/'finetuning/cluster-free-dataset/annotations'
spec=importlib.util.spec_from_file_location('bench',ROOT/'scripts/diagnostics/31_benchmark_message_boundaries.py'); bench=importlib.util.module_from_spec(spec); spec.loader.exec_module(bench)
VARIANTS=json.loads(sys.argv[1]); protos=sys.argv[2].split(',')
env=dict(os.environ,PYTHONPATH=str(ROOT/'src'))
def oracle(data, ann_path, share):
    """Fixed-offset ceiling: per family, the offsets that are true edges in >= share of its messages."""
    a={int(x['msg_id']):x['family_id'] for x in json.load(open(data/'02_family_assignments.json'))['assignments']}
    votes=defaultdict(Counter); size=Counter()
    for r in bench._iter_jsonl(ann_path):
        fam=a.get(int(r['msg_id'])); size[fam]+=1; votes[fam].update(r['boundaries'])
    fams={str(f):{'field_hypotheses':[{'start':e,'length':0} for e,c in v.items() if c>=share*size[f]]} for f,v in votes.items() if f is not None}
    out=data/f'05_families.exp-oracle{int(share*100)}.json'; json.dump(fams,open(out,'w')); return out.name
table=defaultdict(dict)
for p in protos:
    data=B/p/'data'; ann=ANN/f'{p}.jsonl'
    for name,args in VARIANTS.items():
        out=data/f'05_families.exp-{name}.json'
        cmd=[sys.executable,str(ROOT/'scripts/07_infer_boundaries.py'),str(data/'01_messages.jsonl'),str(out),'--assignments-json',str(data/'02_family_assignments.json'),'--features-json',str(data/'03_family_features.json'),'--framing-json',str(data/'04_framing.json'),'--length-match-threshold','0.8','--boundary-confidence-weight','0.45','--log-dir',str(ROOT/'dol/boundary-recall-experiments/logs'/p/name),*args]
        r=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True)
        if r.returncode: print('FAIL',p,name,r.stderr[-400:]); continue
        table[p][name]=bench.score_protocol(data,ann,out.name)
    for share in (0.5,):
        table[p][f'oracle{int(share*100)}']=bench.score_protocol(data,ann,oracle(data,ann,share))
names=list(VARIANTS)+['oracle50']
print(f"{'protocol':10s} "+' '.join(f'{n:>22s}' for n in names)); print(f"{'':10s} "+' '.join(f"{'P     R     F1':>22s}" for _ in names))
for p in protos:
    print(f'{p:10s} '+' '.join((f"{table[p][n]['precision']:.2f}  {table[p][n]['recall']:.2f}  {table[p][n]['f1']:.3f}".rjust(22)) if n in table[p] else ' '*22 for n in names))
print(f"{'macro F1':10s} "+' '.join(f"{sum(table[p][n]['f1'] for p in protos if n in table[p])/len(protos):>22.3f}" for n in names))
json.dump(table,open(ROOT/'dol/boundary-recall-experiments'/f'results-{sys.argv[3]}.json','w'),indent=1)
