"""The beancount format plugin.

Oracle: beancount's own parser (`oracle.BeancountOracle`), in process.

Normalizers (all enabled by default; turn one off with
`plugin.normalizer(name).enabled = False`):

* `strip-bom` (oracle input): beancount 3.2.3 does not strip a UTF-8 BOM at
  byte 0 and reports it as an invalid token. An implementation that accepts
  it would otherwise mismatch on every BOM-prefixed file whatever the rest
  says, so the oracle reads the input without it. A BOM anywhere else is
  left alone.
* `eol-error-on-statement-line` (oracle): a syntax error whose unexpected
  token is an end of line (`syntax error, unexpected EOL, ...`) is reported
  by beancount on the line AFTER the statement (the parser's location for
  that token is the lexer's, which has already counted the newline). It is
  moved back to the statement's line. An error at end of file is not moved.
* `drop-builder-errors` (oracle): errors beancount's parser actions raise
  about option names and values, account names, and cost merging. They are
  not syntax errors and an implementation may well check them at another
  stage.

Category keys (`plugin.keys`, the first is the default):

* `shape`: `coarse` plus the token shape of the first disagreeing line, from
  beancount's black-box lexer (`lex_iter_string` token names; see
  `line_shape`);
* `coarse`: `side|who:kinds|line-kind` (see `FormatPlugin.coarse_key`).

A key built from a parser's state at the error needs that parser's tables;
it plugs in as another entry of `keys` (see the package README).

Semantic differential (`ptadiff.semantic`): the oracle is beancount's full
loader (`semantic.BeancountSemanticOracle`, `loader.load_file`), the
normalizers, features and `sem` key are in `semkey.py`, the generators of
well-formed ledgers in `semgen.py`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ...model import Error
from ..base import FormatPlugin, Mismatch, Normalizer, generic_semantic_key
from . import semkey
from .generators import GENERATORS
from .oracle import BeancountOracle
from .semantic import MAIN, BeancountSemanticOracle
from .semgen import SEMANTIC_GENERATORS

#: The beancount release the bundled normalizers and keys were checked against.
TESTED_VERSION = "3.2.3"

EOL_SYNTAX_ERROR = "syntax error, unexpected EOL"

#: Message prefixes / fragments of errors beancount's parser ACTIONS raise
#: (option names and values, account names, cost merging), not its grammar.
BUILDER_ERROR_MARKERS = (
    "Invalid option",
    "Invalid account name",
    "Error for option",
    "may not be set",
    "Renamed to '",
    "Allowing pipe separator",
    "Cost merging is not supported yet",
)

_SYNTAX = re.compile(r"syntax error, unexpected (.+?)(?:,|$)")


def strip_bom(text: str) -> str:
    return text[1:] if text.startswith("\ufeff") else text


def eol_error_on_statement_line(text: str, errors: list[Error]) -> list[Error]:
    return [
        e._replace(line=e.line - 1) if e.msg.startswith(EOL_SYNTAX_ERROR) and e.line > 1 else e
        for e in errors
    ]


def drop_builder_errors(text: str, errors: list[Error]) -> list[Error]:
    return [e for e in errors if not any(m in e.msg for m in BUILDER_ERROR_MARKERS)]


def error_kind(error: Error) -> str:
    """beancount's error, named by what it is about:

    * `lex:token`, `lex:date`, `lex:number`, `lex`: the lexer's invalid
      token, invalid date, invalid number, or another lexer error;
    * `syn:<TOKEN>`: a syntax error at an unexpected `<TOKEN>` (the name the
      message gives, `end of file` written `end_of_file`);
    * otherwise the error's type (`ParserError`, ...).
    """
    if error.code == "LexerError":
        if error.msg.startswith("Invalid token"):
            return "lex:token"
        if "Invalid number format" in error.msg:
            return "lex:number"
        if error.msg.startswith("ValueError:") and any(
            w in error.msg for w in ("month", "day", "year")
        ):
            return "lex:date"
        return "lex"
    m = _SYNTAX.match(error.msg)
    if m:
        return "syn:" + m.group(1).replace(" ", "_")
    return error.code


def line_shape(tokens, line: int) -> str:
    """The token shape of `line`, from beancount's token names on it
    (end-of-line tokens left out):

    * with an invalid token (`error`): the token just before the first one,
      `^` when it starts the line, then `error` (`DATE error`, `^ error`,
      `INDENT error`): where on the line the lexer gave up;
    * otherwise its first two tokens (`DATE OPEN`, `INDENT KEY`);
    * `-` for a line with no tokens.

    Deliberately short: the key should group inputs by the construct the
    difference is in, not by everything else on the line.
    """
    names = [t.kind for t in tokens if t.line == line and t.kind != "EOL"]
    first = next((i for i, n in enumerate(names) if n == "error"), None)
    if first is None:
        return " ".join(names[:2]) or "-"
    return ("^" if first == 0 else names[first - 1]) + " error"


@dataclass
class BeancountFormat(FormatPlugin):
    name: str = "beancount"
    extensions: tuple[str, ...] = (".beancount", ".bean")
    needs_tokens: bool = True
    main_file: str = MAIN

    def __post_init__(self) -> None:
        self.normalizers = [
            Normalizer("strip-bom", "oracle-input", strip_bom, "drop a UTF-8 BOM at byte 0"),
            Normalizer(
                "eol-error-on-statement-line",
                "oracle",
                eol_error_on_statement_line,
                "move an unexpected-EOL syntax error back to its statement's line",
            ),
            Normalizer(
                "drop-builder-errors",
                "oracle",
                drop_builder_errors,
                "drop option, account-name and cost-merge errors",
            ),
        ]
        self.keys = {"shape": self.shape_key, "coarse": self.coarse_key}
        self.generators = dict(GENERATORS)
        self.semantic_normalizers = [
            Normalizer(
                "error-at-directive",
                "both",
                lambda led, snap, side: semkey.error_at_directive(self, led, snap, side),
                "place each error on its directive's first line",
            ),
            Normalizer(
                "drop-errored-transactions",
                "both",
                lambda led, snap, side: semkey.drop_errored_transactions(self, led, snap, side),
                "leave out a transaction its own side reports an error in",
            ),
            Normalizer(
                "placeholder-locations",
                "both",
                lambda led, snap, side: semkey.placeholder_locations(self, led, snap, side),
                "locate what has no place in the input at nowhere",
            ),
            Normalizer(
                "load-errors-at-directive",
                "oracle",
                lambda led, snap, side: semkey.load_errors_at_directive(self, led, snap, side),
                "place a missing include, plugin or document root on its directive",
            ),
            Normalizer(
                "errored-transaction-balances",
                "pair",
                lambda led, o, i: semkey.errored_transaction_balances(self, led, o, i),
                "compare no balance of an account an errored transaction posts to",
            ),
            Normalizer(
                "tolerance-fallback",
                "oracle",
                lambda led, snap, side: semkey.tolerance_fallback(self, led, snap, side),
                "fill in the `*` tolerance default beancount applies on lookup",
            ),
            Normalizer(
                "drop-zero-tolerances",
                "both",
                lambda led, snap, side: semkey.drop_zero_tolerances(self, led, snap, side),
                "drop a zero inferred tolerance",
            ),
        ]
        self.semantic_keys = {
            "sem": lambda m: semkey.sem_key(self, m),
            "field": generic_semantic_key,
        }
        self.semantic_generators = dict(SEMANTIC_GENERATORS)

    def semantic_oracle(self, version: str | None = TESTED_VERSION, **options):
        return BeancountSemanticOracle(version=version, **options)

    def ledger_features(self, ledger) -> list[str]:
        return semkey.ledger_features(self, ledger)

    def oracle_unjudged(self, ledger, snapshot: dict) -> str | None:
        return semkey.missing_third_party_plugin(snapshot)

    def well_formed(self, snapshot: dict) -> bool:
        return not any(e["code"] in semkey.SYNTAX_ERRORS for e in snapshot.get("errors", ()))

    def oracle(self, version: str | None = TESTED_VERSION, **options):
        return BeancountOracle(version=version, **options)

    def oracle_error_kind(self, error: Error) -> str:
        return error_kind(error)

    def shape_key(self, m: Mismatch) -> str:
        if m.divergence.line == 0:
            shape = "-"
        elif m.tokens is None:  # the oracle's lexer crashed on this input
            shape = "?"
        else:
            shape = line_shape(m.tokens, m.divergence.line)
        return self.coarse_key(m) + "|" + shape


__all__ = [
    "BUILDER_ERROR_MARKERS",
    "TESTED_VERSION",
    "BeancountFormat",
    "BeancountOracle",
    "BeancountSemanticOracle",
    "error_kind",
    "line_shape",
]
