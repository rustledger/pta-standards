"""Semantic snapshots: what a ledger MEANS after a full load, format-generic.

The parse-error differential compares where two parsers report errors. A
semantic differential compares what two implementations make of a
well-formed ledger once it is loaded the whole way (booking, interpolation,
pads, balance checks, plugins, options, includes): the booked entries, the
final balance of every account, the options in effect, and the errors. Both
sides emit a *snapshot* in the schema documented in `SNAPSHOT.md`
(`ptadiff-snapshot/1`); this module canonicalizes two snapshots and finds
where they differ.

Nothing here knows any ledger format. A format plugin supplies the oracle
that produces the reference snapshot, the normalizers that remove its known
representation differences, and the key that names a difference
(`FormatPlugin.semantic_keys`).

Canonical form (`canonicalize`), applied to BOTH sides after their
normalizers:

* numbers are compared by value: each is parsed as a decimal, rounded to
  `SIGNIFICANT_DIGITS` significant digits (half-even) when it has more, and
  written without exponent or trailing zeros (`-0` is `0`). `10.00` and `10`
  are the same number; the scale an implementation keeps is compared, where
  it is observable at all, through `options.display_precision`;
* every unordered collection is sorted: errors, entries (by date, type,
  file, line, then content), tags, links, an open's currencies, an
  account's positions, the per-currency maps;
* postings keep their order: it is the order the entry holds them in, and
  booking that splits one posting over several lots inserts them in place.
"""

from __future__ import annotations

import contextlib
import json
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from decimal import Context, Decimal, InvalidOperation
from typing import Any

SCHEMA = "ptadiff-snapshot/1"

#: Numbers with more significant digits than this are rounded to it before
#: they are compared. Two decimal engines with different coefficient limits
#: (a 28-digit context and a 96-bit integer coefficient, say) disagree in the
#: last digits of a long quotient (a per-unit price from an `@@` total, a
#: tolerance derived from it); that is the engines, not the ledger. Twenty
#: digits is far past any amount a ledger states, and far short of either
#: engine's limit.
SIGNIFICANT_DIGITS = 20

#: The top-level fields of a snapshot, in the order a difference in them is
#: reported: an error is usually the cause of whatever else differs.
FIELDS = ("errors", "entries", "balances", "options")

#: Keys whose value is a number (or null), wherever they appear.
NUMBER_KEYS = frozenset({"number", "number_per", "number_total", "tolerance"})
#: Keys whose value is a `{currency: number}` map.
NUMBER_MAP_KEYS = frozenset({"tolerances", "inferred_tolerance_default"})
#: Option values that are numbers.
NUMBER_OPTIONS = frozenset({"tolerance_multiplier"})
#: List-valued keys whose order carries no meaning.
SET_KEYS = frozenset({"tags", "links", "currencies", "operating_currency"})

#: Within one date, the order entries are listed in (only to make the
#: canonical form readable; the comparison pairs entries by identity).
TYPE_ORDER = {
    t: n
    for n, t in enumerate(
        (
            "open",
            "balance",
            "commodity",
            "pad",
            "transaction",
            "price",
            "note",
            "event",
            "query",
            "custom",
            "document",
            "close",
        )
    )
}


def canonical_number(value: Any) -> str | None:
    """`value` (a number, a numeric string, or None) in canonical form."""
    if value is None:
        return None
    try:
        d = Decimal(str(value))
    except InvalidOperation:
        return str(value)
    if not d.is_finite():
        return str(d)
    if len(d.as_tuple().digits) > SIGNIFICANT_DIGITS:
        d = Context(prec=SIGNIFICANT_DIGITS).plus(d)
    d = d.normalize()
    if d.is_zero():
        return "0"
    return format(d, "f")


def _canon(value: Any, key: str = "") -> Any:
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k in NUMBER_KEYS:
                out[k] = canonical_number(v)
            elif k in NUMBER_MAP_KEYS and isinstance(v, dict):
                out[k] = {c: canonical_number(n) for c, n in sorted(v.items())}
            else:
                out[k] = _canon(v, k)
        return out
    if isinstance(value, list):
        items = [_canon(v) for v in value]
        if key in SET_KEYS:
            return sorted(items, key=_sort_text)
        return items
    return value


