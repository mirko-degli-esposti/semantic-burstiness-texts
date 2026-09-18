# Changes from `paper3_main_v8` to `v11`

Consolidated record for the co-author. Covers three revision steps:

| step | date | nature |
|---|---|---|
| v8 → v9 | 16 Sep 2026 | every number regenerated from a single consistent pipeline |
| v9 → v10 | 17 Sep 2026 | figures consolidated into panels; per-text figures moved to an appendix |
| v10 → v11 | 18 Sep 2026 | statistics (permutation tests, Spearman), notation collisions, text corrections |

Every number is produced by the released code from the tokenised texts with
fixed seeds, and is reproduced by `scripts/paper_numbers.py data/corpus`,
which writes `results/paper_numbers.md`.

**Status column**: `done` = already in the `.tex`; `pending` = agreed but not yet
applied. Nothing marked `pending` should be taken as final.

---

## 0. What matters most, in four points

1. **The pipeline is reproducible.** The four Pearson correlations
   regenerate exactly (0.702, 0.295, 0.511, 0.571), verified against
   `scipy` by an assertion inside `paper_numbers.py`. Everything else in
   this document rests on that.

2. **The FGN surrogate is a permutation of the original text.** The
   rank-to-word mapping reproduces the empirical rank histogram exactly,
   so all three sequences — original, word-shuffled, FGN — share the same
   token multiset and therefore the same embedding covariance, PCA
   eigensystem and projected marginals, *exactly*. They differ only in the
   ordering. This is stronger than what the paper currently claims, and it
   exposed three stale passages that survived from v8 (§3.6).

3. **The significance tests changed, and two marks moved.** The parametric
   $t$-test on $r$ assumes bivariate normality; the eigenvalue spectrum is
   strongly skewed, so it was replaced by a permutation test over the
   pairing of the two spectra. *War and Peace* drops from `***` to `**`,
   *Ulysses* from `**` to `*`. The substantive conclusions are unchanged.

4. **Four factual errors were found, all traceable to v8.** The burstiest
   direction of *Origin of Species* (PC2 → PC6, §3.5); the OOV rate
   ("5–15%" → under 2%, §3.9); the number of shuffled realisations behind
   the ACF curve (10 → 1, §3.9); and the claim that the FGN and original
   covariance structures differ by a few percent (they are identical,
   §3.6). Three of the four were contradicted by the paper's own tables or
   captions.

## 1. v8 → v9 — regenerated numbers

The earlier version mixed results from three separate Colab batches, each
of which recomputed PCA and the FGN surrogate independently. The pipeline
now computes them once per text, so the burstiness, ACF and DFA tables
share the same surrogate (same $\alpha_0$, same realisation).

Two consequences worth stating plainly to a referee:

- The FGN surrogate was previously built from a differently tokenised
  stream (regex `\w+`). DFA exponents in the corpus table shift by up to
  0.03 (*Ulysses*: 0.794 → 0.763).
- In the previous ACF batch the FGN of every text had been tuned to
  $\alpha = 0.769$ by a coding slip. The FGN autocorrelation is negligible
  either way, so the ACF conclusions are unchanged.

### 1.1 Corpus (status: done)

*Alice in Wonderland* removed (7,237 filtered tokens — too short for a
reliable IET estimate at $q = 0.95$). Corpus is now 16 texts.

| quantity | v8 | v9+ |
|---|---|---|
| texts | 17 | 16 |
| raw token range | 27,000–565,000 | 56,000–565,000 |
| filtered token range | 12,000–321,000 | 17,000–236,000 |
| DFA exponent range | $[0.61, 0.85]$ | $[0.63, 0.85]$ |

A column $\alpha_0$ (FGN generator exponent) was added to the corpus table.
$\alpha_0$ is determined only to $\pm 0.01$ by the bisection tolerance and
is therefore reported with two decimals throughout.

### 1.2 Four showcase texts (status: done)

| text | $\alpha$ v8 → v9 | $\alpha_0$ v8 → v9 | $r$ v8 → v9 |
|---|---|---|---|
| War and Peace | 0.719 → 0.721 | 0.770 → 0.76 | 0.702 → 0.702 |
| Origin of Species | 0.769 → 0.771 | 0.804 → 0.80 | 0.294 → 0.295 |
| Great Expectations | 0.688 → 0.689 | 0.735 → 0.74 | 0.522 → 0.511 |
| Ulysses | 0.794 → 0.763 | 0.839 → 0.80 | 0.578 → 0.571 |

