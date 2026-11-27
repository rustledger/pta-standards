"""What a format plugs into the shared pipeline.

The shared stages (compare, minimize, cluster, report) know nothing about any
format. A `FormatPlugin` supplies the rest:

* the oracle: the reference implementation, behind `Oracle`;
* normalizers: rewrites of either side's errors that remove KNOWN, deliberate
  differences before comparing (each named, so a consumer can turn one off);
* the category key: how a mismatch is named, from a registry of key functions
  so a better key (say, the reference grammar's parser state at the error) can
  be added without touching any stage;
* generators: seeded, deterministic input generators;
* shrink units: how the minimizer cuts an input below the line level.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from ..compare import Divergence
from ..model import Error, Token


@dataclass(frozen=True)
class Mismatch:
    """Everything a key function may look at for one mismatching input.

    `text` is the input as the ORACLE read it (after the format's oracle-input
    normalizers), so its lines line up with `tokens` and with both error
    lists, which are already normalized.
    """

    text: str
    oracle: tuple[Error, ...]
    impl: tuple[Error, ...]
    divergence: Divergence
    tokens: tuple[Token, ...] | None = None


#: A key function: a mismatch's category, as a short `|`-separated string.
KeyFn = Callable[[Mismatch], str]


@dataclass(frozen=True)
class Generator:
    """A deterministic input generator: `fn(seed, n)` returns `n` distinct
    inputs, sorted, the same ones on every run and platform."""

    name: str
    fn: Callable[[int, int], list[str]]
    description: str = ""

    def __call__(self, seed: int, n: int) -> list[str]:
        return self.fn(seed, n)


@dataclass
class Normalizer:
    """One named normalization. `side` is `oracle-input` (a rewrite of the
    text the oracle parses), `oracle` or `impl` (a rewrite of that side's
    error list, given the text the oracle read)."""

    name: str
    side: str
    fn: Callable
    description: str = ""
    enabled: bool = True


_SHRINK_WORDS = re.compile(r"[ \t]+|[^ \t\n]+|\n")


@dataclass
class FormatPlugin:
    """The base plugin. Subclasses override what their format needs; the
    defaults are format-neutral and usable as they are."""

    name: str = "generic"
    extensions: tuple[str, ...] = ()
    normalizers: list[Normalizer] = field(default_factory=list)
    #: Key functions by name; the first one is the default.
    keys: dict[str, KeyFn] = field(default_factory=dict)
    generators: dict[str, Generator] = field(default_factory=dict)
    #: Whether any key function reads `Mismatch.tokens` (the oracle's lexer
    #: is then run on every mismatching input).
    needs_tokens: bool = False

    def __post_init__(self) -> None:
        if not self.keys:
            self.keys = {"coarse": self.coarse_key}

    # -- the oracle -------------------------------------------------------

    def oracle(self, **options):
        raise NotImplementedError(f"format {self.name!r} has no oracle adapter")

    # -- normalization ----------------------------------------------------

    def normalizer(self, name: str) -> Normalizer:
        for n in self.normalizers:
            if n.name == name:
                return n
        raise KeyError(f"format {self.name!r} has no normalizer {name!r}")

    def oracle_input(self, text: str) -> str:
        for n in self.normalizers:
            if n.enabled and n.side == "oracle-input":
                text = n.fn(text)
        return text

    def normalize(self, side: str, text: str, errors: list[Error]) -> list[Error]:
        """`errors` of `side` (`oracle` or `impl`) after every enabled
        normalizer of that side, in order; `text` is the oracle's input."""
        for n in self.normalizers:
            if n.enabled and n.side == side:
                errors = n.fn(text, errors)
        return errors

    # -- category keys ----------------------------------------------------

    @property
    def default_key(self) -> str:
        return next(iter(self.keys))

    def key(self, name: str | None = None) -> KeyFn:
        name = name or self.default_key
        try:
            return self.keys[name]
        except KeyError:
            raise KeyError(
                f"format {self.name!r} has no key {name!r} (have: {', '.join(self.keys)})"
            ) from None

    def oracle_error_kind(self, error: Error) -> str:
        return error.code

    def impl_error_kind(self, error: Error) -> str:
        return error.code

    def line_kind(self, text: str, line: int) -> str:
        """`eof` for line 0, else `blank`, `indented` or `top`."""
        if line == 0:
            return "eof"
        lines = text.split("\n")
        if line > len(lines):
            return "past-end"
        src = lines[line - 1]
        if not src.strip(" \t\r"):
            return "blank"
        return "indented" if src[:1] in (" ", "\t") else "top"

    def coarse_key(self, m: Mismatch) -> str:
        """`side|who:kinds|line-kind`, all on the first line the two sides
        disagree on:

        * side: `impl-more` or `impl-fewer` (errors on that line), or `eof`
          when the first disagreement is a file-level error (line 0, which
          sorts after every line);
        * who:kinds: the error kinds of the side that reports MORE there
          (`impl:` or `oracle:`; the oracle for `eof` when it has more),
          sorted and `+`-joined, `-` for none. The side with the surplus is
          the one whose errors are the difference; the other side's kinds
          mostly restate the line's content, and an implementation's own
          codes for an error it shares with the oracle would only split one
          difference by how the implementation happens to name it;
        * line-kind: what that line is (`line_kind`).
        """
        d = m.divergence
        side = "eof" if d.line == 0 else ("impl-more" if d.impl > d.oracle else "impl-fewer")
        if d.impl > d.oracle:
            who, kinds = "impl", {self.impl_error_kind(e) for e in m.impl if e.line == d.line}
        else:
            who, kinds = "oracle", {self.oracle_error_kind(e) for e in m.oracle if e.line == d.line}
        return f"{side}|{who}:{'+'.join(sorted(kinds)) or '-'}|{self.line_kind(m.text, d.line)}"

    # -- minimization -----------------------------------------------------

    def shrink_units(self, text: str, level: str) -> list[str]:
        """`text` cut into units whose concatenation is `text`, for the
        minimizer's `level`: `lines` (each with its `\\n`), `tokens` (runs of
        blanks, runs of non-blanks, and newlines) or `chars`."""
        if level == "lines":
            return [u for u in re.split(r"(?<=\n)", text) if u]
        if level == "tokens":
            return _SHRINK_WORDS.findall(text)
        if level == "chars":
            return list(text)
        raise ValueError(f"unknown shrink level {level!r}")
