"""Black-box oracle: run beancount's own lexer and parser on inputs.

Only the *public Python API* is used, as a black box:

* ``beancount.parser.lexer.lex_iter_string`` -> token stream
  ``(token_name, line, text, value)``;
* ``beancount.parser.parser.parse_string`` -> ``(entries, errors, options)``.

beancount can crash the whole interpreter on some inputs (a division by
zero inside an arithmetic expression segfaults 3.2.3), so every call runs in
a separate worker process.  Workers are long-lived and fed over a pipe; a
worker that dies takes only the input it was processing with it, which is
reported as ``crash``.

Run as a script, this module is the worker itself.
"""

from __future__ import annotations

import base64
import json
import os
import selectors
import subprocess
import sys
from collections import deque

# Interpreter that has beancount importable.  Defaults to the current one.
PYTHON = os.environ.get("BEANCOUNT_PYTHON", sys.executable)


def analyse(data: bytes) -> dict:
    """In-process oracle call (the worker body)."""
    from beancount.parser import lexer, parser

    toks = [(t[0], t[1]) for t in lexer.lex_iter_string(data)]
    _, errs, _ = parser.parse_string(data)
    syn = []
    other = []
    for e in errs:
        line = e.source.get("lineno") if isinstance(e.source, dict) else None
        if e.message.startswith("syntax error"):
            syn.append((line, e.message))
        else:
            other.append((line, type(e).__name__, e.message[:200]))
    return {"tokens": toks, "syntax": syn, "other": other}


def _worker_main() -> None:
    out = sys.stdout
    for line in sys.stdin:
        data = base64.b64decode(line)
        try:
            res = analyse(data)
            res["status"] = "ok"
        except Exception as ex:  # beancount raised: report, keep going
            res = {"status": "exception", "error": f"{type(ex).__name__}: {ex}"[:300]}
        out.write(json.dumps(res) + "\n")
        out.flush()


class OraclePool:
    """A pool of worker processes that survive beancount crashes."""

    def __init__(self, jobs: int | None = None):
        self.jobs = jobs or os.cpu_count() or 2

    def _spawn(self):
        return subprocess.Popen(
            [PYTHON, "-I", os.path.abspath(__file__)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=0,
        )

    def map(self, inputs: list[bytes]):
        """Yield ``(index, result)`` for every input, in completion order."""
        pending = deque(range(len(inputs)))
        sel = selectors.DefaultSelector()
        workers = {}

        def start(p=None):
            if not pending:
                if p is not None:
                    p.stdin.close()
                    p.wait()
                return
            if p is None:
                p = self._spawn()
                buf = bytearray()
                sel.register(p.stdout, selectors.EVENT_READ, (p, buf))
            i = pending.popleft()
            workers[p.pid] = i
            p.stdin.write(base64.b64encode(inputs[i]) + b"\n")
            p.stdin.flush()

        for _ in range(min(self.jobs, len(inputs))):
            start()
        while workers:
            for key, _ in sel.select():
                p, buf = key.data
                chunk = os.read(p.stdout.fileno(), 1 << 16)
                if not chunk:  # worker died
                    sel.unregister(p.stdout)
                    p.wait()
                    i = workers.pop(p.pid)
                    yield i, {"status": "crash", "error": f"worker exited with {p.returncode}"}
                    start()
                    continue
                buf.extend(chunk)
                while b"\n" in buf:
                    line, _, rest = bytes(buf).partition(b"\n")
                    buf[:] = rest
                    i = workers.pop(p.pid)
                    yield i, json.loads(line)
                    if pending:
                        start(p)
                    else:
                        sel.unregister(p.stdout)
                        p.stdin.close()
                        p.wait()
                        break


if __name__ == "__main__":
    _worker_main()
