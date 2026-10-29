"""Shared helpers for the baseline comparison (runs under any of the venvs; stdlib only)."""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
BENCH = os.path.join(ROOT, 'dol', 'benchmark-14-protocols')
HERE = os.path.join(ROOT, 'dol', 'baseline-comparison')
PROTOCOLS = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua',
             'powerlink', 's7comm', 'zigbee']

def iter_jsonl(path):
    with open(path, encoding='utf-8') as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)

HELDOUT = os.path.join(ROOT, 'dol', 'heldout')
HELDOUT_PROTOCOLS = ['synphasor', 'ams', 'doip', 'cnip']   # not used to develop the method (ams: seen once in a rejected design option; doip, cnip: added after the design was frozen)


def load_sample(protocol):
    """Sampled message records (01_messages rows) in capture order; held-out protocols live in dol/heldout."""
    if protocol in HELDOUT_PROTOCOLS:
        ids = set(json.load(open(os.path.join(HELDOUT, protocol, 'sample.json'))))
        path = os.path.join(HELDOUT, protocol, 'data', '01_messages.jsonl')
    else:
        ids = set(json.load(open(os.path.join(HERE, 'samples', protocol + '.json'))))
        path = os.path.join(BENCH, protocol, 'data', '01_messages.jsonl')
    return [r for r in iter_jsonl(path) if r['msg_id'] in ids]

def write_preds(tool, protocol, rows, meta):
    out = os.path.join(HERE, 'preds', tool)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, protocol + '.jsonl'), 'w') as handle:
        for row in rows:
            handle.write(json.dumps(row) + '\n')
    json.dump(meta, open(os.path.join(out, protocol + '.meta.json'), 'w'), indent=2)
