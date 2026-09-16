"""Threshold events, inter-event times, burstiness, and the word-shuffled null model.

Definitions (as in the notebook):
  events(k)     : positions where proj[:, k] > quantile_q(proj[:, k])     (strict >)
  tau           : differences between consecutive event positions
  B             : std(tau) / mean(tau), population std (ddof=0); NaN if < 2 events
Thresholds for the null models are always those of the ORIGINAL text.

Word-shuffled surrogate s (s = 0 .. n_surr-1): permutation of the tokens drawn with
numpy default_rng(seed=s).  Because the PCA axes are permutation-invariant, the
surrogate projections are proj[perm] exactly; no re-fit is needed.
"""
from __future__ import annotations

import numpy as np


def inter_event_times(events: np.ndarray) -> np.ndarray:
    idx = np.flatnonzero(events)
    return np.diff(idx) if len(idx) > 1 else np.array([], dtype=np.int64)


def burstiness(taus: np.ndarray) -> float:
    return float(taus.std() / taus.mean()) if len(taus) > 1 else np.nan


def thresholds(proj: np.ndarray, q: float) -> np.ndarray:
    """Per-component q-quantile of the projections, shape (K,)."""
    return np.quantile(proj, q, axis=0)


def burstiness_spectrum(proj: np.ndarray, thresh: np.ndarray) -> np.ndarray:
    """B_k for each component, using the given per-component thresholds."""
    return np.array([burstiness(inter_event_times(proj[:, k] > thresh[k]))
                     for k in range(proj.shape[1])])


def shuffle_permutations(M: int, n_surr: int) -> list[np.ndarray]:
    return [np.random.default_rng(seed=s).permutation(M) for s in range(n_surr)]


def shuffled_burstiness(proj: np.ndarray, perms: list[np.ndarray], thresh: np.ndarray):
    """Mean and std (ddof=0, NaNs dropped) of B_k over the shuffled surrogates."""
    B = np.array([burstiness_spectrum(proj[p], thresh) for p in perms])  # (n_surr, K)
    mean = np.array([np.mean(col[~np.isnan(col)]) if np.any(~np.isnan(col)) else np.nan for col in B.T])
    std = np.array([np.std(col[~np.isnan(col)]) if np.any(~np.isnan(col)) else np.nan for col in B.T])
    return mean, std
