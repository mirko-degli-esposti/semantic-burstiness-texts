# Physica A — what the manuscript still needs

Elsevier's "Your Paper Your Way" means the *first* submission does not have to be in
the `elsarticle` template: the current `article` class, the inline `thebibliography`
and the author-year citations are acceptable for review, and reformatting is only
required after acceptance. Confirm on the journal's Guide for Authors page before
submitting. So the work below is about content and completeness, not about LaTeX
templates.

## Required at submission
| item | status | where |
|---|---|---|
| Abstract within the journal limit (currently 285 words) | draft ready, ~215 words | `physicaA_frontmatter.tex` §2 |
| Highlights, 3-5 bullets, <= 85 characters each | drafted | `physicaA_frontmatter.tex` §1 (submit as a separate file) |
| Keywords | already present | after the abstract |
| CRediT authorship contribution statement | drafted, needs the real division of work | §3 |
| Declaration of competing interest | drafted | §3 |
| Declaration of generative AI use | drafted; delete if not applicable | §3 |
| Data availability statement | drafted | §3 |
| Acknowledgements (funding, computing) | to write | §3 |
| Corresponding author, full postal addresses, ORCID | to add to the title block | title page |
| Suggested referees (usually 3) | to decide | submission system |
| Cover letter | to write | submission system |

## Housekeeping in the .tex
- `\date{Draft --- \today}` -> remove or replace with the submission date.
- `\TODO` / `\NOTE` macros and the `totcount` counter: strip before submission
  (`grep -n 'TODO{\|NOTE{' paper3_main_v9.tex`).
- The header comment already says "Target: Physica A" — the README and the BibTeX
  citation entry in the repository still say PNAS and must be updated.
- Title: the file header and `\title` disagree ("Topical Burstiness in Literary
  Texts: A Semantic Trajectory Approach" vs "Semantic burstiness across principal
  directions of textual variation"). Pick one.

## Figures: 30 is a lot even for Physica A
Current inventory:
- 20 per-text figures: 4 showcase texts x 5 (`02` spectra, `03` IET, `04` burstiness,
  `06` quantile sweep, `07` semantic poles)
- 6 corpus figures (`fig1`-`fig3`, `acf_corpus_*`)
- 4 ACF/DFA figures for *Great Expectations*

Proposal: keep one complete per-text series in the main text (*Great Expectations*,
already the text used for the ACF and DFA sections), move the other three texts'
15 figures to an appendix. Main text: 15 figures; appendix: 15. The per-text
sections stay where they are, with their figures referenced in the appendix.

## Reference style
Physica A publishes numbered references. The manuscript uses author-year
(`apalike` + `\citep`). Switching later is mechanical: `elsarticle` loads `natbib`,
so `\citep` keeps working and only `\bibliographystyle` changes — but the current
bibliography is a hand-written `thebibliography`, so a real `.bib` file would have
to be built first. Worth doing at some point regardless, for reuse across papers.
