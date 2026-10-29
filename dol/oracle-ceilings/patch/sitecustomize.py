"""Oracle clustering ceiling: when stage 04 finishes, every message with a truth type (annotations 'type',
$ORACLE_TYPES jsonl) is assigned to a family named after its type; messages without a type keep their stage-04
family. Loaded into every stage via dol/ablation-final/patches/main_with_patch.py; only stage 04 is touched."""
import atexit
import json
import os
import sys

if sys.argv and os.path.basename(sys.argv[0]) == '04_discover_families.py' and os.environ.get('ORACLE_TYPES'):
    out_path = sys.argv[2]

    def _oracle():
        types = {}
        with open(os.environ['ORACLE_TYPES'], encoding='utf-8') as fh:
            for line in fh:
                if line.strip():
                    a = json.loads(line)
                    if a.get('type'):
                        types[int(a['msg_id'])] = a['type']
        names = {t: f'family_t{k}' for k, t in enumerate(sorted(set(types.values())))}
        with open(out_path, encoding='utf-8') as fh:
            data = json.load(fh)
        mode = os.environ.get('ORACLE_MODE', 'full')
        if mode == 'full':                      # every family = one truth type
            for a in data['assignments']:
                t = types.get(int(a['msg_id']))
                if t is not None:
                    a['family_id'] = names[t]
        elif mode == 'split':                   # fix merges only: split each family by truth type
            for a in data['assignments']:
                t = types.get(int(a['msg_id']))
                if t is not None and a['family_id'] != 'noise':
                    a['family_id'] = f"{a['family_id']}_{names[t][7:]}"
        elif mode == 'merge':                   # fix splits only: families with the same majority type are merged
            from collections import Counter, defaultdict
            c = defaultdict(Counter)
            for a in data['assignments']:
                t = types.get(int(a['msg_id']))
                if t is not None:
                    c[a['family_id']][t] += 1
            maj = {f: names[v.most_common(1)[0][0]] for f, v in c.items() if f != 'noise'}
            for a in data['assignments']:
                if a['family_id'] in maj:
                    a['family_id'] = maj[a['family_id']]
        with open(out_path, 'w', encoding='utf-8') as fh:
            json.dump(data, fh)

    atexit.register(_oracle)
