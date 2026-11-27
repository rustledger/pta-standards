"""A key-preserving minimizer.

Shrinks a mismatching input by lines, then tokens, then characters, keeping a
step only if the smaller input STILL mismatches with the SAME category key.
Preserving the key (not just "still mismatches") is what keeps the result an
example of the category it was taken from: a plain mismatch-preserving
reducer drifts to whichever bug is easiest to hit.

The search is delta debugging's complement pass: at each granularity, try
removing each of `n` chunks; on success keep the smaller input and coarsen,
on failure refine, down to single units. All candidates of one round are
judged in one batch (the oracle and implementation are much cheaper per
input in batches), and the first success in candidate order wins, so the
result is deterministic.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

#: `texts -> keys`, `None` where a text matches (or the oracle crashed).
KeysOf = Callable[[Sequence[str]], Sequence[str | None]]
#: `(text, level) -> units` whose concatenation is `text`.
UnitsOf = Callable[[str, str], list[str]]

LEVELS = ("lines", "tokens", "chars")


@dataclass
class Minimized:
    text: str
    key: str
    evaluations: int
    #: False when the budget ran out before a fixed point.
    complete: bool = True


class _Budget(Exception):
    pass


def minimize(
    text: str,
    key: str,
    keys_of: KeysOf,
    units_of: UnitsOf,
    *,
    levels: Sequence[str] = LEVELS,
    max_evaluations: int = 5000,
    max_passes: int = 4,
) -> Minimized:
    """The smallest input this search finds that has category `key`.

    `text` should itself have that key (it is returned unchanged otherwise).
    Passes over `levels` repeat until one changes nothing, at most
    `max_passes` times; at most `max_evaluations` candidates are judged.
    """
    cache: dict[str, str | None] = {}
    count = 0
    # The smallest input seen with the key, so a budget that runs out in the
    # middle of a level still keeps that level's progress.
    best = text

    def test(cands: list[str]) -> list[bool]:
        nonlocal count, best
        todo = [c for c in dict.fromkeys(cands) if c not in cache]
        if todo:
            if count + len(todo) > max_evaluations:
                raise _Budget
            count += len(todo)
            for c, k in zip(todo, keys_of(todo), strict=True):
                cache[c] = k
        oks = [cache[c] == key for c in cands]
        for c, ok in zip(cands, oks, strict=True):
            if ok and (len(c), c) < (len(best), best):
                best = c
        return oks

    try:
        if not test([text])[0]:
            return Minimized(text, key, count, complete=False)
    except _Budget:
        return Minimized(text, key, count, complete=False)
    current = text
    complete = True
    try:
        for _ in range(max_passes):
            before = current
            for level in levels:
                current = "".join(_shrink(units_of(current, level), test))
            if current == before:
                break
        else:
            complete = False
    except _Budget:
        current, complete = best, False
    return Minimized(current, key, count, complete)


def _shrink(units: list[str], test: Callable[[list[str]], list[bool]]) -> list[str]:
    n = 2
    while len(units) >= 2:
        size = -(-len(units) // n)
        cands = [units[:i] + units[i + size :] for i in range(0, len(units), size)]
        oks = test(["".join(c) for c in cands])
        hit = next((c for c, ok in zip(cands, oks, strict=True) if ok), None)
        if hit is not None:
            units = hit
            n = max(n - 1, 2)
        elif size == 1:
            break
        else:
            n = min(n * 2, len(units))
    return units
