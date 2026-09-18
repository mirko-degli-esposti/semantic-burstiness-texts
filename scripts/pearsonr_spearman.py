import numpy as np
from scipy.stats import rankdata

def _corr_vs(x, Y):
    """Pearson r between vector x (K,) and each row of Y (n,K)."""
    xc = x - x.mean()
    Yc = Y - Y.mean(axis=1, keepdims=True)
    return (Yc @ xc) / np.sqrt((xc**2).sum() * (Yc**2).sum(axis=1))

def eigen_burst_association(lam, B, n_perm=100_000, seed=0):
    """Pearson r and Spearman rho between the eigenvalue and burstiness
    spectra, with permutation P-values over component pairings."""
    lam = np.asarray(lam, float); B = np.asarray(B, float)
    K = lam.size
    rng = np.random.default_rng(seed)
    perms = np.argsort(rng.random((n_perm, K)), axis=1)

    r_obs    = _corr_vs(lam, B[None, :])[0]
    r_null   = _corr_vs(lam, B[perms])

    lam_r, B_r = rankdata(lam), rankdata(B)
    rho_obs  = _corr_vs(lam_r, B_r[None, :])[0]
    rho_null = _corr_vs(lam_r, B_r[perms])

    pv = lambda null, obs: (np.sum(np.abs(null) >= abs(obs)) + 1) / (n_perm + 1)
    return {"pearson_r":     r_obs,   "P_perm_pearson":  pv(r_null,   r_obs),
            "spearman_rho":  rho_obs, "P_perm_spearman": pv(rho_null, rho_obs)}