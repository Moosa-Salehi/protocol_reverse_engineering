"""Boundary-model training seed: stage 04b's HistGradientBoostingClassifier gets random_state=$HGB_SEED (the shipped
code uses 0; the seed drives early stopping's validation split). Loaded via dol/ablation-final/patches/main_with_patch.py."""
import os
import sys

if sys.argv and os.path.basename(sys.argv[0]) == '04b_fewshot_boundaries.py':
    from protocol_re.inference import fewshot_boundaries as fsb

    def hgb():
        from sklearn.ensemble import HistGradientBoostingClassifier
        return HistGradientBoostingClassifier(max_iter=300, learning_rate=0.06, max_depth=5, l2_regularization=1.0,
                                              random_state=int(os.environ['HGB_SEED']))

    fsb.hgb = hgb
    print(f"[boundary-seeds] HGB random_state={os.environ['HGB_SEED']}", flush=True)
