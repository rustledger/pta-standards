"""Compare two sides' errors by line and count.

Two sides AGREE on an input when they report errors on the same lines, the
same number of errors per line. Messages and codes are not compared: two
implementations never word an error alike, and where an error lands and how
many there are is what a user sees first.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import NamedTuple

from .model import Error


class Divergence(NamedTuple):
    """One line the sides disagree on, and how many errors each puts there."""

    line: int
    oracle: int
    impl: int


def line_counts(errors: Iterable[Error]) -> Counter[int]:
    return Counter(e.line for e in errors)


def _line_order(line: int) -> tuple[bool, int]:
    # Line 0 (file-level) sorts after every real line.
    return (line == 0, line)


def divergences(oracle: Iterable[Error], impl: Iterable[Error]) -> list[Divergence]:
    """Every line the two sides disagree on, in line order, line 0 last."""
    a, b = line_counts(oracle), line_counts(impl)
    return [
        Divergence(line, a.get(line, 0), b.get(line, 0))
        for line in sorted(set(a) | set(b), key=_line_order)
        if a.get(line, 0) != b.get(line, 0)
    ]


def first_divergence(oracle: Iterable[Error], impl: Iterable[Error]) -> Divergence | None:
    """The first line the sides disagree on, or None when they agree.

    The first divergence is the one to read: later ones are usually its
    cascade (a recovery that resynchronizes differently)."""
    found = divergences(oracle, impl)
    return found[0] if found else None


def agree(oracle: Iterable[Error], impl: Iterable[Error]) -> bool:
    return line_counts(oracle) == line_counts(impl)
