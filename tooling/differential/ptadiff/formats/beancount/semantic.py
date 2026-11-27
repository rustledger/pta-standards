"""beancount as a SEMANTIC oracle: the snapshot of a fully loaded ledger.

Through beancount's public API only: `beancount.loader.load_file` loads the
ledger the whole way (parse, includes, options, plugins, booking,
interpolation, pads, validation), and the returned entries, errors and
options map are read as data. Inventories are summed with
`beancount.core.inventory.Inventory`. Nothing here reads, copies or
re-implements beancount's code.

Each input is written to a fresh temporary directory (the main file and any
included files at their relative paths) and loaded from there, in a forked,
crash-isolated worker (`ptadiff.pool.run_forked`), with beancount's pickle
cache off. Every path in the snapshot is made relative to that directory;
a placeholder location (`<auto_accounts>`) is kept as it is.

The snapshot is `ptadiff-snapshot/1` (`SNAPSHOT.md`), RAW: numbers are
beancount's decimals as strings and nothing is sorted. ptadiff canonicalizes
both sides the same way (`ptadiff.snapshot.canonicalize`).
"""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any

from ...pool import DEFAULT_TIMEOUT_S, Crash, run_forked

#: The main file's name in the temporary directory.
MAIN = "main.beancount"


def _num(n: Any) -> str | None:
    from decimal import Decimal

    return str(n) if isinstance(n, Decimal) else None


def _date(d: Any) -> str | None:
    return d.isoformat() if d is not None and hasattr(d, "isoformat") else None


def _amount(a: Any) -> dict | None:
    if a is None or not hasattr(a, "currency"):
        return None
    cur = a.currency if isinstance(a.currency, str) else None
    return {"number": _num(a.number), "currency": cur}


def _cost(c: Any) -> dict | None:
    from beancount.core import data

    if c is None:
        return None
    if isinstance(c, data.Cost):
        return {
            "number": _num(c.number),
            "currency": c.currency,
            "date": _date(c.date),
            "label": c.label,
        }
    # A cost spec booking did not resolve (only on an entry it refused).
    cur = getattr(c, "currency", None)
    return {
        "spec": True,
        "number_per": _num(getattr(c, "number_per", None)),
        "number_total": _num(getattr(c, "number_total", None)),
        "currency": cur if isinstance(cur, str) else None,
        "date": _date(getattr(c, "date", None)),
        "label": getattr(c, "label", None),
        "merge": bool(getattr(c, "merge", False)),
    }


class _Paths:
    def __init__(self, root: str) -> None:
        self.root = os.path.realpath(root)

    def rel(self, filename: Any) -> str:
        if not filename:
            return ""
        filename = str(filename)
        if filename.startswith("<"):
            return filename
        real = os.path.realpath(filename)
        if real == self.root or real.startswith(self.root + os.sep):
            return os.path.relpath(real, self.root).replace(os.sep, "/")
        return filename


def _loc(meta: Any, paths: _Paths) -> tuple[str, int]:
    meta = meta or {}
    try:
        line = int(meta.get("lineno") or 0)
    except (TypeError, ValueError):
        line = 0
    return paths.rel(meta.get("filename")), line


def _entry(e: Any, paths: _Paths) -> dict[str, Any]:
    from beancount.core import data

    file, line = _loc(e.meta, paths)
    base: dict[str, Any] = {"date": _date(e.date), "file": file, "line": line}
    if isinstance(e, data.Transaction):
        out = {
            "type": "transaction",
            **base,
            "flag": e.flag,
            "payee": e.payee,
            "narration": e.narration,
            "tags": sorted(e.tags or ()),
            "links": sorted(e.links or ()),
            "postings": [
                {
                    "account": p.account,
                    "units": _amount(p.units),
                    "cost": _cost(p.cost),
                    "price": _amount(p.price),
                    "flag": p.flag,
                }
                for p in e.postings
            ],
        }
        tol = (e.meta or {}).get("__tolerances__")
        if isinstance(tol, Mapping):
            # A currency booking could not name (`MISSING`) is no currency.
            out["tolerances"] = {c: _num(n) for c, n in tol.items() if isinstance(c, str)}
        return out
    if isinstance(e, data.Open):
        return {
            "type": "open",
            **base,
            "account": e.account,
            "currencies": sorted(e.currencies or ()),
            "booking": e.booking.name if e.booking is not None else None,
        }
    if isinstance(e, data.Close):
        return {"type": "close", **base, "account": e.account}
    if isinstance(e, data.Commodity):
        return {"type": "commodity", **base, "currency": e.currency}
    if isinstance(e, data.Pad):
        return {"type": "pad", **base, "account": e.account, "source_account": e.source_account}
    if isinstance(e, data.Balance):
        return {
            "type": "balance",
            **base,
            "account": e.account,
            "amount": _amount(e.amount),
            "tolerance": _num(e.tolerance),
        }
    if isinstance(e, data.Price):
        return {"type": "price", **base, "currency": e.currency, "amount": _amount(e.amount)}
    if isinstance(e, data.Note):
        return {"type": "note", **base, "account": e.account, "comment": e.comment}
    if isinstance(e, data.Event):
        return {"type": "event", **base, "event": e.type, "description": e.description}
    if isinstance(e, data.Query):
        return {"type": "query", **base, "name": e.name, "query": e.query_string}
    if isinstance(e, data.Document):
        return {
            "type": "document",
            **base,
            "account": e.account,
            "filename": paths.rel(e.filename),
        }
    if isinstance(e, data.Custom):
        return {"type": "custom", **base, "custom": e.type, "values": len(e.values or ())}
    return {"type": type(e).__name__.lower(), **base}


