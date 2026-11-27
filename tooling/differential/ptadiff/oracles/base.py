"""The interface every oracle adapter implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ..model import Outcome, Token
from ..pool import Crash


class Oracle(ABC):
    """A reference implementation: parses inputs and reports their errors.

    `parse` must give every input an `Outcome`: its raw errors (no
    normalization: that is the format plugin's job, so it is the same for
    every oracle of a format), or a crash. An oracle that can expose its own
    lexer's tokens sets `can_lex` and implements `lex`; key functions that
    name a mismatch by token shape need it.
    """

    name: str = "oracle"
    can_lex: bool = False

    def version(self) -> str:
        return "unknown"

    @abstractmethod
    def parse(self, items: Sequence[tuple[str, str]], *, jobs: int = 1) -> dict[str, Outcome]:
        """`{id: Outcome}` for every `(id, text)`."""

    def lex(
        self, items: Sequence[tuple[str, str]], *, jobs: int = 1
    ) -> dict[str, list[Token] | Crash]:
        """`{id: tokens}` for every `(id, text)`, a `Crash` where the lexer
        died."""
        raise NotImplementedError(f"oracle {self.name!r} cannot lex")
