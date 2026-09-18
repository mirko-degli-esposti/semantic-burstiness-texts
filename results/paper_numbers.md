# Numbers for the paper (regenerated)

## 1. Four showcase texts (Table tab:single_text_summary and per-text sections)

| text | N | M | OOV (old) | alpha (old) | alpha0 (old) | r(lambda,B), P (old) | rho, P | B2 (old) | LaTeX |
|---|---|---|---|---|---|---|---|---|---|
| War and Peace | 564,788 | 235,933 | 1.6% (1.6%) | 0.721 (0.721) | 0.76 (0.76) | 0.702, P=0.0055 (0.702, 0.0006) | 0.850, P=0.0000 | 1.855 (1.855) | 0.702$^{**}$ |
| Origin of Species | 151,179 | 58,913 | 0.4% (0.4%) | 0.771 (0.771) | 0.80 (0.8) | 0.295, P=0.1694 (0.295, 0.207) | 0.460, P=0.0421 | 1.888 (1.888) | 0.295 |
| Great Expectations | 188,925 | 64,410 | 1.3% (1.3%) | 0.689 (0.689) | 0.74 (0.74) | 0.511, P=0.0136 (0.511, 0.021) | 0.579, P=0.0085 | 1.209 (1.209) | 0.511$^{*}$ |
| Ulysses | 264,165 | 101,489 | 0.7% (0.7%) | 0.763 (0.763) | 0.80 (0.8) | 0.571, P=0.0406 (0.571, 0.009) | 0.817, P=0.0000 | 1.495 (1.495) | 0.571$^{*}$ |

### War and Peace
- EVR PC1 6.98% (old 6.98), PC2 4.21% (old 4.21), PC3 2.97%, first ten 27.2% (old 27.2)
- q=0.95: B1=1.643, B2=1.855, B3=2.045; largest at PC3 (B=2.045); null at that k: surr 0.976, FGN 0.974
- mean over k=1..20: B_orig 1.358 (old Bbar 1.36), B_surr 0.974, B_FGN 0.973; null range surr [0.970,0.977], FGN [0.959,0.996]
- ordering B_orig > B_FGN and > B_surr at q=0.95: 20/20
- quantile sweep, full ordering: q=0.6: 20/20, q=0.7: 20/20, q=0.8: 20/20, q=0.9: 20/20, q=0.95: 20/20, q=0.99: 20/20

### Origin of Species
- EVR PC1 6.61% (old 6.61), PC2 3.58% (old 3.58), PC3 2.99%, first ten 26.4% (old 26.4)
- q=0.95: B1=1.255, B2=1.888, B3=1.727; largest at PC6 (B=1.900); null at that k: surr 0.967, FGN 0.975
- mean over k=1..20: B_orig 1.350 (old Bbar 1.35), B_surr 0.974, B_FGN 0.978; null range surr [0.967,0.982], FGN [0.945,1.012]
- ordering B_orig > B_FGN and > B_surr at q=0.95: 20/20
- quantile sweep, full ordering: q=0.6: 20/20, q=0.7: 20/20, q=0.8: 20/20, q=0.9: 20/20, q=0.95: 20/20, q=0.99: 20/20

### Great Expectations
- EVR PC1 6.54% (old 6.54), PC2 4.34% (old 4.34), PC3 3.00%, first ten 27.2% (old 27.2)
- q=0.95: B1=1.228, B2=1.209, B3=1.244; largest at PC3 (B=1.244); null at that k: surr 0.982, FGN 1.002
- mean over k=1..20: B_orig 1.176 (old Bbar 1.18), B_surr 0.975, B_FGN 0.977; null range surr [0.965,0.982], FGN [0.949,1.009]
- ordering B_orig > B_FGN and > B_surr at q=0.95: 20/20
- quantile sweep, full ordering: q=0.6: 20/20, q=0.7: 20/20, q=0.8: 20/20, q=0.9: 20/20, q=0.95: 20/20, q=0.99: 20/20

### Ulysses
- EVR PC1 6.76% (old None), PC2 3.43% (old None), PC3 3.06%, first ten 25.0% (old 25.0)
- q=0.95: B1=1.286, B2=1.495, B3=1.329; largest at PC2 (B=1.495); null at that k: surr 0.976, FGN 0.969
- mean over k=1..20: B_orig 1.234 (old Bbar 1.23), B_surr 0.976, B_FGN 0.976; null range surr [0.970,0.981], FGN [0.936,0.997]
- ordering B_orig > B_FGN and > B_surr at q=0.95: 20/20
- quantile sweep, full ordering: q=0.6: 20/20, q=0.7: 20/20, q=0.8: 20/20, q=0.9: 20/20, q=0.95: 20/20, q=0.99: 20/20

## 2. Corpus table (tab:corpus) — 16 texts, from corpus_burstiness.csv

