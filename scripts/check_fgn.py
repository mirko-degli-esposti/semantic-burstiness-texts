"""Step 4b validation: FGN surrogate. For each text: alpha (pipeline tokeniser), alpha0,
alpha measured on the surrogate; then B_fgn against the reference CSV.

Exact agreement with the CSV is NOT expected (different tokeniser, different noise
realisation): the check is that alpha_surr matches alpha_text within tolerance, that
B_fgn is close to B_surr (the two nulls agree), and that B_orig / B_fgn ratios are
consistent with the reference at the level of a single-realisation surrogate.

Usage:
    python scripts/check_fgn.py data/corpus                 # doriangray.txt
    python scripts/check_fgn.py data/corpus --all
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from semburst.burst import burstiness_spectrum, thresholds
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
    ap.add_argument("--ref", default="results/reference/corpus_burstiness.csv")
    args = ap.parse_args()

    ref = pd.read_csv(args.ref)
    texts = sorted(ref.file.unique()) if args.all else args.texts
    wv = load_vectors()

    summary = []
    for fname in texts:
        t0 = time.time()
        fpath = Path(args.corpus_dir) / fname
        tt = load_text(fpath)
        vecs, _ = build_trajectory(tt.tokens_filtered, wv)
        pca = fit_pca(vecs, P.k_burst)

        fgn = fgn_surrogate(tt.tokens_all, seed=P.fgn_seed)
        tok_fgn = [t for t in fgn.tokens if t not in tt.stopset and tt.freq[t] >= P.min_freq]
        vecs_fgn, _ = build_trajectory(tok_fgn, wv)
        proj_fgn = project(vecs_fgn, pca)

        r = ref[ref.file == fname]
        a_ref, a0_ref = r.alpha.iloc[0], r.alpha0.iloc[0]
        print(f"\n{fname}   {time.time()-t0:.0f} s   bisection: {len(fgn.log)} evals, seed {fgn.seed}")
        print(f"  alpha  text {fgn.alpha_text:.4f} (ref {a_ref:.4f})   alpha0 {fgn.alpha0:.4f} (ref {a0_ref:.4f})   "
              f"alpha_surr {fgn.alpha_surr:.4f}   M_fgn {len(vecs_fgn)} (M {len(vecs)})")

        rows = []
        for q in P.q_sweep:
            th = thresholds(pca.proj, q)
            b_fgn = burstiness_spectrum(proj_fgn, th)
            b_orig = burstiness_spectrum(pca.proj, th)
            for k in range(P.k_burst):
                rows.append(dict(file=fname, q=q, k=k + 1, B_fgn=b_fgn[k], B_orig=b_orig[k]))
        m = pd.DataFrame(rows).merge(r, on=["file", "q", "k"], suffixes=("", "_ref"))
        d = (m.B_fgn - m.B_fgn_ref)
        gap_mine = m.B_fgn - m.B_surr_mean        # FGN vs shuffled, my run
        gap_ref = m.B_fgn_ref - m.B_surr_mean     # same, reference
        print(f"  B_fgn - ref : mean {d.mean():+.4f}  std {d.std():.4f}  max|.| {d.abs().max():.4f}")
        print(f"  B_fgn - B_surr: mine mean {gap_mine.mean():+.4f} (std {gap_mine.std():.4f})   "
              f"ref mean {gap_ref.mean():+.4f} (std {gap_ref.std():.4f})")
        frac_mine = (m.B_orig > m.B_fgn).mean()
        frac_ref = (m.B_orig_ref > m.B_fgn_ref).mean()
        print(f"  fraction B_orig > B_fgn over (q,k): mine {frac_mine:.3f}   ref {frac_ref:.3f}")
        summary.append(dict(file=fname, alpha=fgn.alpha_text, alpha_ref=a_ref, alpha0=fgn.alpha0,
                            alpha0_ref=a0_ref, alpha_surr=fgn.alpha_surr, dB_mean=d.mean(), dB_max=d.abs().max(),
                            frac_mine=frac_mine, frac_ref=frac_ref))

    s = pd.DataFrame(summary)
    print("\n" + s.round(4).to_string(index=False))
    print(f"\nmax |alpha_surr - alpha| = {(s.alpha_surr - s.alpha).abs().max():.4f}   "
          f"max |B_fgn - ref| = {s.dB_max.max():.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
