"""One-pass analysis of a single text: tokens -> trajectory -> PCA -> null models ->
burstiness spectra, ACF and DFA rows.  Used by scripts/run_corpus.py and scripts/run_text.py.

The reference Colab run recomputed PCA and the FGN surrogate separately for each of the
three batches; here they are computed once, so the three result tables share the same
surrogate (same alpha0, same realisation).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .acf import ACF_LAGS_SAVE, acf_matrix, ci95, lag_max_for
from .burst import burstiness_spectrum, shuffle_permutations, shuffled_burstiness, thresholds
from .config import DEFAULT, Params
from .dfa import projection_alpha
from .embed import build_trajectory
from .pca import PCAResult, fit_pca, project
from .surrogates import FGNSurrogate, fgn_surrogate
from .text import TokenisedText, load_text

N_SURR_DFA = 10   # shuffled realisations for the DFA band (as in the reference run)


@dataclass
class TextAnalysis:
    text: TokenisedText
    M: int
    pca: PCAResult
    perms: list[np.ndarray]      # word-shuffled permutations, seeds 0..n_surr-1
    fgn: FGNSurrogate
    proj_fgn: np.ndarray         # FGN trajectory projected on the original axes
    M_fgn: int

    @property
    def name(self) -> str:
        return self.text.name


def analyse_text(path: str | Path, wv, params: Params = DEFAULT) -> TextAnalysis:
    tt = load_text(path, params)
    vecs, _ = build_trajectory(tt.tokens_filtered, wv)
    pca = fit_pca(vecs, params.k_burst)
    perms = shuffle_permutations(len(vecs), params.n_surr)
    fgn = fgn_surrogate(tt.tokens_all, seed=params.fgn_seed)
    tok_fgn = [t for t in fgn.tokens if t not in tt.stopset and tt.freq[t] >= params.min_freq]
    vecs_fgn, _ = build_trajectory(tok_fgn, wv)
    proj_fgn = project(vecs_fgn, pca)
    return TextAnalysis(tt, len(vecs), pca, perms, fgn, proj_fgn, len(vecs_fgn))


def analyse_blocks(paths, wv, params: Params = DEFAULT, center_blocks: bool = True,
                   name: str = "concat") -> TextAnalysis:
    """Analyse a concatenation of several texts (e.g. encyclopedia entries) as one series.

    With center_blocks=True each block's trajectory is centred on its own mean before
    concatenation, so the between-block covariance vanishes and the PCA captures
    within-block semantic directions only.  The word-shuffled null permutes tokens
    within each block; the FGN surrogate is built on the concatenated token stream
    (its DFA exponent measured on the concatenation) and re-split into the original
    block lengths for centring.  Frequency filtering (top-R, min_freq) uses the pooled
    frequencies of the concatenation.
    """
    from collections import Counter
    from .text import load_raw, tokenise

    toks_all_blocks = [tokenise(load_raw(p)) for p in paths]
    tokens_all = [t for b in toks_all_blocks for t in b]
    freq = Counter(tokens_all)
    stopset = set(w for w, _ in freq.most_common(params.max_freq_rank))
    keep = lambda t: t not in stopset and freq[t] >= params.min_freq
    tokens_filtered = [t for t in tokens_all if keep(t)]
    tt = TokenisedText(name, tokens_all, tokens_filtered, freq, stopset)

    def centred_vecs(token_blocks):
        blocks, lengths = [], []
        for b in token_blocks:
            v, _ = build_trajectory([t for t in b if keep(t)], wv)
            if len(v) == 0:
                continue
            if center_blocks:
                v = v - v.mean(axis=0)
            blocks.append(v); lengths.append(len(v))
        return np.concatenate(blocks), lengths

    vecs, lengths = centred_vecs(toks_all_blocks)
    pca = fit_pca(vecs, params.k_burst)
    bounds = np.cumsum([0] + lengths)
    perms = []
    for s in range(params.n_surr):
        rng = np.random.default_rng(seed=s)
        perms.append(np.concatenate([bounds[i] + rng.permutation(lengths[i]) for i in range(len(lengths))]))
    fgn = fgn_surrogate(tokens_all, seed=params.fgn_seed)
    raw_bounds = np.cumsum([0] + [len(b) for b in toks_all_blocks])
    fgn_blocks = [fgn.tokens[raw_bounds[i]:raw_bounds[i + 1]] for i in range(len(toks_all_blocks))]
    vecs_fgn, _ = centred_vecs(fgn_blocks)
    proj_fgn = project(vecs_fgn, pca)
    a = TextAnalysis(tt, len(vecs), pca, perms, fgn, proj_fgn, len(vecs_fgn))
    a.block_lengths = lengths
    return a


def _r(x, nd=4):
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), nd)


def burstiness_rows(a: TextAnalysis, params: Params = DEFAULT) -> list[dict]:
    rows = []
    for q in params.q_sweep:
        th = thresholds(a.pca.proj, q)
        b_o = burstiness_spectrum(a.pca.proj, th)
        b_sm, b_ss = shuffled_burstiness(a.pca.proj, a.perms, th)
        b_f = burstiness_spectrum(a.proj_fgn, th)
        for k in range(params.k_burst):
            rows.append({
                "file": a.name, "N_all": a.text.N_all, "N_filt": a.text.N_filt, "M_filtered": a.M,
                "alpha": _r(a.fgn.alpha_text), "alpha0": _r(a.fgn.alpha0),
                "q": q, "k": k + 1,
                "B_orig": _r(b_o[k]), "B_surr_mean": _r(b_sm[k]), "B_surr_std": _r(b_ss[k]),
                "B_fgn": _r(b_f[k]),
                "orig_surr": _r(b_o[k] / b_sm[k]) if b_sm[k] > 0 else "",
                "orig_fgn": _r(b_o[k] / b_f[k]) if b_f[k] > 0 else "",
            })
    return rows


def acf_rows(a: TextAnalysis, params: Params = DEFAULT) -> list[dict]:
    lmax = lag_max_for(a.M)
    lmax_f = min(lmax, len(a.proj_fgn) // 5)
    rho_o = acf_matrix(a.pca.proj, lmax)
    rho_s = acf_matrix(a.pca.proj[a.perms[0]], lmax)       # single shuffled realisation
    rho_f = acf_matrix(a.proj_fgn, lmax_f)
    ci = ci95(a.M)
    rows = []
    for k in range(params.k_burst):
        for lag in ACF_LAGS_SAVE:
            if lag > lmax:
                continue
            lf = min(lag, lmax_f)
            rows.append({
                "file": a.name, "M_filtered": a.M, "alpha": _r(a.fgn.alpha_text),
                "k": k + 1, "lag": lag,
                "rho_orig": _r(rho_o[k, lag], 5), "rho_fgn": _r(rho_f[k, lf], 5),
                "rho_surr": _r(rho_s[k, lag], 5), "ci_95": _r(ci, 5),
                "orig_sig": int(abs(rho_o[k, lag]) > ci),
                "fgn_sig": int(abs(rho_f[k, lf]) > ci),
                "surr_sig": int(abs(rho_s[k, lag]) > ci),
            })
    return rows


def dfa_rows(a: TextAnalysis, params: Params = DEFAULT) -> list[dict]:
    rows = []
    for k in range(params.k_burst):
        a_o = projection_alpha(a.pca.proj[:, k])
        a_f = projection_alpha(a.proj_fgn[:, k])
        a_s = np.array([projection_alpha(a.pca.proj[p, k]) for p in a.perms[:N_SURR_DFA]])
        a_s = a_s[np.isfinite(a_s)]
        rows.append({
            "file": a.name, "k": k + 1, "M_filtered": a.M,
            "alpha_text": _r(a.fgn.alpha_text), "alpha0_text": _r(a.fgn.alpha0),
            "dfa_orig": _r(a_o), "dfa_fgn": _r(a_f),
            "dfa_surr_mean": _r(a_s.mean()) if len(a_s) else "",
            "dfa_surr_std": _r(a_s.std()) if len(a_s) else "",
        })
    return rows
