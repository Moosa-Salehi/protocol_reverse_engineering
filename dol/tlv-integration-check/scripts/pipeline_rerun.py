"""Rerun the patched stage 07 on the 14 benchmark runs (same arguments as
dol/boundary-recall-experiments/scripts/recall_exp.py) and score with the patched
benchmark scorer, with and without the per-message TLV layouts. Outputs stay in
dol/tlv-integration-check/runs/<protocol>/."""
import importlib.util, json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
ROOT = Path('/mnt/d/tez/practical/protocol_re'); B = ROOT / 'dol/benchmark-14-protocols'
ANN = ROOT / 'finetuning/cluster-free-dataset/annotations'; OUT = ROOT / 'dol/tlv-integration-check'
spec = importlib.util.spec_from_file_location('bench', ROOT / 'scripts/diagnostics/31_benchmark_message_boundaries.py')
bench = importlib.util.module_from_spec(spec); spec.loader.exec_module(bench)
PROTOS = 'modbus,hart_ip,zigbee,bacnet,powerlink,s7comm,mms,goose,dnp3,enip,cip,ethercat,opcua,iec104'.split(',')
VARIANTS = {'default': [], 'perbyte0.5': ['--max-fields-per-byte', '0.5']}
env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'))

def run(job):
    p, name = job
    data = B / p / 'data'; out = OUT / 'runs' / p / f'05_families.{name}.json'; out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(ROOT / 'scripts/07_infer_boundaries.py'), str(data / '01_messages.jsonl'), str(out),
           '--assignments-json', str(data / '02_family_assignments.json'), '--features-json', str(data / '03_family_features.json'),
           '--framing-json', str(data / '04_framing.json'), '--length-match-threshold', '0.8', '--boundary-confidence-weight', '0.45',
           '--log-dir', str(OUT / 'logs' / p / name), *VARIANTS[name]]
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    return p, name, r.returncode, r.stderr[-300:], out

results = {}
with ThreadPoolExecutor(4) as pool:
    for p, name, code, err, out in pool.map(run, [(p, n) for p in PROTOS for n in VARIANTS]):
        if code:
            print('FAIL', p, name, err); continue
        data = B / p / 'data'
        with_l = bench.score_protocol(data, ANN / f'{p}.jsonl', str(out))
        without = bench.score_protocol(data, ANN / f'{p}.jsonl', str(out), use_message_layouts=False)
        results.setdefault(p, {})[name] = {'with_layouts': with_l, 'fixed_only': without}
        print(p, name, 'fixed', without['f1'], 'with layouts', with_l['f1'], 'layout families', with_l['message_layout_families'], flush=True)
json.dump(results, open(OUT / 'pipeline-rerun.json', 'w'), indent=1)
old = json.load(open(ROOT / 'dol/boundary-recall-experiments/results-cap-scaling.json'))
print(f"\n{'protocol':10s} {'old base':>9s} {'fixed':>7s} {'+layout':>8s} | {'old pb0.5':>9s} {'fixed':>7s} {'+layout':>8s}")
for p in PROTOS:
    r = results[p]
    print(f"{p:10s} {old[p]['base']['f1']:9.3f} {r['default']['fixed_only']['f1']:7.3f} {r['default']['with_layouts']['f1']:8.3f} | "
          f"{old[p]['perbyte0.5']['f1']:9.3f} {r['perbyte0.5']['fixed_only']['f1']:7.3f} {r['perbyte0.5']['with_layouts']['f1']:8.3f}")
m = lambda f: np.mean([f(p) for p in PROTOS])
print(f"{'macro':10s} {m(lambda p: old[p]['base']['f1']):9.3f} {m(lambda p: results[p]['default']['fixed_only']['f1']):7.3f} {m(lambda p: results[p]['default']['with_layouts']['f1']):8.3f} | "
      f"{m(lambda p: old[p]['perbyte0.5']['f1']):9.3f} {m(lambda p: results[p]['perbyte0.5']['fixed_only']['f1']):7.3f} {m(lambda p: results[p]['perbyte0.5']['with_layouts']['f1']):8.3f}")
