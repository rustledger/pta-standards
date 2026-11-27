"""The ledger format plugin: a stub.

The oracle is the `ledger` CLI, one process per input. What is missing is
`LedgerOracle.parse_output`: turning ledger's diagnostics (`While parsing file
"...", line N:` followed by `Error: ...`) into `Error(line, code, msg)`, with
`code` a stable short name for the kind of error. Until then the plugin
supports the format-neutral `coarse` key, the shared stages, and no
generators.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..oracles.cli import CliOracle
from .base import FormatPlugin


class LedgerOracle(CliOracle):
    name = "ledger"
    argv = ("ledger", "-f", "{file}", "--permissive", "balance")
    suffix = ".ledger"

    def parse_output(self, returncode, stdout, stderr):
        raise NotImplementedError(
            "LedgerOracle.parse_output: map ledger's 'While parsing file ..., line N:' "
            "diagnostics to Error(line, code, msg)"
        )


@dataclass
class LedgerFormat(FormatPlugin):
    name: str = "ledger"
    extensions: tuple[str, ...] = (".ledger", ".dat")

    def oracle(self, **options):
        return LedgerOracle()
