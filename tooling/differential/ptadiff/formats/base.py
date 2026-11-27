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

For the SEMANTIC differential (`ptadiff.semantic`, whole ledgers compared by
what a full load makes of them) a format supplies the same kinds of parts,
in their own registries: `semantic_oracle`, `semantic_normalizers` (rewrites
of a canonical snapshot), `semantic_keys`, `semantic_generators` (which
return `ptadiff.snapshot.Ledger`s, so an input can span several files), and
`deviations` (normally empty: an implementation's deliberate differences are
its consumer's to declare, through a hooks module).
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


def generic_semantic_key(m) -> str:
    """`field|path|kind` of a semantic mismatch's first difference."""
    d = m.diff
    return f"{d.field}|{d.path}|{d.kind}"


_SHRINK_WORDS = re.compile(r"[ \t]+|[^ \t\n]+|\n")
_WORDS = re.compile(r"[^ \t\n]+[ \t]*|[ \t]+|\n")


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
    #: Semantic differential parts (see the module docstring). A semantic
    #: normalizer's `side` is `oracle`, `impl` or `both`, and its `fn` takes
    #: `(ledger, snapshot, side)` and returns the rewritten snapshot; or
    #: `pair`, and its `fn` takes `(ledger, oracle, impl)` and returns both.
    semantic_normalizers: list[Normalizer] = field(default_factory=list)
    semantic_keys: dict[str, Callable] = field(default_factory=dict)
    semantic_generators: dict[str, Generator] = field(default_factory=dict)
    deviations: list = field(default_factory=list)
    #: The main file's name, in the directory a multi-file input is laid out in.
    main_file: str = "main"

    def __post_init__(self) -> None:
        if not self.keys:
            self.keys = {"coarse": self.coarse_key}
        if not self.semantic_keys:
            self.semantic_keys = {"field": generic_semantic_key}

    # -- the semantic oracle ----------------------------------------------

    def semantic_oracle(self, **options):
        raise NotImplementedError(f"format {self.name!r} has no semantic oracle adapter")

    def oracle_unjudged(self, ledger, snapshot: dict) -> str | None:
        """Why the oracle's (canonical) snapshot cannot judge `ledger`, or
        None. An oracle that could not run the ledger as written for a
        reason of its ENVIRONMENT (a third-party plugin that is not
        installed where it runs) gives no verdict on it, as a crash gives
        none. None by default."""
        return None

    def well_formed(self, snapshot: dict) -> bool:
        """Whether the oracle's (canonical) snapshot says the ledger parsed
        cleanly. The semantic minimizer keeps only candidates that still do,
        so a minimized example stays a ledger the oracle reads as written,
        not one whose meaning hangs on how a parser recovers from an error
        (that is the parse differential's subject). True by default."""
        return True

    def ledger_features(self, ledger) -> list[str]:
        """The features a ledger is made of, for a report's minimized
        examples. None by default."""
        return []

    def semantic_normalizer(self, name: str) -> Normalizer:
        for n in self.semantic_normalizers:
            if n.name == name:
                return n
        raise KeyError(f"format {self.name!r} has no semantic normalizer {name!r}")

    def directive_lines(self, text: str, line: int) -> tuple[int, int]:
        """The 1-based first and last line of the directive `line` is in: the
        nearest line at or above it that starts in column 0 and is not blank
        or a comment, through the last indented line after it. Every
        plain-text-accounting format indents a directive's continuation
        lines; a format that does not overrides this. `(line, line)` when
        `line` is 0 or past the end."""
        lines = text.split("\n")
        if line <= 0 or line > len(lines):
            return line, line

        def top(s: str) -> bool:
            return bool(s.strip()) and s[:1] not in (" ", "\t") and not s.startswith(";")

        start = line
        while start > 1 and not top(lines[start - 1]):
            start -= 1
        end = start
        while end < len(lines) and lines[end][:1] in (" ", "\t") and lines[end].strip():
            end += 1
        return start, max(end, line)

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
        blanks, runs of non-blanks, and newlines), `words` (a run of
        non-blanks with the blanks after it, so dropping one never glues two
        words together: the level that keeps a minimized ledger readable) or
        `chars`."""
        if level == "lines":
            return [u for u in re.split(r"(?<=\n)", text) if u]
        if level == "words":
            return _WORDS.findall(text)
        if level == "tokens":
            return _SHRINK_WORDS.findall(text)
        if level == "chars":
            return list(text)
        raise ValueError(f"unknown shrink level {level!r}")
