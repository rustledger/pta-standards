"""The hledger format plugin: a stub.

The oracle is the `hledger` CLI, one process per input (`hledger check`
parses the journal and exits non-zero on the first error). What is missing is
`HledgerOracle.parse_output`: turning hledger's `hledger: Error: FILE:LINE:COL:`
diagnostics into `Error(line, code, msg)`. hledger stops at the first error,
so a comparison against it can only be of the first error's line; a plugin
should say so with a normalizer that keeps only the implementation's first
error. Until then the plugin supports the `coarse` key and the shared stages.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..oracles.cli import CliOracle
from .base import FormatPlugin


class HledgerOracle(CliOracle):
    name = "hledger"
    argv = ("hledger", "-f", "{file}", "check")
    suffix = ".journal"

    def parse_output(self, returncode, stdout, stderr):
        raise NotImplementedError(
            "HledgerOracle.parse_output: map hledger's 'FILE:LINE:COL:' diagnostics "
            "to Error(line, code, msg)"
        )


@dataclass
class HledgerFormat(FormatPlugin):
    name: str = "hledger"
    extensions: tuple[str, ...] = (".journal", ".hledger")

    def oracle(self, **options):
        return HledgerOracle()
