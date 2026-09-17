"""Long-range-correlated, Zipf-preserving surrogate ("FGN surrogate").

Construction (Degli Esposti & Montemurro, Physica A 2025):
  1. one realisation of Gaussian white noise, length N (seed fixed);
  2. power-law spectral filter |f|^(-beta/2), beta = 2*alpha0 - 1, inverse FFT -> correlated noise;
  3. the word types of the text are laid out by increasing frequency rank (rarest first,
     most frequent last), each repeated as many times as it occurs; position i of the
     surrogate receives the word whose slot equals the rank of the noise value at i.
     The frequency of every word type is therefore preserved exactly.
  4. alpha0 is found by bisection so that the DFA exponent of the surrogate's rank series
     matches that of the original text within `tol`.

The white noise is drawn once per seed and reused for every alpha0 in the bisection, so
alpha_surr(alpha0) is a deterministic, smooth function and the whole procedure is
reproducible from (tokens, seed).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .dfa import DFA_L_MIN, DFA_N_SCALES, dfa_exponent, rank_l_max, text_alpha, zipf_ranks, zipf_table

BISECT_LOW, BISECT_HIGH, BISECT_TOL, BISECT_MAX_ITER = 0.55, 0.92, 1e-2, 20


def _white_noise_fft(n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.fft.fft(rng.standard_normal(n))


def _powerlaw_noise(fx: np.ndarray, alpha0: float) -> np.ndarray:
    """Filter the FFT of white noise into 1/f^beta noise, beta = 2*alpha0 - 1."""
    n = len(fx)
    beta = 2.0 * alpha0 - 1.0
    freq = np.abs(np.fft.fftfreq(n)) ** (beta / 2.0)
    out = fx.copy()
    out[1:] = out[1:] / freq[1:]          # DC component untouched
    return np.real(np.fft.ifft(out))


def _rank_layout(tokens: list[str]) -> tuple[np.ndarray, list[str]]:
    """Return (raw_ranks, rank_to_word). raw_ranks lists rank V (rarest) ... rank 1, each
    repeated by its count; rank_to_word[r-1] is the word of rank r."""
    table = zipf_table(tokens)
    counts = np.array([c for _, c in table])
    ranks = np.arange(len(table), 0, -1)
    raw = np.repeat(ranks, counts[::-1])
    return raw, [w for w, _ in table]


def surrogate_ranks(alpha0: float, raw_ranks: np.ndarray, fx: np.ndarray) -> np.ndarray:
    """Rank sequence of the surrogate for a given alpha0 and white-noise FFT."""
    y = _powerlaw_noise(fx, alpha0)
    order = np.argsort(y)              # positions sorted by noise value
    slot = np.argsort(order)           # rank of the noise value at each position
    return raw_ranks[slot]


@dataclass
class FGNSurrogate:
    tokens: list[str]        # surrogate token sequence (same multiset as the input)
    alpha_text: float        # DFA exponent of the original rank series
    alpha0: float            # generator exponent found by bisection
    alpha_surr: float        # DFA exponent measured on the surrogate rank series
    seed: int                # seed actually used (may differ from the requested one, see log)
    log: list = field(default_factory=list)


def fgn_surrogate(tokens: list[str], seed: int = 42,
                  low: float = BISECT_LOW, high: float = BISECT_HIGH,
                  tol: float = BISECT_TOL, max_iter: int = BISECT_MAX_ITER,
                  max_restarts: int = 5) -> FGNSurrogate:
    """Build the FGN surrogate of a token sequence, matching its DFA exponent."""
    n = len(tokens)
    alpha = text_alpha(tokens)
    l_max = rank_l_max(n)          # same scale range for text and surrogate
    raw, words = _rank_layout(tokens)
    measure = lambda r: dfa_exponent(r, DFA_L_MIN, l_max, DFA_N_SCALES)
    log = []
    for restart in range(max_restarts):
        s = seed + restart
        fx = _white_noise_fft(n, s)
        a1, a2 = low, high
        for it in range(max_iter):
            am = 0.5 * (a1 + a2)
            a_m = measure(surrogate_ranks(am, raw, fx))
            log.append((s, it, am, a_m))
            if not np.isfinite(a_m):
                raise RuntimeError(f"DFA of the surrogate is undefined (n={n} tokens too short)")
            if abs(a_m - alpha) < tol:
                ranks = surrogate_ranks(am, raw, fx)
                return FGNSurrogate([words[r - 1] for r in ranks], alpha, am, a_m, s, log)
            if a_m > alpha:
                a2 = am
            else:
                a1 = am
        log.append((s, "restart", None, None))
    raise RuntimeError(f"FGN bisection did not converge (alpha={alpha:.4f}); log={log[-5:]}")
