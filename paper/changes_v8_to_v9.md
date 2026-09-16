# Changes from paper3_main_v8 to v9 — regenerated numbers (semburst, 16 Sep 2026)

Source of every number: `results/paper_numbers.md`, `results/corpus_*.csv`, `results/compare_reference.txt`.
Line numbers refer to `paper3_main_v8_reordered_results.tex`.

---

## PART A — mechanical replacements

### A1. Abstract (l. 98)
- `exceeds the FGN surrogate in $99.4\%$ of pairs` → `exceeds the FGN surrogate in all pairs`
  (new: 100 % at q = 0.95; 98.1 % only at q = 0.99)

### A2. Figure paths (30 `\includegraphics`)
| old | new |
|---|---|
| `figures/wrnpc/eng_wrnpc_NN_*.png` | `figures/eng_wrnpc/eng_wrnpc_NN_*.png` |
| `figures/darwin/darwin_origin_NN_*.png` | `figures/darwin_origin/darwin_origin_NN_*.png` |
| `figures/greatexp/great_expectations_NN_*.png` | `figures/great_expectations_cut_clean/great_expectations_cut_clean_NN_*.png` |
| `figures/ulysses/eng_ulysses_NN_*.png` | `figures/eng_ulysses/eng_ulysses_NN_*.png` |
| `figures/acf_decay_loglag.png` | `figures/great_expectations_cut_clean/great_expectations_cut_clean_08_acf_decay_loglag.png` |
| `figures/acf_mean_loglag.png` | `.../great_expectations_cut_clean_09_acf_mean_loglag.png` |
| `figures/dfa_projections_spectrum.png` | `.../great_expectations_cut_clean_10_dfa_projections_spectrum.png` |
| `figures/dfa_projections_loglog.png` | `.../great_expectations_cut_clean_11_dfa_projections_loglog.png` |
| `figures/fig1_mean_spectrum.png`, `fig2_…`, `fig3_…`, `acf_corpus_*.png` | unchanged names, regenerated files |

### A3. Table tab:single_text_summary (l. 810–817)
```
War and Peace      & 564{,}788 & 235{,}933 & 1.6\% & 0.721 & 0.76 & 0.702$^{***}$ & 1.855 \\
Origin of Species  & 151{,}179 &  58{,}913 & 0.4\% & 0.771 & 0.80 & 0.295          & 1.888 \\
Great Expectations & 188{,}925 &  64{,}410 & 1.3\% & 0.689 & 0.74 & 0.511$^{*}$    & 1.209 \\
Ulysses            & 264{,}165 & 101{,}489 & 0.7\% & 0.763 & 0.80 & 0.571$^{**}$   & 1.495 \\
```
Caption: add after "$\alpha_0$: FGN bisection parameter": `(resolved to $\pm0.01$ by the bisection tolerance)`.

### A4. Per-text sections
- l. 847: `$\alpha=0.719$, and the fitted FGN parameter is $\alpha_0=0.770$` → `$\alpha=0.721$ … $\alpha_0=0.76$`
- l. 931–932: `$\alpha=0.769$ and $\alpha_0=0.804$` → `$\alpha=0.771$ and $\alpha_0=0.80$`
- l. 1018–1019: `$\alpha=0.688$ and $\alpha_0=0.735$` → `$\alpha=0.689$ and $\alpha_0=0.74$`
- l. 1105: `$\alpha=0.794$ and $\alpha_0=0.839$` → `$\alpha=0.763$ and $\alpha_0=0.80$`
- l. 1252 and 1270–1271: `$r=0.294$ ($p=0.209$)` → `$r=0.295$ ($p=0.207$)` (twice)
- l. 1285: `$r=0.522$ ($p=0.018$)` → `$r=0.511$ ($p=0.021$)`
- l. 1314: `$r=0.578$ ($p=0.008$)` → `$r=0.571$ ($p=0.009$)`
- l. 1215–1216 (War and Peace, PC3 nulls): `$B_3^{\rm surr}=0.976$, $B_3^{\rm FGN}=0.961$` → `$B_3^{\rm surr}=0.976$, $B_3^{\rm FGN}=0.974$`
- l. 1281–1282 (Great Expectations): `null values lie near $0.94$--$0.98$` → `null values lie in $0.95$--$1.00$`
- l. 1336–1343: **rewritten, see B1**

