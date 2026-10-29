"""Stage-04-only harness: run scripts/04_discover_families.py (refinement + TLV merge included) with the HDBSCAN call
replaced by a rule, then score the final families against the truth-file message types (ARI, V-measure, noise).
Truth types are used only to compare a few label-free rules. usage: harness.py <rule> <full|sample> [protocols]
rules: C0 / C1 pipeline code, reassignment off / on | P tuned per-protocol (reference) | R0 global fraction | R1 R0 + noise->nearest cluster | R2 silhouette-selected size (noise reassigned, 2000-point subsample) + noise->nearest"""
import json, os, runpy, sys, tempfile
import numpy as np
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, os.path.join(ROOT, 'src'))
import hdbscan as real_hdbscan
import protocol_re.clustering.family_discovery as fd
from sklearn import metrics
from sklearn.metrics import silhouette_score
rule, corpus = sys.argv[1], sys.argv[2]
# C0 / C1: current pipeline code (global setting), noise reassignment off / on (Clustering.REASSIGN_NOISE_TO_NEAREST)
from protocol_re.config.thresholds import Clustering as _CL
_CL.REASSIGN_NOISE_TO_NEAREST = rule in ('C1', 'D1') or rule.startswith('X')
# X*: current pipeline code with clustering switches from the environment (dol/improve)
from protocol_re.config.thresholds import FamilyRefinement as _FR2
_FR2.UNKNOWN_DIRECTION_VALUE_ONLY = os.environ.get('VALUE_ONLY') == '1'
_FR2.DEEP_MAX_OFFSET = int(os.environ.get('DEEP', '0'))
_FR2.PAIR_TIEBREAK_MARGIN = float(os.environ.get('TIEBREAK', '0'))
P = sys.argv[3].split(',') if len(sys.argv) > 3 else ['bacnet', 'cip', 'dnp3', 'enip', 'ethercat', 'goose', 'hart_ip', 'iec104', 'mms', 'modbus', 'opcua', 'powerlink', 's7comm', 'zigbee']
FILTER = {'bacnet': 'bacapp', 'ethercat': 'ecat', 'iec104': 'iec60870_104', 'powerlink': 'epl', 'zigbee': 'zbee_nwk'}
GRID = (0.0025, 0.005, 0.01, 0.02, 0.04, 0.08)
info = {}
current = {}
import torch
PER_PROTOCOL = torch.load(f'{ROOT}/VAE_supervised_train/checkpoints/best_v3.pth', map_location='cpu', weights_only=False)['metrics']['hdbscan_per_protocol']

def nearest_reassign(X, labels):
    labels = np.asarray(labels).copy()
    noise = labels == -1
    if noise.all() or not noise.any():
        return labels
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=1).fit(X[~noise])
    _, idx = nn.kneighbors(X[noise])
    labels[noise] = labels[~noise][idx[:, 0]]
    return labels

class Shim:
    def __init__(self, **kw):
        self.kw = kw
    def fit_predict(self, X):
        X = np.asarray(X)
        kw = dict(self.kw)
        if rule == 'R2':
            best = None
            for f in GRID:
                size = max(2, round(len(X) * f))
                if size >= len(X):
                    continue
                raw = real_hdbscan.HDBSCAN(**{**kw, 'min_cluster_size': size}).fit_predict(X)
                full = nearest_reassign(X, raw)
                n = len(set(full) - {-1})
                if n >= 2:
                    rng = np.random.RandomState(0)
                    idx = rng.choice(len(X), min(2000, len(X)), replace=False)
                    score = silhouette_score(X[idx], full[idx]) if len(set(full[idx])) >= 2 else -1.0
                else:
                    score = -1.0
                info.setdefault('grid', []).append((f, size, n, round(float(score), 3)))
                if best is None or score > best[0]:
                    best = (score, size, raw)
            info['chosen_size'] = best[1]
            labels = best[2]
        else:
            if rule == 'P':   # reference only: the removed per-protocol tuned settings
                tuned = PER_PROTOCOL[current['p']]
                kw.update(min_cluster_size=min(tuned['min_cluster_size'], len(X)), min_samples=tuned.get('min_samples'))
            labels = real_hdbscan.HDBSCAN(**kw).fit_predict(X)
            info['chosen_size'] = kw.get('min_cluster_size')
        info['noise_before'] = float(np.mean(np.asarray(labels) == -1))
        if rule in ('R1', 'R2'):
            labels = nearest_reassign(X, labels)
        return labels

fd.hdbscan = type('M', (), {'HDBSCAN': Shim})
out_rows = []
for p in P:
    info.clear(); current['p'] = p
    src = f'{ROOT}/dol/benchmark-14-protocols/{p}/data/01_messages.jsonl'
    tmp = tempfile.mkdtemp(dir=f'{ROOT}/dol/hdbscan-global')
    if corpus == 'sample':
        ids = set(json.load(open(f'{ROOT}/dol/baseline-comparison/samples/{p}.json')))
        path = f'{tmp}/msgs.jsonl'
        open(path, 'w').writelines(l for l in open(src) if l.strip() and json.loads(l)['msg_id'] in ids)
        src = path
    cache = f'{ROOT}/dol/hdbscan-global/global-only/{corpus}/{p}/data/02_latent_cache.json'
    out = f'{tmp}/02.json'
    sys.argv = ['04', src, out, '--sample-size', '100000', '--feature-mode', 'neural', '--neural-model-path',
                f'{ROOT}/VAE_supervised_train/checkpoints/best_v3.pth', '--neural-batch-size', '256', '--tshark-filter', FILTER.get(p, p),
                '--supervised-hdbscan-checkpoint', f'{ROOT}/VAE_supervised_train/checkpoints/best_v3.pth',
                '--latent-cache-path', cache, '--refine-discriminator', '--tlv-family-merge', '--log-dir', f'{tmp}/log']
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(f'{ROOT}/scripts/04_discover_families.py', run_name='__main__')
    doc = json.load(open(out)); fam = {a['msg_id']: a['family_id'] for a in doc['assignments']}
    ref = doc['metadata'].get('discriminator_refinement') or {}
    truth = {json.loads(l)['msg_id']: json.loads(l).get('type') for l in open(f'{ROOT}/dol/accuracy-push/annotations-truthconv/{p}.jsonl')}
    ids = [m for m in fam if truth.get(m)]
    y = [truth[m] for m in ids]; z = [fam[m] for m in ids]
    row = dict(protocol=p, ari=round(metrics.adjusted_rand_score(y, z), 3), v=round(metrics.v_measure_score(y, z), 3),
               families=len(set(z) - {'noise'}), noise=round(sum(f == 'noise' for f in z) / len(z), 3),
               size=info.get('chosen_size'), disc=(ref.get('offset'), ref.get('reason'), ref.get('family_count_before')), hdb_noise=round(info.get('noise_before', 0), 3), grid=info.get('grid'))
    out_rows.append(row)
    print(f"{p:10s} ARI={row['ari']:.3f} V={row['v']:.3f} fams={row['families']:3d} noise={row['noise']:.0%} size={row['size']} hdbscan-noise={row['hdb_noise']:.0%} disc={row['disc']}", flush=True)
    import shutil; shutil.rmtree(tmp, ignore_errors=True)
print(f"MACRO {rule} {corpus}: ARI={np.mean([r['ari'] for r in out_rows]):.3f} V={np.mean([r['v'] for r in out_rows]):.3f}")
json.dump(out_rows, open(f'{ROOT}/dol/hdbscan-global/harness-{rule}-{corpus}.json', 'w'), indent=1)
