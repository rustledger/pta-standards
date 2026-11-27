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

Semantic mode (`JsonlImplementation.snapshots`, the semantic differential)
uses the same framing. An input may hold several files: the main file's text
is `text`, its name `main`, and every other file is in `files`, by path
relative to the main file's directory (an `include` in the main file names
them)::

    {"id": "...", "text": "include \"a.beancount\"\n", "main": "main.beancount",
     "files": {"a.beancount": "2024-01-01 open Assets:A\n"}}

and the answer is the ledger's snapshot (`ptadiff-snapshot/1`,
`SNAPSHOT.md`), or why there is none (the implementation crashed on it: a
finding, never a match)::

    {"id": "...", "snapshot": {"errors": [...], "entries": [...], "balances": {...}, "options": {...}}}
    {"id": "...", "crash": "panicked: ..."}
"""

from __future__ import annotations

import json
import shlex
import subprocess
from collections.abc import Sequence
from typing import Any

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
        return parse_output(self._call(payload), [i for i, _ in items], self.name)

    def _call(self, payload: str) -> str:
        proc = subprocess.run(
            self.argv, input=payload.encode("utf-8"), capture_output=True, check=False
        )
        if proc.returncode != 0:
            raise ProtocolError(
                f"{self.name} exited {proc.returncode}:\n"
                + proc.stderr.decode("utf-8", "replace")[-4000:]
            )
        return proc.stdout.decode("utf-8")

    def snapshots(
        self, items: Sequence[tuple[str, Any]], *, main: str, jobs: int = 1, batch: int = 500
    ) -> dict[str, Any]:
        """`{id: snapshot dict, or the crash message as a str}` for every
        `(id, Ledger)`, in semantic mode: one process per `batch` inputs, up
        to `jobs` of them at once. Results do not depend on `jobs`."""
        chunks = [items[s : s + batch] for s in range(0, len(items), batch)]

        def one(chunk):
            payload = "".join(
                json.dumps(led.to_json(i, main), ensure_ascii=False) + "\n" for i, led in chunk
            )
            return parse_snapshots(self._call(payload), [i for i, _ in chunk], self.name)

        out: dict[str, Any] = {}
        if jobs <= 1 or len(chunks) <= 1:
            for c in chunks:
                out.update(one(c))
            return out
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=jobs) as pool:
            for part in pool.map(one, chunks):
                out.update(part)
        return out


def _lines(stdout: str) -> list[str]:
    # `\n` only: `str.splitlines` also splits at U+2028 and friends, which a
    # JSON encoder may leave unescaped inside a message.
    lines = stdout.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def parse_snapshots(stdout: str, ids: Sequence[str], name: str = "implementation"):
    """The `{id: snapshot or crash str}` a semantic-mode `stdout` holds,
    checked against the `ids` it was sent, in order."""
    lines = _lines(stdout)
    if len(lines) != len(ids):
        raise ProtocolError(f"{name} answered {len(lines)} of {len(ids)} inputs")
    results: dict[str, Any] = {}
    for want, line in zip(ids, lines, strict=True):
        try:
            obj = json.loads(line)
            got = obj["id"]
            if "snapshot" in obj:
                value = obj["snapshot"]
                if not isinstance(value, dict):
                    raise TypeError("snapshot is not an object")
            else:
                value = str(obj["crash"])
        except (ValueError, KeyError, TypeError) as exc:
            raise ProtocolError(f"{name}: bad output line {line[:200]!r}: {exc}") from exc
        if got != want:
            raise ProtocolError(f"{name} answered {got!r} where {want!r} was next")
        results[got] = value
    return results


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
