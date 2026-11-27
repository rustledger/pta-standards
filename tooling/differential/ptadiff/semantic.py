"""The semantic differential: one oracle, one implementation, one format, a
verdict and a category for every LEDGER, from what each side makes of it
after a full load (see `snapshot.py` and `SNAPSHOT.md`).

It is the parse differential's pipeline (`pipeline.Differ`) with snapshots in
place of error lists. Every other stage is shared: the protocol
(`JsonlImplementation.snapshots`), the forked worker pool the oracle runs in,
the key-preserving minimizer, the clusterer and the report.

Stages for one batch:

1. the oracle and the implementation each give a raw snapshot (or crash);
2. both are canonicalized (`snapshot.canonicalize`), run through the
   format's semantic normalizers and any consumer hooks (each a named
   rewrite of one side, or of both, that removes a KNOWN representation
   difference), and canonicalized again; then the `pair` normalizers, which
   see both sides at once, run;
3. the first difference (`snapshot.first_diff`) decides: none is a match;
4. a mismatch that a declared DEVIATION explains (a difference the
   implementation makes on purpose, stated with a reference to where it is
   documented) is counted as that deviation, apart from the mismatches, so
   it does not pollute the metric;
5. every other mismatch is named by the format's semantic key.

An implementation crash (it answered `crash`) is a mismatch keyed
`impl-crash|...`: a finding. An oracle crash leaves the input unjudged, and
so does a ledger the format says the oracle cannot judge where it runs
(`FormatPlugin.oracle_unjudged`: a plugin that is not installed there);
both are counted as `crash`, with the reason.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from .formats.base import FormatPlugin, generic_semantic_key
from .minimize import minimize
from .pool import Crash
from .snapshot import FieldDiff, Ledger, canonicalize, diffs, first_diff


@dataclass(frozen=True)
class SemanticMismatch:
    """Everything a semantic key or a deviation predicate may look at for
    one mismatching ledger. Snapshots are canonical and normalized."""

    ledger: Ledger
    main: str
    oracle: dict
    impl: dict
    diff: FieldDiff
    diffs: tuple[FieldDiff, ...] = ()

    def text_of(self, file: str) -> str:
        """The text of `file` (the main file's name, or an included one's)."""
        if not file or file == self.main:
            return self.ledger.text
        return self.ledger.files.get(file, "")


#: A semantic key function.
SemanticKeyFn = Callable[[SemanticMismatch], str]


@dataclass(frozen=True)
class Deviation:
    """A difference an implementation makes ON PURPOSE.

    `applies(mismatch)` says whether it explains a mismatch; `ref` says where
    the difference is documented (the implementation's compatibility notes),
    so every exclusion from the metric is traceable to a decision."""

    name: str
    ref: str
    applies: Callable[[SemanticMismatch], bool]
    description: str = ""


@dataclass(frozen=True)
class SemanticVerdict:
    """The comparison of one ledger. `status` is `match`, `mismatch`,
    `deviation` (a declared deviation explains the difference; `deviation`
    names it) or `crash` (the oracle crashed: not judged)."""

    status: str
    oracle: dict | None = None
    impl: dict | None = None
    diff: FieldDiff | None = None
    key: str | None = None
    crash: str | None = None
    deviation: str | None = None


def normalize_snapshot(fmt: FormatPlugin, side: str, ledger: Ledger, snap: dict) -> dict:
    """`snap` (raw) of `side` (`oracle` or `impl`), canonical and normalized."""
    snap = canonicalize(snap)
    for n in fmt.semantic_normalizers:
        if n.enabled and n.side in (side, "both"):
            snap = n.fn(ledger, snap, side)
    return canonicalize(snap)


#: `field|path|kind` of the first difference: which snapshot field, what in
#: it, and in which kind of directive. Every format's fallback key.
generic_key = generic_semantic_key


class SemanticDiffer:
    """Runs both sides over batches of ledgers and judges each one."""

    def __init__(
        self,
        fmt: FormatPlugin,
        oracle,
        impl,
        *,
        key: str | None = None,
        jobs: int = 1,
        deviations: Sequence[Deviation] | None = None,
        error_mode: str = "lines",
    ) -> None:
        self.fmt, self.oracle, self.impl = fmt, oracle, impl
        self.key_name = key or next(iter(fmt.semantic_keys))
        self.keyfn: SemanticKeyFn = fmt.semantic_keys[self.key_name]
        self.jobs = jobs
        self.deviations = list(fmt.deviations if deviations is None else deviations)
        self.main = fmt.main_file
        #: How errors are compared: `snapshot.ERROR_MODES`.
        self.error_mode = error_mode

    def judge(self, ledger: Ledger, oracle_raw: Any, impl_raw: Any) -> SemanticVerdict:
        """One verdict from both sides' raw answers."""
        if isinstance(oracle_raw, Crash):
            return SemanticVerdict("crash", crash=oracle_raw.why)
        oracle = normalize_snapshot(self.fmt, "oracle", ledger, oracle_raw)
        unjudged = self.fmt.oracle_unjudged(ledger, oracle)
        if unjudged:
            return SemanticVerdict("crash", oracle, crash=unjudged)
        if isinstance(impl_raw, str):
            why = impl_raw.split(":")[0].strip() or "crash"
            d = FieldDiff("crash", why, "-", oracle=None, impl=impl_raw)
            return SemanticVerdict("mismatch", oracle, None, d, f"impl-crash|{why}", crash=impl_raw)
        impl = normalize_snapshot(self.fmt, "impl", ledger, impl_raw)
        for n in self.fmt.semantic_normalizers:
            if n.enabled and n.side == "pair":
                oracle, impl = n.fn(ledger, oracle, impl)
                oracle, impl = canonicalize(oracle), canonicalize(impl)
        mode = self.error_mode
        d = first_diff(oracle, impl, error_mode=mode)
        if d is None:
            return SemanticVerdict("match", oracle, impl)
        m = SemanticMismatch(
            ledger, self.main, oracle, impl, d, tuple(diffs(oracle, impl, error_mode=mode))
        )
        for dev in self.deviations:
            if dev.applies(m):
                return SemanticVerdict(
                    "deviation", oracle, impl, d, f"deviation:{dev.name}", deviation=dev.name
                )
        return SemanticVerdict("mismatch", oracle, impl, d, self.keyfn(m))

    def evaluate(self, items: Sequence[tuple[str, Ledger]]) -> dict[str, SemanticVerdict]:
        """`{id: SemanticVerdict}` for every `(id, Ledger)`."""
        items = list(items)
        oracle_out = self.oracle.snapshot(items, jobs=self.jobs)
        impl_out = self.impl.snapshots(items, main=self.main, jobs=self.jobs)
        return {i: self.judge(led, oracle_out[i], impl_out[i]) for i, led in items}

    def keys_of(self, ledgers: Sequence[Ledger], *, well_formed: bool = False) -> list[str | None]:
        """Each ledger's category key, `None` where it matches, is a
        deviation, or the oracle crashed: the minimizer's test. With
        `well_formed`, also `None` where the oracle reports a syntax error
        (`FormatPlugin.well_formed`)."""
        items = [(f"m{n}", led) for n, led in enumerate(ledgers)]
        v = self.evaluate(items)
        return [
            v[i].key
            if v[i].status == "mismatch"
            and (not well_formed or self.fmt.well_formed(v[i].oracle or {}))
            else None
            for i, _ in items
        ]

    def minimizer_test(self, ledger: Ledger):
        """The minimizer's test for `ledger`: `keys_of`, requiring every
        candidate to be well-formed when `ledger` itself is."""
        first = self.evaluate([("m", ledger)])["m"]
        strict = first.oracle is not None and self.fmt.well_formed(first.oracle)
        return lambda ledgers: self.keys_of(ledgers, well_formed=strict)

    def minimize(self, ledger: Ledger, key: str, **options) -> MinimizedLedger:
        """`minimize_ledger` with this differ's test and format."""
        return minimize_ledger(
            ledger, key, self.minimizer_test(ledger), self.fmt.shrink_units, **options
        )


@dataclass
class MinimizedLedger:
    ledger: Ledger
    key: str
    evaluations: int
    complete: bool = True
    #: Files the minimizer dropped (no longer needed for the key).
    dropped: list[str] = field(default_factory=list)


def minimize_ledger(
    ledger: Ledger,
    key: str,
    keys_of: Callable[[Sequence[Ledger]], Sequence[str | None]],
    units_of,
    *,
    levels: Sequence[str] = ("lines", "words"),
    max_evaluations: int = 3000,
) -> MinimizedLedger:
    """The smallest ledger this search finds with category `key`: the main
    file's text, then each other file's, shrunk with `ptadiff.minimize` at
    `levels` (by default lines, then whole words: a semantic example is
    read by a person deciding what the ledger means, so it stays a ledger
    rather than a string of characters), and every file the key no longer
    needs dropped."""
    budget = max_evaluations
    complete = True
    total = 0

    def shrink(current: Ledger, path: str | None) -> Ledger:
        nonlocal budget, complete, total
        if budget <= 0:
            complete = False
            return current
        text = current.text if path is None else current.files[path]

        def rebuild(t: str) -> Ledger:
            return current.with_text(t) if path is None else current.with_file(path, t)

        r = minimize(
            text,
            key,
            lambda texts: keys_of([rebuild(t) for t in texts]),
            units_of,
            levels=levels,
            max_evaluations=budget,
        )
        budget -= r.evaluations
        total += r.evaluations
        complete = complete and r.complete
        return rebuild(r.text)

    current = shrink(ledger, None)
    dropped = []
    for path in sorted(current.files):
        cand = Ledger(current.text, {p: t for p, t in current.files.items() if p != path})
        total += 1
        if keys_of([cand])[0] == key:
            current = cand
            dropped.append(path)
    for path in sorted(current.files):
        current = shrink(current, path)
    return MinimizedLedger(current, key, total, complete, dropped)
