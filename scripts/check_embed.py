"""Step 2 validation: embedding trajectory length (M_filtered) against the Colab reference CSV.

Usage:
    python scripts/check_embed.py data/corpus
"""
import argparse
import sys
import time
from pathlib import Path

import pandas as pd

from semburst.embed import build_trajectory, load_vectors
from semburst.text import load_text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--ref", default="results/reference/corpus_burstiness.csv")
    args = ap.parse_args()

    t0 = time.time()
    wv = load_vectors()
    print(f"vectors: {len(wv):,} words x {wv.vector_size}d  ({time.time()-t0:.0f} s)\n")

    ref = pd.read_csv(args.ref).groupby("file")[["N_filt", "M_filtered"]].first()
    corpus = Path(args.corpus_dir)

    bad = 0
    print(f"{'file':36s} {'N_filt':>8s} {'M_filt':>8s} {'ref':>8s}   {'OOV%':>5s}  ok")
    for fname, row in ref.iterrows():
        fpath = corpus / fname
        if not fpath.exists():
            print(f"{fname:36s} MISSING"); continue
        tt = load_text(fpath)
        vecs, pos = build_trajectory(tt.tokens_filtered, wv)
        M = len(vecs)
        ok = M == row.M_filtered
        bad += not ok
        print(f"{fname:36s} {tt.N_filt:8d} {M:8d} {row.M_filtered:8d}   {100*(1-M/tt.N_filt):5.1f}  {'OK' if ok else 'XX'}")
    print(f"\n{len(ref) - bad}/{len(ref)} files match exactly")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
