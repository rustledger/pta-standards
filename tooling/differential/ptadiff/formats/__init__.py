"""Format plugins, by name."""

from __future__ import annotations

from .base import FormatPlugin, Generator, KeyFn, Mismatch, Normalizer


def get_format(name: str) -> FormatPlugin:
    """A fresh plugin for format `name` (`beancount`, `ledger`, `hledger`)."""
    if name == "beancount":
        from .beancount import BeancountFormat

        return BeancountFormat()
    if name == "ledger":
        from .ledger import LedgerFormat

        return LedgerFormat()
    if name == "hledger":
        from .hledger import HledgerFormat

        return HledgerFormat()
    raise KeyError(f"unknown format {name!r}")


FORMATS = ("beancount", "ledger", "hledger")

__all__ = ["FORMATS", "FormatPlugin", "Generator", "KeyFn", "Mismatch", "Normalizer", "get_format"]