| file | N | M | alpha | alpha0 |
|---|---|---|---|---|
| THE_ANALYSIS_OF_MIND.txt | 88,342 | 30,449 | 0.743 | 0.76 |
| darwin_beagle.txt | 206,728 | 84,931 | 0.629 | 0.67 |
| darwin_origin.txt | 151,179 | 58,913 | 0.770 | 0.80 |
| davidcopperfield.txt | 363,557 | 134,409 | 0.727 | 0.78 |
| doriangray.txt | 55,619 | 16,776 | 0.845 | 0.87 |
| eng_missisipi.txt | 145,924 | 52,741 | 0.774 | 0.83 |
| eng_moby.txt | 215,652 | 82,773 | 0.694 | 0.73 |
| eng_pride.txt | 122,226 | 42,364 | 0.642 | 0.67 |
| eng_quixote.txt | 403,152 | 147,279 | 0.711 | 0.76 |
| eng_sawyer.txt | 71,102 | 22,085 | 0.788 | 0.80 |
| eng_ulysses.txt | 264,165 | 101,489 | 0.763 | 0.80 |
| eng_wrnpc.txt | 564,788 | 235,933 | 0.721 | 0.76 |
| great_expectations_cut_clean.txt | 188,925 | 64,410 | 0.689 | 0.73 |
| kipling_junglebook.txt | 151,161 | 49,522 | 0.775 | 0.83 |
| olivertwist_cut_clean.txt | 161,529 | 59,729 | 0.711 | 0.76 |
| principia_newton.txt | 112,225 | 26,347 | 0.815 | 0.85 |

N range [55,619, 564,788]; M range [16,776, 235,933] (old: 27,000–565,000 and 12,000–321,000, with Alice); alpha range [0.63, 0.85] (old [0.61, 0.85])

## 3. Corpus-level burstiness (sec. Component-resolved ... corpus-wide, Robustness, Distribution)

- <B_k^orig>_texts over k: range [1.16, 1.54], mean 1.26 (old [1.12,1.37], 1.22)
- <B_k^surr>_texts: [0.973, 0.978] (old [0.972,0.978]); <B_k^FGN>_texts: [0.958, 0.983] (old [0.970,0.992])
- pairs (text,k) at q=0.95: 320; B_orig > B_surr in 100.0% (old 100%); B_orig > B_FGN in 100.0% (old 99.4%); |B_FGN/B_surr - 1| < 0.05 in 95.6% (old 95.9%)
- ratio orig/surr: mean over pairs 1.2945 ± s.e. 0.0124 (sd 0.221), range [1.05, 3.85]; per-text means: mean 1.295, sd 0.135, range [1.17, 1.73]; t-test vs 1: t=23.80, p=1.05e-72   (old 1.248±0.011, texts [1.14,1.30] sd 0.044)
- ratio orig/FGN: mean over pairs 1.2943 ± s.e. 0.0127 (sd 0.226), range [1.03, 3.94]; per-text means: mean 1.294, sd 0.137, range [1.17, 1.74]; t-test vs 1: t=23.26, p=1.16e-70   (old 1.244±0.010)
- ratio FGN/surr: mean over pairs 1.0008 ± s.e. 0.0012 (sd 0.022), range [0.91, 1.09]; per-text means: mean 1.001, sd 0.003, range [1.00, 1.01]; t-test vs 1: t=0.63, p=0.527   (old 1.0035±0.0012, range [0.94,1.11], t=2.88 p=0.011)

Per-text mean ratios at q=0.95 (definition of eq. ratio_corpus):

| file | orig/surr | orig/FGN | FGN/surr |
|---|---|---|---|
| eng_pride.txt | 1.172 | 1.172 | 1.0003 |
| davidcopperfield.txt | 1.203 | 1.203 | 1.0008 |
| great_expectations_cut_clean.txt | 1.207 | 1.204 | 1.0023 |
| doriangray.txt | 1.209 | 1.209 | 1.0014 |
| olivertwist_cut_clean.txt | 1.212 | 1.209 | 1.0023 |
| eng_sawyer.txt | 1.219 | 1.223 | 0.9975 |
| eng_quixote.txt | 1.219 | 1.217 | 1.0019 |
| eng_moby.txt | 1.264 | 1.268 | 0.9964 |
| eng_ulysses.txt | 1.265 | 1.264 | 1.0008 |
| eng_missisipi.txt | 1.278 | 1.272 | 1.0053 |
| kipling_junglebook.txt | 1.280 | 1.281 | 0.9995 |
| THE_ANALYSIS_OF_MIND.txt | 1.335 | 1.329 | 1.0051 |
| darwin_beagle.txt | 1.336 | 1.339 | 0.9975 |
| darwin_origin.txt | 1.387 | 1.381 | 1.0046 |
| eng_wrnpc.txt | 1.394 | 1.396 | 0.9990 |
| principia_newton.txt | 1.732 | 1.741 | 0.9978 |
- orig/surr: mean over 16 texts 1.2945 ± s.e. 0.0337 (sd 0.1348), range [1.172, 1.732], t=8.74, p=2.8e-07
- orig/FGN: mean over 16 texts 1.2943 ± s.e. 0.0341 (sd 0.1365), range [1.172, 1.741], t=8.62, p=3.4e-07
- FGN/surr: mean over 16 texts 1.0008 ± s.e. 0.0007 (sd 0.0028), range [0.996, 1.005], t=1.13, p=0.28

