"""The records every stage passes around: errors, tokens, and outcomes.

Everything here is format-generic. A format plugin decides what an error's
`code` means and what a token's `kind` is; the shared stages only compare
lines, count, and hash.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, NamedTuple


class Error(NamedTuple):
    """One reported parse error: a 1-based line (0 means "the whole file"),
    a short machine-readable code, and the human message."""

    line: int
    code: str
    msg: str

    def to_json(self) -> dict[str, Any]:
        return {"line": self.line, "code": self.code, "msg": self.msg}

    @classmethod
    def from_json(cls, obj: Any) -> Error:
        """An error from the protocol's `{line, code, msg}` object (or a
        `[line, code, msg]` triple, the older list form)."""
        if isinstance(obj, dict):
            return cls(int(obj["line"]), str(obj["code"]), str(obj.get("msg", "")))
        line, code, msg = obj
        return cls(int(line), str(code), str(msg))


class Token(NamedTuple):
    """One token as the oracle's own lexer names it, on a 1-based line."""

    kind: str
    line: int
    text: str


@dataclass(frozen=True)
class Outcome:
    """What one side said about one input: its errors, or why it said
    nothing (`crash`: it died, raised, or timed out)."""

    errors: tuple[Error, ...] = ()
    crash: str | None = None

    @property
    def ok(self) -> bool:
        return self.crash is None


def content_id(text: str) -> str:
    """The id of an input: the first 12 hex digits of its UTF-8 sha256."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
