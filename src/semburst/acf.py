"""Autocorrelation of the PCA projection series.

rho(l) = sum_t x_t x_{t+l} / sum_t x_t^2 on the mean-centred series (biased estimator, as in
the notebook), computed via FFT.  The i.i.d. 95% band is +-1.96/sqrt(M).
Reference: corpus_acf.csv (rho_orig, rho_surr; rho_fgn there is unreliable, see notes).
"""
from __future__ import annotations

import numpy as np

ACF_LAG_MAX = 300
ACF_LAGS_SAVE = (1, 2, 5, 10, 20, 50, 100, 200, 300)


def acf(x: np.ndarray, max_lag: int) -> np.ndarray:
    """rho(0..max_lag) of a 1-d series."""
    x = np.asarray(x, dtype=np.float64)
    x = x - x.mean()
    var = x @ x
    if var == 0:
        return np.zeros(max_lag + 1)
    n = len(x)
    nfft = 1 << int(np.ceil(np.log2(2 * n - 1)))
    fx = np.fft.rfft(x, nfft)
    r = np.fft.irfft(fx * np.conj(fx), nfft)[: max_lag + 1]
    return r / var


def acf_matrix(proj: np.ndarray, max_lag: int) -> np.ndarray:
    """rho(0..max_lag) for every column of proj -> (K, max_lag+1)."""
    return np.array([acf(proj[:, k], max_lag) for k in range(proj.shape[1])])


def ci95(M: int) -> float:
    return 1.96 / np.sqrt(M)


def lag_max_for(M: int, cap: int = ACF_LAG_MAX) -> int:
    """At most 20% of the series length, as in the reference run."""
    return min(cap, M // 5)