By q (fraction of pairs):

| q | orig>surr | orig>FGN | full ordering | \|FGN/surr-1\|<0.05 |
|---|---|---|---|---|
| 0.6 | 100.0% | 100.0% | 100.0% | 100.0% |
| 0.7 | 100.0% | 100.0% | 100.0% | 100.0% |
| 0.8 | 100.0% | 100.0% | 100.0% | 100.0% |
| 0.9 | 100.0% | 100.0% | 100.0% | 99.4% |
| 0.95 | 100.0% | 100.0% | 100.0% | 95.6% |
| 0.99 | 99.4% | 98.1% | 98.1% | 73.4% |

(old: orig>FGN >= 99.4% for q<=0.95 and 98.7% at 0.99; |FGN/surr-1|<0.05 >98% for q<=0.90, 85% at 0.99)

## 4. ACF (sec. Empirical results, Corpus-level ACF results)

### Great Expectations (alpha=0.689, old 0.688; M=64,410; ci95=0.008)
- rho_k(1) orig range [0.049, 0.208] (old [0.042,0.179]); FGN: all < 0.025? True, max |rho_FGN(1)| 0.007, inside band 20/20 (old 19/20); rho_1^FGN(1)=0.004 (old 0.023)

Table tab:acf_summary (k=1..10):

| k | rho(1) orig | rho(1) FGN | rho(100) orig | rho(100) FGN |
|---|---|---|---|---|
| 1 | 0.060 | 0.004 | 0.008 | 0.004 |
| 2 | 0.208 | 0.007 | 0.015 | 0.004 |
| 3 | 0.136 | -0.002 | 0.018 | 0.004 |
| 4 | 0.123 | -0.003 | 0.008 | -0.003 |
| 5 | 0.086 | -0.002 | 0.004 | -0.004 |
| 6 | 0.121 | 0.004 | 0.005 | -0.001 |
| 7 | 0.127 | 0.002 | 0.007 | -0.003 |
| 8 | 0.103 | 0.001 | 0.004 | 0.003 |
| 9 | 0.082 | -0.002 | 0.008 | 0.001 |
| 10 | 0.083 | 0.004 | 0.003 | 0.003 |

k=11..20: max |rho_FGN(1)| = 0.007 (old 'all < 0.007'); bold = |rho| > ci95 = 0.008

### Corpus (16 texts, 320 (text,k) pairs)
- lag 1: rho_orig 0.100 ± 0.045; rho_FGN 0.002 ± 0.005; rho_surr 0.000 ± 0.004
- lag 10: rho_orig 0.032 ± 0.021; rho_FGN 0.000 ± 0.004; rho_surr 0.001 ± 0.004
- lag 100: rho_orig 0.011 ± 0.011; rho_FGN -0.000 ± 0.005; rho_surr 0.000 ± 0.005
  (old: orig 0.096±0.044 / 0.026±0.017 / 0.010±0.009; FGN(1) 0.003±0.009; surr(1) 0.000±0.004)

| lag | orig sig | FGN sig | surr sig |
|---|---|---|---|
| 1 | 100.0% | 10.9% | 4.7% |
| 2 | 100.0% | 6.9% | 5.6% |
| 5 | 98.4% | 7.2% | 5.6% |
| 10 | 93.4% | 2.5% | 6.6% |
| 20 | 86.2% | 6.9% | 3.4% |
| 50 | 72.8% | 3.8% | 5.6% |
| 100 | 56.9% | 6.6% | 5.0% |
| 200 | 40.3% | 5.3% | 4.1% |
| 300 | 35.0% | 6.2% | 6.2% |

'original significant and FGN not' by lag: 1: 89.1%, 2: 93.1%, 5: 91.6%, 10: 90.9%, 20: 80.9%, 50: 70.0%, 100: 52.8%, 200: 37.5%, 300: 32.2% (old: peak 89.7% at lag 2, >56% up to 100)

(old lag 1: 100% / 17.2% / 4.7%; lag 2: 89.7% orig; 'above 56% up to lag ...')
- rho_k(1) orig range [0.026, 0.264] (old [0.020,0.282]); FGN range [-0.014, 0.023] (old [-0.015,0.058]); t-test FGN rho(1) vs 0: t=5.05, p=7.53e-07 (old t=5.83); orig-null gap 0.099 (old 0.093)
- fraction of FGN pairs with rho(1) > 0.007: 13.1%

