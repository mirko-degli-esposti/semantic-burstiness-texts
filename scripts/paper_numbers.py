"""Every data-dependent number quoted in the paper, recomputed from results/corpus_*.csv
and from a per-text pass on the four showcase texts.  Writes results/paper_numbers.md,
listing each quantity with its definition, the new value, and (where known) the value
currently in the .tex ("old").

Usage:
    python scripts/paper_numbers.py data/corpus
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, ttest_1samp

from semburst.acf import acf_matrix, ci95
from semburst.burst import burstiness_spectrum, shuffled_burstiness, thresholds
from semburst.config import DEFAULT as P
from semburst.dfa import projection_alpha
from semburst.embed import load_vectors
from semburst.pipeline import N_SURR_DFA, analyse_text

SHOWCASE = [("eng_wrnpc.txt", "War and Peace"), ("darwin_origin.txt", "Origin of Species"),
            ("great_expectations_cut_clean.txt", "Great Expectations"), ("eng_ulysses.txt", "Ulysses")]
OLD = {  # values currently in paper3_main_v8_reordered_results.tex
    "War and Peace": dict(oov="1.6%", alpha=0.719, alpha0=0.770, r=0.702, p=0.0006, B2=1.855, evr1=6.98, evr2=4.21, cum10=27.2, Bbar=1.18),
    "Origin of Species": dict(oov="0.4%", alpha=0.769, alpha0=0.804, r=0.294, p=0.209, B2=1.888, evr1=6.61, evr2=3.58, cum10=26.4, Bbar=1.10),
    "Great Expectations": dict(oov="1.3%", alpha=0.688, alpha0=0.735, r=0.522, p=0.018, B2=1.209, evr1=6.54, evr2=4.34, cum10=27.2, Bbar=1.07),
    "Ulysses": dict(oov="0.7%", alpha=0.794, alpha0=0.839, r=0.578, p=0.008, B2=1.495, evr1=None, evr2=None, cum10=25.0, Bbar=1.13),
}
L = []


def w(s=""):
    L.append(s)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir")
    ap.add_argument("--out", default="results/paper_numbers.md")
    args = ap.parse_args()
    corpus = Path(args.corpus_dir)
    b = pd.read_csv("results/corpus_burstiness.csv")
    a = pd.read_csv("results/corpus_acf.csv")
    d = pd.read_csv("results/corpus_dfa.csv")
    wv = load_vectors()

    # ───────────────────────── 1. showcase texts ─────────────────────────
    w("# Numbers for the paper (regenerated)\n")
    w("## 1. Four showcase texts (Table tab:single_text_summary and per-text sections)\n")
    w("| text | N | M | OOV (old) | alpha (old) | alpha0 (old) | r(lambda,B) p (old) | B2 (old) |")
    w("|---|---|---|---|---|---|---|---|")
    details = []
    analyses = {}
    for fname, title in SHOWCASE:
        an = analyse_text(corpus / fname, wv)
        analyses[title] = an
        o = OLD[title]
        th = thresholds(an.pca.proj, P.quantile)
        b_o = burstiness_spectrum(an.pca.proj, th)
        b_s, _ = shuffled_burstiness(an.pca.proj, an.perms, th)
        b_f = burstiness_spectrum(an.proj_fgn, th)
        lam = an.pca.eigenvalues[:P.k_burst]
        r, p = pearsonr(lam, b_o)
        oov = 100 * (1 - an.M / an.text.N_filt)
        evr = 100 * an.pca.explained_variance_ratio
        w(f"| {title} | {an.text.N_all:,} | {an.M:,} | {oov:.1f}% ({o['oov']}) | {an.fgn.alpha_text:.3f} ({o['alpha']}) | "
          f"{an.fgn.alpha0:.2f} ({o['alpha0']}) | {r:.3f}, p={p:.4f} ({o['r']}, {o['p']}) | {b_o[1]:.3f} ({o['B2']}) |")
        kmax = int(np.argmax(b_o)) + 1
        details.append((title, o, evr, b_o, b_s, b_f, kmax, an))
    w()
    for title, o, evr, b_o, b_s, b_f, kmax, an in details:
        w(f"### {title}")
        w(f"- EVR PC1 {evr[0]:.2f}% (old {o['evr1']}), PC2 {evr[1]:.2f}% (old {o['evr2']}), PC3 {evr[2]:.2f}%, "
          f"first ten {evr[:10].sum():.1f}% (old {o['cum10']})")
        w(f"- q=0.95: B1={b_o[0]:.3f}, B2={b_o[1]:.3f}, B3={b_o[2]:.3f}; largest at PC{kmax} (B={b_o[kmax-1]:.3f}); "
          f"null at that k: surr {b_s[kmax-1]:.3f}, FGN {b_f[kmax-1]:.3f}")
        w(f"- mean over k=1..20: B_orig {b_o.mean():.3f} (old Bbar {o['Bbar']}), B_surr {b_s.mean():.3f}, B_FGN {b_f.mean():.3f}; "
          f"null range surr [{b_s.min():.3f},{b_s.max():.3f}], FGN [{b_f.min():.3f},{b_f.max():.3f}]")
        w(f"- ordering B_orig > B_FGN and > B_surr at q=0.95: {int(((b_o > b_f) & (b_o > b_s)).sum())}/20")
        fr = []
        for q in P.q_sweep:
            th = thresholds(an.pca.proj, q)
            bo = burstiness_spectrum(an.pca.proj, th); bs, _ = shuffled_burstiness(an.pca.proj, an.perms, th)
            bf = burstiness_spectrum(an.proj_fgn, th); fr.append(f"q={q}: {int(((bo > bf) & (bo > bs)).sum())}/20")
        w("- quantile sweep, full ordering: " + ", ".join(fr))
        w()

    # ───────────────────────── 2. corpus table ─────────────────────────
    w("## 2. Corpus table (tab:corpus) — 16 texts, from corpus_burstiness.csv\n")
    t = b.groupby("file")[["N_all", "M_filtered", "alpha", "alpha0"]].first().sort_index()
    w("| file | N | M | alpha | alpha0 |"); w("|---|---|---|---|---|")
    for f, row in t.iterrows():
        w(f"| {f} | {int(row.N_all):,} | {int(row.M_filtered):,} | {row.alpha:.3f} | {row.alpha0:.2f} |")
    w(f"\nN range [{t.N_all.min():,}, {t.N_all.max():,}]; M range [{t.M_filtered.min():,}, {t.M_filtered.max():,}] "
      f"(old: 27,000–565,000 and 12,000–321,000, with Alice); alpha range [{t.alpha.min():.2f}, {t.alpha.max():.2f}] (old [0.61, 0.85])\n")

    # ───────────────────────── 3. corpus burstiness ─────────────────────────
    w("## 3. Corpus-level burstiness (sec. Component-resolved ... corpus-wide, Robustness, Distribution)\n")
    q95 = b[b.q == 0.95].copy()
    per_k = q95.groupby("k")[["B_orig", "B_surr_mean", "B_fgn"]].mean()
    w(f"- <B_k^orig>_texts over k: range [{per_k.B_orig.min():.2f}, {per_k.B_orig.max():.2f}], mean {per_k.B_orig.mean():.2f} (old [1.12,1.37], 1.22)")
    w(f"- <B_k^surr>_texts: [{per_k.B_surr_mean.min():.3f}, {per_k.B_surr_mean.max():.3f}] (old [0.972,0.978]); "
      f"<B_k^FGN>_texts: [{per_k.B_fgn.min():.3f}, {per_k.B_fgn.max():.3f}] (old [0.970,0.992])")
    n = len(q95)
    w(f"- pairs (text,k) at q=0.95: {n}; B_orig > B_surr in {100*(q95.B_orig > q95.B_surr_mean).mean():.1f}% (old 100%); "
      f"B_orig > B_FGN in {100*(q95.B_orig > q95.B_fgn).mean():.1f}% (old 99.4%); "
      f"|B_FGN/B_surr - 1| < 0.05 in {100*((q95.B_fgn/q95.B_surr_mean - 1).abs() < 0.05).mean():.1f}% (old 95.9%)")
    for num, den, lab, old in [("B_orig", "B_surr_mean", "orig/surr", "1.248±0.011, texts [1.14,1.30] sd 0.044"),
                               ("B_orig", "B_fgn", "orig/FGN", "1.244±0.010"),
                               ("B_fgn", "B_surr_mean", "FGN/surr", "1.0035±0.0012, range [0.94,1.11], t=2.88 p=0.011")]:
        rr = q95[num] / q95[den]
        pt = rr.groupby(q95.file).mean()
        tt = ttest_1samp(rr, 1.0)
        w(f"- ratio {lab}: mean over pairs {rr.mean():.4f} ± s.e. {rr.std(ddof=1)/np.sqrt(n):.4f} (sd {rr.std(ddof=1):.3f}), "
          f"range [{rr.min():.2f}, {rr.max():.2f}]; per-text means: mean {pt.mean():.3f}, sd {pt.std(ddof=1):.3f}, range [{pt.min():.2f}, {pt.max():.2f}]; "
          f"t-test vs 1: t={tt.statistic:.2f}, p={tt.pvalue:.3g}   (old {old})")
    w("\nPer-text mean ratios at q=0.95 (definition of eq. ratio_corpus):\n")
    w("| file | orig/surr | orig/FGN | FGN/surr |"); w("|---|---|---|---|")
    pt = q95.assign(rs=q95.B_orig/q95.B_surr_mean, rf=q95.B_orig/q95.B_fgn, rfs=q95.B_fgn/q95.B_surr_mean).groupby("file")[["rs", "rf", "rfs"]].mean()
    for f, row in pt.sort_values("rs").iterrows():
        w(f"| {f} | {row.rs:.3f} | {row.rf:.3f} | {row.rfs:.4f} |")
    for c, lab in [("rs", "orig/surr"), ("rf", "orig/FGN"), ("rfs", "FGN/surr")]:
        tt = ttest_1samp(pt[c], 1.0)
        w(f"- {lab}: mean over 16 texts {pt[c].mean():.4f} ± s.e. {pt[c].std(ddof=1)/4:.4f} (sd {pt[c].std(ddof=1):.4f}), "
          f"range [{pt[c].min():.3f}, {pt[c].max():.3f}], t={tt.statistic:.2f}, p={tt.pvalue:.2g}")
    w("\nBy q (fraction of pairs):\n")
    w("| q | orig>surr | orig>FGN | full ordering | \\|FGN/surr-1\\|<0.05 |"); w("|---|---|---|---|---|")
    for q in P.q_sweep:
        s = b[b.q == q]
        w(f"| {q} | {100*(s.B_orig > s.B_surr_mean).mean():.1f}% | {100*(s.B_orig > s.B_fgn).mean():.1f}% | "
          f"{100*((s.B_orig > s.B_fgn) & (s.B_orig > s.B_surr_mean)).mean():.1f}% | {100*((s.B_fgn/s.B_surr_mean - 1).abs() < 0.05).mean():.1f}% |")
    w("\n(old: orig>FGN >= 99.4% for q<=0.95 and 98.7% at 0.99; |FGN/surr-1|<0.05 >98% for q<=0.90, 85% at 0.99)\n")

    # ───────────────────────── 4. ACF ─────────────────────────
    w("## 4. ACF (sec. Empirical results, Corpus-level ACF results)\n")
    ge = analyses["Great Expectations"]
    lmax = 300
    r_o = acf_matrix(ge.pca.proj, lmax); r_f = acf_matrix(ge.proj_fgn, lmax); ci = ci95(ge.M)
    w(f"### Great Expectations (alpha={ge.fgn.alpha_text:.3f}, old 0.688; M={ge.M:,}; ci95={ci:.3f})")
    w(f"- rho_k(1) orig range [{r_o[:,1].min():.3f}, {r_o[:,1].max():.3f}] (old [0.042,0.179]); "
      f"FGN: all < 0.025? {bool((np.abs(r_f[:,1]) < 0.025).all())}, max |rho_FGN(1)| {np.abs(r_f[:,1]).max():.3f}, "
      f"inside band {(np.abs(r_f[:,1]) <= ci).sum()}/20 (old 19/20); rho_1^FGN(1)={r_f[0,1]:.3f} (old 0.023)")
    w("\nTable tab:acf_summary (k=1..10):\n")
    w("| k | rho(1) orig | rho(1) FGN | rho(100) orig | rho(100) FGN |"); w("|---|---|---|---|---|")
    for k in range(10):
        w(f"| {k+1} | {r_o[k,1]:.3f} | {r_f[k,1]:.3f} | {r_o[k,100]:.3f} | {r_f[k,100]:.3f} |")
    w(f"\nk=11..20: max |rho_FGN(1)| = {np.abs(r_f[10:,1]).max():.3f} (old 'all < 0.007'); bold = |rho| > ci95 = {ci:.3f}\n")

    a16 = a[a.file != "aliceinwonderland.txt"]
    w("### Corpus (16 texts, 320 (text,k) pairs)")
    for lag in (1, 10, 100):
        s = a16[a16.lag == lag]
        w(f"- lag {lag}: rho_orig {s.rho_orig.mean():.3f} ± {s.rho_orig.std(ddof=1):.3f}; "
          f"rho_FGN {s.rho_fgn.mean():.3f} ± {s.rho_fgn.std(ddof=1):.3f}; rho_surr {s.rho_surr.mean():.3f} ± {s.rho_surr.std(ddof=1):.3f}")
    w("  (old: orig 0.096±0.044 / 0.026±0.017 / 0.010±0.009; FGN(1) 0.003±0.009; surr(1) 0.000±0.004)")
    w("\n| lag | orig sig | FGN sig | surr sig |"); w("|---|---|---|---|")
    for lag in sorted(a16.lag.unique()):
        s = a16[a16.lag == lag]
        w(f"| {lag} | {100*s.orig_sig.mean():.1f}% | {100*s.fgn_sig.mean():.1f}% | {100*s.surr_sig.mean():.1f}% |")
    only = a16.assign(x=(a16.orig_sig == 1) & (a16.fgn_sig == 0)).groupby("lag").x.mean()
    w("\n'original significant and FGN not' by lag: " + ", ".join(f"{l}: {100*v:.1f}%" for l, v in only.items()) + " (old: peak 89.7% at lag 2, >56% up to 100)")
    s1 = a16[a16.lag == 1]
    tt = ttest_1samp(s1.rho_fgn, 0.0)
    w(f"\n(old lag 1: 100% / 17.2% / 4.7%; lag 2: 89.7% orig; 'above 56% up to lag ...')")
    w(f"- rho_k(1) orig range [{s1.rho_orig.min():.3f}, {s1.rho_orig.max():.3f}] (old [0.020,0.282]); "
      f"FGN range [{s1.rho_fgn.min():.3f}, {s1.rho_fgn.max():.3f}] (old [-0.015,0.058]); "
      f"t-test FGN rho(1) vs 0: t={tt.statistic:.2f}, p={tt.pvalue:.3g} (old t=5.83); orig-null gap {s1.rho_orig.mean()-s1.rho_fgn.mean():.3f} (old 0.093)")
    w(f"- fraction of FGN pairs with rho(1) > 0.007: {100*(s1.rho_fgn > 0.007).mean():.1f}%\n")

    # ───────────────────────── 5. DFA ─────────────────────────
    w("## 5. DFA of projections (sec. DFA of projected series)\n")
    d_o = np.array([projection_alpha(ge.pca.proj[:, k]) for k in range(20)])
    d_f = np.array([projection_alpha(ge.proj_fgn[:, k]) for k in range(20)])
    d_s = np.array([[projection_alpha(ge.pca.proj[p, k]) for k in range(20)] for p in ge.perms[:N_SURR_DFA]]).mean(0)
    w("### Great Expectations, table tab:dfa_proj\n")
    w("| k | orig | FGN | surr |"); w("|---|---|---|---|")
    for k in range(20):
        w(f"| {k+1} | {d_o[k]:.3f} | {d_f[k]:.3f} | {d_s[k]:.3f} |")
    w(f"\nmeans ± sd: orig {d_o.mean():.3f} ± {d_o.std(ddof=1):.3f} (old 0.637±0.032); FGN {d_f.mean():.3f} ± {d_f.std(ddof=1):.3f} (old 0.502±0.015); "
      f"surr {d_s.mean():.3f} ± {d_s.std(ddof=1):.3f} (old 0.499±0.002)")
    w(f"- orig > 0.5: {(d_o > 0.5).sum()}/20; |FGN-0.5|<0.05: {(np.abs(d_f-0.5) < 0.05).sum()}/20; "
      f"orig range [{d_o.min():.3f}, {d_o.max():.3f}] (old [0.575,0.698]); "
      f"max orig at PC{int(np.argmax(d_o))+1}={d_o.max():.3f}, min at PC{int(np.argmin(d_o))+1}={d_o.min():.3f}\n")
    w("### Corpus")
    w(f"- mean ± sd over 320 pairs: orig {d.dfa_orig.mean():.3f} ± {d.dfa_orig.std(ddof=1):.3f}; FGN {d.dfa_fgn.mean():.3f} ± {d.dfa_fgn.std(ddof=1):.3f}; "
      f"surr {d.dfa_surr_mean.mean():.3f} ± {d.dfa_surr_mean.std(ddof=1):.3f}; orig>0.5 in {100*(d.dfa_orig > 0.5).mean():.1f}%, "
      f"|FGN-0.5|<0.05 in {100*((d.dfa_fgn-0.5).abs() < 0.05).mean():.1f}%")

    Path(args.out).write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
