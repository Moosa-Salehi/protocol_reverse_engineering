"""Few-shot vs copy baseline inside the pipeline: stage 04b's per-message edges are replaced by a supervised copy
baseline built from the same labels ($COPY_MODE = offsets | align, see dol/supervised-baselines/make_preds.py);
the layout split (04b), 07c and every later stage are unchanged. Loaded into every stage via
dol/ablation-final/patches/main_with_patch.py; only stage 04b is patched."""
import os
import sys

if sys.argv and os.path.basename(sys.argv[0]) == '04b_fewshot_boundaries.py':
    from protocol_re.inference import fewshot_boundaries as fsb

    def predict_edges(order, family_of, payload, body_start_of, labels, training_set, exclude=(), **_):
        mode = os.environ.get('COPY_MODE', 'offsets')
        seen = list(labels)
        final = {}
        for m in order:
            if m in labels:
                final[m] = {int(x) for x in labels[m]}
                continue
            b = payload[m]
            a = fsb.neighbour(b, seen, payload)
            if mode == 'align':
                e = fsb.transfer(payload[a], labels[a], b)[0]
            else:
                e = set(labels[a])
            final[m] = {int(x) for x in e if 0 < x < len(b)}
        return final, {'labelled_messages': len(seen), 'copy_mode': mode}

    fsb.predict_edges = predict_edges
