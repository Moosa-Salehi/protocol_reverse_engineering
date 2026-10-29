"""Rescore saved runs with stage 17's content-based type pairing (default since 2026-10-29). For every run data dir
under the given roots: the structure pairing must reproduce the stored overall score (anything else in the evaluator
is unchanged); with --write the stored result is kept as 15_evaluation_result.pre-content.json and replaced by the
content-pairing result (runs whose corpus the annotations do not describe fall back to structure and keep their
score). usage: rescore_write.py [--write] <root> [<root> ...]"""
import glob
import importlib.util
import json
import os
import shutil
import sys

ROOT = '/mnt/d/tez/practical/protocol_re'
spec = importlib.util.spec_from_file_location('ev17', f'{ROOT}/scripts/17_evaluate_protocol_spec.py')
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
write = '--write' in sys.argv
KEYS = (('overall', None), ('mt', 'message_type_matching'), ('bnd', 'field_boundary'), ('sem', 'field_semantics'), ('rel', 'relations'))


def summ(r):
    return {k: (r['summary']['overall_score'] if m is None else r['metrics'][m]['f1_score']) for k, m in KEYS}


def evaluate(d, truth_path, mode):
    ev._PAIRING['requested'] = mode
    model_path = f'{d}/14_evaluation_model_data.json'
    used = ev.load_content_pairing(model_path, truth_path, f'{d}/01_messages.jsonl')
    model = json.load(open(model_path)); truth = json.load(open(truth_path))
    tp = truth.get('ground_truth_protocol') or truth.get('predicted_protocol') or {}
    scope = ev.corpus_discriminator_scope(f'{d}/01_messages.jsonl', tp.get('message_types', []) or [])
    rep = ev.evaluate_protocol_spec_with_refinement(model, truth, scope)
    rep['inputs'] = {'predicted_protocol_file': model_path, 'ground_truth_protocol_file': truth_path,
                     'type_pairing': used, 'type_pairing_note': ev._PAIRING['reason']}
    return rep


bad = done = fallback = 0
for root in [a for a in sys.argv[1:] if a != '--write']:
    for res_path in sorted(glob.glob(f'{root}/**/data/15_evaluation_result.json', recursive=True)):
        d = os.path.dirname(res_path)
        if not os.path.exists(f'{d}/14_evaluation_model_data.json') or not os.path.exists(f'{d}/01_messages.jsonl'):
            continue
        orig = f'{d}/15_evaluation_result.pre-content.json'
        stored = json.load(open(orig if os.path.exists(orig) else res_path))
        if (stored.get('inputs') or {}).get('type_pairing') == 'content' and not os.path.exists(orig):
            continue                                   # produced by the new default already
        truth_path = (stored.get('inputs') or {}).get('ground_truth_protocol_file')
        if not truth_path:
            print(f'  ?? no truth path: {d}'); continue
        truth_path = truth_path if os.path.isabs(truth_path) else os.path.join(ROOT, truth_path)
        a = evaluate(d, truth_path, 'structure')
        if abs(summ(a)['overall'] - summ(stored)['overall']) > 1e-6:
            print(f'  !! structure {summ(a)["overall"]:.4f} != stored {summ(stored)["overall"]:.4f}: {d}'); bad += 1
            continue
        b = evaluate(d, truth_path, 'content')
        fallback += b['inputs']['type_pairing'] != 'content'; done += 1
        if write:
            if not os.path.exists(orig):
                shutil.copy(res_path, orig)
            json.dump(b, open(res_path, 'w'), indent=2, ensure_ascii=False)
    print(f'{root}: rescored {done} so far, fallback {fallback}, mismatches {bad}', flush=True)
print(f'TOTAL rescored {done} (structure fallback {fallback}), mismatches {bad}')
