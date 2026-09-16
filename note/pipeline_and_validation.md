# `semburst` — pipeline, scripts, and validation against the Colab results

*Written 16 September 2026, when the Colab notebook (`word2vec_pca_trajectory_v7.ipynb`)
was replaced by the `semburst` package. This note records what the code does, which
choices were made where the notebook was inconsistent, and how the regenerated results
compare with the reference tables produced by the notebook.*

## 1. Layout

```
src/semburst/          the package (pip install -e .)
  config.py            all parameters (R=100, min_freq=5, K=20, q sweep, 20 shuffled, seeds)
  text.py              Gutenberg stripping, NLTK word_tokenize (alphabetic tokens), top-R + min_freq filter
  embed.py             GloVe 6B 300d loading (SHA-256 checked, .kv cache), trajectory construction
  pca.py               PCA written explicitly (covariance + eigh), sklearn sign convention
  burst.py             threshold events, inter-event times, burstiness B, word-shuffled null
  surrogates.py        FGN surrogate: Zipf-preserving, alpha-matched by deterministic bisection
  dfa.py               Zipf-rank coding, DFA-1 (rank series and projection series)
  acf.py               autocorrelation via FFT, i.i.d. band
  pipeline.py          analyse_text(): one pass per text -> rows of the three corpus tables
  figures.py           the per-text figures of the paper
scripts/
  check_text.py        validation: N_all, N_filt vs reference           (exact 16/16)
  check_embed.py       validation: M_filtered vs reference              (exact 16/16)
  check_burst.py       validation: B_orig, B_surr vs reference          (see §4)
  check_dfa.py         validation: alpha of the rank series, both tokenisers
  check_fgn.py         validation: FGN surrogate (alpha match, B_fgn)
  check_acf.py         validation: rho vs reference                     (rho_orig exact)
  check_dfa_proj.py    validation: DFA of projections vs reference      (dfa_orig exact)
  run_corpus.py        production: the three corpus tables (results/corpus_*.csv), ~40 s on CPU
  run_text.py          production: per-text figures (figures/<stem>/)
  compare_reference.py compares two sets of corpus tables column by column + paper-level numbers
results/
  corpus_burstiness.csv, corpus_acf.csv, corpus_dfa.csv   regenerated tables (current)
  reference/           the tables produced by the Colab notebook (frozen)
  validation_*.txt, compare_reference.txt, run_corpus.log
data/corpus/           the 16 texts;  data/vectors/ (not tracked): glove.6B.300d.txt
```

## 2. Pipeline (per text)

1. Strip Gutenberg boilerplate; lower-case; `nltk.word_tokenize` (nltk 3.9.1, pinned — 3.10
   changes a few dozen tokens per text); keep alphabetic tokens → `tokens_all` (N_all).
2. Remove the R=100 most frequent types and types with frequency < 5 → `tokens_filtered` (N_filt).
3. Map to GloVe 6B 300d; drop OOV tokens → trajectory (M×300).
4. PCA, K=20 components: covariance + symmetric eigendecomposition in float64, each
   component oriented so that its largest-|entry| is positive (sklearn convention — the
   sign matters because events are `projection > threshold`).
5. Word-shuffled null: 20 permutations `default_rng(seed=s)`, s=0..19. The covariance is
   permutation-invariant, so the surrogate projections are exactly `proj[perm]`.
6. FGN surrogate (seed 42): DFA exponent α of the Zipf-rank series of `tokens_all`
   (10 scales, 100..10 000); one white-noise realisation; power-law spectral filter with
   exponent α₀ found by bisection in [0.55, 0.92] until |α_surr − α| < 0.01; words laid
   out by rank on the sorted noise (multiset preserved exactly); then the same filter,
   trajectory, and projection onto the *original* axes and mean.
7. Burstiness spectrum for q ∈ {0.60, 0.70, 0.80, 0.90, 0.95, 0.99}: thresholds from the
   original; B = std(τ)/mean(τ) (population std). ACF (biased estimator, FFT) up to
   min(300, M/5). DFA of each projection series (20 scales, 10..M/4); shuffled band from
   the first 10 permutations.

All three tables come from the same `analyse_text()` call, hence share one PCA and one FGN
surrogate. The notebook recomputed PCA and FGN separately in each batch.

## 3. Choices that differ from the notebook (deliberate)

**One tokeniser.** In the notebook the FGN surrogate was built from a *different* token
stream: a regex `\w+` tokeniser with digits removed and no Gutenberg stripping (the
Paper-1 `text()` function). Contractions were split differently (`don't` → `don`, `t`),
creating spurious high-frequency types. This shifts the rank-series exponent α by up to
0.031 (Ulysses −0.031, Tom Sawyer −0.017, Principia −0.013; mean |Δ| 0.006 over the
corpus). The reference FGN was therefore tuned to an α that is not the α of the
analysed sequence. `semburst` uses `word_tokenize` everywhere. **Consequence: the α and
α₀ values of the corpus table change** (see §5).

**Explicit PCA.** `sklearn.PCA(random_state=42)` picks its solver by version. The explicit
covariance/eigh computation reproduces sklearn 1.9 exactly (verified) and removes the
version dependence.