def _balances(entries: Sequence[Any]) -> dict[str, list[dict]]:
    from beancount.core import data
    from beancount.core.inventory import Inventory

    invs: dict[str, Any] = {}
    for e in entries:
        if not isinstance(e, data.Transaction):
            continue
        for p in e.postings:
            u = p.units
            if u is None or _num(getattr(u, "number", None)) is None:
                continue
            if not isinstance(u.currency, str):
                continue
            cost = p.cost if isinstance(p.cost, data.Cost) else None
            invs.setdefault(p.account, Inventory()).add_amount(u, cost)
    return {
        account: [{"units": _amount(pos.units), "cost": _cost(pos.cost)} for pos in inv]
        for account, inv in invs.items()
    }


def _display_precision(dcontext: Any) -> dict[str, dict[str, int | None]]:
    from beancount.core.display_context import Precision

    out = {}
    for cur, ctx in sorted(getattr(dcontext, "ccontexts", {}).items()):
        if cur.startswith("__"):
            continue
        fixed = getattr(ctx, "fractional_digits", None)
        if fixed is not None:
            # `option "display_precision"`: one precision under any policy.
            out[cur] = {"common": fixed, "max": fixed}
            continue
        out[cur] = {
            "common": ctx.get_fractional(Precision.MOST_COMMON),
            "max": ctx.get_fractional(Precision.MAXIMUM),
        }
    return out


def _options(options: Mapping[str, Any]) -> dict[str, Any]:
    booking = options.get("booking_method")
    return {
        "operating_currency": list(options.get("operating_currency") or []),
        "booking_method": getattr(booking, "name", None) if booking is not None else None,
        "inferred_tolerance_default": {
            str(c): _num(n) for c, n in (options.get("inferred_tolerance_default") or {}).items()
        },
        "tolerance_multiplier": _num(
            options.get("tolerance_multiplier", options.get("inferred_tolerance_multiplier"))
        ),
        "infer_tolerance_from_cost": bool(options.get("infer_tolerance_from_cost")),
        "display_precision": _display_precision(options.get("dcontext")),
    }


def snapshot_of(entries, errors, options, root: str) -> dict[str, Any]:
    """The raw snapshot of one `load_file` result; paths relative to `root`."""
    paths = _Paths(root)
    errs = []
    for e in errors:
        file, line = _loc(getattr(e, "source", None), paths)
        errs.append({"file": file, "line": line, "code": type(e).__name__, "msg": str(e.message)})
    return {
        "errors": errs,
        "entries": [_entry(e, paths) for e in entries],
        "balances": _balances(entries),
        "options": _options(options),
    }


def write_ledger(root: str, main: str, text: str, files: Mapping[str, str]) -> str:
    """Write the input under `root`; the main file's path."""
    for rel, body in {**files, main: text}.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path) or root, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(body)
    return os.path.join(root, main)


def _load_one(payload: Mapping[str, Any]) -> dict[str, Any]:
    from beancount import loader

    root = tempfile.mkdtemp(prefix="ptadiff-")
    try:
        main = write_ledger(
            root, payload.get("main") or MAIN, payload["text"], payload.get("files") or {}
        )
        entries, errors, options = loader.load_file(main)
        return snapshot_of(entries, errors, options, root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


class BeancountSemanticOracle:
    """beancount's full loader. `version` pins the release expected."""

    name = "beancount"

    def __init__(self, version: str | None = None, timeout: int = DEFAULT_TIMEOUT_S) -> None:
        self.expected_version = version
        self.timeout = timeout
        self._version: str | None = None

    def version(self) -> str:
        if self._version is None:
            # Imported in the parent, so every forked worker inherits them
            # (and the plugins beancount ships, which a ledger may name).
            import beancount
            import beancount.core.inventory
            import beancount.loader
            import beancount.plugins

            beancount.loader.initialize(use_cache=False)
            self._version = beancount.__version__
            if self.expected_version and self._version != self.expected_version:
                raise RuntimeError(
                    f"beancount {self._version} is installed, {self.expected_version} expected"
                )
        return self._version

    def snapshot(self, items, *, jobs: int = 1) -> dict[str, dict | Crash]:
        """`{id: raw snapshot or Crash}` for every `(id, Ledger)`."""
        self.version()
        payloads = [
            (i, {"text": led.text, "files": dict(led.files), "main": MAIN}) for i, led in items
        ]
        return run_forked(payloads, _load_one, jobs=jobs, timeout=self.timeout)