### A5. Corpus description and table (l. 1410–1457)
- l. 1417–1420: `Raw token counts range from approximately $27{,}000$ (Alice in Wonderland) to $565{,}000$ (War and Peace), with filtered token counts $M$ … between $12{,}000$ and $321{,}000$.` →
  `Raw token counts range from approximately $56{,}000$ (The Picture of Dorian Gray) to $565{,}000$ (War and Peace), with filtered token counts $M$ (after high-frequency and hapax removal, OOV excluded) between $17{,}000$ and $236{,}000$.`
- l. 1421: `$[0.61, 0.85]$` → `$[0.63, 0.85]$`
- l. 1428: `Corpus of 17 literary and scientific texts.` → `Corpus of 16 literary and scientific texts.`
- caption, after "$\alpha$: DFA scaling exponent of the rank sequence.": add `$\alpha_0$: FGN generator exponent matched to $\alpha$ (bisection tolerance $0.01$).`
- header: `Title & Author & $N$ & $M$ & $\alpha$ \\` → `Title & Author & $N$ & $M$ & $\alpha$ & $\alpha_0$ \\`, tabular `{llrrl}` → `{llrrll}`
- rows (Alice removed):
```
Pride and Prejudice        & Austen    & 122{,}226 &  42{,}364 & 0.642 & 0.67 \\
Don Quixote (transl.)      & Cervantes & 403{,}152 & 147{,}279 & 0.711 & 0.76 \\
On the Origin of Species   & Darwin    & 151{,}179 &  58{,}913 & 0.771 & 0.80 \\
The Voyage of the Beagle   & Darwin    & 206{,}728 &  84{,}931 & 0.629 & 0.67 \\
David Copperfield          & Dickens   & 363{,}557 & 134{,}409 & 0.727 & 0.78 \\
Great Expectations         & Dickens   & 188{,}925 &  64{,}410 & 0.689 & 0.74 \\
Oliver Twist               & Dickens   & 161{,}529 &  59{,}729 & 0.711 & 0.76 \\
Ulysses                    & Joyce     & 264{,}165 & 101{,}489 & 0.763 & 0.80 \\
The Jungle Book            & Kipling   & 151{,}161 &  49{,}522 & 0.775 & 0.83 \\
Moby Dick                  & Melville  & 215{,}652 &  82{,}773 & 0.694 & 0.73 \\
Principia Mathematica      & Newton    & 112{,}225 &  26{,}347 & 0.815 & 0.85 \\
The Analysis of Mind       & Russell   &  88{,}342 &  30{,}449 & 0.743 & 0.76 \\
War and Peace              & Tolstoy   & 564{,}788 & 235{,}933 & 0.721 & 0.76 \\
Huckleberry Finn           & Twain     & 145{,}924 &  52{,}741 & 0.774 & 0.83 \\
Tom Sawyer                 & Twain     &  71{,}102 &  22{,}085 & 0.788 & 0.80 \\
The Picture of Dorian Gray & Wilde     &  55{,}619 &  16{,}776 & 0.845 & 0.87 \\
```
- l. 1460–1465 (quote about Dropbox folders): replace with
  `\begin{quote} Per-text IET distributions and burstiness spectra for all texts and thresholds can be regenerated with \texttt{scripts/run\_text.py} in the code repository. The main text reports the aggregated corpus results. \end{quote}`

### A6. Corpus burstiness sections
- l. 1477–1520: **rewritten, see B2**
- l. 1544–1560: **rewritten, see B3**
- fig2 caption (l. ~1576): `the slight degradation at $q = 0.99$ is due to estimator noise at $p = 0.01$.` — unchanged.
- l. 1598–1606: **rewritten, see B4**
- l. 1616: `with a consistent $\sim 25\%$ excess` → `with a $\sim 30\%$ mean excess`
- fig3 caption (l. 1630–1636): `tightly centred on 1 (mean $1.0035$, s.e.\ $0.0012$; $t = 2.88$, $p = 0.011$). The $0.35\%$ deviation from unity is negligible relative to the $25\%$ orig--null gap, confirming` →
  `tightly centred on 1 (mean $1.0008$, s.e.\ $0.0012$; $t = 0.63$, $p = 0.53$), statistically indistinguishable from unity, confirming`

