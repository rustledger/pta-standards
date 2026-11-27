"""Oracle adapters: the reference implementation each format is compared to."""

from .base import Oracle
from .cli import CliOracle

__all__ = ["CliOracle", "Oracle"]