Mean burstiness over the first 20 components at $q = 0.95$ was previously
reported without stating the quantile and with values from a different
batch: 1.18 / 1.10 / 1.07 / 1.13 → **1.36** (War and Peace), **1.35**
(Origin), **1.23** (Ulysses), **1.18** (Great Expectations), against
$\bar B \simeq 0.97$–$0.98$ for both null models in every case.

### 1.3 Corpus-level burstiness (status: done)

| quantity | v8 | v9+ |
|---|---|---|
| $\langle B_k^{\rm orig}\rangle_{\rm texts}$ | $[1.12, 1.37]$, mean 1.22 | $[1.16, 1.54]$, mean 1.26 |
| $\langle B_k^{\rm surr}\rangle$ | $[0.972, 0.978]$ | $[0.973, 0.978]$ |
| $\langle B_k^{\rm FGN}\rangle$ | $[0.970, 0.992]$ | $[0.958, 0.983]$ |
| $B^{\rm orig} > B^{\rm FGN}$ | 99.4% of pairs | **100%** of pairs |
| $\|B^{\rm FGN}/B^{\rm surr} - 1\| < 0.05$ | 95.9% | 95.6% |
| per-text mean ratio orig/surr | $1.248 \pm 0.011$ | $\mathbf{1.29 \pm 0.03}$ |
| FGN/surr ratio | $1.0035 \pm 0.0012$, $t=2.88$, $p=0.011$ | $\mathbf{1.001 \pm 0.001}$, $t=1.1$, $P=0.28$ |

The last row is the most useful change for the argument. In v8 the two
null models were *significantly different* from each other, which was
awkward to explain away as estimator noise. With the consistent pipeline
they are statistically indistinguishable — the cleaner and stronger
statement.

The abstract changed accordingly: "exceeds the FGN surrogate in $99.4\%$
of pairs" → "in all pairs".

The excess of the original over the nulls is now described as a $\sim 30\%$
mean excess (was: a consistent $\sim 25\%$ excess). The per-text spread is
reported explicitly: $[1.17, 1.39]$ for fifteen texts with *Principia
Mathematica* an outlier at 1.73, sd $= 0.13$.

### 1.4 ACF and DFA (status: done)

| quantity | v8 | v9+ |
|---|---|---|
| GE: $\rho_k(1)$ original range | $[0.042, 0.179]$ | $[0.049, 0.208]$ |
| GE: i.i.d. band $1.96/\sqrt{M}$ | $\pm 0.006$ | $\pm 0.008$ |
| GE: FGN lag-1 | $< 0.025$, 19/20 inside band | $\le 0.007$, **20/20** inside band |
| corpus $\bar\rho^{\rm orig}(1)$ | $0.096 \pm 0.044$ | $0.100 \pm 0.045$ |
| corpus $\bar\rho^{\rm FGN}(1)$ | $0.003 \pm 0.009$ | $0.002 \pm 0.005$ |
| FGN pairs significant at lag 1 | 17.2% | 10.9% |
| $t$-test FGN $\rho(1)$ vs 0 | $t = 5.83$ | $t = 5.05$ |
| GE: $\bar\alpha^{\rm orig}$ | $0.637 \pm 0.032$ | $0.623 \pm 0.034$ |
| GE: $\bar\alpha^{\rm FGN}$ | $0.502 \pm 0.015$ | $0.499 \pm 0.014$ |
| GE: $\alpha_k^{\rm orig}$ range | $[0.575, 0.698]$ | $[0.564, 0.693]$ |

A remark about PC1 lying outside the i.i.d. band ($\rho_1^{\rm FGN}(1) =
0.023$) was **deleted**: with the consistent pipeline the value is 0.004,
inside the band.

The residual FGN excess at lag 1 is now quantified rather than asserted:
the significant cases concentrate on PC1 (56% of PC1 pairs against 8% for
$k \geq 4$), consistent with the known GloVe artefact from rare
transliterated proper nouns.

---

## 2. v9 → v10 — figure consolidation (status: done)

No numbers changed in this step. Structural only:

- Four per-text burstiness-spectrum figures → one 4-panel figure
  (`fig:burst_panel`, panels A–D).
