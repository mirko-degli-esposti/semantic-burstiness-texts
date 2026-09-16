"""Word vectors and embedding trajectory.

Vectors: GloVe 6B 300d (Pennington, Socher & Manning 2014), file glove.6B.300d.txt from
https://nlp.stanford.edu/data/glove.6B.zip.  The file is fingerprinted on first load;
the gensim downloader model 'glove-wiki-gigaword-300' used in the Colab notebook is the
same data repackaged, so vocabulary and vectors are identical.

Reference number: M_filtered in results/reference/corpus_burstiness.csv.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

VECTORS_PATH = Path("data/vectors/glove.6B.300d.txt")
VECTORS_SHA256 = "91125602f730fea7ca768736c6f442e668b49db095682bf2aad375db061c21ed"


def sha256(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_vectors(path: str | Path = VECTORS_PATH, verify: bool = True):
    """Return gensim KeyedVectors. First call converts the .txt and caches a .kv next to it."""
    from gensim.models import KeyedVectors

    path = Path(path)
    cache = path.with_suffix(".kv")
    if cache.exists():
        return KeyedVectors.load(str(cache), mmap="r")
    if not path.exists():
        raise FileNotFoundError(f"{path} not found; download glove.6B.zip from Stanford NLP")
    if verify:
        digest = sha256(path)
        if digest != VECTORS_SHA256:
            raise RuntimeError(f"vectors fingerprint mismatch:\n  got      {digest}\n  expected {VECTORS_SHA256}")
    wv = KeyedVectors.load_word2vec_format(str(path), binary=False, no_header=True)
    wv.save(str(cache))
    return wv


def build_trajectory(tokens: list[str], wv) -> tuple[np.ndarray, np.ndarray]:
    """Map tokens to vectors, skipping out-of-vocabulary tokens.

    Returns (vecs, pos): vecs is (M, 300) float32 in text order, pos[i] is the index in
    `tokens` of the i-th kept token.  Identical to the notebook's build_trajectory().
    """
    key = wv.key_to_index
    pos = np.fromiter((i for i, t in enumerate(tokens) if t in key), dtype=np.int32)
    idx = np.fromiter((key[tokens[i]] for i in pos), dtype=np.int64, count=len(pos))
    vecs = np.asarray(wv.vectors[idx], dtype=np.float32)
    return vecs, pos
