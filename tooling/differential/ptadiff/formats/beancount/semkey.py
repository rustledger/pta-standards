"""The beancount format's semantic normalizers, features and category key.

Normalizers (`SEMANTIC_NORMALIZERS`, all on by default; each a named rewrite
of a canonical snapshot, applied to the side(s) it names):

* `error-at-directive` (both): an error is placed on the first line of the
  directive it is in. beancount locates some errors at a posting
  (`CategorizationError` at the posting's line) and others at the entry;
  an implementation may choose either. Where in a directive an error is
  reported is presentation; which directive has it is semantics.
* `drop-errored-entries` (both): an entry with an error of the same side
  inside its lines is left out of `entries`. beancount drops an entry its
  parser or booking refuses (an `open` of an invalid account name, a
  `balance` with a syntax error, a transaction booking cannot resolve), or
  keeps it emptied, depending on the error; an implementation may keep it
  as written. Its errors are compared (they come first); its form is not,
  because there is none to agree on. Entries a load generates (located
  nowhere) are kept.
* `placeholder-locations` (both): an entry or error located nowhere in the
  input (beancount's `<auto_accounts>`, `<load>`, any `<...>` name, with
  whatever line the plugin gave it; an implementation's synthesized
  location) is located at `("", 0)` on both sides, so a plugin-generated
  entry pairs with its counterpart by type, date and content. So is an
  error with no line (line 0), whatever file it names.
* `tolerance-fallback` (oracle): beancount's per-transaction tolerances
  (`__tolerances__`) leave out the `*` default of `option
  "inferred_tolerance_default"`, which it applies when it looks a currency
  up; a named currency's default is in them. The `*` default is filled in
  for every currency a posting of the transaction names (units, cost or
  price) that has no tolerance, so both sides list the tolerance in effect.
* `errored-transaction-balances` (pair): when a transaction holds an error
  (the same on both sides, or the errors differ first), what it leaves in
  the inventories is the implementation's choice: beancount keeps some
  refused entries' postings and drops others, an implementation may leave
  every refused entry out. The balances of the accounts such a
  transaction's postings name are not compared.
* `drop-zero-tolerances` (both): a zero in a transaction's inferred
  `tolerances` is dropped (an integer amount contributes none; beancount
  omits the currency, an implementation may list it as 0).

Features (`directive_features`): the constructs a directive's lines hold,
from a fixed vocabulary, for the category key: `cost`, `cost-empty`,
`cost-total` (`{{`), `cost-compound` (`#`), `cost-date`, `cost-label`,
`cost-merge` (`*`), `price`, `price-total`, `elided` (a posting with no
amount), `expr` (an arithmetic amount), `tolerance` (`~`), `reduce` (a
negative posting with a cost), `multi-currency`.

The key, `sem` (the default): `field|path|kind|booking|features`, where
`field|path|kind` is the generic key, `booking` the booking method of the
account the difference is about (`-` where no cost is involved) and
`features` the `+`-joined features of the directive the difference is in.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from ...snapshot import Ledger

#: beancount error messages to short kinds, for the category key (the
#: implementation's own codes name its side). First match wins.
ERROR_KINDS: tuple[tuple[str, str], ...] = (
    (r"does not balance", "unbalanced"),
    (r"^Balance failed", "balance-failed"),
    (r"Unused Pad", "pad-unused"),
    (r"[Pp]ad", "pad"),
    (r"inactive account|unknown account|Invalid reference to", "account-inactive"),
    (r"Duplicate open|already open", "open-duplicate"),
    (r"Not enough lots|No position matches|Ambiguous", "reduce"),
    (r"auto-posting|categorize|Unable to infer|Too many missing", "interpolate"),
    (r"Invalid currency|not allowed in", "currency-constraint"),
    (r"AVERAGE method is not supported", "average-unsupported"),
    (r"Cost merging is not supported", "merge-unsupported"),
    (r"Invalid option|Error for option|may not be set", "option"),
    (r"Duplicate|duplicate", "duplicate"),
    (r"Cost and price currencies", "cost-price-currency"),
    (r"[Ii]mplicit", "plugin"),
)
_ERROR_KINDS = [(re.compile(p), k) for p, k in ERROR_KINDS]

#: The error types beancount's parser and lexer raise: a ledger with one is
#: not well-formed (`BeancountFormat.well_formed`).
SYNTAX_ERRORS = frozenset({"ParserError", "ParserSyntaxError", "LexerError"})


def oracle_error_kind(error: Mapping) -> str:
    msg = error.get("msg", "")
    for pattern, kind in _ERROR_KINDS:
        if pattern.search(msg):
            return kind
    return error.get("code", "") or "-"


# -- normalizers --------------------------------------------------------------


def error_at_directive(fmt, ledger: Ledger, snap: dict, side: str) -> dict:
    texts = {fmt.main_file: ledger.text, **ledger.files}
    errors = []
    for e in snap["errors"]:
        text = texts.get(e["file"])
        if text is not None and e["line"] > 0:
            e = {**e, "line": fmt.directive_lines(text, e["line"])[0]}
        errors.append(e)
    return {**snap, "errors": errors}


def drop_errored_entries(fmt, ledger: Ledger, snap: dict, side: str) -> dict:
    texts = {fmt.main_file: ledger.text, **ledger.files}
    err_lines: dict[str, set[int]] = {}
    for e in snap["errors"]:
        err_lines.setdefault(e["file"], set()).add(e["line"])
    kept = []
    for entry in snap["entries"]:
        if entry.get("file") in err_lines:
            text = texts.get(entry["file"])
            if text is not None and entry.get("line", 0) > 0:
                start, end = fmt.directive_lines(text, entry["line"])
                if any(start <= ln <= end for ln in err_lines[entry["file"]]):
                    continue
        kept.append(entry)
    return {**snap, "entries": kept}


def _nowhere(file: str, ledger: Ledger, main: str) -> bool:
    return not file or file.startswith("<") or (file != main and file not in ledger.files)


def placeholder_locations(fmt, ledger: Ledger, snap: dict, side: str) -> dict:
    main = fmt.main_file
    return {
        **snap,
        "errors": [
            {**e, "file": "", "line": 0}
            if _nowhere(e["file"], ledger, main) or not e["line"]
            else e
            for e in snap["errors"]
        ],
        "entries": [
            {**e, "file": "", "line": 0} if _nowhere(e.get("file", ""), ledger, main) else e
            for e in snap["entries"]
        ],
    }


def tolerance_fallback(fmt, ledger: Ledger, snap: dict, side: str) -> dict:
    fallback = ((snap.get("options") or {}).get("inferred_tolerance_default") or {}).get("*")
    if fallback is None:
        return snap
    entries = []
    for entry in snap["entries"]:
        tol = entry.get("tolerances")
        if isinstance(tol, dict):
            named = set()
            for p in entry.get("postings") or ():
                for part in (p.get("units"), p.get("cost"), p.get("price")):
                    if isinstance(part, dict) and part.get("currency"):
                        named.add(part["currency"])
            entry = {**entry, "tolerances": {**{c: fallback for c in named}, **tol}}
        entries.append(entry)
    return {**snap, "entries": entries}


_IMPORT = re.compile(r'^Error importing "([^"]*)"')


def missing_third_party_plugin(snapshot: dict) -> str | None:
    """`BeancountFormat.oracle_unjudged`: beancount could not import a
    plugin from outside its own package (`beancount_reds_plugins...`, a
    local module): whether it would run is a fact about the environment the
    oracle runs in, not about the ledger. A `beancount.*` plugin that does
    not import is a fact about the ledger (the name is wrong) and is
    judged."""
    for e in snapshot.get("errors", ()):
        m = _IMPORT.match(e["msg"])
        if m and not m.group(1).startswith("beancount."):
            return f"unjudged: the oracle cannot import plugin {m.group(1)!r}"
    return None


_POSTING_ACCOUNT = re.compile(r"^[ \t]+(?:[*!&#?%PSTCURM][ \t]+)?([A-Z][^ \t;]*:[^ \t;]*)")


def errored_transaction_balances(fmt, ledger: Ledger, oracle: dict, impl: dict):
    texts = {fmt.main_file: ledger.text, **ledger.files}
    accounts: set[str] = set()
    for e in [*oracle["errors"], *impl["errors"]]:
        text = texts.get(e["file"])
        if text is None or e["line"] <= 0 or line_kind(text, e["line"]) != "transaction":
            continue
        start, end = fmt.directive_lines(text, e["line"])
        for line in text.split("\n")[start:end]:
            m = _POSTING_ACCOUNT.match(line)
            if m:
                accounts.add(m.group(1))
    if not accounts:
        return oracle, impl

    def drop(snap):
        return {
            **snap,
            "balances": {a: p for a, p in snap["balances"].items() if a not in accounts},
        }

    return drop(oracle), drop(impl)


def drop_zero_tolerances(fmt, ledger: Ledger, snap: dict, side: str) -> dict:
    entries = []
    for entry in snap["entries"]:
        tol = entry.get("tolerances")
        if isinstance(tol, dict):
            entry = {**entry, "tolerances": {c: n for c, n in tol.items() if n != "0"}}
        entries.append(entry)
    return {**snap, "entries": entries}


# -- features -----------------------------------------------------------------

_BRACES = re.compile(r"\{\{?([^{}]*)\}\}?")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_POSTING = re.compile(r"^[ \t]+(?:[*!&#?%PSTCURM][ \t]+)?([A-Z][^ \t;]*:[^ \t;]*)(.*)$")
_NUMBER = re.compile(r"[-+]?(?:\d[\d,]*)?\.?\d")
_EXPR = re.compile(r"\d[ \t]*[-+*/][ \t]*[(\d.]|\(")
_CURRENCY = re.compile(r"\b[A-Z][A-Z0-9'._-]{0,22}[A-Z0-9]\b|\b[A-Z]\b")


def directive_features(text: str, start: int, end: int) -> set[str]:
    lines = text.split("\n")[start - 1 : end]
    out: set[str] = set()
    currencies: set[str] = set()
    for n, line in enumerate(lines):
        body = line.split(";", 1)[0]
        if n == 0:
            if "~" in body:
                out.add("tolerance")
            continue
        m = _POSTING.match(body)
        if not m:
            continue
        rest = m.group(2)
        before_cost = re.split(r"[{@]", rest, maxsplit=1)[0]
        if not _NUMBER.search(before_cost):
            out.add("elided")
        elif _EXPR.search(before_cost):
            out.add("expr")
        for c in _CURRENCY.findall(before_cost):
            currencies.add(c)
        for b in _BRACES.finditer(rest):
            inner = b.group(1)
            out.add("cost")
            if b.group(0).startswith("{{"):
                out.add("cost-total")
            if not inner.strip():
                out.add("cost-empty")
            if "#" in inner:
                out.add("cost-compound")
            if _DATE.search(inner):
                out.add("cost-date")
            if '"' in inner:
                out.add("cost-label")
            if "*" in inner:
                out.add("cost-merge")
            if before_cost.strip().startswith("-"):
                out.add("reduce")
        if "@@" in rest:
            out.add("price-total")
        elif "@" in rest:
            out.add("price")
    if len(currencies) > 1:
        out.add("multi-currency")
    return out


def _bookings(snap: Mapping) -> dict[str, str]:
    return {
        e["account"]: e["booking"]
        for e in snap.get("entries", [])
        if e.get("type") == "open" and e.get("booking")
    }


def _booking_of(snap: Mapping, account: str) -> str:
    return _bookings(snap).get(account) or (snap.get("options") or {}).get("booking_method") or "-"


_KIND_WORD = re.compile(r"^\d{4}[-/]\d{2}[-/]\d{2}[ \t]+(\S+)")


def line_kind(text: str, line: int) -> str:
    """What directive the line starts: `transaction`, `open`, `balance`...,
    `option`, `plugin`, `include`, or `-`."""
    lines = text.split("\n")
    if line <= 0 or line > len(lines):
        return "-"
    src = lines[line - 1]
    m = _KIND_WORD.match(src)
    if m:
        word = m.group(1)
        if word in ("*", "!", "txn") or word.startswith('"') or len(word) == 1:
            return "transaction"
        return word
    first = src.split(None, 1)[0] if src.split() else "-"
    return first if first in ("option", "plugin", "include", "pushtag", "pushmeta") else "-"


def sem_key(fmt, m) -> str:
    """`field|path|kind|booking|features` (see the module docstring)."""
    d = m.diff
    head = f"{d.field}|{d.path}|{d.kind}"
    if d.field == "errors":
        bigger = d.impl if len(d.impl or ()) > len(d.oracle or ()) else d.oracle
        if bigger is d.impl:
            kinds = sorted({e["code"] for e in d.impl})
            who = "impl"
        else:
            kinds = sorted({oracle_error_kind(e) for e in d.oracle})
            who = "oracle"
        text = m.text_of(d.file)
        kind = line_kind(text, d.line)
        head = f"errors|{d.path}|{who}:{'+'.join(kinds) or '-'}|{kind}"
        feats = directive_features(text, *fmt.directive_lines(text, d.line)) if d.line else set()
        account = ""
    elif d.field == "entries":
        text = m.text_of(d.file)
        feats = directive_features(text, *fmt.directive_lines(text, d.line)) if d.line else set()
        account = d.subject if d.posting is not None else ""
        if not account:
            entry = d.oracle if isinstance(d.oracle, dict) else d.impl
            if isinstance(entry, dict):
                for p in entry.get("postings") or ():
                    if p.get("cost"):
                        account = p.get("account", "")
                        break
    elif d.field == "balances":
        account = d.subject
        feats = set()
        for e in m.oracle.get("entries", []):
            if e.get("type") == "transaction" and any(
                p.get("account") == account for p in e.get("postings") or ()
            ):
                text = m.text_of(e.get("file", ""))
                if e.get("line"):
                    feats |= directive_features(text, *fmt.directive_lines(text, e["line"]))
    else:
        return f"{head}|-|-"
    booking = (
        _booking_of(m.oracle, account)
        if account and any(f.startswith("cost") for f in feats)
        else "-"
    )
    return f"{head}|{booking}|{'+'.join(sorted(feats)) or '-'}"


def ledger_features(fmt, ledger: Ledger) -> list[str]:
    """Every feature of every directive of every file, plus the ledger-wide
    ones (`include`, `plugin:<name>`, `option:<name>`, `booking:<method>`,
    `pad`, `balance`): what a minimized example is made of, for a report."""
    out: set[str] = set()
    for text in (ledger.text, *ledger.files.values()):
        lines = text.split("\n")
        for n, line in enumerate(lines, 1):
            if line.startswith("include"):
                out.add("include")
            m = re.match(r'plugin[ \t]+"([^"]+)"', line)
            if m:
                out.add("plugin:" + m.group(1).rsplit(".", 1)[-1])
            m = re.match(r'option[ \t]+"([^"]+)"', line)
            if m:
                out.add("option:" + m.group(1))
            m = re.match(r'\d{4}-\d\d-\d\d[ \t]+open\b.*"([A-Z_]+)"', line)
            if m:
                out.add("booking:" + m.group(1))
            kind = line_kind(text, n)
            if kind in ("pad", "balance"):
                out.add(kind)
            if kind == "transaction":
                out |= directive_features(text, *fmt.directive_lines(text, n))
    return sorted(out)
