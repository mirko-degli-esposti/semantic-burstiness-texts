"""Step 3 validation: B_orig, B_surr_mean, B_surr_std against the Colab reference CSV,
for all q in the sweep and all K components.

Usage:
    python scripts/check_burst.py data/corpus                    # doriangray.txt only
    python scripts/check_burst.py data/corpus --texts eng_ulysses.txt darwin_origin.txt
    python scripts/check_burst.py data/corpus --all
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from semburst.burst import burstiness_spectrum, shuffle_permutations, shuffled_burstiness, thresholds
from semburst.config import DEFAULT as P
from semburst.embed import build_trajectory, load_vectors
from semburst.pca import fit_pca
from semburst.text import load_text

TOL_EXACT = 5.1e-5   # CSV values are rounded to 4 decimals
TOL_LOOSE = 2e-3


def fit_pca_sklearn(vecs, k):
    """Exactly the notebook's call, for diagnostics only."""
    from sklearn.decomposition import PCA
    from semburst.pca import PCAResult
    mean = vecs.mean(axis=0)
    X = vecs - mean
    sk = PCA(n_components=k, random_state=42)
    proj = sk.fit_transform(X)
    return PCAResult(mean, sk.components_, proj, sk.explained_variance_, sk.explained_variance_ratio_)


def run_text(fpath: Path, wv, use_sklearn=False, n_surr=P.n_surr) -> pd.DataFrame:
    tt = load_text(fpath)
    vecs, _ = build_trajectory(tt.tokens_filtered, wv)
    pca = fit_pca_sklearn(vecs, P.k_burst) if use_sklearn else fit_pca(vecs, P.k_burst)
    perms = shuffle_permutations(len(vecs), n_surr)
    rows = []
    for q in P.q_sweep:
        th = thresholds(pca.proj, q)
        b_orig = burstiness_spectrum(pca.proj, th)
        b_mean, b_std = shuffled_burstiness(pca.proj, perms, th)
        for k in range(P.k_burst):
            rows.append(dict(file=fpath.name, q=q, k=k + 1, M=len(vecs),
                             B_orig=b_orig[k], B_surr_mean=b_mean[k], B_surr_std=b_std[k]))
    return pd.DataFrame(rows), pca


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--texts", nargs="*", default=["doriangray.txt"])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--ref", default="results/reference/corpus_burstiness.csv")
    ap.add_argument("--sklearn", action="store_true", help="use sklearn PCA exactly as the notebook did")
    ap.add_argument("--nsurr", type=int, default=P.n_surr,
                    help="number of shuffled surrogates; >20 enables the z-score test of the reference mean")
    args = ap.parse_args()
    if args.sklearn:
        import sklearn
        print(f"using sklearn {sklearn.__version__} PCA(random_state=42)")

    ref = pd.read_csv(args.ref)
    texts = sorted(ref.file.unique()) if args.all else args.texts
    wv = load_vectors()

    worst = 0.0
    all_z = []
    for fname in texts:
        t0 = time.time()
        mine, pca = run_text(Path(args.corpus_dir) / fname, wv, args.sklearn, args.nsurr)
        r = ref[ref.file == fname]
        m = mine.merge(r, on=["file", "q", "k"], suffixes=("", "_ref"))
        print(f"\n{fname}   M={mine.M.iloc[0]} (ref {r.M_filtered.iloc[0]})   "
              f"EVR PC1..3 = {pca.explained_variance_ratio[:3].round(4)}   {time.time()-t0:.0f} s")
        for col in ["B_orig", "B_surr_mean", "B_surr_std"]:
            d = (m[col] - m[f"{col}_ref"]).abs()
            worst = max(worst, np.nanmax(d))
            print(f"  {col:12s} max|diff|={np.nanmax(d):.5f}   "
                  f"exact {(d <= TOL_EXACT).sum():3d}/{len(d)}   within {TOL_LOOSE:g} {(d <= TOL_LOOSE).sum():3d}/{len(d)}")
        byq = m.groupby("q").apply(lambda g: pd.Series({c: (g[c] - g[f"{c}_ref"]).abs().max()
                                                          for c in ["B_orig", "B_surr_mean", "B_surr_std"]}))
        print("  max|diff| by q:\n" + byq.round(5).to_string())
        if args.nsurr > P.n_surr:
            # reference mean is over 20 permutations: its standard error is sigma/sqrt(20)
            z = (m.B_surr_mean_ref - m.B_surr_mean) / (m.B_surr_std / np.sqrt(P.n_surr))
            z = z[np.isfinite(z)]
            all_z.append(z)
            print(f"  z-test of B_surr_mean_ref (n={args.nsurr} local perms): mean z={z.mean():+.3f}  "
                  f"std z={z.std():.3f}  |z|>2: {(z.abs() > 2).mean():.1%}  |z|>3: {(z.abs() > 3).mean():.1%}")
        # sign diagnostic: components where B_orig is off for every q
        off = m.assign(d=(m.B_orig - m.B_orig_ref).abs()).groupby("k").d.min()
        bad_k = list(off[off > TOL_LOOSE].index)
        if bad_k:
            print(f"  components off at every q: {bad_k}  -> probable sign / axis mismatch")
    print(f"\nworst |diff| overall: {worst:.5f}")
    if all_z:
        z = pd.concat(all_z)
        print(f"pooled z over {len(z)} rows: mean {z.mean():+.3f}  std {z.std():.3f}  "
              f"|z|>2: {(z.abs() > 2).mean():.1%} (expect ~4.6%)  |z|>3: {(z.abs() > 3).mean():.1%} (expect ~0.3%)")
    return 0 if worst <= TOL_LOOSE else 1


if __name__ == "__main__":
    sys.exit(main())
