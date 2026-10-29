"""Rescore saved runs with the evaluator's truth-declared body offsets (--body-offset-source truth) instead of each
family's predicted body start. For every run dir: the 'predicted' mode must reproduce the stored
15_evaluation_result.json; with --write, the stored result is kept as 15_evaluation_result.pre-truthbase.json and
replaced by the 'truth' mode result.  usage: rescore_truthbase.py [--write] <run-root> [<run-root> ...]
(a run root holds <protocol>/data/14_evaluation_model_data.json)"""
import importlib.util, json, os, shutil, sys
ROOT = '/mnt/d/tez/practical/protocol_re'
spec = importlib.util.spec_from_file_location('ev17', f'{ROOT}/scripts/17_evaluate_protocol_spec.py')
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
write = '--write' in sys.argv
KEYS = (('overall', None), ('mt', 'message_type_matching'), ('bnd', 'field_boundary'), ('sem', 'field_semantics'), ('roles', 'field_roles'), ('rel', 'relations'))
def summ(r):
    return {k: (r['summary']['overall_score'] if m is None else r['metrics'][m]['f1_score']) for k, m in KEYS}
def run(d, p, source):
    ev._ALIGN['source'] = source
    model = json.load(open(f'{d}/14_evaluation_model_data.json'))
    truth_path = f'{ROOT}/truth_files/{p}.json'; truth = json.load(open(truth_path))
    tp = truth.get('ground_truth_protocol') or truth.get('predicted_protocol') or {}
    scope = ev.corpus_discriminator_scope(f'{d}/01_messages.jsonl', tp.get('message_types', []) or [])
    rep = ev.evaluate_protocol_spec_with_refinement(model, truth, scope)
    rep['inputs'] = {'predicted_protocol_file': f'{d}/14_evaluation_model_data.json', 'ground_truth_protocol_file': truth_path,
                     'body_offset_source': source}
    return rep
for root in [a for a in sys.argv[1:] if a != '--write']:
    tot = {'pred': {k: 0 for k, _ in KEYS}, 'truth': {k: 0 for k, _ in KEYS}}; n = 0
    # <root> holds <protocol>/data; <run-dir>::<truth name> is a single run (e.g. a supplementary corpus)
    items = [(f'{root}/{p}/data', p) for p in P] if '::' not in root else [(root.split('::')[0] + '/data', root.split('::')[1])]
    for d, p in items:
        if not os.path.exists(f'{d}/14_evaluation_model_data.json'):
            continue
        stored_path = f'{d}/15_evaluation_result.json'
        orig = f'{d}/15_evaluation_result.pre-truthbase.json'
        stored = json.load(open(orig if os.path.exists(orig) else stored_path))
        a = run(d, p, 'predicted'); b = run(d, p, 'truth')
        if abs(summ(a)['overall'] - summ(stored)['overall']) > 1e-6:
            print(f'  !! {root} {p}: predicted mode {summ(a)["overall"]:.4f} != stored {summ(stored)["overall"]:.4f}')
        sa, sb = summ(a), summ(b); n += 1
        for k in sa: tot['pred'][k] += sa[k]; tot['truth'][k] += sb[k]
        print(f'  {p:10s} ' + ' '.join(f'{k}={sa[k]:.3f}->{sb[k]:.3f}' for k in sa))
        if write:
            if not os.path.exists(orig):
                shutil.copy(stored_path, orig)
            json.dump(b, open(stored_path, 'w'), indent=2, ensure_ascii=False)
    print(f'{root} ({n} protocols) macro: ' + ' '.join(f"{k}={tot['pred'][k]/max(n,1):.3f}->{tot['truth'][k]/max(n,1):.3f}" for k, _ in KEYS))