### A7. ACF, Great Expectations (l. 1740–1806)
- l. 1745: `$\rho_k(1) \in [0.042, 0.179]$` → `$\rho_k(1) \in [0.049, 0.208]$`
- l. 1744: `$\pm 0.006$` → `$\pm 0.008$` (M = 64,410 → 1.96/√M = 0.0077); same at l. 1772
- l. 1754–1755: `All 20 components have $\rho_k^{\rm FGN}(1) < 0.025$, with 19 of 20 inside the i.i.d.\ band.` → `All 20 components have $|\rho_k^{\rm FGN}(1)| \le 0.007$, inside the i.i.d.\ band.`
- l. 1737, 1758, 1826, 2031, 2057: `$\alpha = 0.688$` → `$\alpha = 0.689$` (five places)
- Table tab:acf_summary rows (bold = |ρ| > 0.008):
```
 1 & \textbf{0.060} &    0.004 && \textbf{0.008} &    0.004 \\
 2 & \textbf{0.208} &    0.007 && \textbf{0.015} &    0.004 \\
 3 & \textbf{0.136} & $-$0.002 && \textbf{0.018} &    0.004 \\
 4 & \textbf{0.123} & $-$0.003 && \textbf{0.008} & $-$0.003 \\
 5 & \textbf{0.086} & $-$0.002 &&    0.004 & $-$0.004 \\
 6 & \textbf{0.121} &    0.004 &&    0.005 & $-$0.001 \\
 7 & \textbf{0.127} &    0.002 &&    0.007 & $-$0.003 \\
 8 & \textbf{0.103} &    0.001 &&    0.004 &    0.003 \\
 9 & \textbf{0.082} & $-$0.002 && \textbf{0.008} &    0.001 \\
10 & \textbf{0.083} &    0.004 &&    0.003 &    0.003 \\
```
  (k=1 and k=4 at lag 100 are 0.0077 and 0.0078, i.e. at the band edge 0.0077: bold k=1 only if you prefer strict ">"; I suggest un-bolding both to avoid a 4th-decimal argument.)
- l. 1794: `(k=11..20 all have $|\rho^{\rm FGN}| < 0.007$` → `(k=11..20 all have $|\rho^{\rm FGN}(1)| \le 0.007$`
- Remark l. 1800–1806: **delete** (PC1 is no longer outside the band: ρ₁^FGN(1) = 0.004).

### A8. ACF, corpus (l. 1871–1935 and captions)
- l. 1871–1885: `0.096 \pm 0.044` → `0.100 \pm 0.045`; `0.026 \pm 0.017` → `0.032 \pm 0.021`; `0.010 \pm 0.009` → `0.011 \pm 0.011`; `\bar\rho^{\rm FGN}(1) = 0.003 \pm 0.009` → `0.002 \pm 0.005`; `\bar\rho^{\rm surr}(1) = 0.000 \pm 0.004` unchanged
- l. 1897–1906: **rewritten, see B5**
- l. 1908–1910: `peaks at $89.7\%$ at lag $\ell = 2$ and remains above $56\%$ up to lag $\ell = 100$` → `peaks at $93\%$ at lag $\ell = 2$ and remains above $50\%$ up to lag $\ell = 100$`
- l. 1921–1923: `$\rho_k(1) \in [0.020, 0.282]$ with mean $0.096$` → `$\rho_k(1) \in [0.026, 0.264]$ with mean $0.100$`; `$\rho_k(1) \in [-0.015, 0.058]$ with mean $0.003$` → `$\rho_k(1) \in [-0.014, 0.023]$ with mean $0.002$`
- l. 1928–1929: `$t = 5.83$, $p < 0.001$: … negligibly small ($0.003$) relative to the orig--null gap ($0.093$)` → `$t = 5.05$, $p < 10^{-6}$: … negligibly small ($0.002$) relative to the orig--null gap ($0.098$)`
- acf_rho1 caption (l. 1994–1996): `$t = 5.83$` → `$t = 5.05$`; `($0.003$)` → `($0.002$)`; `($0.093$)` → `($0.098$)`
- acf_corpus_frac caption: unchanged (PC1 concentration verified: 56 % of FGN lag-1 exceedances on PC1 vs 8 % for k ≥ 4).