def _sort_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def entry_identity(entry: Mapping[str, Any]) -> tuple:
    """What pairs an entry with its counterpart on the other side: its
    type, date, and where it was written (an entry a plugin or a pad
    generates carries its source's location, so two generated entries of
    one source are told apart by their order in the canonical list)."""
    return (
        entry.get("type", ""),
        entry.get("date", ""),
        entry.get("file", ""),
        entry.get("line", 0),
    )


def _entry_sort_key(entry: Mapping[str, Any]) -> tuple:
    return (
        entry.get("date", ""),
        TYPE_ORDER.get(entry.get("type", ""), len(TYPE_ORDER)),
        entry.get("file", ""),
        entry.get("line", 0),
        _sort_text(entry),
    )


def canonicalize(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """`snapshot` in canonical form (see the module docstring)."""
    errors = sorted(
        (
            {
                "file": e.get("file", ""),
                "line": int(e.get("line") or 0),
                "code": str(e.get("code", "")),
                "msg": str(e.get("msg", "")),
            }
            for e in snapshot.get("errors", [])
        ),
        key=lambda e: (e["file"], e["line"], e["code"], e["msg"]),
    )
    entries = sorted((_canon(e) for e in snapshot.get("entries", [])), key=_entry_sort_key)
    balances = {}
    for account, positions in sorted((snapshot.get("balances") or {}).items()):
        ps = sorted((_canon(p) for p in positions), key=_sort_text)
        ps = [p for p in ps if (p.get("units") or {}).get("number") not in ("0", None)]
        if ps:
            balances[account] = ps
    options = {}
    for k, v in sorted((snapshot.get("options") or {}).items()):
        if k in NUMBER_OPTIONS:
            options[k] = canonical_number(v)
        elif k == "display_precision" and isinstance(v, dict):
            options[k] = {c: dict(sorted(p.items())) for c, p in sorted(v.items())}
        else:
            options[k] = _canon(v, k)
    return {"errors": errors, "entries": entries, "balances": balances, "options": options}


# -- differences --------------------------------------------------------------


@dataclass(frozen=True)
class FieldDiff:
    """One place two canonical snapshots differ.

    * `field`: the snapshot field (`errors`, `entries`, `balances`,
      `options`);
    * `path`: what differs inside it, with list indices dropped so it names
      a construct, not a position (`postings.cost.number`,
      `missing-in-impl`, `impl-more`, `units`);
    * `kind`: the directive type it is in (`transaction`, `balance`, ...),
      `account` for a balance, the option's name for an option, `-` else;
    * `file`, `line`: where, when it has a location (an entry's, an
      error's), else `""` and 0;
    * `subject`: the account, option or error location it is about;
    * `oracle`, `impl`: the two values (None where one side has nothing).
    """

    field: str
    path: str
    kind: str
    file: str = ""
    line: int = 0
    subject: str = ""
    oracle: Any = None
    impl: Any = None
    #: The index of the posting the difference is in, when it is in one.
    posting: int | None = None


def _leaf_diff(a: Any, b: Any, path: str = "") -> tuple[str, Any, Any, int | None] | None:
    """The first leaf where `a` and `b` differ: `(path, a_leaf, b_leaf,
    posting_index)`, or None when they are equal."""
    if a == b:
        return None
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=lambda k: (k == "postings", k)):
            if a.get(k) != b.get(k):
                sub = _leaf_diff(a.get(k), b.get(k), f"{path}.{k}" if path else k)
                if sub is not None:
                    return sub
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return (f"{path}.count", len(a), len(b), None)
        if Counter(map(_sort_text, a)) == Counter(map(_sort_text, b)):
            return (f"{path}.order", a, b, None)
        for n, (x, y) in enumerate(zip(a, b, strict=True)):
            sub = _leaf_diff(x, y, path)
            if sub is not None:
                p, xa, yb, idx = sub
                return (p, xa, yb, n if path == "postings" and idx is None else idx)
        return None
    return (path or "value", a, b, None)


