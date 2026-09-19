"""Top-n word types at each pole of a principal component, as LaTeX cells."""
from collections import Counter
import numpy as np

def poles(an, wv, k, n=6, min_freq=1):
    """Return (positive, negative) lists of (word, freq) for component k (0-based).
    min_freq is a display threshold only; it does not affect the analysis."""
    freq  = Counter(an.text.tokens_filtered)
    types = [t for t in freq if t in wv and freq[t] >= min_freq]
    E     = np.array([wv[t] for t in types], dtype=float)
    s     = (E - an.pca.mean) @ an.pca.components[k]
    order = np.argsort(s)
    neg = [(types[i], freq[types[i]]) for i in order[:n]]
    pos = [(types[i], freq[types[i]]) for i in order[::-1][:n]]
    return pos, neg

def latex_rows(an, wv, k, B_k, n=6, bold=False, min_freq=1):
    pos, neg = poles(an, wv, k, n, min_freq)
    fmt = lambda lst: ", ".join(rf"\emph{{{t}}} ({f})" for t, f in lst)
    b = rf"\textbf{{{B_k:.3f}}}" if bold else f"{B_k:.3f}"
    return (f"PC{k+1} & $+$ & {b} &\n  {fmt(pos)}\n  & INTERPRETATION \\\\\n"
            f"PC{k+1} & $-$ & &\n  {fmt(neg)}\n  & INTERPRETATION \\\\")

if __name__ == "__main__":
    import argparse
    from pathlib import Path
    from semburst.burst import burstiness_spectrum, thresholds
    from semburst.config import DEFAULT as P
    from semburst.embed import load_vectors
    from semburst.pipeline import analyse_text

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("text", help="corpus file, as given to run_text.py")
    ap.add_argument("--pcs", type=int, nargs="+", default=[1, 2, 3],
                    help="1-based component indices (default: 1 2 3)")
    ap.add_argument("-n", type=int, default=6, help="words per pole")
    ap.add_argument("--min-freq", type=int, default=1,
                    help="display threshold: show only types with at least this frequency")
    args = ap.parse_args()

    wv = load_vectors()
    an = analyse_text(Path(args.text), wv)
    B = burstiness_spectrum(an.pca.proj, thresholds(an.pca.proj, P.quantile))
    kmax = int(np.argmax(B))
    print(f"% {Path(args.text).stem}: B_max = {B[kmax]:.3f} at PC{kmax+1}"
          f"{f', display threshold freq >= {args.min_freq}' if args.min_freq > 1 else ''}")
    for i, pc in enumerate(args.pcs):
        k = pc - 1
        if not 0 <= k < an.pca.components.shape[0]:
            raise SystemExit(f"PC{pc} unavailable: only {an.pca.components.shape[0]} eigenvectors stored")
        print(latex_rows(an, wv, k, B[k], n=args.n, bold=(k == kmax), min_freq=args.min_freq))
        if i < len(args.pcs) - 1:
            print(r"\midrule")