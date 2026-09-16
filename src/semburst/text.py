"""Text loading, tokenisation and frequency filtering.

Reproduces exactly the preprocessing of the Colab notebook (cell "Load, tokenise, filter"
and the corpus-batch cells): Gutenberg boilerplate stripping, NLTK word_tokenize on the
lower-cased text, alphabetic tokens only, removal of the top-R word types and of types
with frequency < min_freq.  Reference numbers: N_all, N_filt in results/reference/corpus_burstiness.csv.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .config import DEFAULT, Params

_GUTENBERG_START = "*** START OF"
_GUTENBERG_END = "*** END OF"


def _ensure_nltk() -> None:
    import nltk
    for res in ("punkt", "punkt_tab"):
        try:
            nltk.data.find(f"tokenizers/{res}")
        except LookupError:
            nltk.download(res, quiet=True)


def strip_gutenberg(raw: str) -> str:
    """Remove Project Gutenberg header/footer if the standard markers are present."""
    i = raw.find(_GUTENBERG_START)
    if i != -1:
        raw = raw[raw.find("\n", i) + 1:]
    j = raw.find(_GUTENBERG_END)
    if j != -1:
        raw = raw[:j]
    return raw


def load_raw(path: str | Path) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return strip_gutenberg(f.read())


def tokenise(raw: str) -> list[str]:
    """Lower-case, NLTK word_tokenize, keep purely alphabetic tokens."""
    _ensure_nltk()
    from nltk.tokenize import word_tokenize
    return [t for t in word_tokenize(raw.lower()) if t.isalpha()]


@dataclass
class TokenisedText:
    name: str
    tokens_all: list[str]        # every alphabetic token, in order
    tokens_filtered: list[str]   # after frequency filtering, in order
    freq: Counter                # type frequencies on tokens_all
    stopset: set                 # the R most frequent types (removed)

    @property
    def N_all(self) -> int:
        return len(self.tokens_all)

    @property
    def N_filt(self) -> int:
        return len(self.tokens_filtered)


def frequency_filter(tokens_all: list[str], params: Params = DEFAULT) -> tuple[list[str], Counter, set]:
    """Remove the top-R types and rare types (freq < min_freq); order is preserved."""
    freq = Counter(tokens_all)
    stopset = set(w for w, _ in freq.most_common(params.max_freq_rank))
    kept = [t for t in tokens_all if t not in stopset and freq[t] >= params.min_freq]
    return kept, freq, stopset


def load_text(path: str | Path, params: Params = DEFAULT) -> TokenisedText:
    path = Path(path)
    tokens_all = tokenise(load_raw(path))
    tokens_filtered, freq, stopset = frequency_filter(tokens_all, params)
    return TokenisedText(path.name, tokens_all, tokens_filtered, freq, stopset)
