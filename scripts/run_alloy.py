#!/usr/bin/env python3
"""Run every command of every Alloy model and judge the outcomes.

Alloy's ``exec`` CLI exits 0 whether or not a ``check`` finds a
counterexample, so its exit code only tells us the model compiled. The
verdict comes from ``receipt.json``: a command whose entry carries a
``solution`` key was satisfiable (a ``run`` found an instance, a ``check``
found a counterexample); a command without one was unsatisfiable within its
scope.

Expected outcome of each command:

* ``check``  -- no counterexample (UNSAT), unless the command says ``expect 1``.
* ``run``    -- an instance exists (SAT), unless the command says ``expect 0``.

A command listed in the known-failures file (see ``KNOWN_FAILURES`` below) is
allowed to have the unexpected outcome; it is reported as XFAIL. If it starts
behaving as expected it is reported as XPASS and fails the job, so the list
cannot go stale silently.

Usage: run_alloy.py --jar alloy.jar [--known-failures FILE] [model.als ...]
With no models, every ``*.als`` under the repository root is run.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWN_FAILURES = ROOT / "scripts" / "alloy-known-failures.txt"
MODEL_TIMEOUT_S = 600
COMMAND_LINE = re.compile(r"^\d+ ?\. (Check|Run) ")  # "9 . Run", "10. Run"


@dataclass
class Result:
    model: str
    command: str
    kind: str
    source: str
    verdict: str  # PASS, FAIL, XFAIL, XPASS, ERROR
    detail: str
    seconds: float | None = None


def load_known_failures(path: Path) -> dict[tuple[str, str], str]:
    """Parse ``<model path> <command name>  # reason`` lines."""
    known: dict[tuple[str, str], str] = {}
    if not path.exists():
        return known
    for lineno, raw in enumerate(path.read_text().splitlines(), 1):
        line, _, reason = raw.partition("#")
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            sys.exit(f"{path}:{lineno}: expected '<model.als> <command>', got {raw!r}")
        known[(parts[0], parts[1])] = reason.strip()
    return known


def java(jar: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["java", "-jar", jar, *args],
        capture_output=True,
        text=True,
        timeout=MODEL_TIMEOUT_S,
    )


def first_error(text: str) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("\tat ")]
    return " ".join(lines[1:4] if len(lines) > 1 else lines)[:400]


def run_model(jar: str, model: Path, known: dict[tuple[str, str], str]) -> list[Result]:
    rel = model.relative_to(ROOT).as_posix()

    listing = java(jar, "commands", str(model))
    if listing.returncode != 0:
        return [
            Result(
                rel,
                "-",
                "-",
                "-",
                "ERROR",
                "does not compile: " + first_error(listing.stderr + listing.stdout),
            )
        ]
    declared = [ln for ln in listing.stdout.splitlines() if COMMAND_LINE.match(ln)]

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        start = time.monotonic()
        # -n: discard instances in which integer arithmetic overflowed, so a
        # wrapped-around sum cannot masquerade as a counterexample or example.
        proc = java(
            jar, "exec", "-q", "-f", "-n", "-c", "*", "-t", "json", "-o", str(out), str(model)
        )
        elapsed = time.monotonic() - start
        if proc.returncode != 0:
            return [
                Result(
                    rel,
                    "-",
                    "-",
                    "-",
                    "ERROR",
                    "exec failed: " + first_error(proc.stderr + proc.stdout),
                )
            ]
        if not declared:
            return [Result(rel, "-", "-", "-", "PASS", "compiles; declares no commands", elapsed)]
        receipt = json.loads((out / "receipt.json").read_text())

    commands = receipt.get("commands", {})
    results: list[Result] = []
    if len(commands) != len(declared):
        # receipt.json is keyed by command name, so two commands with the same
        # name (e.g. `check A for 3` and `check A for 5`) overwrite each other.
        results.append(
            Result(
                rel,
                "-",
                "-",
                "-",
                "ERROR",
                f"{len(declared)} commands declared but {len(commands)} in receipt; "
                "give every command a distinct name",
            )
        )

    for name, cmd in commands.items():
        kind = cmd["type"]
        sat = "solution" in cmd
        expects = cmd.get("expects", -1)
        want_sat = (expects == 1) if expects in (0, 1) else (kind == "run")
        if kind == "check":
            outcome = "counterexample found" if sat else "no counterexample"
        else:
            outcome = "instance found" if sat else "no instance"
        ok = sat == want_sat
        reason = known.get((rel, name))
        if reason is not None:
            verdict = "XPASS" if ok else "XFAIL"
            detail = outcome + (
                " -- listed as a known failure but now passes; remove it"
                if ok
                else f" (known: {reason})"
            )
        else:
            verdict = "PASS" if ok else "FAIL"
            detail = outcome
        results.append(Result(rel, name, kind, cmd.get("source", ""), verdict, detail))
    if results:
        results[-1].seconds = elapsed
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", required=True)
    ap.add_argument("--known-failures", type=Path, default=KNOWN_FAILURES)
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("models", nargs="*", type=Path)
    args = ap.parse_args()

    known = load_known_failures(args.known_failures)
    models = [m.resolve() for m in args.models] or sorted(
        p for p in ROOT.rglob("*.als") if "node_modules" not in p.parts
    )
    filtered = bool(args.models)

    def guarded(model: Path) -> list[Result]:
        try:
            return run_model(args.jar, model, known)
        except subprocess.TimeoutExpired:
            rel = model.relative_to(ROOT).as_posix()
            return [Result(rel, "-", "-", "-", "ERROR", f"timed out after {MODEL_TIMEOUT_S}s")]

    results: list[Result] = []
    # Models are independent; run them concurrently (one JVM each).
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        per_model = list(pool.map(guarded, models))
    for rs in per_model:
        for r in rs:
            secs = f" [{r.seconds:.1f}s]" if r.seconds is not None else ""
            print(f"{r.verdict:5} {r.model} {r.command}: {r.detail}{secs}", flush=True)
            if r.verdict in ("FAIL", "ERROR", "XPASS") and os.environ.get("GITHUB_ACTIONS"):
                print(f"::error file={r.model}::{r.command}: {r.detail}")
        results.extend(rs)

    ran = {(r.model, r.command) for r in results}
    if not filtered:
        for model, command in sorted(set(known) - ran):
            r = Result(
                model,
                command,
                "-",
                "-",
                "ERROR",
                "listed in known failures but no such command ran",
            )
            print(f"{r.verdict:5} {r.model} {r.command}: {r.detail}")
            results.append(r)

    bad = [r for r in results if r.verdict in ("FAIL", "ERROR", "XPASS")]
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        icon = {"PASS": "✅", "XFAIL": "⚠️", "FAIL": "❌", "XPASS": "❌", "ERROR": "❌"}
        with open(summary, "a") as fh:
            counts = {v: sum(r.verdict == v for r in results) for v in icon}
            fh.write("## Alloy model verification\n\n")
            fh.write(" · ".join(f"{v}: {n}" for v, n in counts.items() if n) + "\n\n")
            fh.write("| | Model | Command | Source | Outcome |\n|---|---|---|---|---|\n")
            for r in results:
                src = r.source.replace("|", "\\|")
                fh.write(
                    f"| {icon[r.verdict]} {r.verdict} | `{r.model}` | `{r.command}` | `{src}` | {r.detail} |\n"
                )
    print(f"\n{len(results)} results, {len(bad)} failing")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
