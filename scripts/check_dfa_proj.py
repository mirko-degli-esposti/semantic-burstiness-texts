"""Step 6 validation: DFA exponents of the projection series vs corpus_dfa.csv.

dfa_orig should reproduce the CSV to ~1e-3 (float32 projections, smooth statistic).
dfa_surr_mean (10 shuffled) and dfa_fgn are compared statistically: shuffled ~ 0.5,
FGN close to the reference realisation up to single-realisation noise.

Usage:
    python scripts/check_dfa_proj.py data/corpus [--all]
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from semburst.burst import shuffle_permutations
from semburst.config import DEFAULT as P
from semburst.dfa import projection_alpha
from semburst.embed import build_trajectory, load_vectors
from semburst.pca import fit_pca, project
from semburst.surrogates import fgn_surrogate
from semburst.text import load_text

N_SURR_DFA = 10   # as in the reference run


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--texts", nargs="*", default=["doriangray.txt"])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ref", default="results/reference/corpus_dfa.csv")
    args = ap.parse_args()

    ref = pd.read_csv(args.ref)
    texts = sorted(ref.file.unique()) if args.all else args.texts
    wv = load_vectors()

    summary = []
    for fname in texts:
        t0 = time.time()
        tt = load_text(Path(args.corpus_dir) / fname)
        vecs, _ = build_trajectory(tt.tokens_filtered, wv)
        M = len(vecs)
        pca = fit_pca(vecs, P.k_burst)
        fgn = fgn_surrogate(tt.tokens_all, seed=P.fgn_seed)
        tok_fgn = [t for t in fgn.tokens if t not in tt.stopset and tt.freq[t] >= P.min_freq]
        proj_fgn = project(build_trajectory(tok_fgn, wv)[0], pca)
        perms = shuffle_permutations(M, N_SURR_DFA)

        rows = []
        for k in range(P.k_burst):
            a_s = np.array([projection_alpha(pca.proj[p, k]) for p in perms])
            rows.append(dict(file=fname, k=k + 1, dfa_orig=projection_alpha(pca.proj[:, k]),
                             dfa_fgn=projection_alpha(proj_fgn[:, k]),
                             dfa_surr_mean=np.nanmean(a_s), dfa_surr_std=np.nanstd(a_s)))
        m = pd.DataFrame(rows).merge(ref[ref.file == fname], on=["file", "k"], suffixes=("", "_ref"))
        d_o = (m.dfa_orig - m.dfa_orig_ref).abs()
        d_f = m.dfa_fgn - m.dfa_fgn_ref
        d_s = m.dfa_surr_mean - m.dfa_surr_mean_ref
        print(f"\n{fname}   M={M}   alpha {fgn.alpha_text:.3f} -> alpha0 {fgn.alpha0:.3f}   {time.time()-t0:.0f} s")
        print(f"  dfa_orig : max|diff| {d_o.max():.4f}   within 1e-3 {(d_o <= 1e-3).sum()}/{len(d_o)}")
        print(f"  dfa_fgn  : mine mean {m.dfa_fgn.mean():.4f}  ref {m.dfa_fgn_ref.mean():.4f}   diff mean {d_f.mean():+.4f} max|.| {d_f.abs().max():.4f}")
        print(f"  dfa_surr : mine mean {m.dfa_surr_mean.mean():.4f}  ref {m.dfa_surr_mean_ref.mean():.4f}   diff mean {d_s.mean():+.4f} max|.| {d_s.abs().max():.4f}")
        print(f"  orig mean {m.dfa_orig.mean():.4f}  (ref {m.dfa_orig_ref.mean():.4f})   orig > fgn: mine {(m.dfa_orig > m.dfa_fgn).mean():.2f} ref {(m.dfa_orig_ref > m.dfa_fgn_ref).mean():.2f}")
        summary.append(dict(file=fname, d_orig_max=d_o.max(), fgn_mine=m.dfa_fgn.mean(), fgn_ref=m.dfa_fgn_ref.mean(),
                            surr_mine=m.dfa_surr_mean.mean(), surr_ref=m.dfa_surr_mean_ref.mean(),
                            orig=m.dfa_orig.mean()))
    s = pd.DataFrame(summary)
    print("\n" + s.round(4).to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
