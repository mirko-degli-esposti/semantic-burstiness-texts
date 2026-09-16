"""Detrended Fluctuation Analysis (order-1) and the Zipf-rank coding of a token sequence.

This is the Paper-1 measurement of long-range correlations in a text: code each token by
its frequency rank (1 = most frequent), integrate the rank series, and fit the scaling of
the detrended fluctuation F(L) ~ L^alpha over log-spaced window sizes L.
Defaults (100 .. 10000, 10 scales) are those used for the reference results.

`dfa()` is also used, unchanged, on the PCA projection series (corpus_dfa.csv).
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
    dl = (np.log2(l_max) - np.log2(l_min)) / (n - 1)
    return np.unique(np.round(l_min * 2 ** (dl * np.arange(n)))).astype(int)


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
    """Return (scales, F) for the order-1 DFA of `series`."""
    x = np.asarray(series, dtype=np.float64)
    profile = np.cumsum(x - x.mean())
    Ls = dfa_scales(l_min, l_max, n)
    F = np.array([dfa_fluctuation(profile, L) for L in Ls])
    return Ls, F


def dfa_exponent(series: np.ndarray, l_min: int = DFA_L_MIN, l_max: int = DFA_L_MAX,
                 n: int = DFA_N_SCALES) -> float:
    """Slope of log F vs log L."""
    Ls, F = dfa(series, l_min, l_max, n)
    return float(linregress(np.log(Ls), np.log(F)).slope)


def text_alpha(tokens: list[str]) -> float:
    """DFA exponent of the Zipf-rank series of a token sequence."""
    return dfa_exponent(zipf_ranks(tokens))
