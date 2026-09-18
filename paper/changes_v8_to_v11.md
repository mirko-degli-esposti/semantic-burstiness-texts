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

## 0. What matters most, in three points

1. **The pipeline is reproducible.** The four Pearson correlations
   regenerate exactly (0.702, 0.295, 0.511, 0.571), verified against
   `scipy` by an assertion inside `paper_numbers.py`. Everything else in
   this document rests on that.

2. **The significance tests changed, and two marks moved.** The parametric
   $t$-test on $r$ assumes bivariate normality; the eigenvalue spectrum is
   strongly skewed, so it was replaced by a permutation test over the
   pairing of the two spectra. *War and Peace* drops from `***` to `**`,
   *Ulysses* from `**` to `*`. The substantive conclusions are unchanged.

3. **One factual error was found and corrected.** The body text claimed
   PC2 is the burstiest direction of *On the Origin of Species*; the
   maximum is at PC6 ($B_6 = 1.900$ vs $B_2 = 1.888$). The v10 figure
   caption already said PC6, so the paper contradicted itself. This also
   gave us a better argument — see §3.5.

---

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

### 3.6 Editorial changes (status: done)

- §1.2 retitled *The Altmann et al. mechanism* → *From word-level
  burstiness to topical organisation*. The mechanism is joint work and the
  old title over-attributed it; the citation remains in the first sentence.
- "biological variation" → "geographical distribution" in the list of
  example topics, so the examples match the semantic poles actually found
  (Darwin's PC2 is geographical).
- $K = 20$ stated once, where the burstiness spectrum is defined, with a
  note that higher-order components add progressively less variance and
  leave the qualitative picture unchanged.
- Redundant restatements of "PCA maximises variance, not burstiness"
  and of the word-shuffled null's properties compressed.

---

## 4. Open items

1. Apply the four remaining `p` → `P` (§3.1) and the three symbol
   renames (§3.2).
2. Table `tab:single_text_summary`: new marks on $r$, new $\rho$ column,
   caption naming the permutation test.
3. Rewrite of the *Origin of Species* subsection (§3.5).
4. Check the other three per-text subsections for the same class of
   error — any claim that PC1, or the wrong PC, is the burstiest.
5. `paper_numbers.py` sections 2–5 still carry hardcoded "(old …)"
   strings from v8. The `.tex` itself is correct and in sync; only the
   script's comparison column is stale, so its output for those sections
   currently flags differences that do not exist.
6. Decide whether $\rho$ goes in the table as its own column or is
   mentioned once in the methodology. Current recommendation: the column,
   since $\rho$ says something $r$ does not.

---

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
