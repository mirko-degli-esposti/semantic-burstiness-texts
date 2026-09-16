"""All pipeline parameters in one place. Values are those used for the paper results."""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Params:
    # --- text preprocessing (text.py) ---
    max_freq_rank: int = 100   # remove the R most frequent word types (function words)
    min_freq: int = 5          # remove word types with fewer than this many occurrences

    # --- embeddings / PCA ---
    vector_dim: int = 300
    k_burst: int = 20          # number of principal components analysed
    pca_seed: int = 42

    # --- burstiness ---
    quantile: float = 0.95     # event = projection above the q-quantile
    q_sweep: tuple = (0.60, 0.70, 0.80, 0.90, 0.95, 0.99)

    # --- null models ---
    n_surr: int = 20           # word-shuffled surrogates (seeds 0 .. n_surr-1)
    fgn_seed: int = 42

    # --- ACF / DFA ---
    acf_lags: tuple = field(default_factory=lambda: tuple(range(1, 301)))


DEFAULT = Params()
