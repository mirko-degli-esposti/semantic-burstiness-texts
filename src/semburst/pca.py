"""PCA of the embedding trajectory.

The notebook used sklearn.decomposition.PCA(n_components=K, random_state=42) on the
mean-centred trajectory.  For M >= 3000 samples and 300 features recent sklearn selects
the exact 'covariance_eigh' solver, so the result is deterministic.  Here the same
computation is written out explicitly (covariance matrix + symmetric eigendecomposition)
so the code does not depend on sklearn's solver-selection policy.

Sign convention (matters: events are defined by projection > threshold): as in sklearn,
each component is oriented so that its entry of largest absolute value is positive.

Note: the covariance matrix of the trajectory is invariant under any permutation of the
tokens, hence the word-shuffled surrogate shares the PCA axes of the original exactly.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PCAResult:
    mean: np.ndarray          # (D,)  mean vector
    components: np.ndarray    # (K, D) principal directions, rows unit-norm
    proj: np.ndarray          # (M, K) projections of the centred trajectory
    eigenvalues: np.ndarray   # (D,) all eigenvalues of the covariance, descending
    explained_variance_ratio: np.ndarray  # (K,)

    @property
    def K(self) -> int:
        return self.components.shape[0]


def fit_pca(vecs: np.ndarray, k: int) -> PCAResult:
    """Mean-centre `vecs` (M, D) and return the top-k principal components and projections."""
    vecs = np.asarray(vecs, dtype=np.float32)
    mean = vecs.mean(axis=0)
    X = vecs - mean
    X64 = X.astype(np.float64)
    cov = (X64.T @ X64) / (len(X64) - 1)
    w, V = np.linalg.eigh(cov)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    comps = V[:, :k].T.copy()
    # sklearn sign convention: largest-|entry| of each component positive
    imax = np.argmax(np.abs(comps), axis=1)
    signs = np.sign(comps[np.arange(k), imax])
    signs[signs == 0] = 1.0
    comps *= signs[:, None]
    comps = comps.astype(np.float32)
    proj = X @ comps.T
    return PCAResult(mean, comps, proj, w, w[:k] / w.sum())


def project(vecs: np.ndarray, pca: PCAResult) -> np.ndarray:
    """Project new vectors (e.g. an FGN surrogate trajectory) onto the fitted axes."""
    X = np.asarray(vecs, dtype=np.float32) - pca.mean
    return X @ pca.components.T
