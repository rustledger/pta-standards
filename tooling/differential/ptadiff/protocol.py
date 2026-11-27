"""The JSON-lines protocol between this package and an implementation under
test.

The implementation is a command. It reads its standard input as JSON lines,
one input per line::

    {"id": "3f2a9c0d1b7e", "text": "2024-01-01 open Assets:A\\n"}

and writes one JSON line per input to standard output, in the same order::

    {"id": "3f2a9c0d1b7e", "errors": [{"line": 1, "code": "P0003", "msg": "..."}]}

* `line` is 1-based, the line an editor would jump to; 0 means a file-level
  error with no line (an unclosed push at end of file, say).
* `code` is the implementation's own short error code; `msg` its message.
  Neither is compared verbatim: the comparison is by line and count, and the
  code only names a category.
* The command must answer every input, exit 0, and keep standard output free
  of anything else (diagnostics go to standard error).

Texts are whole files, any size, newlines included (JSON escapes them).
"""

from __future__ import annotations

import json
import shlex
import subprocess
from collections.abc import Sequence

from .model import Error


class ProtocolError(RuntimeError):
    """The implementation broke the protocol."""


class JsonlImplementation:
    """An implementation under test, run as `argv` over a batch of inputs."""

    def __init__(self, argv: Sequence[str] | str, name: str | None = None) -> None:
        self.argv = shlex.split(argv) if isinstance(argv, str) else list(argv)
        self.name = name or self.argv[0]

    def run(self, items: Sequence[tuple[str, str]]) -> dict[str, list[Error]]:
        """`{id: errors}` for every `(id, text)`: one process per batch."""
        if not items:
            return {}
        payload = "".join(json.dumps({"id": i, "text": t}) + "\n" for i, t in items)
        proc = subprocess.run(
            self.argv, input=payload.encode("utf-8"), capture_output=True, check=False
        )
        if proc.returncode != 0:
            raise ProtocolError(
                f"{self.name} exited {proc.returncode}:\n"
                + proc.stderr.decode("utf-8", "replace")[-4000:]
            )
        return parse_output(proc.stdout.decode("utf-8"), [i for i, _ in items], self.name)


def parse_output(stdout: str, ids: Sequence[str], name: str = "implementation"):
    """The `{id: errors}` an implementation's `stdout` holds, checked against
    the `ids` it was sent, in order."""
    results: dict[str, list[Error]] = {}
    # `\n` only: `str.splitlines` also splits at U+2028 and friends, which a
    # JSON encoder may leave unescaped inside a message.
    lines = stdout.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if len(lines) != len(ids):
        raise ProtocolError(f"{name} answered {len(lines)} of {len(ids)} inputs")
    for want, line in zip(ids, lines, strict=True):
        try:
            obj = json.loads(line)
            got = obj["id"]
            errors = [Error.from_json(e) for e in obj["errors"]]
        except (ValueError, KeyError, TypeError) as exc:
            raise ProtocolError(f"{name}: bad output line {line[:200]!r}: {exc}") from exc
        if got != want:
            raise ProtocolError(f"{name} answered {got!r} where {want!r} was next")
        results[got] = errors
    return results
