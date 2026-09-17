"""Detrended Fluctuation Analysis (order-1) and the Zipf-rank coding of a token sequence.

This is the Paper-1 measurement of long-range correlations in a text: code each token by
its frequency rank (1 = most frequent), integrate the rank series, and fit the scaling of
the detrended fluctuation F(L) ~ L^alpha over log-spaced window sizes L.
Defaults (100 .. 10000, 10 scales) are those used for the reference results.

`projection_alpha()` applies the same DFA to a PCA projection series with the settings of
the reference run (20 scales from 10 to N/4; corpus_dfa.csv).
"""
from __future__ import annotations

from collections import Counter

import numpy as np
from scipy.stats import linregress

DFA_L_MIN, DFA_L_MAX, DFA_N_SCALES = 100, 10000, 10


def zipf_table(tokens: list[str]) -> list[tuple[str, int]]:
    """(word, count) sorted by decreasing count; ties keep first-occurrence order (stable sort)."""
    return sorted(Counter(tokens).items(), key=lambda x: x[1], reverse=True)


def zipf_ranks(tokens: list[str]) -> np.ndarray:
    """Token sequence -> sequence of frequency ranks (1-based), int32."""
    rank = {w: r for r, (w, _) in enumerate(zipf_table(tokens), start=1)}
    return np.fromiter((rank[t] for t in tokens), dtype=np.int32, count=len(tokens))


def dfa_scales(l_min: int = DFA_L_MIN, l_max: int = DFA_L_MAX, n: int = DFA_N_SCALES) -> np.ndarray:
    """n log-spaced window sizes between l_min and l_max (rounded, duplicates removed)."""
    return np.unique(np.round(np.logspace(np.log10(l_min), np.log10(l_max), n))).astype(int)


def dfa_fluctuation(profile: np.ndarray, L: int) -> float:
    """RMS fluctuation of the integrated series around a linear fit, in non-overlapping windows of size L."""
    n_seg = len(profile) // L
    seg = profile[: n_seg * L].reshape(n_seg, L)
    t = np.arange(L, dtype=np.float64)
    t_c = t - t.mean()
    seg_c = seg - seg.mean(axis=1, keepdims=True)
    slope = seg_c @ t_c / (t_c @ t_c)
    resid = seg_c - slope[:, None] * t_c
    return float(np.sqrt(np.mean(resid ** 2)))


def dfa(series: np.ndarray, l_min: int = DFA_L_MIN, l_max: int = DFA_L_MAX,
        n: int = DFA_N_SCALES) -> tuple[np.ndarray, np.ndarray]:
    """Return (scales, F) for the order-1 DFA of `series`.

    Scales are restricted to those with at least two non-overlapping windows and a
    strictly positive fluctuation; short series therefore return fewer than n scales
    instead of NaNs.
    """
    x = np.asarray(series, dtype=np.float64)
    profile = np.cumsum(x - x.mean())
    N = len(x)
    Ls = np.array([L for L in dfa_scales(l_min, min(l_max, N // 2), n) if N // L >= 2])
    if len(Ls) == 0:
        return Ls, np.array([])
    F = np.array([dfa_fluctuation(profile, L) for L in Ls])
    ok = F > 0
    return Ls[ok], F[ok]


def dfa_exponent(series: np.ndarray, l_min: int = DFA_L_MIN, l_max: int = DFA_L_MAX,
                 n: int = DFA_N_SCALES) -> float:
    """Slope of log F vs log L."""
    Ls, F = dfa(series, l_min, l_max, n)
    if len(Ls) < 3:
        return np.nan
    return float(linregress(np.log(Ls), np.log(F)).slope)


PROJ_L_MIN, PROJ_N_SCALES = 10, 20


def projection_alpha(x: np.ndarray, l_min: int = PROJ_L_MIN, n: int = PROJ_N_SCALES) -> float:
    """DFA exponent of a PCA projection series: n scales between l_min and len(x)//4.
    Returns NaN if the series is too short (fewer than 3 usable scales)."""
    N = len(x)
    l_max = N // 4
    if l_min >= l_max:
        return np.nan
    Ls, F = dfa(x, l_min, l_max, n)
    ok = np.isfinite(F) & (N // Ls >= 2)
    if ok.sum() < 3:
        return np.nan
    return float(linregress(np.log(Ls[ok]), np.log(F[ok])).slope)


def rank_l_max(n_tokens: int, l_max: int = DFA_L_MAX) -> int:
    """Largest DFA window for a rank series of n_tokens: at most n/4, so that the
    largest scale still has four windows.  Returns DFA_L_MAX for n >= 40,000, i.e. for
    every text of the literary corpus."""
    return min(l_max, max(DFA_L_MIN * 2, n_tokens // 4))


def text_alpha(tokens: list[str]) -> float:
    """DFA exponent of the Zipf-rank series of a token sequence.
    The largest scale is capped at N/4 (irrelevant for N >= 40,000, i.e. for the whole
    literary corpus; it matters for short texts such as encyclopedia entries)."""
    return dfa_exponent(zipf_ranks(tokens), DFA_L_MIN, rank_l_max(len(tokens)), DFA_N_SCALES)