## 5. DFA of projections (sec. DFA of projected series)

### Great Expectations, table tab:dfa_proj

| k | orig | FGN | surr |
|---|---|---|---|
| 1 | 0.605 | 0.511 | 0.501 |
| 2 | 0.681 | 0.500 | 0.491 |
| 3 | 0.693 | 0.518 | 0.495 |
| 4 | 0.634 | 0.514 | 0.499 |
| 5 | 0.642 | 0.486 | 0.496 |
| 6 | 0.633 | 0.515 | 0.501 |
| 7 | 0.647 | 0.504 | 0.498 |
| 8 | 0.633 | 0.469 | 0.497 |
| 9 | 0.643 | 0.482 | 0.494 |
| 10 | 0.630 | 0.482 | 0.503 |
| 11 | 0.575 | 0.506 | 0.500 |
| 12 | 0.642 | 0.493 | 0.502 |
| 13 | 0.564 | 0.512 | 0.500 |
| 14 | 0.595 | 0.484 | 0.497 |
| 15 | 0.645 | 0.486 | 0.497 |
| 16 | 0.579 | 0.505 | 0.494 |
| 17 | 0.586 | 0.511 | 0.493 |
| 18 | 0.617 | 0.515 | 0.507 |
| 19 | 0.595 | 0.489 | 0.505 |
| 20 | 0.622 | 0.495 | 0.502 |

means ± sd: orig 0.623 ± 0.034 (old 0.637±0.032); FGN 0.499 ± 0.014 (old 0.502±0.015); surr 0.499 ± 0.004 (old 0.499±0.002)
- orig > 0.5: 20/20; |FGN-0.5|<0.05: 20/20; orig range [0.564, 0.693] (old [0.575,0.698]); max orig at PC3=0.693, min at PC13=0.564

### Corpus
- mean ± sd over 320 pairs: orig 0.666 ± 0.054; FGN 0.504 ± 0.019; surr 0.499 ± 0.004; orig>0.5 in 100.0%, |FGN-0.5|<0.05 in 97.5%

## 6. Verification: does the frequency filter preserve rank-level scaling?

Calibration column: `a(rank,unfilt)` is `projection_alpha` applied to the
unfiltered rank sequence, to be compared with `alpha_text` computed by the
pipeline. If the two disagree, the remaining columns are not comparable.

| text | M | M_FGN | M_FGN/M | a(rank,unfilt) | alpha_text | a(rank orig,filt) | a(rank FGN,filt) |
|---|---|---|---|---|---|---|---|
| War and Peace | 235,933 | 235,933 | 1.0000 | 0.693 | 0.721 | 0.674 | 0.633 |
| Origin of Species | 58,913 | 58,913 | 1.0000 | 0.726 | 0.771 | 0.694 | 0.645 |
| Great Expectations | 64,410 | 64,410 | 1.0000 | 0.672 | 0.689 | 0.609 | 0.567 |
| Ulysses | 101,489 | 101,489 | 1.0000 | 0.805 | 0.763 | 0.772 | 0.629 |
  - multiset identical to original: True

### Multiset identity vs the high-frequency cutoff R

| text | unfiltered | R=100 | R=150 | R=200 |
|---|---|---|---|---|
| War and Peace | True | True (239,725/239,725) | True (210,240/210,240) | True (188,835/188,835) |
| Origin of Species | True | True (59,173/59,173) | True (51,075/51,075) | True (45,424/45,424) |
| Great Expectations | True | True (65,285/65,285) | True (54,085/54,085) | True (46,309/46,309) |
| Ulysses | True | True (102,234/102,234) | True (91,229/91,229) | True (83,362/83,362) |
- PCA components retained: 300
- eigenvalues 300, proj (101489, 20), attrs ['K', 'components', 'eigenvalues', 'explained_variance_ratio', 'mean', 'proj']

### Burstiness beyond the retained K=20 (PCA refitted with K=50)

| text | cum.var 20 | 50 | 100 | mean B 1..20 | 21..50 | min B 21..50 | all > geom | refit err |
|---|---|---|---|---|---|---|---|---|
| War and Peace | 37.8% | 57.1% | 76.4% | 1.358 | 1.138 | 1.085 | True | 9.5e-07 |
| Origin of Species | 38.1% | 59.0% | 78.6% | 1.350 | 1.188 | 1.095 | True | 9.5e-07 |
| Great Expectations | 38.5% | 59.0% | 78.7% | 1.176 | 1.112 | 1.041 | True | 9.5e-07 |
| Ulysses | 35.0% | 53.2% | 72.7% | 1.234 | 1.120 | 1.041 | True | 9.5e-07 |