- Four per-text quantile-sweep figures → one 4-panel figure
  (`fig:sweep_panel`).
- The four "semantic poles" figures were **removed**; the same information
  is in the PC tables (`tab:wrnpc_pc` and siblings), which are more precise
  and cost less space.
- Per-text eigenvalue spectra and IET distributions moved to a new
  appendix, *Additional per-text figures* (`app:pertext`), keeping only
  *War and Peace* in the main text as the worked example.
- Figure paths now follow the corpus filenames
  (`figures/<stem>/<stem>_NN_<name>.png`), so every figure is regenerable
  by `scripts/run_text.py`.
- Dropbox references replaced by a pointer to the code repository.

Net effect: roughly fifteen figures down to the panels plus the appendix.

---

## 3. v10 → v11 — statistics, notation, corrections

### 3.1 Notation: `p` was overloaded (status: partly done)

`p` meant both the **event rate** $p = 1 - q$ (Sec. 2.3, and in the
robustness section at $p = 0.01$) and the **p-value** of the correlation
and $t$-tests — both small decimals, a few pages apart. The event rate is
structural and appears throughout, so the p-value was renamed `P`.

Seven occurrences converted (status: done): the four $(r, p)$ pairs in the
per-text sections, and three $t$-test p-values in the corpus sections.

Four occurrences still open (status: **pending**) — they use `<` and `>`
rather than `=`, so the first pass missed them:

- table `tab:single_text_summary` footnote: `$^*p<0.05$`, `$^{**}p<0.01$`,
  `$^{***}p<0.001$`, `no mark: $p>0.05$`
- `t = 8.7,\quad p < 10^{-6}` (eq. `ratio_corpus`)
- `$t = 5.05$, $p < 10^{-6}$` (corpus ACF)

### 3.2 Three further symbol collisions (status: pending)

| symbol | conflicting meanings | resolution |
|---|---|---|
| $\alpha$ | matching condition in $u_t^{(\alpha)}$ vs DFA exponent (≈65 uses) | matching condition → $\mathcal{C}$ (6 occurrences) |
| $\gamma$ | Zipf exponent $f(r)\sim r^{-\gamma}$ vs diffusion exponent | diffusion exponent → $H$, tied explicitly to the DFA $\alpha$ of the stationary series |
| $\tilde{\mathbf{s}}$ | retained tokens $(\tilde s_1,\ldots,\tilde s_M)$ vs FGN surrogate word sequence | surrogate → $\mathbf{s}^{\rm FGN}$ (1 occurrence) |

$H$ and "Hurst" appear nowhere else in the paper, so this introduces no
new collision.

### 3.3 Significance by permutation, not by the parametric test (status: pending)

The $K = 20$ pairs $(\lambda_k, B_k)$ are not independent draws:
$\{\lambda_k\}$ is a deterministic decreasing sequence and both spectra
derive from the same trajectory. The $t$-test on $r$ is therefore not a
valid significance test here. It is replaced by a permutation test over
the pairing between the two spectra ($10^5$ pairings, seed 0), implemented
in `scripts/pearsonr_spearman.py` and called from `paper_numbers.py`.

| text | $r$ | parametric $p$ | permutation $P$ | mark |
|---|---|---|---|---|
| War and Peace | 0.702 | 0.0006 | **0.0055** | `***` → `**` |
| Origin of Species | 0.295 | 0.207 | 0.169 | none → none |
| Great Expectations | 0.511 | 0.021 | 0.0136 | `*` → `*` |
| Ulysses | 0.571 | 0.009 | **0.0406** | `**` → `*` |

The parametric test was anticonservative by up to an order of magnitude,
as expected when the predictor is strongly skewed.

Note for the reader of the table: *Ulysses* has a larger $r$ than *Great
Expectations* but a larger $P$. This is not an error — the permutation
null depends on the shape of each text's eigenvalue spectrum.

### 3.4 Spearman added (status: pending)

The eigenvalue spectrum decays steeply, so Pearson is dominated by the
leading components. The rank correlation was computed as a robustness
check and turns out to carry information of its own:

| text | $r$ | $\rho$ | $P_\rho$ |
|---|---|---|---|
| War and Peace | 0.702 | **0.850** | $< 10^{-4}$ |
| Origin of Species | 0.295 | **0.460** | **0.042** |
| Great Expectations | 0.511 | 0.579 | 0.0085 |
| Ulysses | 0.571 | **0.817** | $< 10^{-4}$ |

