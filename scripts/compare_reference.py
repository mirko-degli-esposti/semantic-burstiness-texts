"""Compare the regenerated corpus tables (results/) with the Colab reference tables
(results/reference/): per-column agreement, and the corpus-level numbers used in the paper.

Usage:
    python scripts/compare_reference.py [--new results --ref results/reference]
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KEYS = {"burstiness": ["file", "q", "k"], "acf": ["file", "k", "lag"], "dfa": ["file", "k"]}


def column_report(new: pd.DataFrame, ref: pd.DataFrame, keys: list[str], title: str) -> pd.DataFrame:
    m = new.merge(ref, on=keys, suffixes=("", "_ref"))
    rows = []
    for c in new.columns:
        if c in keys or f"{c}_ref" not in m or not np.issubdtype(m[c].dtype, np.number):
            continue
        d = m[c] - m[f"{c}_ref"]
        rows.append(dict(column=c, mean_diff=d.mean(), max_abs=d.abs().max(),
                         exact=(d.abs() <= 5.1e-5).mean(), within_1e2=(d.abs() <= 1e-2).mean()))
    rep = pd.DataFrame(rows)
    print(f"\n=== {title}: {len(m)} matched rows (new {len(new)}, ref {len(ref)})")
    print(rep.round(4).to_string(index=False))
    return m


def paper_numbers(m: pd.DataFrame) -> None:
    print("\n--- corpus-level numbers (burstiness) ---")
    for tag in ("", "_ref"):
        q95 = m[m.q == 0.95]
        per_text = q95.groupby("file").apply(
            lambda g: pd.Series({"orig/surr": (g[f"B_orig{tag}"] / g[f"B_surr_mean{tag}"]).mean(),
                                 "orig/fgn": (g[f"B_orig{tag}"] / g[f"B_fgn{tag}"]).mean(),
                                 "fgn/surr": (g[f"B_fgn{tag}"] / g[f"B_surr_mean{tag}"]).mean()}))
        print(f"{'NEW' if tag == '' else 'REF'} q=0.95 mean ratio over texts: "
              f"orig/surr {per_text['orig/surr'].mean():.3f} (sd {per_text['orig/surr'].std():.3f})   "
              f"orig/fgn {per_text['orig/fgn'].mean():.3f} (sd {per_text['orig/fgn'].std():.3f})   "
              f"fgn/surr {per_text['fgn/surr'].mean():.3f} (sd {per_text['fgn/surr'].std():.3f})")
    print("\nfraction of (text,k) with B_orig > B_fgn and B_orig > B_surr_mean, by q:")
    for q in sorted(m.q.unique()):
        s = m[m.q == q]
        f_new = ((s.B_orig > s.B_fgn) & (s.B_orig > s.B_surr_mean)).mean()
        f_ref = ((s.B_orig_ref > s.B_fgn_ref) & (s.B_orig_ref > s.B_surr_mean_ref)).mean()
        print(f"  q={q:<5} new {f_new:.3f}   ref {f_ref:.3f}")
    print("\nalpha / alpha0 per text (new vs ref):")
    a = m.groupby("file")[["alpha", "alpha_ref", "alpha0", "alpha0_ref"]].first()
    a["d_alpha"] = a.alpha - a.alpha_ref
    a["d_alpha0"] = a.alpha0 - a.alpha0_ref
    print(a.round(4).to_string())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", default="results")
    ap.add_argument("--ref", default="results/reference")
    args = ap.parse_args()
    new, ref = Path(args.new), Path(args.ref)

    b = column_report(pd.read_csv(new / "corpus_burstiness.csv"), pd.read_csv(ref / "corpus_burstiness.csv"),
                      KEYS["burstiness"], "corpus_burstiness")
    paper_numbers(b)

    a = column_report(pd.read_csv(new / "corpus_acf.csv"), pd.read_csv(ref / "corpus_acf.csv"),
                      KEYS["acf"], "corpus_acf  (ref rho_fgn/fgn_sig/alpha unreliable)")
    print("\nfraction outside 95% band, by lag (new | ref):")
    for lag in (1, 10, 50, 100, 300):
        s = a[a.lag == lag]
        if s.empty:
            continue
        print(f"  lag {lag:>3}: orig {s.orig_sig.mean():.3f} | {s.orig_sig_ref.mean():.3f}   "
              f"fgn {s.fgn_sig.mean():.3f} | {s.fgn_sig_ref.mean():.3f}   surr {s.surr_sig.mean():.3f} | {s.surr_sig_ref.mean():.3f}")

    d = column_report(pd.read_csv(new / "corpus_dfa.csv"), pd.read_csv(ref / "corpus_dfa.csv"),
                      KEYS["dfa"], "corpus_dfa")
    print("\nDFA of projections, corpus mean over (text,k) (new | ref):")
    for c in ("dfa_orig", "dfa_fgn", "dfa_surr_mean"):
        print(f"  {c:14s} {d[c].mean():.4f} (sd {d[c].std():.4f}) | {d[f'{c}_ref'].mean():.4f} (sd {d[f'{c}_ref'].std():.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
