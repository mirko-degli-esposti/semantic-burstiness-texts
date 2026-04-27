# Semantic Burstiness in Literary Texts

Code and data for:

> M. Degli Esposti, M. A. Montemurro  
> **Semantic burstiness reveals the topical origin of long-range correlations in texts**  
> *Proceedings of the National Academy of Sciences*, 2026 (submitted)

## Overview

This repository contains the full analysis pipeline for the paper.
We map literary texts to word embedding trajectories (GloVe, 300d),
apply PCA to identify dominant semantic directions, and measure
**burstiness** of threshold-crossing events along each direction.
Comparing original texts against two null models — word-shuffled
surrogates and FGN surrogates (Degli Esposti & Montemurro, *Physica A*, 2025) —
we show that semantic burstiness is a universal property of literary texts,
absent from both nulls despite the FGN matching the DFA scaling exponent
of the original.

**Central result:**  
$B_k^{\rm orig} \gg B_k^{\rm FGN} \approx B_k^{\rm shuf}$  
across 16 texts and 20 PCA components, robust for all quantile
thresholds $q \in [0.60, 0.99]$.

---

## Repository structure

```
semantic-burstiness-texts/
│
├── notebooks/
│   └── word2vec_pca_trajectory_v6.ipynb   # main analysis notebook (Colab)
│
├── paper/
│   └── paper3_pnas_v1.tex                 # LaTeX source
│
├── figures/                               # all figures in the paper
│
├── data/
│   └── corpus/                            # 16 Project Gutenberg texts
│       └── README_corpus.txt              # titles, authors, PG IDs
│
└── results/
    ├── corpus_burstiness.csv              # burstiness spectrum, all texts
    ├── corpus_acf.csv                     # ACF results, all texts
    └── corpus_block_entropy.csv           # block entropy, all texts
```

---

## Requirements

```
python >= 3.9
numpy
scipy
scikit-learn
matplotlib
pandas
gensim          # GloVe loading
nltk            # tokenisation
```

For GPU acceleration (corpus batch runs):
```
cupy-cuda12x
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Quickstart

The notebook is designed to run on **Google Colab** with a T4/L4 GPU.

1. Upload `word2vec_pca_trajectory_v6.ipynb` to Colab
2. Mount Google Drive and set `BASE_PATH` to your Drive folder
3. Download GloVe vectors (`glove.6B.300d`) from  
   https://nlp.stanford.edu/projects/glove/  
   and place them at `BASE_PATH/glove.6B.300d.txt`
4. Place corpus `.txt` files at `BASE_PATH/corpus/`
5. Run cells sequentially — each section is self-contained

The notebook produces all figures in the paper plus the three
corpus-level CSV files under `results/`.

---

## Corpus

16 English literary texts from Project Gutenberg (public domain).  
Full list with token counts, DFA exponents, and Gutenberg IDs
in `data/corpus/README_corpus.txt`.

---

## FGN surrogate

The FGN surrogate construction follows:

> M. Degli Esposti, M. A. Montemurro  
> *A Zipf-preserving, long-range correlated surrogate for written language
> and other symbolic sequences*  
> Physica A: Statistical Mechanics and its Applications, 2025

Code for the surrogate is embedded in the notebook (Section 2).

---

## Notebook structure

| Section | Content |
|---------|---------|
| 0 | Setup, Google Drive mount, surrogate functions |
| 1 | Imports and global parameters |
| 2 | Parameters |
| 3 | Load and tokenise text |
| 4 | Load GloVe vectors |
| 5 | Build embedding trajectory |
| 6 | PCA |
| 7 | Helper functions (burstiness, IET) |
| 8 | Filtering diagnostic |
| 9 | Word-shuffled null model |
| 10 | FGN surrogate |
| 10c–h | Single-text figures (6-panel, IET, burstiness spectrum) |
| 11 | Semantic interpretation of PC directions |
| 12 | ACF of projections — single text |
| 13 | DFA of projections — single text |
| 13b | **Fig. 1**: semantic trajectory (centroid windows) |
| 14 | Block entropy — single text |
| 15 | Corpus batch: burstiness spectrum |
| 16 | Corpus batch: ACF |
| 17 | Corpus batch: block entropy |
| 18 | Additional analyses (diagnostic) |

---

## Citation

```bibtex
@article{DegliEspostiMontemurro2026,
  author  = {Degli Esposti, Mirko and Montemurro, Marcelo A.},
  title   = {Semantic burstiness reveals the topical origin of
             long-range correlations in texts},
  journal = {Proceedings of the National Academy of Sciences},
  year    = {2026},
  note    = {submitted}
}
```

---

## License

Code: [MIT License](LICENSE).  
Texts: public domain (Project Gutenberg).  
GloVe vectors: see [Stanford NLP licence](https://nlp.stanford.edu/projects/glove/).