**Deterministic FGN.** The white noise is drawn once per seed and reused for every α₀
in the bisection (the notebook re-seeded the legacy global RNG at every call, which is the
same thing done implicitly). The non-convergence fallback uses seed+1, seed+2, …
(the notebook drew a random seed). With real texts the bisection converges in 1–4
evaluations; the fallback never fires.

**Shuffled surrogates without re-fit.** `proj[perm]` instead of `X[perm] @ components.T`:
identical numbers, no matrix product.

## 4. Validation against the Colab reference tables

Everything that depends only on the text and on the NumPy RNG is reproduced exactly:

| quantity | agreement with reference |
|---|---|
| N_all, N_filt, M_filtered | 16/16 exact |
| α of rank series (legacy tokeniser, for the check only) | 16/16 exact at 4 dp |
| B_orig (1920 rows, 6 q × 20 k × 16 texts) | 1911/1920 exact at 4 dp; remaining 9 at q ≥ 0.95, max diff 0.006 |
| ρ_orig (2880 rows), orig_sig | 100 % exact at 5 dp |
| DFA of projections: dfa_orig, dfa_surr_mean/std (10 shuffled) | 100 % exact at 4 dp |

`B_surr_mean` and `B_surr_std` (20 shuffled) agree only statistically (z-test with 200
local permutations: std of z = 1.005, tails at the expected rates; a small systematic
offset of ~2·10⁻⁴ in B, 14/16 texts negative, remains unexplained). The DFA batch, which
also used `default_rng(seed=s)` permutations, reproduces the shuffled band *exactly*;
the burstiness batch was evidently run with a different generator (the CuPy version of
the cell). This is immaterial at the reported precision.

`B_fgn` agrees cell by cell only at the level of single-realisation noise (max |Δ| 0.36
at q = 0.99 on the shortest text; 51 % of cells within 0.01), with **no bias** (mean Δ per
text between −0.005 and +0.004). The aggregate quantities agree (§5).

**Bug in the reference ACF table.** In the notebook's ACF batch the bisection received a
stale variable, so `corpus_acf.csv` has the FGN of *all* texts tuned to α = 0.7694
(*Origin of Species*), and its `alpha` column is constant. The FGN ACF is
indistinguishable from zero either way, so the fractions outside the 95 % band are
unchanged within noise (e.g. lag 1: 0.109 vs 0.119; lag 50: 0.037 vs 0.056), but the
numbers of the "Corpus-level ACF results" section should be taken from the regenerated
table.

**Cross-machine reproducibility.** The three tables regenerated on macOS/arm64
(Accelerate) and on WSL Ubuntu/x86-64 (OpenBLAS), same package versions, are identical
in every column at the stored precision (`compare_reference.py`, 16 Sep 2026). The
residual differences from the Colab tables are therefore due to the Colab environment
(sklearn solver path, vector loading), not to the hardware.

## 5. Corpus-level numbers, reference vs regenerated

| | reference (Colab) | regenerated |
|---|---|---|
| mean over texts of ⟨B_orig/B_surr⟩_k at q=0.95 | 1.295 ± 0.135 | 1.295 ± 0.135 |
| mean over texts of ⟨B_orig/B_FGN⟩_k at q=0.95 | 1.290 ± 0.131 | 1.294 ± 0.137 |
| mean over texts of ⟨B_FGN/B_surr⟩_k at q=0.95 | 1.004 ± 0.008 | 1.001 ± 0.003 |
| fraction of (text, k) with B_orig > B_FGN and B_orig > B_surr, q ≤ 0.95 | 1.000 | 1.000 |
| same, q = 0.99 | 0.984 | 0.981 |
| DFA of projections, corpus mean: original / FGN / shuffled | 0.666 / 0.503 / 0.499 | 0.666 / 0.504 / 0.499 |

What changes in the paper:

- **α per text** (corpus table): new values in `results/corpus_burstiness.csv`, column
  `alpha`. Largest changes: Ulysses 0.794 → 0.763, Tom Sawyer 0.805 → 0.789,
  Principia 0.828 → 0.815.
- **α₀ per text**: 11/16 unchanged, 5 differ by 0.01–0.07. α₀ is only defined up to the
  bisection grid (tolerance 0.01 on α): report it with two decimals, or tighten the
  tolerance and state it.
- **Per-text figures**: regenerated with `run_text.py`; the FGN points move individually
  (single realisation), the pattern does not. Figure paths are now `figures/<stem>/`.
- **ACF section**: FGN fractions from the regenerated table.
- No conclusion changes.

## 6. Precision of B at high q

On a 17k-token text at q = 0.99 there are ~170 events and moving a single event changes B
by ~0.01. Differences of this size between runs, machines or realisations at q = 0.99 are
the intrinsic resolution of the estimator, not errors. Values of B for individual
components at q = 0.99 should not be quoted to three decimals.

## 7. How to reproduce

```
conda create -n semburst python=3.11 && conda activate semburst
pip install -e .
# data/vectors/glove.6B.300d.txt from https://nlp.stanford.edu/data/glove.6B.zip
#   (SHA-256 91125602…21ed, checked at first load; a .kv cache is written next to it)
python scripts/run_corpus.py data/corpus                 # ~40 s: results/corpus_*.csv
python scripts/run_text.py data/corpus/eng_wrnpc.txt     # figures/eng_wrnpc/
python scripts/compare_reference.py                      # vs results/reference/
```