def _paired(entries: Iterable[Mapping[str, Any]]) -> dict[tuple, Mapping[str, Any]]:
    seen: Counter[tuple] = Counter()
    out = {}
    for e in entries:
        ident = entry_identity(e)
        out[(*ident, seen[ident])] = e
        seen[ident] += 1
    return out


def _loc_order(file: str, line: int) -> tuple:
    # A location-less (line 0) item sorts after every located one.
    return (line == 0, file, line)


#: How two snapshots' errors are compared (`error_diffs`):
#:
#: * `lines` (the default): by the SET of locations with an error. A
#:   location one side flags and the other does not is a difference; how
#:   many errors each side reports there is not. One fault yields different
#:   counts on different implementations as a matter of reporting style
#:   (beancount reports an unknown account in a `balance` three times, an
#:   implementation may report it once, and one implementation reports
#:   each unbalanced currency where another lists them in one message),
#:   while whether a directive is in error is what the ledger means.
#: * `counts`: by the number of errors per location, as the parse
#:   differential compares.
ERROR_MODES = ("lines", "counts")


def error_diffs(
    oracle: Mapping[str, Any], impl: Mapping[str, Any], mode: str = "lines"
) -> list[FieldDiff]:
    if mode not in ERROR_MODES:
        raise ValueError(f"unknown error mode {mode!r}")
    a = Counter((e["file"], e["line"]) for e in oracle["errors"])
    b = Counter((e["file"], e["line"]) for e in impl["errors"])
    if mode == "lines":
        a, b = Counter(set(a)), Counter(set(b))
    out = []
    for f, ln in sorted(set(a) | set(b), key=lambda fl: _loc_order(*fl)):
        if a[(f, ln)] != b[(f, ln)]:
            side = "impl-more" if b[(f, ln)] > a[(f, ln)] else "impl-fewer"
            out.append(
                FieldDiff(
                    "errors",
                    side,
                    "-",
                    f,
                    ln,
                    f"{f}:{ln}",
                    [e for e in oracle["errors"] if (e["file"], e["line"]) == (f, ln)],
                    [e for e in impl["errors"] if (e["file"], e["line"]) == (f, ln)],
                )
            )
    return out


def entry_diffs(oracle: Mapping[str, Any], impl: Mapping[str, Any]) -> list[FieldDiff]:
    a, b = _paired(oracle["entries"]), _paired(impl["entries"])
    found = []
    for ident in set(a) | set(b):
        ea, eb = a.get(ident), b.get(ident)
        kind, date, f, ln = ident[:4]
        if ea is None or eb is None:
            path = "extra-in-impl" if ea is None else "missing-in-impl"
            found.append((date, f, ln, FieldDiff("entries", path, kind, f, ln, kind, ea, eb)))
            continue
        d = _leaf_diff(ea, eb)
        if d is not None:
            path, va, vb, posting = d
            subject = (
                (ea.get("account") or ea.get("currency") or kind)
                if posting is None
                else (
                    (ea.get("postings") or [{}])[posting].get("account", "")
                    if posting < len(ea.get("postings") or [])
                    else ""
                )
            )
            found.append(
                (date, f, ln, FieldDiff("entries", path, kind, f, ln, subject, va, vb, posting))
            )
    found.sort(key=lambda t: (t[0], *_loc_order(t[1], t[2]), t[3].path))
    return [d for *_, d in found]


def _units_by_currency(positions: list[Mapping[str, Any]]) -> dict[str, Decimal]:
    out: dict[str, Decimal] = {}
    for p in positions:
        u = p.get("units") or {}
        with contextlib.suppress(InvalidOperation):
            out[u.get("currency", "")] = out.get(u.get("currency", ""), Decimal(0)) + Decimal(
                u.get("number") or 0
            )
    return {c: n for c, n in out.items() if n}


def balance_diffs(oracle: Mapping[str, Any], impl: Mapping[str, Any]) -> list[FieldDiff]:
    a, b = oracle["balances"], impl["balances"]
    out = []
    for account in sorted(set(a) | set(b)):
        pa, pb = a.get(account), b.get(account)
        if pa == pb:
            continue
        if pa is None or pb is None:
            path = "extra-in-impl" if pa is None else "missing-in-impl"
        elif _units_by_currency(pa) != _units_by_currency(pb):
            path = "units"
        else:
            path = "lots"
        out.append(FieldDiff("balances", path, "account", subject=account, oracle=pa, impl=pb))
    return out