$\rho > r$ in all four texts: the association between semantic variance
and burstiness is **monotone but not linear**, and Pearson understates it.

`P = 0.0000` in the regenerated output is the floor of $10^5$ permutations
($1/100001$) and is reported as $P < 10^{-4}$, not as zero.

### 3.5 Text correction: the burstiness maximum of Darwin (status: pending)

The body text of the *Origin of Species* subsection states that PC2 is the
burstiest direction. It is not: the maximum is at **PC6**, $B_6 = 1.900$,
against $B_2 = 1.888$. The v10 caption of `fig:burst_panel` already gives
the maxima correctly as PC3, PC6, PC3, PC2, so the paper currently
contradicts itself. The body text is a leftover from v9, when the
now-removed per-text figure `fig:darwin_burst` carried the PC2 claim.

This matters beyond the correction. The subsection used the weak
correlation as its argument:

> The weak eigenvalue–burstiness correlation, $r=0.295$ ($p=0.207$), shows
> especially clearly that the direction of greatest semantic variance need
> not be the direction of greatest temporal clustering.

That argument no longer survives contact with Spearman: $\rho = 0.460$,
$P = 0.042$ is a significant association. The displacement of the maximum
to PC6 says the same thing directly, needs no correlation measure at all,
and holds in every text (PC3, PC6, PC3, PC2 — never PC1). The subsection
is rewritten around that fact, with the two correlations reported as
description rather than as the argument.

### 3.6 The FGN surrogate is a permutation — and three stale passages (status: pending)

Verified directly: `Counter(tokens_all)` of the FGN surrogate equals that
of the original, for every showcase text, and the filtered counts agree to
the token at $R = 100$, $150$ and $200$. Multiset identity at the
unfiltered level makes the result independent of $R$ by construction, not
by observation.

| text | $M$ | $M_{\rm FGN}$ | ratio | multiset identical |
|---|---|---|---|---|
| War and Peace | 235,933 | 235,933 | 1.0000 | yes |
| Origin of Species | 58,913 | 58,913 | 1.0000 | yes |
| Great Expectations | 64,410 | 64,410 | 1.0000 | yes |
| Ulysses | 101,489 | 101,489 | 1.0000 | yes |

Consequences. By Eq. `sigma_invariant`, $\Sigma_{\rm FGN} =
\Sigma_{\rm orig}$ **exactly**: the original eigenvectors *are* the
surrogate's own principal directions. The design can now be stated in one
line — *the three sequences are permutations of one another and differ
only in the ordering of visits through a fixed semantic geometry* — and
the two null models differ in exactly one ingredient, the rank-level
scaling.

Three passages assert the opposite and are all v8 leftovers, from when the
FGN was tokenised with a different regex and the multisets genuinely
differed:

- `rem:fgn_cov`: "does not impose covariance invariance as an algebraic
  constraint … empirically very close" → the invariance *is* algebraic.
- §Text preprocessing: "increasing $R$ to 150 or 200 … begins to degrade
  the alignment between the original and FGN covariance structures" → no
  such degradation is possible; sentence deleted.
- §FGN surrogate generation: "any residual difference is below $3\%$ in
  eigenvalue and below $5\%$ in eigenvector angle" → the difference is
  zero.

A fourth passage becomes redundant rather than wrong: the sentence added
earlier today noting that $M_{\rm FGN}$ need not equal $M$ is removed,
since the two are equal by construction.

One further consequence, in the paper's favour. The code computes the
event threshold once from the original series and applies it to all three
(`th = thresholds(an.pca.proj, q)`), whereas §2.3 describes each series
being thresholded at its own quantile. The two conventions coincide
exactly, because permutations share a marginal distribution — so the
event rate is exactly $1-q$ for all three sequences, and this can now be
stated as a consequence rather than assumed.

### 3.7 Does the frequency filter destroy the rank-level scaling? (status: new result)

A referee can reasonably ask whether the FGN's projected series show
$\bar\alpha = 0.499$ because rank-level memory does not reach embedding
space — the paper's claim — or simply because the top-$R$ filter destroyed
that memory before the projection. The question was settled by measuring
the DFA exponent of the *filtered* rank sequence for both the original and
the surrogate.

