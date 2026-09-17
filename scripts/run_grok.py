"""Grokipedia vs Wikipedia: does semantic burstiness distinguish LLM-generated from
human-written encyclopedia entries?

Two analyses, same titles in every corpus (Buddhism excluded: v0.1 copied from Wikipedia):
  A. per-entry, paired by title (parameters adapted to ~15k-token texts):
     mean burstiness spectrum of the original vs the two nulls, DFA of projections,
     rank-series alpha; paired t-test and Wilcoxon between corpora on the same titles.
  B. concatenated corpus with per-entry centring (see pipeline.analyse_blocks):
     the 20-component burstiness spectrum as in the paper, one per corpus.

Usage:
    python scripts/run_grok.py --wiki DIR --grok DIR [--grok01 DIR] [--out results/grok]
Files are matched across corpora by normalised file stem.
"""
import argparse
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ttest_rel, wilcoxon

from semburst.burst import burstiness_spectrum, shuffled_burstiness, thresholds
from semburst.config import Params
from semburst.dfa import projection_alpha
from semburst.embed import load_vectors
from semburst.pipeline import analyse_blocks, analyse_text, burstiness_rows

# per-entry parameters: ~15k raw tokens, M ~ 4-6k
P_ENTRY = Params(max_freq_rank=100, min_freq=3, k_burst=10, quantile=0.90,
                 q_sweep=(0.80, 0.90, 0.95), n_surr=20)
# concatenated corpus: paper parameters
P_CONCAT = Params()
EXCLUDE = {"buddhism"}


def norm(stem: str) -> str:
    return re.sub(r"[^a-z0-9]", "", stem.lower())


def index_dir(d: str | Path) -> dict[str, Path]:
    d = Path(d)
    if not d.is_dir():
        sys.exit(f"error: {d} is not a directory")
    idx = {norm(p.stem): p for p in sorted(d.glob("*.txt"))}
    if not idx:
        sys.exit(f"error: no .txt files in {d}")
    return idx


def entry_summary(fpath: Path, wv, corpus: str) -> dict:
    a = analyse_text(fpath, wv, P_ENTRY)
    q = P_ENTRY.quantile
    th = thresholds(a.pca.proj, q)
    b_o = burstiness_spectrum(a.pca.proj, th)
    b_s, b_ss = shuffled_burstiness(a.pca.proj, a.perms, th)
    b_f = burstiness_spectrum(a.proj_fgn, th)
    d_o = np.array([projection_alpha(a.pca.proj[:, k]) for k in range(P_ENTRY.k_burst)])
    d_f = np.array([projection_alpha(a.proj_fgn[:, k]) for k in range(P_ENTRY.k_burst)])
    return dict(corpus=corpus, title=norm(fpath.stem), file=fpath.name, N=a.text.N_all, M=a.M,
                alpha=a.fgn.alpha_text, alpha0=a.fgn.alpha0, alpha_surr=a.fgn.alpha_surr,
                B_orig=np.nanmean(b_o), B_surr=np.nanmean(b_s), B_fgn=np.nanmean(b_f),
                gap_surr=np.nanmean(b_o) - np.nanmean(b_s), gap_fgn=np.nanmean(b_o) - np.nanmean(b_f),
                frac_orig_gt_both=float(np.mean((b_o > b_s) & (b_o > b_f))),
                dfa_orig=np.nanmean(d_o), dfa_fgn=np.nanmean(d_f), evr1=a.pca.explained_variance_ratio[0])


def paired(df: pd.DataFrame, a: str, b: str, cols) -> pd.DataFrame:
    x = df[df.corpus == a].set_index("title"); y = df[df.corpus == b].set_index("title")
    common = x.index.intersection(y.index)
    rows = []
    for c in cols:
        d = (y.loc[common, c] - x.loc[common, c]).astype(float)
        t = ttest_rel(y.loc[common, c], x.loc[common, c])
        try:
            w = wilcoxon(d).pvalue
        except ValueError:
            w = np.nan
        rows.append(dict(quantity=c, n=len(common), mean_a=x.loc[common, c].mean(), mean_b=y.loc[common, c].mean(),
                         mean_diff=d.mean(), sd_diff=d.std(ddof=1), t=t.statistic, p_t=t.pvalue, p_wilcoxon=w,
                         frac_b_gt_a=float((d > 0).mean())))
    return pd.DataFrame(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wiki", required=True); ap.add_argument("--grok", required=True); ap.add_argument("--grok01", default=None)
    ap.add_argument("--out", default="results/grok")
    ap.add_argument("--skip-concat", action="store_true")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    corpora = {"wiki": index_dir(Path(args.wiki)), "grok": index_dir(Path(args.grok))}
    if args.grok01:
        corpora["grok01"] = index_dir(Path(args.grok01))
    titles = set.intersection(*[set(v) for v in corpora.values()]) - EXCLUDE
    titles = sorted(titles)
    if not titles:
        sys.exit("error: no titles common to all corpora (check that file names match across directories)")
    print(f"{len(titles)} titles common to {list(corpora)}; per-corpus sizes: " + ", ".join(f"{k}={len(v)}" for k, v in corpora.items()))
    wv = load_vectors()

    # A. per-entry
    rows = []
    for c, idx in corpora.items():
        for i, t in enumerate(titles, 1):
            t0 = time.time()
            r = entry_summary(idx[t], wv, c); rows.append(r)
            print(f"[{c} {i}/{len(titles)}] {t:28s} M={r['M']:6d} alpha={r['alpha']:.3f} B_orig={r['B_orig']:.3f} "
                  f"surr={r['B_surr']:.3f} fgn={r['B_fgn']:.3f} dfa={r['dfa_orig']:.3f}  {time.time()-t0:.1f}s")
    df = pd.DataFrame(rows); df.to_csv(out / "entries.csv", index=False)
    cols = ["M", "alpha", "B_orig", "gap_surr", "gap_fgn", "frac_orig_gt_both", "dfa_orig", "evr1"]
    print("\n=== per-corpus means")
    print(df.groupby("corpus")[cols].agg(["mean", "std"]).round(3).to_string())
    tests = []
    for a, b in [("wiki", "grok")] + ([("wiki", "grok01"), ("grok01", "grok")] if "grok01" in corpora else []):
        pt = paired(df, a, b, cols); pt.insert(0, "pair", f"{a} -> {b}"); tests.append(pt)
        print(f"\n=== paired {a} -> {b}\n" + pt.round(4).to_string(index=False))
    pd.concat(tests).to_csv(out / "paired_tests.csv", index=False)

    # B. concatenated with per-entry centring
    if not args.skip_concat:
        allrows = []
        for c, idx in corpora.items():
            t0 = time.time()
            a = analyse_blocks([idx[t] for t in titles], wv, P_CONCAT, center_blocks=True, name=c)
            r = burstiness_rows(a, P_CONCAT); allrows += r
            q95 = [x for x in r if x["q"] == 0.95]
            print(f"\nconcat {c}: N={a.text.N_all} M={a.M} alpha={a.fgn.alpha_text:.3f} alpha0={a.fgn.alpha0:.3f}  "
                  f"q=0.95 mean B: orig {np.mean([x['B_orig'] for x in q95]):.3f} surr {np.mean([x['B_surr_mean'] for x in q95]):.3f} "
                  f"fgn {np.mean([x['B_fgn'] for x in q95]):.3f}   EVR PC1 {100*a.pca.explained_variance_ratio[0]:.2f}%  {time.time()-t0:.0f}s")
        pd.DataFrame(allrows).to_csv(out / "concat_burstiness.csv", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
