"""Main-text figures for the four showcase texts: the multi-panel versions that replace
the four separate per-text figures, plus the LaTeX table of semantic poles.

Writes, under --out (default figures/):
    panel_burstiness_spectra.png    2x2 burstiness spectra (replaces four *_04_* figures)
    panel_quantile_sweep.png        2x2 quantile sweep    (replaces four *_06_* figures)
    table_semantic_poles.tex        top word types on PC1-PC3 (replaces four *_07_* figures)

The per-text figures themselves are still produced by scripts/run_text.py; the three
non-showcase series (02 spectra, 03 IET) go to the appendix.

Usage:
    python scripts/run_main_figures.py data/corpus
    python scripts/run_main_figures.py data/corpus --texts a.txt b.txt --n-top 12
"""
import argparse
import sys
import time
from pathlib import Path

import matplotlib.pyplot as plt

from semburst import figures as F
from semburst.embed import load_vectors
from semburst.pipeline import analyse_text

SHOWCASE = ["eng_wrnpc.txt", "darwin_origin.txt", "great_expectations_cut_clean.txt", "eng_ulysses.txt"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--texts", nargs="*", default=SHOWCASE)
    ap.add_argument("--out", default="figures")
    ap.add_argument("--n-pc", type=int, default=3, help="components in the poles table")
    ap.add_argument("--n-top", type=int, default=10, help="word types per component")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    wv = load_vectors()

    analyses = []
    for name in args.texts:
        t0 = time.time()
        a = analyse_text(Path(args.corpus_dir) / name, wv)
        analyses.append(a)
        print(f"{name}: M={a.M} alpha={a.fgn.alpha_text:.3f} alpha0={a.fgn.alpha0:.2f}  ({time.time()-t0:.0f} s)")

    for fig, fname in [(F.fig_burstiness_panel(analyses), "panel_burstiness_spectra.png"),
                       (F.fig_quantile_sweep_panel(analyses), "panel_quantile_sweep.png")]:
        p = out / fname
        fig.savefig(p, dpi=args.dpi, bbox_inches="tight")
        plt.close(fig)
        print(p)

    tex = out / "table_semantic_poles.tex"
    tex.write_text(F.semantic_poles_table(analyses, wv, n_pc=args.n_pc, n_top=args.n_top) + "\n")
    print(tex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
