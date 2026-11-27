"""Run a function over many inputs in forked workers that may crash.

An in-process oracle (a C parser behind a Python API) can segfault, loop, or
raise on hostile input. Each worker is a `fork()` of the caller, so whatever
the caller imported is already loaded and nothing is pickled: `fn` may be any
callable, closures included. A worker that dies loses only the input it was
on, which is reported as a crash; a fresh worker takes the rest of its share.

POSIX only (it needs `fork`).
"""

from __future__ import annotations

import faulthandler
import json
import os
import resource
import selectors
import signal
from collections.abc import Callable, Sequence
from typing import Any

#: A single input that runs longer than this (seconds) is a crash.
DEFAULT_TIMEOUT_S = 20


class Crash:
    """Why an input has no result."""

    __slots__ = ("why",)

    def __init__(self, why: str) -> None:
        self.why = why

    def __repr__(self) -> str:
        return f"Crash({self.why!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Crash) and other.why == self.why

    def __hash__(self) -> int:
        return hash(self.why)


def _worker(items: Sequence[tuple[str, Any]], fn, timeout: int, wfd: int) -> None:
    with os.fdopen(wfd, "w", encoding="utf-8") as w:
        for item_id, payload in items:
            signal.alarm(timeout)
            try:
                record = {"ok": fn(payload)}
            except Exception as exc:  # the oracle raised: no result
                record = {"crash": f"raised {type(exc).__name__}: {exc}"}
            signal.alarm(0)
            w.write(json.dumps([item_id, record]) + "\n")
            w.flush()


def _spawn(items, fn, timeout):
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:  # pragma: no cover - runs in the child
        os.close(r)
        code = 3
        try:
            # A segfaulting oracle is an expected outcome here, so a core file
            # is pure waste (tens of MB each, thousands per fuzz run).
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            # Nor a faulthandler traceback (pytest enables it) per segfault.
            faulthandler.disable()
            _worker(items, fn, timeout, w)
            code = 0
        finally:
            # Never return into the parent's code from the child.
            os._exit(code)
    os.close(w)
    return pid, os.fdopen(r, "rb")


def run_forked(
    items: Sequence[tuple[str, Any]],
    fn: Callable[[Any], Any],
    *,
    jobs: int = 1,
    timeout: int = DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """`{id: fn(payload)}` for every `(id, payload)` in `items`, computed in
    up to `jobs` forked workers; an input whose worker died, raised, or ran
    past `timeout` seconds maps to a `Crash` instead.

    `fn` must return something JSON-serializable. Ids must be unique.
    Results do not depend on `jobs`.
    """
    results: dict[str, Any] = {}
    jobs = max(1, min(jobs, len(items)))
    sel = selectors.DefaultSelector()

    def start(share):
        pid, f = _spawn(share, fn, timeout)
        # state: pid, share, how many answered, partial line
        sel.register(f, selectors.EVENT_READ, [pid, share, 0, b""])

    for i in range(jobs):
        share = list(items[i::jobs])
        if share:
            start(share)
    while sel.get_map():
        for key, _ in sel.select():
            f, state = key.fileobj, key.data
            chunk = os.read(f.fileno(), 1 << 16)  # type: ignore[union-attr]
            if chunk:
                state[3] += chunk
                *lines, state[3] = state[3].split(b"\n")
                for line in lines:
                    item_id, record = json.loads(line)
                    expected = state[1][state[2]][0]
                    if item_id != expected:
                        raise RuntimeError(f"worker answered {item_id}, expected {expected}")
                    results[item_id] = record["ok"] if "ok" in record else Crash(record["crash"])
                    state[2] += 1
                continue
            sel.unregister(f)
            f.close()  # type: ignore[union-attr]
            _, status = os.waitpid(state[0], 0)
            done, share = state[2], state[1]
            if done < len(share):
                if os.WIFSIGNALED(status):
                    why = f"killed by {signal.Signals(os.WTERMSIG(status)).name}"
                else:
                    why = f"exited {os.WEXITSTATUS(status)}"
                results[share[done][0]] = Crash(why)
                rest = share[done + 1 :]
                if rest:
                    start(rest)
            elif not os.WIFEXITED(status) or os.WEXITSTATUS(status) != 0:
                raise RuntimeError(f"a worker failed after finishing its share: {status}")
    return results
