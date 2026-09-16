"""Single-text figures for the paper.  Writes figures/<stem>/<stem>_<nn>_<name>.png.

Usage:
    python scripts/run_text.py data/corpus/eng_wrnpc.txt
    python scripts/run_text.py data/corpus/eng_wrnpc.txt data/corpus/eng_ulysses.txt --only 04 06
"""
import argparse
import sys
import time
from pathlib import Path

from semburst import figures as F
from semburst.embed import load_vectors
from semburst.pipeline import analyse_text

FIGS = {
    "02_spectra_comparison":     lambda a, wv: F.fig_spectra(a, wv),
    "03_iet_comparison":         lambda a, wv: F.fig_iet(a),
    "04_burstiness_spectrum":    lambda a, wv: F.fig_burstiness(a),
    "06_quantile_sweep":         lambda a, wv: F.fig_quantile_sweep(a),
    "07_semantic_pos_poles":     lambda a, wv: F.fig_semantic_poles(a, wv),
    "08_acf_decay_loglag":       lambda a, wv: F.fig_acf_decay(a),
    "09_acf_mean_loglag":        lambda a, wv: F.fig_acf_mean(a),
    "10_dfa_projections_spectrum": lambda a, wv: F.fig_dfa_spectrum(a),
    "11_dfa_projections_loglog": lambda a, wv: F.fig_dfa_loglog(a),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="figures")
    ap.add_argument("--only", nargs="*", default=None, help="figure number prefixes, e.g. 04 06")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    wv = load_vectors()
    for f in args.files:
        fpath = Path(f); stem = fpath.stem
        outdir = Path(args.out) / stem; outdir.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        a = analyse_text(fpath, wv)
        print(f"{fpath.name}: M={a.M} alpha={a.fgn.alpha_text:.3f} alpha0={a.fgn.alpha0:.3f}  ({time.time()-t0:.0f} s)")
        for name, fn in FIGS.items():
            if args.only and not any(name.startswith(p) for p in args.only):
                continue
            fig = fn(a, wv)
            path = outdir / f"{stem}_{name}.png"
            fig.savefig(path, dpi=args.dpi, bbox_inches="tight")
            import matplotlib.pyplot as plt; plt.close(fig)
            print(f"  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
