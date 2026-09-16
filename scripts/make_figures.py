"""Corpus-level figures of the paper, from results/corpus_*.csv only (no recomputation).

  figures/fig1_mean_spectrum.png           mean B_k over texts, q=0.95
  figures/fig2_robustness_vs_q.png         ordering fractions vs q
  figures/fig3_difference_distributions.png distributions of burstiness ratios, q=0.95
  figures/acf_corpus_mean_decay.png        mean rho(l) over (text,k)
  figures/acf_corpus_frac_significant.png  fraction significant vs lag
  figures/acf_corpus_rho1_distribution.png distribution of rho_k(1)

Usage:  python scripts/make_figures.py [--results results --out figures]
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp

C_ORIG, C_SURR, C_FGN, C_FULL = "steelblue", "tomato", "seagreen", "purple"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})


def fig1(b, q=0.95):
    s = b[b.q == q]
    g = s.groupby("k")[["B_orig", "B_surr_mean", "B_fgn"]].agg(["mean", "std"])
    ks = g.index.values
    fig, ax = plt.subplots(figsize=(10, 5))
    for col, lab, c, m in [("B_orig", "Original", C_ORIG, "o-"), ("B_fgn", "FGN surrogate", C_FGN, "^-"),
                           ("B_surr_mean", "Word-shuffled", C_SURR, "s--")]:
        mu, sd = g[(col, "mean")], g[(col, "std")]
        ax.plot(ks, mu, m, color=c, ms=6, lw=1.8, label=lab)
        ax.fill_between(ks, mu - sd, mu + sd, color=c, alpha=0.12)
    ax.axhline(np.sqrt(q), color="black", ls="--", lw=1.5, label=f"Geometric baseline $\\sqrt{{q}}={np.sqrt(q):.3f}$")
    ax.set_xlabel("PCA component $k$", fontsize=12); ax.set_ylabel(r"$\langle B_k\rangle_{\rm texts}$", fontsize=12)
    ax.set_xticks(ks); ax.set_title(f"Mean burstiness spectrum over {s.file.nunique()} texts   $q={q}$")
    ax.legend(); ax.grid(alpha=0.25); fig.tight_layout()
    return fig


def fig2(b):
    qs = sorted(b.q.unique())
    rows = []
    for q in qs:
        s = b[b.q == q]
        rows.append(dict(q=q, surr=(s.B_orig > s.B_surr_mean).mean(), fgn=(s.B_orig > s.B_fgn).mean(),
                         full=((s.B_orig > s.B_surr_mean) & (s.B_orig > s.B_fgn)).mean(),
                         close=((s.B_fgn / s.B_surr_mean - 1).abs() < 0.05).mean()))
    r = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(r.q, r.full, "o-", color=C_FULL, ms=8, lw=2, label=r"$B^{\rm orig}_k > B^{\rm surr}_k$ and $B^{\rm orig}_k > B^{\rm FGN}_k$")
    ax.plot(r.q, r.surr, "s-", color=C_SURR, ms=6, lw=1.3, label=r"$B^{\rm orig}_k > B^{\rm surr}_k$")
    ax.plot(r.q, r.fgn, "^-", color=C_FGN, ms=6, lw=1.3, label=r"$B^{\rm orig}_k > B^{\rm FGN}_k$")
    ax.plot(r.q, r.close, "D--", color="grey", ms=6, lw=1.3, label=r"$|B^{\rm FGN}_k/B^{\rm surr}_k - 1| < 0.05$")
    ax.set_xlabel("Quantile threshold $q$", fontsize=12); ax.set_ylabel("Fraction of (text, $k$) pairs", fontsize=12)
    ax.set_ylim(0.6, 1.02); ax.set_xticks(qs); ax.grid(alpha=0.25); ax.legend(loc="lower left")
    ax.set_title(f"Robustness of the ordering across $q$  ({len(b[b.q == qs[0]])} pairs per $q$)")
    fig.tight_layout()
    return fig, r


def fig3(b, q=0.95):
    s = b[b.q == q]
    r_s, r_f, r_fs = s.B_orig / s.B_surr_mean, s.B_orig / s.B_fgn, s.B_fgn / s.B_surr_mean
    t = ttest_1samp(r_fs, 1.0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
    bins = np.linspace(0.9, min(2.5, max(r_s.max(), r_f.max())), 45)
    ax1.hist(r_s, bins=bins, color=C_SURR, alpha=0.55, label=r"$B^{\rm orig}_k / B^{\rm surr}_k$")
    ax1.hist(r_f, bins=bins, color=C_FGN, alpha=0.55, label=r"$B^{\rm orig}_k / B^{\rm FGN}_k$")
    ax1.axvline(1, color="black", lw=1.2); ax1.set_xlabel("ratio"); ax1.set_ylabel("count")
    ax1.set_title(f"A.  original / null   (means {r_s.mean():.3f}, {r_f.mean():.3f})"); ax1.legend(); ax1.grid(alpha=0.25)
    ax2.hist(r_fs, bins=40, color="grey", alpha=0.7)
    ax2.axvline(1, color="black", lw=1.2); ax2.set_xlabel(r"$B^{\rm FGN}_k / B^{\rm surr}_k$"); ax2.set_ylabel("count")
    ax2.set_title(f"B.  FGN / shuffled   (mean {r_fs.mean():.4f}, s.e. {r_fs.std(ddof=1)/np.sqrt(len(r_fs)):.4f}; "
                  f"$t={t.statistic:.2f}$, $p={t.pvalue:.2g}$)")
    ax2.grid(alpha=0.25)
    fig.suptitle(f"Burstiness ratios over {len(s)} (text, $k$) pairs at $q={q}$"); fig.tight_layout()
    return fig


def acf_mean(a):
    g = a.groupby("lag")[["rho_orig", "rho_fgn", "rho_surr", "ci_95"]].agg(["mean", "std"])
    lags = g.index.values
    fig, ax = plt.subplots(figsize=(9, 5))
    for col, lab, c, m in [("rho_orig", "Original", C_ORIG, "o-"), ("rho_fgn", "FGN surrogate", C_FGN, "^-"),
                           ("rho_surr", "Word-shuffled", C_SURR, "s--")]:
        mu, sd = g[(col, "mean")], g[(col, "std")]
        ax.semilogx(lags, mu, m, color=c, ms=6, lw=1.8, label=lab)
        ax.fill_between(lags, mu - sd, mu + sd, color=c, alpha=0.12)
    ci = g[("ci_95", "mean")].mean()
    ax.axhspan(-ci, ci, color="grey", alpha=0.2, label=r"mean 95% i.i.d. band $\pm1.96/\sqrt{M}$")
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xlabel(r"Lag $\ell$", fontsize=12); ax.set_ylabel(r"$\bar\rho(\ell)$ over (text, $k$)", fontsize=12)
    ax.set_title(f"Mean ACF of projected series — {a.file.nunique()} texts × 20 components"); ax.legend(); ax.grid(alpha=0.2, which="both")
    fig.tight_layout()
    return fig


def acf_frac(a):
    g = a.groupby("lag")[["orig_sig", "fgn_sig", "surr_sig"]].mean()
    both = a.assign(x=(a.orig_sig == 1) & (a.fgn_sig == 0)).groupby("lag").x.mean()
    lags = g.index.values
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.semilogx(lags, g.orig_sig, "o-", color=C_ORIG, ms=6, lw=1.8, label="Original")
    ax.semilogx(lags, g.fgn_sig, "^-", color=C_FGN, ms=6, lw=1.5, label="FGN surrogate")
    ax.semilogx(lags, g.surr_sig, "s-", color=C_SURR, ms=6, lw=1.5, label="Word-shuffled")
    ax.semilogx(lags, both, "d--", color=C_FULL, ms=5, lw=1.2, label="Original significant and FGN not")
    ax.axhline(0.05, color="grey", ls=":", lw=1.2, label="5% (false-positive rate)")
    ax.set_ylim(0, 1.02); ax.set_xlabel(r"Lag $\ell$", fontsize=12); ax.set_ylabel("Fraction of (text, $k$) pairs", fontsize=12)
    ax.set_title(r"Fraction of pairs with $|\rho_k(\ell)| > 1.96/\sqrt{M}$"); ax.legend(); ax.grid(alpha=0.2, which="both")
    fig.tight_layout()
    return fig, g


def acf_rho1(a):
    s = a[a.lag == 1]
    t = ttest_1samp(s.rho_fgn, 0.0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.8))
    bins = np.linspace(min(s.rho_fgn.min(), 0) - 0.01, s.rho_orig.max() + 0.01, 50)
    ax1.hist(s.rho_orig, bins=bins, color=C_ORIG, alpha=0.6, label="Original")
    ax1.hist(s.rho_fgn, bins=bins, color=C_FGN, alpha=0.6, label="FGN surrogate")
    ax1.set_xlabel(r"$\rho_k(1)$"); ax1.set_ylabel("count"); ax1.set_title("A.  original vs FGN"); ax1.legend(); ax1.grid(alpha=0.25)
    lim = 1.1 * max(s.rho_fgn.abs().max(), s.rho_surr.abs().max())
    bins2 = np.linspace(-lim, lim, 40)
    ax2.hist(s.rho_fgn, bins=bins2, color=C_FGN, alpha=0.6, label="FGN surrogate")
    ax2.hist(s.rho_surr, bins=bins2, color=C_SURR, alpha=0.6, label="Word-shuffled")
    ax2.axvline(0, color="black", lw=1)
    ax2.set_xlabel(r"$\rho_k(1)$"); ax2.set_title(f"B.  FGN vs shuffled   (FGN mean {s.rho_fgn.mean():.4f}, $t={t.statistic:.2f}$)")
    ax2.legend(); ax2.grid(alpha=0.25)
    fig.suptitle(f"Distribution of $\\rho_k(1)$ over {len(s)} (text, $k$) pairs"); fig.tight_layout()
    return fig


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--out", default="figures")
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()
    R, out = Path(args.results), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    b = pd.read_csv(R / "corpus_burstiness.csv")
    a = pd.read_csv(R / "corpus_acf.csv")
    a = a[a.file != "aliceinwonderland.txt"]

    figs = {"fig1_mean_spectrum": fig1(b)}
    f2, r2 = fig2(b); figs["fig2_robustness_vs_q"] = f2
    figs["fig3_difference_distributions"] = fig3(b)
    figs["acf_corpus_mean_decay"] = acf_mean(a)
    f5, g5 = acf_frac(a); figs["acf_corpus_frac_significant"] = f5
    figs["acf_corpus_rho1_distribution"] = acf_rho1(a)
    for name, fig in figs.items():
        p = out / f"{name}.png"; fig.savefig(p, dpi=args.dpi, bbox_inches="tight"); plt.close(fig); print(p)

    # numbers behind the captions
    print("\nordering fractions vs q:\n" + r2.round(4).to_string(index=False))
    print("\nfraction significant by lag:\n" + g5.round(4).to_string())
    s1 = a[a.lag == 1]
    byk = s1.groupby("k").fgn_sig.mean()
    print(f"\nFGN significant at lag 1, by component: PC1 {byk.loc[1]:.3f}, PC2 {byk.loc[2]:.3f}, PC3 {byk.loc[3]:.3f}, "
          f"mean over k>=4 {byk.loc[4:].mean():.3f}  (caption claims the excess is concentrated in PC1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
