"""Run stage 04 on one protocol and pickle the (records, bootstrap assignments) handed to the discriminator
refinement, so candidate statistics can be studied offline. Same stage-04 arguments as the truth-eval runs.
usage: dump_bootstrap.py <protocol> <tshark-filter>"""
import pickle, runpy, sys, os
ROOT = '/mnt/d/tez/practical/protocol_re'
sys.path.insert(0, os.path.join(ROOT, 'src'))
import protocol_re.clustering.family_discovery as fd
protocol = sys.argv[1]
out = os.path.join(ROOT, 'dol/iec104-discriminator/bootstrap', protocol + '.pkl')
original = fd.refine_families_by_discriminator
def hook(records, assignments, *a, **k):
    pickle.dump((list(records), list(assignments)), open(out, 'wb'))
    return original(records, assignments, *a, **k)
fd.refine_families_by_discriminator = hook
run = f'{ROOT}/dol/iec104-discriminator/bootstrap/{protocol}-04.json'
sys.argv = ['04_discover_families.py', f'{ROOT}/dol/benchmark-14-protocols/{protocol}/data/01_messages.jsonl', run,
            '--sample-size', '100000', '--feature-mode', 'neural', '--neural-model-path',
            f'{ROOT}/VAE_supervised_train/checkpoints/best_v3.pth', '--neural-batch-size', '256',
            '--tshark-filter', sys.argv[2],
            '--supervised-hdbscan-checkpoint', f'{ROOT}/VAE_supervised_train/checkpoints/best_v3.pth',
            '--latent-cache-path', f'{ROOT}/dol/iec104-discriminator/bootstrap/{protocol}-latent.json',
            '--refine-discriminator', '--tlv-family-merge',
            '--log-dir', f'{ROOT}/dol/iec104-discriminator/bootstrap/log']
os.chdir(ROOT)
runpy.run_path(f'{ROOT}/scripts/04_discover_families.py', run_name='__main__')
print('dumped', out)
