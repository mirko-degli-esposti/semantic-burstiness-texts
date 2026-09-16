"""Step 5 validation: ACF of projections vs corpus_acf.csv.

rho_orig must reproduce the CSV (5 decimals, up to float32 noise).  rho_surr in the CSV
is one shuffled realisation with an unrecoverable permutation: compared statistically
against the i.i.d. band.  rho_fgn in the CSV was produced with a mis-tuned surrogate
(stale alpha) and is only reported, not used as a target.

Usage:
    python scripts/check_acf.py data/corpus [--all]
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from semburst.acf import ACF_LAGS_SAVE, acf_matrix, ci95, lag_max_for
from semburst.burst import shuffle_permutations
from semburst.config import DEFAULT as P
from semburst.embed import build_trajectory, load_vectors
from semburst.pca import fit_pca, project
from semburst.surrogates import fgn_surrogate
from semburst.text import load_text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--texts", nargs="*", default=["doriangray.txt"])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ref", default="results/reference/corpus_acf.csv")
    args = ap.parse_args()

    ref = pd.read_csv(args.ref)
    texts = sorted(set(ref.file.unique()) - {"aliceinwonderland.txt"}) if args.all else args.texts
    wv = load_vectors()

    worst = 0.0
    for fname in texts:
        t0 = time.time()
        tt = load_text(Path(args.corpus_dir) / fname)
        vecs, _ = build_trajectory(tt.tokens_filtered, wv)
        M = len(vecs)
        pca = fit_pca(vecs, P.k_burst)
        lmax = lag_max_for(M)
        rho_o = acf_matrix(pca.proj, lmax)
        perm = shuffle_permutations(M, 1)[0]                       # seed 0 (reference used seed 42)
        rho_s = acf_matrix(pca.proj[perm], lmax)
        fgn = fgn_surrogate(tt.tokens_all, seed=P.fgn_seed)
        tok_fgn = [t for t in fgn.tokens if t not in tt.stopset and tt.freq[t] >= P.min_freq]
        proj_fgn = project(build_trajectory(tok_fgn, wv)[0], pca)
        rho_f = acf_matrix(proj_fgn, min(lmax, len(proj_fgn) // 5))

        r = ref[ref.file == fname]
        rows = [dict(file=fname, k=k + 1, lag=lag, rho_orig=rho_o[k, lag], rho_surr=rho_s[k, lag],
                     rho_fgn=rho_f[k, min(lag, rho_f.shape[1] - 1)])
                for k in range(P.k_burst) for lag in ACF_LAGS_SAVE if lag <= lmax]
        m = pd.DataFrame(rows).merge(r, on=["file", "k", "lag"], suffixes=("", "_ref"))
        d = (m.rho_orig - m.rho_orig_ref).abs()
        worst = max(worst, d.max())
        ci = ci95(M)
        print(f"\n{fname}   M={M}  ci95={ci:.5f}  alpha {fgn.alpha_text:.3f} -> alpha0 {fgn.alpha0:.3f}   {time.time()-t0:.0f} s")
        print(f"  rho_orig  max|diff| {d.max():.5f}   exact(5dp) {(d <= 1.1e-5).sum()}/{len(d)}   within 1e-4 {(d <= 1e-4).sum()}/{len(d)}")
        print(f"  outside CI  orig: mine {(m.rho_orig.abs() > ci).mean():.3f} ref {m.orig_sig.mean():.3f}   "
              f"surr: mine {(m.rho_surr.abs() > ci).mean():.3f} ref {m.surr_sig.mean():.3f}   "
              f"fgn: mine {(m.rho_fgn.abs() > ci).mean():.3f} ref {m.fgn_sig.mean():.3f} (ref mis-tuned)")
        l1 = m[m.lag == 1]
        print(f"  lag 1 mean over k: orig {l1.rho_orig.mean():.4f} (ref {l1.rho_orig_ref.mean():.4f})   "
              f"fgn {l1.rho_fgn.mean():.4f} (ref {l1.rho_fgn_ref.mean():.4f})   surr {l1.rho_surr.mean():.4f} (ref {l1.rho_surr_ref.mean():.4f})")
    print(f"\nworst |rho_orig - ref| = {worst:.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
