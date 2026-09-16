"""Corpus batch: for every text, burstiness spectrum x quantile sweep, ACF of projections,
DFA of projections — one PCA and one FGN surrogate per text, shared by the three tables.

Writes results/corpus_burstiness.csv, results/corpus_acf.csv, results/corpus_dfa.csv
(same columns as the reference tables) and results/run_corpus.log with environment info.
Per-text partial results are cached in results/runs/<file>.<table>.csv, so an interrupted
run resumes where it stopped; use --force to recompute.

Usage:
    python scripts/run_corpus.py data/corpus
    python scripts/run_corpus.py data/corpus --texts eng_ulysses.txt doriangray.txt
    python scripts/run_corpus.py data/corpus --force
"""
import argparse
import platform
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd

from semburst import __version__
from semburst.config import DEFAULT as P
from semburst.embed import VECTORS_SHA256, load_vectors
from semburst.pipeline import acf_rows, analyse_text, burstiness_rows, dfa_rows

TABLES = {"burstiness": burstiness_rows, "acf": acf_rows, "dfa": dfa_rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--texts", nargs="*", default=None, help="subset of file names (default: all *.txt)")
    ap.add_argument("--out", default="results")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    corpus = Path(args.corpus_dir)
    out = Path(args.out)
    runs = out / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    files = sorted(corpus / f for f in args.texts) if args.texts else sorted(corpus.glob("*.txt"))

    import nltk
    log = [f"semburst {__version__}  python {platform.python_version()}  numpy {np.__version__}  "
           f"nltk {nltk.__version__}  {platform.platform()}",
           f"vectors sha256 {VECTORS_SHA256}", f"params {asdict(P)}", f"{len(files)} files"]
    print("\n".join(log))
    wv = load_vectors()

    for i, fpath in enumerate(files, 1):
        parts = {t: runs / f"{fpath.name}.{t}.csv" for t in TABLES}
        if not args.force and all(p.exists() for p in parts.values()):
            print(f"[{i}/{len(files)}] {fpath.name}: cached")
            continue
        t0 = time.time()
        a = analyse_text(fpath, wv)
        for t, fn in TABLES.items():
            pd.DataFrame(fn(a)).to_csv(parts[t], index=False)
        line = (f"[{i}/{len(files)}] {fpath.name}: N={a.text.N_all} M={a.M} M_fgn={a.M_fgn} "
                f"alpha={a.fgn.alpha_text:.4f} alpha0={a.fgn.alpha0:.4f} alpha_surr={a.fgn.alpha_surr:.4f} "
                f"seed={a.fgn.seed} bisect_evals={len(a.fgn.log)}  {time.time()-t0:.0f} s")
        print(line)
        log.append(line)

    for t in TABLES:
        df = pd.concat([pd.read_csv(runs / f"{f.name}.{t}.csv") for f in files], ignore_index=True)
        df.to_csv(out / f"corpus_{t}.csv", index=False)
        log.append(f"corpus_{t}.csv: {len(df)} rows, {df.file.nunique()} files")
    (out / "run_corpus.log").write_text("\n".join(log) + "\n")
    print("\n".join(log[-3:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