def option_diffs(oracle: Mapping[str, Any], impl: Mapping[str, Any]) -> list[FieldDiff]:
    a, b = oracle["options"], impl["options"]
    out = []
    for name in sorted(set(a) | set(b)):
        if name not in a or name not in b:
            # An option one side does not report is not observable there.
            continue
        if a[name] != b[name]:
            path = name
            if isinstance(a[name], dict) and isinstance(b[name], dict):
                sub = sorted(
                    k for k in set(a[name]) | set(b[name]) if a[name].get(k) != b[name].get(k)
                )
                path = f"{name}.{sub[0]}" if sub else name
                if name == "display_precision" and sub:
                    path = name  # per-currency: the currency names no construct
            out.append(FieldDiff("options", path, name, subject=name, oracle=a[name], impl=b[name]))
    return out


DIFFERS: dict[str, Callable[[Mapping[str, Any], Mapping[str, Any]], list[FieldDiff]]] = {
    "errors": error_diffs,
    "entries": entry_diffs,
    "balances": balance_diffs,
    "options": option_diffs,
}


def _field_diffs(f: str, oracle, impl, error_mode: str) -> list[FieldDiff]:
    if f == "errors":
        return error_diffs(oracle, impl, error_mode)
    return DIFFERS[f](oracle, impl)


def diffs(
    oracle: Mapping[str, Any],
    impl: Mapping[str, Any],
    fields: Iterable[str] = FIELDS,
    *,
    error_mode: str = "lines",
) -> list[FieldDiff]:
    """Every difference between two CANONICAL snapshots, field by field in
    `fields` order, each field's in location order."""
    out: list[FieldDiff] = []
    for f in fields:
        out += _field_diffs(f, oracle, impl, error_mode)
    return out


def first_diff(
    oracle: Mapping[str, Any],
    impl: Mapping[str, Any],
    fields: Iterable[str] = FIELDS,
    *,
    error_mode: str = "lines",
) -> FieldDiff | None:
    """The difference to read first: the first of `diffs`. An error
    difference comes before the entries it explains, an entry difference
    before the balances it leads to."""
    for f in fields:
        found = _field_diffs(f, oracle, impl, error_mode)
        if found:
            return found[0]
    return None


# -- inputs -------------------------------------------------------------------


@dataclass(frozen=True)
class Ledger:
    """A semantic input: the main file's text and, for a multi-file input,
    the other files by path relative to the main file's directory (which an
    include in the main file names)."""

    text: str
    files: Mapping[str, str] = field(default_factory=dict)

    def to_json(self, ident: str, main: str) -> dict[str, Any]:
        obj: dict[str, Any] = {"id": ident, "text": self.text, "main": main}
        if self.files:
            obj["files"] = dict(sorted(self.files.items()))
        return obj

    @classmethod
    def from_json(cls, obj: Mapping[str, Any]) -> Ledger:
        return cls(obj["text"], dict(obj.get("files") or {}))

    def with_text(self, text: str) -> Ledger:
        return Ledger(text, self.files)

    def with_file(self, path: str, text: str) -> Ledger:
        return Ledger(self.text, {**self.files, path: text})

    @property
    def size(self) -> int:
        return len(self.text) + sum(len(t) for t in self.files.values())

    def render(self, main: str) -> str:
        """All files as one text, each headed by its path: for reports."""
        if not self.files:
            return self.text
        parts = [f";; ==> {main}\n{self.text}"]
        parts += [f";; ==> {p}\n{t}" for p, t in sorted(self.files.items())]
        return "\n".join(parts)


def ledger_id(ledger: Ledger) -> str:
    """A ledger's content id: `content_id(text)` for a single file (so a
    one-file ledger has the id the parse differential gives it), a hash of
    every file for a multi-file one."""
    from .model import content_id

    if not ledger.files:
        return content_id(ledger.text)
    return content_id(json.dumps([ledger.text, sorted(ledger.files.items())], ensure_ascii=False))