### A9. DFA, Great Expectations (l. 2036–2113)
- l. 2037: `0.637 \pm 0.032` → `0.623 \pm 0.034`
- l. 2044: `0.502 \pm 0.015` → `0.499 \pm 0.014`
- l. 2045: `$\alpha \approx 0.71$` → `$\alpha_0 = 0.74$` (the generator exponent; the matched α is 0.689)
- l. 2050: `0.499 \pm 0.002` → `0.499 \pm 0.004`
- Table tab:dfa_proj rows:
```
 1 & 0.605* & 0.511$\sim$ & 0.501 &  11 & 0.575* & 0.506$\sim$ & 0.500 \\
 2 & 0.681* & 0.500$\sim$ & 0.491 &  12 & 0.642* & 0.493$\sim$ & 0.502 \\
 3 & 0.693* & 0.518$\sim$ & 0.495 &  13 & 0.564* & 0.512$\sim$ & 0.500 \\
 4 & 0.634* & 0.514$\sim$ & 0.499 &  14 & 0.595* & 0.484$\sim$ & 0.497 \\
 5 & 0.642* & 0.486$\sim$ & 0.496 &  15 & 0.645* & 0.486$\sim$ & 0.497 \\
 6 & 0.633* & 0.515$\sim$ & 0.501 &  16 & 0.579* & 0.505$\sim$ & 0.494 \\
 7 & 0.647* & 0.504$\sim$ & 0.498 &  17 & 0.586* & 0.511$\sim$ & 0.493 \\
 8 & 0.633* & 0.469$\sim$ & 0.497 &  18 & 0.617* & 0.515$\sim$ & 0.507 \\
 9 & 0.643* & 0.482$\sim$ & 0.494 &  19 & 0.595* & 0.489$\sim$ & 0.505 \\
10 & 0.630* & 0.482$\sim$ & 0.503 &  20 & 0.622* & 0.495$\sim$ & 0.502 \\
```
- l. 2093–2095: `$\bar\alpha^{\rm orig}=0.637\pm0.032$ … $\bar\alpha^{\rm FGN}=0.502\pm0.015$ … $\bar\alpha^{\rm surr}=0.499\pm0.002$` → `0.623\pm0.034 … 0.499\pm0.014 … 0.499\pm0.004`
- l. 2103: `$\alpha_k \approx 0.63$--$0.70$` → `$\alpha_k \approx 0.60$--$0.69$`
- l. 2109: `$\alpha_k^{\rm orig} \in [0.575, 0.698]$` → `$[0.564, 0.693]$`
- l. 2111–2113: `(e.g.\ PC17: $\alpha=0.682$, PC19: $\alpha=0.665$) have stronger long-range correlations than lower-indexed ones (e.g.\ PC16: $\alpha=0.575$)` → `(e.g.\ PC12: $\alpha=0.642$, PC15: $\alpha=0.645$) have stronger long-range correlations than some lower-indexed ones (e.g.\ PC11: $\alpha=0.575$, PC13: $\alpha=0.564$)`

---

## PART B — rewritten paragraphs (for approval)

### B1. l. 1336–1343 (mean burstiness of the four texts)
```latex
Averaged over the first 20 components at $q=0.95$, the representative
texts have $\bar B^{\rm orig}$ of $1.36$ (\emph{War and Peace}),
$1.35$ (\emph{On the Origin of Species}), $1.23$ (\emph{Ulysses}) and
$1.18$ (\emph{Great Expectations}), against $\bar B\simeq0.97$--$0.98$
for both null models in every case. The ordering is not a simple
function of either text length or rank-sequence DFA exponent.
The common feature is that component-level burstiness is present in the
original semantic trajectories and absent from both null models.
```

### B2. l. 1477–1520 (corpus-wide ordering)
```latex
The corpus-level component spectrum is summarised in
Figure~\ref{fig:corpus_spectrum}.
Averaging the burstiness spectrum $\{\bk\}$ across all 16 texts
at quantile $q = 0.95$, the original texts are systematically more
bursty than both null models across all 20 PCA components:
$\langle B_k^{\rm orig}\rangle_{\rm texts} \in [1.16, 1.54]$
(mean $1.26$), while both null models cluster tightly around
the geometric baseline $\CV_{\rm geom} = \sqrt{0.95} \approx 0.975$:
$\langle B_k^{\rm surr}\rangle \in [0.973, 0.978]$ and
$\langle B_k^{\rm FGN}\rangle \in [0.958, 0.983]$.

At the level of individual $({\rm text}, k)$ pairs
($16 \times 20 = 320$ pairs):
\begin{itemize}
  \item $B_k^{\rm orig} > B_k^{\rm surr}$ in $\mathbf{100\%}$ of pairs.
  \item $B_k^{\rm orig} > B_k^{\rm FGN}$ in $\mathbf{100\%}$ of pairs.
  \item $|B_k^{\rm FGN}/B_k^{\rm surr} - 1| < 0.05$ in
        $\mathbf{95.6\%}$ of pairs.
\end{itemize}

The appropriate summary statistic for the magnitude of the effect
is the \emph{per-text mean ratio}, computed by averaging
$B_k^{\rm orig}/B_k^{\rm surr}$ over the 20 components for each
text and then averaging over the 16 texts:
\begin{equation}
  \left\langle \frac{B_k^{\rm orig}}{B_k^{\rm surr}}
  \right\rangle_{\rm texts}
  \;=\; 1.29 \;\pm\; 0.03,
  \qquad t = 8.7,\quad p < 10^{-6},
  \label{eq:ratio_corpus}
\end{equation}
where $\pm$ denotes the standard error of the mean over 16 texts.
The original texts are thus on average $\sim 30\%$ more bursty
than the geometric null. The per-text values range from $1.17$
(\emph{Pride and Prejudice}) to $1.39$ (\emph{War and Peace}) for
fifteen of the sixteen texts, with \emph{Principia Mathematica} as
an outlier at $1.73$; the spread across texts (sd $= 0.13$) is
itself a signature of how differently topical structure is organised
in different works.
The analogous ratio for the FGN surrogate is
$\langle B_k^{\rm orig}/B_k^{\rm FGN}\rangle = 1.29 \pm 0.03$,
indistinguishable from the word-shuffled value.

The two null models satisfy
$\langle B_k^{\rm FGN}/B_k^{\rm surr}\rangle = 1.001 \pm 0.001$
(range over texts $[0.996, 1.005]$; $t = 1.1$, $p = 0.28$):
the FGN surrogate and the word-shuffled null are statistically
indistinguishable at the corpus level
(Section~\ref{sec:corpus_diffs}).
```

