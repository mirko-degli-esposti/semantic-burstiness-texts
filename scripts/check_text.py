"""Step 1 validation: tokenisation + filtering against the Colab reference CSV.

Usage:
    python scripts/check_text.py /path/to/corpus [--ref results/reference/corpus_burstiness.csv]

For every .txt in the corpus dir that appears in the reference, recompute N_all and N_filt
and compare. Exit code 1 if any mismatch.
"""
import argparse
import sys
import time
from pathlib import Path

import pandas as pd

from semburst.text import load_text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--ref", default="results/reference/corpus_burstiness.csv")
    args = ap.parse_args()

    ref = pd.read_csv(args.ref).groupby("file")[["N_all", "N_filt", "M_filtered"]].first()
    corpus = Path(args.corpus_dir)

    bad = 0
    print(f"{'file':36s} {'N_all':>8s} {'ref':>8s}   {'N_filt':>8s} {'ref':>8s}   ok   sec")
    for fname, row in ref.iterrows():
        fpath = corpus / fname
        if not fpath.exists():
            print(f"{fname:36s} MISSING")
            continue
        t0 = time.time()
        tt = load_text(fpath)
        ok = tt.N_all == row.N_all and tt.N_filt == row.N_filt
        bad += not ok
        print(f"{fname:36s} {tt.N_all:8d} {row.N_all:8d}   {tt.N_filt:8d} {row.N_filt:8d}   "
              f"{'OK ' if ok else 'XX '} {time.time()-t0:5.1f}")
    print(f"\n{len(ref) - bad}/{len(ref)} files match exactly")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