| text | unfiltered | $\alpha$ (pipeline) | original, filtered | FGN, filtered |
|---|---|---|---|---|
| War and Peace | 0.693 | 0.721 | 0.674 | 0.633 |
| Origin of Species | 0.726 | 0.771 | 0.694 | 0.645 |
| Great Expectations | 0.672 | 0.689 | 0.609 | 0.567 |
| Ulysses | 0.805 | 0.763 | 0.772 | 0.629 |

**The filter does not destroy the scaling.** Every filtered value stays
well above $0.5$; the FGN arrives at the projection stage still carrying
rank-level memory of $\alpha \simeq 0.57$–$0.65$, and its projections
nevertheless show none. The claim is supported, now with a number behind
it.

**But the filter degrades the surrogate more than the original**, in every
text, and markedly so for *Ulysses* ($-0.176$ against $-0.033$). The
matching $\alpha_{\rm FGN} \simeq \alpha_{\rm orig}$ is imposed before
the filter, so at the level where the comparison is made the null carries
somewhat less memory than intended. This is a handicap to the null model,
not a licence for it, and is worth stating rather than leaving to be
found.

Caveat on these four columns: they were computed with `projection_alpha`,
which does not reproduce the pipeline's own `alpha_text` (discrepancies up
to 0.045, and of opposite sign for *Ulysses*). The three columns are
comparable with one another but should not be printed alongside $\alpha$
and $\alpha_0$ until recomputed with the estimator used inside
`fgn_surrogate`.

### 3.8 Burstiness beyond the retained $K = 20$ (status: new result)

The paper retains $K = 20$ components. Whether anything changes beyond
that was previously asserted without evidence; it has now been measured by
refitting the PCA with $K = 50$.

| text | cum. var. 20 | 50 | 100 | mean $B$ 1–20 | 21–50 | min $B$ 21–50 |
|---|---|---|---|---|---|---|
| War and Peace | 37.8% | 57.1% | 76.4% | 1.358 | 1.138 | 1.085 |
| Origin of Species | 38.1% | 59.0% | 78.6% | 1.350 | 1.188 | 1.095 |
| Great Expectations | 38.5% | 59.0% | 78.7% | 1.176 | 1.112 | 1.041 |
| Ulysses | 35.0% | 53.2% | 72.7% | 1.234 | 1.120 | 1.041 |

Every component up to $K = 50$ stays above the independent-event baseline
$\CV_{\rm geom} = 0.975$ in every text; the worst case, 1.041, is still
$6.8\%$ above it. Variance per component decays from $1.9\%$ over the
first twenty to $0.65\%$ over components 21–50 and $0.39\%$ over 51–100,
and mean burstiness falls by 36–61% of its excess over the baseline.

So the qualitative picture does hold, and the honest formulation states
both halves: burstiness persists well beyond the retained range while
decreasing in magnitude. $K = 20$ is a choice about interpretability, not
a claim that nothing happens further out.

The refit reproduces the stored projections to $10^{-6}$, which is the
float32 precision floor of the GloVe vectors — not a sign flip, which
would have produced an error of order unity and would have changed $B_k$,
since the threshold is applied to the upper tail only.

### 3.9 Errors in the pipeline description (status: pending)

Four statements in the methodology do not describe the code that produced
the results.

- **OOV rate.** "The OOV rate after filtering is typically $5$–$15\%$ for
  Victorian English texts" — the paper's own summary table reports 1.6%,
  0.4%, 1.3% and 0.7%, confirmed independently from the pre- and
  post-lookup token counts (1.58 / 0.44 / 1.34 / 0.73%). Wrong by an order
  of magnitude, and contradicted fifteen pages later.
- **Number of shuffled realisations.** The code uses three different
  conventions — 20 realisations for the burstiness spectrum
  (`n_surr = 20`), a single realisation for the ACF
  (`a.pca.proj[a.perms[0]]`, so labelled in the source), and 10 for the
  DFA band (`N_SURR_DFA`). The methodology describes a single permutation
  throughout, and the ACF figure caption claims "mean over 10
  realisations", which is wrong on both counts. The DFA caption is
  correct.
- **PCA dimensions.** "$K_{\rm show} = 50$ components for eigenvalue
  analysis" and $\mathbf{P} \in \R^{M \times K_{\rm show}}$ describe
  nothing in the code: `fit_pca` retains all 300 eigenvalues but only $K$
  eigenvectors, $K$ entries of `explained_variance_ratio`, and an
  $M \times K$ projection matrix, with $K = 20$.
