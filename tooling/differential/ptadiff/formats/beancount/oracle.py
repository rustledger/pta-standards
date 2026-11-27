"""beancount as an oracle, through its public Python API only.

`beancount.parser.parser.parse_string` gives the parse errors and
`beancount.parser.lexer.lex_iter_string` the lexer's tokens. Both are called
as black boxes, in process, in forked workers (`ptadiff.pool`): beancount's C
parser segfaults on some inputs, and a worker that dies loses only that input,
recorded as a crash. Nothing here reads or embeds beancount's grammar, lexer
rules or generated tables.
"""

from __future__ import annotations

from ...model import Error, Outcome, Token
from ...oracles.base import Oracle
from ...pool import DEFAULT_TIMEOUT_S, Crash, run_forked


def _parse_one(text: str) -> list[list]:
    from beancount.parser import parser

    _, errors, _ = parser.parse_string(text)
    return [
        [int((e.source or {}).get("lineno") or 0), type(e).__name__, str(e.message)] for e in errors
    ]


def _lex_one(text: str) -> list[list]:
    from beancount.parser import lexer

    return [
        [kind, int(line), raw.decode("utf-8", "surrogateescape")]
        for kind, line, raw, _ in lexer.lex_iter_string(text)
    ]


class BeancountOracle(Oracle):
    """beancount's parser. `version` pins the one expected (`None` accepts
    any); a run against another version would read its changes as the
    implementation's."""

    name = "beancount"
    can_lex = True

    def __init__(self, version: str | None = None, timeout: int = DEFAULT_TIMEOUT_S) -> None:
        self.expected_version = version
        self.timeout = timeout
        self._version: str | None = None

    def version(self) -> str:
        if self._version is None:
            # Imported in the parent, so every forked worker inherits it.
            import beancount
            import beancount.parser.lexer
            import beancount.parser.parser

            self._version = beancount.__version__
            if self.expected_version and self._version != self.expected_version:
                raise RuntimeError(
                    f"beancount {self._version} is installed, {self.expected_version} expected"
                )
        return self._version

    def parse(self, items, *, jobs=1):
        self.version()
        raw = run_forked(items, _parse_one, jobs=jobs, timeout=self.timeout)
        out: dict[str, Outcome] = {}
        for item_id, r in raw.items():
            if isinstance(r, Crash):
                out[item_id] = Outcome(crash=r.why)
            else:
                out[item_id] = Outcome(errors=tuple(Error(*e) for e in r))
        return out

    def lex(self, items, *, jobs=1):
        self.version()
        raw = run_forked(items, _lex_one, jobs=jobs, timeout=self.timeout)
        return {
            item_id: r if isinstance(r, Crash) else [Token(*t) for t in r]
            for item_id, r in raw.items()
        }
