"""An oracle that is a command-line program, one process per input.

For formats whose reference implementation has no in-process API (ledger,
hledger): the input is written to a temporary file, the command runs on it,
and `parse_output` turns what it printed into errors. Each run has a timeout;
a run that exceeds it or dies on a signal is a crash.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor

from ..model import Error, Outcome
from .base import Oracle


class CliOracle(Oracle):
    """Subclasses set `argv` (with a `{file}` placeholder) and `suffix`, and
    implement `parse_output`."""

    argv: Sequence[str] = ()
    suffix: str = ".txt"
    timeout: float = 20.0

    def parse_output(self, returncode: int, stdout: str, stderr: str) -> list[Error]:
        """The errors one run reported, from its exit code and output."""
        raise NotImplementedError

    def _run_one(self, text: str) -> Outcome:
        fd, path = tempfile.mkstemp(suffix=self.suffix)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                f.write(text)
            argv = [a.replace("{file}", path) for a in self.argv]
            try:
                proc = subprocess.run(argv, capture_output=True, timeout=self.timeout)
            except subprocess.TimeoutExpired:
                return Outcome(crash=f"timed out after {self.timeout}s")
            if proc.returncode < 0:
                return Outcome(crash=f"killed by signal {-proc.returncode}")
            errors = self.parse_output(
                proc.returncode,
                proc.stdout.decode("utf-8", "replace"),
                proc.stderr.decode("utf-8", "replace"),
            )
            return Outcome(errors=tuple(errors))
        finally:
            os.unlink(path)

    def parse(self, items, *, jobs=1):
        with ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
            outcomes = list(ex.map(lambda it: self._run_one(it[1]), items))
        return {item_id: o for (item_id, _), o in zip(items, outcomes, strict=True)}