- **$\alpha_{\rm FGN}$** in Eq. `fgn_dfa_match` appears exactly once in
  the paper and conflates the generator exponent $\alpha_0$ with the
  measured exponent $\alpha$; the pipeline section states the
  relationship correctly.

Also stale, inside commented-out source that the authors intend to keep:
the shuffle block states $N_{\rm surr} = 10$ against `n_surr = 20` in
`config.py`, and contains a sentence missing its first half. Both should
carry a `% STALE` marker so they are not restored unexamined.

### 3.10 Editorial changes (status: done)

- §1.2 retitled *The Altmann et al. mechanism* → *From word-level
  burstiness to topical organisation*. The mechanism is joint work and the
  old title over-attributed it; the citation remains in the first sentence.
- "biological variation" → "geographical distribution" in the list of
  example topics, so the examples match the semantic poles actually found
  (Darwin's PC2 is geographical).
- $K = 20$ stated once, where the burstiness spectrum is defined. The
  accompanying claim about higher-order components was initially written
  without evidence; it has since been measured and restated with figures
  (§3.8), and is a candidate for the robustness section of the Results
  rather than the introduction.
- Redundant restatements of "PCA maximises variance, not burstiness"
  and of the word-shuffled null's properties compressed.
- §Logical role of the null models now opens with a table
  (`tab:null_taxonomy`) setting out which statistical ingredient each
  sequence retains, and closes with the joint conclusion that both
  answers are negative and non-redundant. Given §3.6, the embedding
  geometry row reads *exact* for both null models, so the two differ in
  exactly one ingredient.
- `rem:fgn_entropy` concerns rank proximity versus semantic proximity and
  mentions no entropy; the label should be renamed while it is cited in
  only one place.

---

## 4. Open items

Ordered by consequence, not by effort.

1. Rewrite `rem:fgn_cov`, delete the $R = 150$/$200$ degradation sentence
   and the "below 3% / below 5%" passage (§3.6). These upgrade three
   hedges into an exact statement.
2. Correct the OOV rate, the ACF caption's realisation count, the
   $K_{\rm show}$ passage and $\alpha_{\rm FGN}$ (§3.9).
3. Rewrite the *Origin of Species* subsection around the PC6 maximum
   (§3.5), and check the other three per-text subsections for the same
   class of error.
4. Apply the four remaining `p` → `P` (§3.1) and the three symbol
   renames (§3.2).
5. Table `tab:single_text_summary`: new marks on $r$, new $\rho$ column,
   caption naming the permutation test.
6. State the three shuffled-realisation conventions in the methodology,
   and the fixed seeds (`pca_seed=42`, `fgn_seed=42`, `n_surr=20` with
   seeds 0–19, $10^5$ permutations with seed 0).
7. Recompute the filtered-rank DFA of §3.7 with the estimator used inside
   `fgn_surrogate` before quoting those numbers in the paper.
8. Decide where the $K = 50$ result belongs: the robustness section of
   the Results, beside the quantile sweep, is the natural home.
9. `paper_numbers.py` sections 2–5 still carry hardcoded "(old …)"
   strings from v8. The `.tex` itself is correct and in sync; only the
   script's comparison column is stale, so its output for those sections
   currently flags differences that do not exist.

## 5. Reproducing everything

```bash
python scripts/run_corpus.py data/corpus        # corpus_*.csv
python scripts/paper_numbers.py data/corpus     # results/paper_numbers.md
python scripts/run_text.py data/corpus/<text>   # per-text figures
```

`paper_numbers.py` asserts that the permutation implementation reproduces
`scipy.stats.pearsonr` to $10^{-9}$ on every text, so a silent divergence
between the two code paths cannot go unnoticed.

Permutation parameters are fixed: $10^5$ pairings, seed 0. Both belong in
the methodology section alongside the test itself.

Section 6 of `results/paper_numbers.md` now carries the verifications
introduced above: $M$ against $M_{\rm FGN}$, multiset identity at three
values of $R$, the filtered-rank DFA exponents, and the $K = 50$
burstiness refit. Each carries its own guard — a calibration column for
the DFA estimator, an assertion that the refit reproduces the stored
projections, and an assertion on the number of components returned, so
that a silent truncation cannot be mistaken for a result.
