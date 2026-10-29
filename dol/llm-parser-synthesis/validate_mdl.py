"""Is the selection score a usable label-free signal? For the largest families of every protocol, compare the score
of the truth segmentation with the pipeline's, one-field-per-byte and one blob (fixed-offset keys), for
score = description length + gamma * learned boundary prior (gamma = 0: description length only; 'prior': prior only).
Reports how often truth scores better than the pipeline, and how often the score orders two candidates like F1.
usage: validate_mdl.py [protocols]"""
from __future__ import annotations

import sys
from collections import defaultdict

import common
import mdl
import prior

K, N = 8, 300
GAMMAS = [0.0, 0.5, 1.0, 2.0, "prior"]


def main():
    protos = sys.argv[1].split(",") if len(sys.argv) > 1 else common.PROTOS + common.HELDOUT
    wins, tot, agree, pairs = defaultdict(int), defaultdict(int), defaultdict(int), defaultdict(int)
    for p in protos:
        d = common.load(p)
        fp = prior.family_probability(p, d)
        fams = sorted(((f, [i for i in m if i in d["truth"]]) for f, m in d["fams"].items()), key=lambda x: -len(x[1]))[:K]
        for f, ids in fams:
            ids = ids[:N]
            if len(ids) < 5:
                continue
            pl = [d["payload"][i] for i in ids]
            cands = {"truth": [d["truth"][i] for i in ids], "pipe": [d["pipe"][i] for i in ids],
                     "bytes": [list(range(1, len(b))) for b in pl], "blob": [[] for _ in pl]}
            dl = {k: mdl.score(pl, mdl.edges_to_segs(pl, e)) for k, e in cands.items()}
            pr = {k: prior.prior_bits(fp.get(f, {}), pl, e) for k, e in cands.items()}
            f1 = {k: common.prf({i: e for i, e in zip(ids, cands[k])}, d["truth"], ids)["f1"] for k in cands}
            for g in GAMMAS:
                s = {k: (pr[k] if g == "prior" else dl[k] + g * pr[k]) for k in cands}
                wins[g] += s["truth"] < s["pipe"]; tot[g] += 1
                ks = list(cands)
                for a in range(len(ks)):
                    for b in range(a + 1, len(ks)):
                        if f1[ks[a]] != f1[ks[b]]:
                            pairs[g] += 1
                            agree[g] += (s[ks[a]] < s[ks[b]]) == (f1[ks[a]] > f1[ks[b]])
        print(p, "done", flush=True)
    for g in GAMMAS:
        print(f"gamma {g}: truth better than pipeline in {wins[g]}/{tot[g]} families; order agrees with F1 in "
              f"{agree[g]}/{pairs[g]} pairs ({agree[g] / max(1, pairs[g]):.2f})")


if __name__ == "__main__":
    main()
