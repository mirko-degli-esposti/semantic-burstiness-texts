"""Per-text figures used in the paper (main text and SI).  All functions take a
TextAnalysis (see pipeline.py) and return a matplotlib Figure; run_text.py saves them.
"""
from __future__ import annotations

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .acf import acf_matrix, ci95
from .burst import burstiness, burstiness_spectrum, inter_event_times, shuffled_burstiness, thresholds
from .config import DEFAULT, Params
from .dfa import dfa, projection_alpha
from .pca import fit_pca
from .pipeline import N_SURR_DFA, TextAnalysis

C_ORIG, C_SURR, C_FGN = "steelblue", "tomato", "seagreen"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})


def _pretty(name: str) -> str:
    return name.replace(".txt", "").replace("_cut_clean", "").replace("eng_", "").replace("_", " ").title()


# ── 02 eigenvalue spectra ─────────────────────────────────────────────────────
def fig_spectra(a: TextAnalysis, wv, k_show: int = 50):
    from .embed import build_trajectory
    ev_orig = a.pca.eigenvalues / a.pca.eigenvalues.sum()
    perm = a.perms[0]
    vecs = build_trajectory(a.text.tokens_filtered, wv)[0]
    ev_surr = fit_pca(vecs[perm], k_show).eigenvalues / ev_orig.sum()
    ev_surr = ev_surr / ev_surr.sum()
    tok_fgn = [t for t in a.fgn.tokens if t not in a.text.stopset and a.text.freq[t] >= DEFAULT.min_freq]
    ev_fgn = fit_pca(build_trajectory(tok_fgn, wv)[0], k_show).eigenvalues
    ev_fgn = ev_fgn / ev_fgn.sum()
    ks = np.arange(1, k_show + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    for ev, lab, c, m in [(ev_orig, "Original", C_ORIG, "o"), (ev_surr, "Word-shuffled", C_SURR, "s"),
                          (ev_fgn, "FGN surrogate", C_FGN, "^")]:
        ax1.semilogy(ks, ev[:k_show], m, color=c, ms=4, lw=1, alpha=0.85, label=lab)
        ax2.plot(ks, np.cumsum(ev[:k_show]), m + "-", color=c, ms=3, lw=1.2, label=lab)
    ax1.set_xlabel("Component $k$"); ax1.set_ylabel("Explained variance ratio"); ax1.legend(); ax1.grid(alpha=0.25)
    ax2.set_xlabel("Component $k$"); ax2.set_ylabel("Cumulative explained variance"); ax2.legend(); ax2.grid(alpha=0.25)
    fig.suptitle(f"Eigenvalue spectra — {_pretty(a.name)}  ($M={a.M:,}$)")
    fig.tight_layout()
    return fig


# ── 03 inter-event-time distributions ────────────────────────────────────────
def _iet_panel(ax, taus, label, color):
    if len(taus) < 10:
        ax.set_title(f"{label} — too few events"); return np.nan
    p = np.clip(1.0 / taus.mean(), 1e-6, 1 - 1e-6)
    B = burstiness(taus)
    bins = np.logspace(0, np.log10(taus.max()), 40)
    hist, _ = np.histogram(taus, bins=bins, density=True)
    mids = np.sqrt(bins[:-1] * bins[1:]); mask = hist > 0
    ax.loglog(mids[mask], hist[mask], "o", ms=5, color=color, label=label)
    tv = np.arange(1, min(int(taus.max()) + 1, 2000))
    ax.loglog(tv, p * (1 - p) ** (tv - 1), "-", color="black", lw=2,
              label=f"Geometric ($p={p:.3f}$, $CV_{{\\rm geom}}={np.sqrt(1-p):.3f}$)")
    ax.set_xlabel(r"Inter-event time $\tau$"); ax.set_ylabel(r"$p(\tau)$")
    ax.set_title(f"{label}   $B={B:.2f}$"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    return B


def fig_iet(a: TextAnalysis, params: Params = DEFAULT, n_pc: int = 3):
    q = params.quantile
    th = thresholds(a.pca.proj, q)
    series = [(a.pca.proj, "Original", C_ORIG), (a.pca.proj[a.perms[0]], "Word-shuffled", C_SURR),
              (a.proj_fgn, "FGN surrogate", C_FGN)]
    fig, axes = plt.subplots(n_pc, 3, figsize=(20, 4.3 * n_pc))
    for row in range(n_pc):
        for col, (proj, lab, c) in enumerate(series):
            _iet_panel(axes[row, col], inter_event_times(proj[:, row] > th[row]), f"{lab} — PC{row+1}", c)
    fig.suptitle(f"IET distributions — {_pretty(a.name)}   $q={q}$, $p={1-q:.2f}$, "
                 f"$CV_{{\\rm geom}}=\\sqrt{{q}}={np.sqrt(q):.3f}$", fontsize=12)
    fig.tight_layout()
    return fig


# ── 04 burstiness spectrum ────────────────────────────────────────────────────
def fig_burstiness(a: TextAnalysis, params: Params = DEFAULT):
    q = params.quantile
    th = thresholds(a.pca.proj, q)
    b_o = burstiness_spectrum(a.pca.proj, th)
    b_sm, b_ss = shuffled_burstiness(a.pca.proj, a.perms, th)
    b_f = burstiness_spectrum(a.proj_fgn, th)
    ks = np.arange(1, params.k_burst + 1)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(ks, b_o, "o-", color=C_ORIG, ms=7, lw=1.8, zorder=4, label="Original")
    ax.errorbar(ks, b_sm, yerr=2 * b_ss, fmt="s--", color=C_SURR, ms=5, lw=1.3, capsize=4,
                label=f"Word-shuffled mean $\\pm2\\sigma$ (n={len(a.perms)})")
    ax.fill_between(ks, b_sm - 2 * b_ss, b_sm + 2 * b_ss, color=C_SURR, alpha=0.12)
    ax.plot(ks, b_f, "^-", color=C_FGN, ms=7, lw=1.8, zorder=3, label="FGN surrogate")
    ax.axhline(np.sqrt(q), color="black", lw=2, ls="--", label=f"Geometric baseline $\\sqrt{{q}}={np.sqrt(q):.3f}$")
    ax.set_xlabel("PCA component $k$", fontsize=12); ax.set_ylabel("$B_k$", fontsize=12)
    ax.set_title(f"Burstiness spectrum — {_pretty(a.name)}   $q={q}$"); ax.set_xticks(ks)
    ax.legend(fontsize=10); ax.grid(alpha=0.25); fig.tight_layout()
    return fig


# ── 06 quantile sweep ─────────────────────────────────────────────────────────
def fig_quantile_sweep(a: TextAnalysis, params: Params = DEFAULT):
    qs = list(params.q_sweep)
    mo, ms_, mf, frac = [], [], [], []
    for q in qs:
        th = thresholds(a.pca.proj, q)
        b_o = burstiness_spectrum(a.pca.proj, th)
        b_sm, _ = shuffled_burstiness(a.pca.proj, a.perms, th)
        b_f = burstiness_spectrum(a.proj_fgn, th)
        mo.append(np.nanmean(b_o)); ms_.append(np.nanmean(b_sm)); mf.append(np.nanmean(b_f))
        frac.append(np.mean((b_o > b_f) & (b_o > b_sm)))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    ax1.plot(qs, mo, "o-", color=C_ORIG, lw=1.8, label="Original")
    ax1.plot(qs, mf, "^-", color=C_FGN, lw=1.8, label="FGN surrogate")
    ax1.plot(qs, ms_, "s--", color=C_SURR, lw=1.3, label="Word-shuffled mean")
    ax1.plot(qs, np.sqrt(qs), "k:", lw=1.5, label="Geometric baseline $\\sqrt{q}$")
    ax1.set_xlabel("Quantile threshold $q$"); ax1.set_ylabel(r"mean $B_k$ over $k=1..%d$" % params.k_burst)
    ax1.legend(); ax1.grid(alpha=0.25)
    ax2.plot(qs, frac, "o-", color="black", lw=1.8)
    ax2.set_ylim(0, 1.05); ax2.set_xlabel("Quantile threshold $q$")
    ax2.set_ylabel(r"fraction of $k$ with $B^{\rm orig}_k > B^{\rm FGN}_k$ and $B^{\rm orig}_k > B^{\rm surr}_k$")
    ax2.grid(alpha=0.25)
    fig.suptitle(f"Quantile sweep — {_pretty(a.name)}"); fig.tight_layout()
    return fig


# ── 07 semantic poles ─────────────────────────────────────────────────────────
def word_scores(a: TextAnalysis, wv, k: int) -> dict[str, float]:
    """Projection score of each word type of the filtered text on component k."""
    vocab = set(a.text.tokens_filtered) & set(wv.key_to_index)
    comp = a.pca.components[k]
    return {w: float((wv[w] - a.pca.mean) @ comp) for w in vocab}


def fig_semantic_poles(a: TextAnalysis, wv, n_pc: int = 4, n_top: int = 15):
    fig, axes = plt.subplots(1, n_pc, figsize=(4.2 * n_pc, 6))
    for k, ax in enumerate(axes):
        top = sorted(word_scores(a, wv, k).items(), key=lambda x: -x[1])[:n_top]
        words, vals = zip(*top)
        ax.barh(range(n_top)[::-1], vals, color=C_ORIG, alpha=0.85)
        ax.set_yticks(range(n_top)[::-1]); ax.set_yticklabels(words)
        ax.set_title(f"PC{k+1} (+)   {100*a.pca.explained_variance_ratio[k]:.1f}%")
        ax.set_xlabel("projection score"); ax.grid(axis="x", alpha=0.25)
    fig.suptitle(f"Positive poles — {_pretty(a.name)}  (R={DEFAULT.max_freq_rank}, top-{n_top} word types)")
    fig.tight_layout()
    return fig


# ── ACF figures ───────────────────────────────────────────────────────────────
def _acf_three(a: TextAnalysis, lag_max: int, n_surr: int):
    lag_max = min(lag_max, a.M // 5, len(a.proj_fgn) // 5)
    r_o = acf_matrix(a.pca.proj, lag_max)
    r_f = acf_matrix(a.proj_fgn, lag_max)
    r_s = np.mean([acf_matrix(a.pca.proj[p], lag_max) for p in a.perms[:n_surr]], axis=0)
    return lag_max, r_o, r_f, r_s


def fig_acf_decay(a: TextAnalysis, lag_max: int = 500, n_pc: int = 3, n_surr: int = 10):
    lag_max, r_o, r_f, r_s = _acf_three(a, lag_max, n_surr)
    lags = np.arange(1, lag_max + 1); ci = ci95(a.M)
    fig, axes = plt.subplots(1, n_pc, figsize=(5 * n_pc, 4.5), sharey=True)
    for k, ax in enumerate(axes):
        ax.semilogx(lags, r_o[k, 1:], color=C_ORIG, lw=2, label="Original")
        ax.semilogx(lags, r_f[k, 1:], color=C_FGN, lw=1.5, label="FGN surrogate")
        ax.semilogx(lags, r_s[k, 1:], color=C_SURR, lw=1.2, ls="--", label=f"Word-shuffled (mean of {n_surr})")
        ax.axhspan(-ci, ci, color="grey", alpha=0.15, label="95% CI (i.i.d.)"); ax.axhline(0, color="black", lw=0.6)
        ax.set_xlabel(r"Lag $\ell$"); ax.set_title(f"PC{k+1}"); ax.set_xlim(1, lag_max); ax.grid(alpha=0.2, which="both")
        if k == 0:
            ax.set_ylabel(r"$\rho_k(\ell)$"); ax.legend(fontsize=9)
    fig.suptitle(f"ACF of semantic projections — {_pretty(a.name)}  ($M={a.M:,}$, $\\alpha={a.fgn.alpha_text:.3f}$)")
    fig.tight_layout()
    return fig


def fig_acf_mean(a: TextAnalysis, lag_max: int = 500, n_surr: int = 10):
    lag_max, r_o, r_f, r_s = _acf_three(a, lag_max, n_surr)
    lags = np.arange(1, lag_max + 1); ci = ci95(a.M)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.semilogx(lags, r_o[:, 1:].mean(0), color=C_ORIG, lw=2, label="Original")
    ax.semilogx(lags, r_f[:, 1:].mean(0), color=C_FGN, lw=1.5, label="FGN surrogate")
    ax.semilogx(lags, r_s[:, 1:].mean(0), color=C_SURR, lw=1.2, ls="--", label=f"Word-shuffled (mean of {n_surr})")
    ax.axhspan(-ci, ci, color="grey", alpha=0.15, label="95% CI (i.i.d.)"); ax.axhline(0, color="black", lw=0.6)
    ax.set_xlabel(r"Lag $\ell$"); ax.set_ylabel(r"$\bar\rho(\ell)$  (mean over %d components)" % a.pca.K)
    ax.set_xlim(1, lag_max); ax.grid(alpha=0.2, which="both"); ax.legend(fontsize=9)
    ax.set_title(f"Mean ACF — {_pretty(a.name)}"); fig.tight_layout()
    return fig


# ── DFA figures ───────────────────────────────────────────────────────────────
def fig_dfa_spectrum(a: TextAnalysis):
    K = a.pca.K; ks = np.arange(1, K + 1)
    d_o = np.array([projection_alpha(a.pca.proj[:, k]) for k in range(K)])
    d_f = np.array([projection_alpha(a.proj_fgn[:, k]) for k in range(K)])
    d_s = np.array([[projection_alpha(a.pca.proj[p, k]) for k in range(K)] for p in a.perms[:N_SURR_DFA]])
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(ks, d_o, "o-", color=C_ORIG, ms=7, lw=1.8, label="Original")
    ax.plot(ks, d_f, "^-", color=C_FGN, ms=7, lw=1.8, label="FGN surrogate")
    ax.errorbar(ks, np.nanmean(d_s, 0), yerr=2 * np.nanstd(d_s, 0), fmt="s--", color=C_SURR, ms=5, lw=1.3,
                capsize=4, label=f"Word-shuffled mean $\\pm2\\sigma$ (n={N_SURR_DFA})")
    ax.axhline(0.5, color="black", lw=1.5, ls="--", label=r"Uncorrelated reference ($\alpha=0.5$)")
    ax.set_xlabel("PCA component $k$", fontsize=12); ax.set_ylabel(r"DFA exponent $\alpha_k$", fontsize=12)
    ax.set_title(f"DFA spectrum — {_pretty(a.name)}   "
                 f"$\\bar\\alpha^{{\\rm orig}}={np.nanmean(d_o):.2f}\\pm{np.nanstd(d_o):.2f}$, "
                 f"$\\bar\\alpha^{{\\rm FGN}}={np.nanmean(d_f):.2f}\\pm{np.nanstd(d_f):.2f}$")
    ax.set_xticks(ks); ax.legend(fontsize=10); ax.grid(alpha=0.25); fig.tight_layout()
    return fig


def fig_dfa_loglog(a: TextAnalysis, n_pc: int = 3):
    fig, axes = plt.subplots(1, n_pc, figsize=(5 * n_pc, 4.5), sharey=True)
    for k, ax in enumerate(axes):
        for proj, lab, c, m in [(a.pca.proj, "Orig", C_ORIG, "o-"), (a.proj_fgn, "FGN", C_FGN, "^-"),
                                (a.pca.proj[a.perms[0]], "Shuffled", C_SURR, "s--")]:
            x = proj[:, k]; Ls, F = dfa(x, 10, len(x) // 4, 20)
            ax.loglog(Ls, F, m, color=c, ms=5, lw=1.4, label=f"{lab}  $\\alpha={projection_alpha(x):.3f}$")
            if lab == "Orig":
                ax.loglog(Ls[[0, -1]], F[0] * (Ls[[0, -1]] / Ls[0]) ** 0.5, "k:", lw=1.2, label="slope 0.5")
        ax.set_xlabel("Box size $s$"); ax.set_title(f"PC{k+1}"); ax.legend(fontsize=8); ax.grid(alpha=0.2, which="both")
        if k == 0:
            ax.set_ylabel("$F(s)$")
    fig.suptitle(f"DFA fluctuation function — {_pretty(a.name)}"); fig.tight_layout()
    return fig


# ── Multi-text panels: one figure for the four showcase texts ─────────────────
def _burstiness_axes(ax, a: TextAnalysis, params: Params = DEFAULT, legend: bool = False):
    q = params.quantile
    th = thresholds(a.pca.proj, q)
    b_o = burstiness_spectrum(a.pca.proj, th)
    b_sm, b_ss = shuffled_burstiness(a.pca.proj, a.perms, th)
    b_f = burstiness_spectrum(a.proj_fgn, th)
    ks = np.arange(1, params.k_burst + 1)
    ax.plot(ks, b_o, "o-", color=C_ORIG, ms=5, lw=1.6, zorder=4, label="Original")
    ax.errorbar(ks, b_sm, yerr=2 * b_ss, fmt="s--", color=C_SURR, ms=4, lw=1.1, capsize=3,
                label=r"Word-shuffled mean $\pm2\sigma$ ($n=%d$)" % len(a.perms))
    ax.fill_between(ks, b_sm - 2 * b_ss, b_sm + 2 * b_ss, color=C_SURR, alpha=0.12)
    ax.plot(ks, b_f, "^-", color=C_FGN, ms=5, lw=1.6, zorder=3, label="FGN surrogate")
    ax.axhline(np.sqrt(q), color="black", lw=1.5, ls="--",
               label=r"Geometric baseline $\sqrt{q}=%.3f$" % np.sqrt(q))
    kmax = int(np.argmax(b_o)) + 1
    ax.set_title(f"{_pretty(a.name)}   ($M={a.M:,}$, max at PC{kmax}: $B={b_o.max():.2f}$)", fontsize=11)
    ax.set_xticks(ks[::2])
    ax.grid(alpha=0.25)
    if legend:
        ax.legend(fontsize=8, loc="upper right")
    return b_o


def fig_burstiness_panel(analyses, params: Params = DEFAULT, ncols: int = 2, labels: bool = True):
    """Burstiness spectra of several texts on one figure (2x2 for the four showcase texts)."""
    n = len(analyses)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(6.4 * ncols, 4.2 * nrows), sharey=True, squeeze=False)
    flat = axes.ravel()
    for i, (ax, a) in enumerate(zip(flat, analyses)):
        _burstiness_axes(ax, a, params, legend=(i == 0))
        if labels:
            ax.text(0.02, 0.95, "ABCDEFGH"[i], transform=ax.transAxes, fontsize=13,
                    fontweight="bold", va="top")
        if i // ncols == nrows - 1:
            ax.set_xlabel("PCA component $k$", fontsize=11)
        if i % ncols == 0:
            ax.set_ylabel("$B_k$", fontsize=11)
    for ax in flat[n:]:
        ax.set_visible(False)
    fig.suptitle(f"Component-resolved burstiness spectra, $q={params.quantile}$", fontsize=13)
    fig.tight_layout()
    return fig


def fig_quantile_sweep_panel(analyses, params: Params = DEFAULT, ncols: int = 2):
    """Quantile sweep for several texts: mean B_k against q, one panel per text."""
    qs = list(params.q_sweep)
    n = len(analyses)
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(6.0 * ncols, 4.0 * nrows), sharey=True, squeeze=False)
    flat = axes.ravel()
    for i, (ax, a) in enumerate(zip(flat, analyses)):
        mo, ms_, mf = [], [], []
        for q in qs:
            th = thresholds(a.pca.proj, q)
            mo.append(np.nanmean(burstiness_spectrum(a.pca.proj, th)))
            ms_.append(np.nanmean(shuffled_burstiness(a.pca.proj, a.perms, th)[0]))
            mf.append(np.nanmean(burstiness_spectrum(a.proj_fgn, th)))
        ax.plot(qs, mo, "o-", color=C_ORIG, lw=1.8, label="Original")
        ax.plot(qs, mf, "^-", color=C_FGN, lw=1.6, label="FGN surrogate")
        ax.plot(qs, ms_, "s--", color=C_SURR, lw=1.2, label="Word-shuffled mean")
        ax.plot(qs, np.sqrt(qs), "k:", lw=1.5, label=r"Geometric baseline $\sqrt{q}$")
        ax.set_title(_pretty(a.name), fontsize=11)
        ax.grid(alpha=0.25)
        ax.text(0.02, 0.95, "ABCDEFGH"[i], transform=ax.transAxes, fontsize=13, fontweight="bold", va="top")
        if i == 0:
            ax.legend(fontsize=8, loc="upper left")
        if i // ncols == nrows - 1:
            ax.set_xlabel("Quantile threshold $q$", fontsize=11)
        if i % ncols == 0:
            ax.set_ylabel(r"mean $B_k$ over $k=1..%d$" % params.k_burst, fontsize=11)
    for ax in flat[n:]:
        ax.set_visible(False)
    fig.suptitle("Mean burstiness against the threshold quantile", fontsize=13)
    fig.tight_layout()
    return fig


# ── Semantic poles as a LaTeX table (replaces the four bar-chart figures) ─────
def semantic_poles_table(analyses, wv, n_pc: int = 3, n_top: int = 10,
                         label: str = "tab:poles") -> str:
    """LaTeX source of a table with the top-n word types on PC1..PC_n_pc for each text."""
    caption = (
        "Positive semantic poles of the leading principal directions: the %d word types "
        "with the largest projection on each component, for the four representative texts. "
        "Percentages are the explained variance of the component. Function words "
        "(top $R=%d$) and types with fewer than %d occurrences are excluded."
        % (n_top, DEFAULT.max_freq_rank, DEFAULT.min_freq)
    )
    out = [r"\begin{table}[htbp]", r"\centering", r"\small",
           r"\caption{%s}" % caption,
           r"\label{%s}" % label,
           r"\begin{tabular}{llrp{0.58\textwidth}}", r"\toprule",
           r"Text & Comp. & \% var. & Top word types \\", r"\midrule"]
    for j, a in enumerate(analyses):
        if j:
            out.append(r"\midrule")
        for k in range(n_pc):
            words = [w for w, _ in sorted(word_scores(a, wv, k).items(), key=lambda x: -x[1])[:n_top]]
            evr = 100 * a.pca.explained_variance_ratio[k]
            name = _pretty(a.name) if k == 0 else ""
            out.append(r"%s & PC%d & %.1f & %s \\" % (name, k + 1, evr, ", ".join(words)))
    out += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(out)
