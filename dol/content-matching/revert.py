"""Revert the 2026-10-29 content-pairing rescoring (user decision): every 15_evaluation_result.pre-content.json goes
back to 15_evaluation_result.json; the content-pairing result is kept as 15_evaluation_result.content-pairing.json.
Runs scored with content pairing by default (no pre-content file) are rescored with structure pairing."""
import glob, json, os, shutil, subprocess, sys
ROOT = '/mnt/d/tez/practical/protocol_re'
restored = rescored = 0
for pre in glob.glob(f'{ROOT}/dol/**/15_evaluation_result.pre-content.json', recursive=True):
    d = os.path.dirname(pre); cur = f'{d}/15_evaluation_result.json'
    shutil.copy(cur, f'{d}/15_evaluation_result.content-pairing.json')
    shutil.copy(pre, cur); os.remove(pre); restored += 1
for cur in glob.glob(f'{ROOT}/dol/**/data/15_evaluation_result.json', recursive=True):
    try:
        r = json.load(open(cur))
    except Exception:
        continue
    if (r.get('inputs') or {}).get('type_pairing') != 'content':
        continue
    d = os.path.dirname(cur)
    truth = r['inputs']['ground_truth_protocol_file']
    shutil.copy(cur, f'{d}/15_evaluation_result.content-pairing.json')
    subprocess.run([sys.executable, f'{ROOT}/scripts/17_evaluate_protocol_spec.py', f'{d}/14_evaluation_model_data.json', truth, cur,
                    '--messages-jsonl', f'{d}/01_messages.jsonl', '--log-dir', '/tmp/claude-1000/-mnt-d-tez-practical-protocol-re/afb3e8dd-2521-49c3-8d36-b158be088ea2/scratchpad/log'],
                   check=True, capture_output=True)
    rescored += 1
print(f'restored {restored}, rescored with structure pairing {rescored}')
