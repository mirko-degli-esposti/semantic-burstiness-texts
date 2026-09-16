"""Step 4a validation: DFA exponent alpha of the Zipf-rank series vs the reference CSV,
computed with (i) the legacy regex tokeniser used by the notebook's FGN code (raw file,
no Gutenberg stripping) and (ii) the pipeline tokeniser (word_tokenize, Gutenberg stripped).

Usage:
    python scripts/check_dfa.py data/corpus
"""
import argparse
import sys
import time
from pathlib import Path

import pandas as pd

from semburst.dfa import text_alpha
from semburst.text import load_text, strip_gutenberg, tokenise_legacy_regex


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--ref", default="results/reference/corpus_burstiness.csv")
    args = ap.parse_args()

    ref = pd.read_csv(args.ref).groupby("file")[["alpha", "alpha0"]].first()
    rows = []
    print(f"{'file':36s} {'ref':>7s} {'legacy':>7s} {'diff':>8s}  {'leg+strip':>9s} {'diff':>8s}   {'nltk':>7s} {'diff':>8s}   sec")
    for fname, row in ref.iterrows():
        fpath = Path(args.corpus_dir) / fname
        t0 = time.time()
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        a_legacy = text_alpha(tokenise_legacy_regex(raw))
        a_strip = text_alpha(tokenise_legacy_regex(strip_gutenberg(raw)))
        a_nltk = text_alpha(load_text(fpath).tokens_all)
        rows.append(dict(file=fname, alpha_ref=row.alpha, alpha_legacy=a_legacy, alpha_strip=a_strip, alpha_nltk=a_nltk))
        print(f"{fname:36s} {row.alpha:7.4f} {a_legacy:7.4f} {a_legacy-row.alpha:+8.4f}  "
              f"{a_strip:9.4f} {a_strip-row.alpha:+8.4f}   "
              f"{a_nltk:7.4f} {a_nltk-row.alpha:+8.4f}   {time.time()-t0:4.1f}")
    df = pd.DataFrame(rows)
    d_leg = (df.alpha_legacy - df.alpha_ref).abs()
    d_nltk = (df.alpha_nltk - df.alpha_ref).abs()
    print(f"\nlegacy tokeniser : max|diff| {d_leg.max():.4f}   exact(4dp) {(d_leg <= 5.1e-5).sum()}/{len(df)}")
    d_strip = (df.alpha_strip - df.alpha_ref).abs()
    print(f"legacy + strip   : max|diff| {d_strip.max():.4f}   mean {d_strip.mean():.4f}   (effect of Gutenberg boilerplate)")
    print(f"nltk tokeniser   : max|diff| {d_nltk.max():.4f}   mean {d_nltk.mean():.4f}   "
          f"max |nltk-legacy| {(df.alpha_nltk-df.alpha_legacy).abs().max():.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
