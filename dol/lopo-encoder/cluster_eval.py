"""Clustering of each benchmark protocol's messages with the encoder that never saw it ("no-<p>") vs the control
trained on all protocols ("all"), same budget. Embeddings -> HDBSCAN with each checkpoint's global setting scaled to
the protocol's population (as stage 04 does), scored against the trusted parser families (weighted purity, V, ARI).
usage: cluster_eval.py  -> cluster_eval.json   (JOBLIB_MULTIPROCESSING=0 recommended)"""
import json, os, sys
ROOT = '/mnt/d/tez/practical/protocol_re'; HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT); sys.path.insert(0, f'{ROOT}/src')
from VAE_supervised_train.data import MessageFamilyDataset
from VAE_supervised_train.evaluate import embed_dataset, evaluate_embeddings
from VAE_supervised_train.model import load_checkpoint
P = ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
from pathlib import Path
DS = Path(f'{ROOT}/VAE_supervised_train/cache/messages.jsonl')
out = json.load(open(f'{HERE}/cluster_eval.json')) if os.path.exists(f'{HERE}/cluster_eval.json') else {}
for p in P:
    for m in (f'no-{p}', 'all'):
        key = f'{p}:{"lopo" if m != "all" else "all"}'
        ck = f'{HERE}/models/{m}/best.pth'
        if key in out or not os.path.exists(ck):
            continue
        model, checkpoint = load_checkpoint(ck, 'cpu')
        g = (checkpoint.get('metrics') or {}).get('hdbscan_global') or {}
        ds = MessageFamilyDataset(DS, [p], model.max_len, 0.9, 1)
        emb = embed_dataset(model, ds, 'cpu', 512)
        mcs = max(2, round(len(ds.rows) * float(g.get('min_cluster_size_fraction', 0)))) if g.get('min_cluster_size_fraction') else int(g.get('min_cluster_size', 5))
        rep = evaluate_embeddings(ds, emb, protocol_parameters={p: {'min_cluster_size': mcs, 'min_samples': g.get('min_samples'),
                                                                   'cluster_selection_epsilon': g.get('cluster_selection_epsilon', 0.0)}})
        out[key] = rep['per_protocol'][p]
        print(key, {k: round(v, 3) for k, v in out[key].items() if k in ('weighted_cluster_purity', 'v_measure', 'adjusted_rand_index')}, flush=True)
        json.dump(out, open(f'{HERE}/cluster_eval.json', 'w'), indent=1)