### B3. l. 1544–1560 (robustness across q)
```latex
The full ordering $B_k^{\rm orig} > B_k^{\rm surr}$ and
$B_k^{\rm orig} > B_k^{\rm FGN}$ is satisfied in $100\%$
of pairs for all $q \in [0.60, 0.95]$, and in $98.1\%$ of pairs at the
extreme $q = 0.99$.
The null-model indistinguishability criterion
$|B_k^{\rm FGN}/B_k^{\rm surr} - 1| < 0.05$ is met by $\geq 99\%$ of
pairs for $q \leq 0.90$, by $96\%$ at $q = 0.95$, and decreases to
$73\%$ at $q = 0.99$.
This degradation at the extreme threshold is expected: with
$p = 0.01$ and $M \approx 80{,}000$ filtered tokens, there are
on average only $\sim 800$ events per series, giving an IET
estimator with relative error $\sim 1/\sqrt{800} \approx 3.5\%$
--- comparable to the magnitude of $B^{\rm FGN} - B^{\rm surr}$
at this threshold, and larger still for the shortest texts
($M < 30{,}000$).
For $q = 0.95$ ($n_{\rm events} \approx 4{,}000$, relative error
$\sim 1.6\%$), the estimator is well within the regime where the
null-model comparison is reliable.
```

### B4. l. 1598–1606 (distribution of ratios, panel B)
```latex
Panel~B isolates the ratio $B^{\rm FGN}/B^{\rm surr}$, which
is tightly concentrated around 1 (mean $1.0008$, s.e.\ $0.0012$,
range $[0.91, 1.09]$).
A one-sample $t$-test against ratio\,=\,1 gives $t = 0.63$,
$p = 0.53$: the two null models are statistically indistinguishable,
and the distribution is symmetric with no indication of a
directional bias.
```

### B5. l. 1897–1906 (corpus ACF, fractions)
```latex
At lag $\ell = 1$: $100\%$ of original-text pairs are significant,
$10.9\%$ of FGN pairs, and $4.7\%$ of shuffled pairs.
The FGN figure exceeds the expected false-positive rate
of $5\%$, but the significant cases are concentrated on PC1
(56\% of the PC1 pairs, against 8\% for $k \geq 4$) --- the component
most affected by the geometric artefact of rare transliterated proper
nouns in the GloVe embedding space (Section~\ref{sec:filtering_results}).
From lag $\ell = 2$ onwards the FGN fraction lies between $2.5\%$ and
$7\%$, at the false-positive level. The effect is in any case tiny
relative to the separation of the original projections from both
controls.
```

---

## Notes for the co-author

1. Every number above is produced by the released code from the tokenised texts with fixed
   seeds, and is identical on two independent machines.
2. The FGN surrogate in the previous version was built from a differently tokenised stream
   (regex `\w+`); the DFA exponents of the corpus table shift by up to 0.03 (Ulysses).
3. In the previous ACF batch the FGN of every text was tuned to α = 0.769 by a coding slip;
   the FGN autocorrelation is negligible either way, so the ACF conclusions are unchanged.
4. The previous FGN/shuffled ratio (1.0035, p = 0.011) was "significantly non-unity"; with the
   consistent pipeline it is 1.0008, p = 0.53. The text now says the two nulls are
   indistinguishable, which is the cleaner statement.
5. α₀ is determined only to ±0.01 by the bisection tolerance and is reported with two decimals.
