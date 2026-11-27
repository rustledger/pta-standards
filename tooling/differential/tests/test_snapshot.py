import json
from pathlib import Path

from ptadiff.model import content_id
from ptadiff.snapshot import (
    Ledger,
    canonical_number,
    canonicalize,
    diffs,
    first_diff,
    ledger_id,
)

SCHEMA = Path(__file__).resolve().parent.parent / "ptadiff" / "schemas" / "snapshot-1.schema.json"


def snap(**kw):
    base = {"errors": [], "entries": [], "balances": {}, "options": {}}
    base.update(kw)
    return base


def txn(line, *postings, **kw):
    return {
        "type": "transaction",
        "date": "2024-01-02",
        "file": "main.beancount",
        "line": line,
        "flag": "*",
        "payee": None,
        "narration": "n",
        "tags": [],
        "links": [],
        "postings": list(postings),
        **kw,
    }


def posting(account, number, currency="USD", cost=None):
    return {
        "account": account,
        "units": {"number": number, "currency": currency},
        "cost": cost,
        "price": None,
        "flag": None,
    }


def test_canonical_number_by_value():
    assert canonical_number("10.00") == canonical_number("10") == "10"
    assert canonical_number("-0.000") == "0"
    assert canonical_number("1E+3") == "1000"
    assert canonical_number(None) is None
    # Past 20 significant digits, rounded.
    assert canonical_number("0.0061171925305859626529298133") == canonical_number(
        "0.0061171925305859626529298132"
    )


def test_canonicalize_sorts_unordered_and_keeps_postings():
    a = snap(
        entries=[txn(5, posting("B", "1"), posting("A", "-1"), tags=["z", "a"]), txn(2)],
        balances={"A": [{"units": {"number": "0", "currency": "USD"}, "cost": None}]},
    )
    c = canonicalize(a)
    assert [e["line"] for e in c["entries"]] == [2, 5]
    assert c["entries"][1]["tags"] == ["a", "z"]
    assert [p["account"] for p in c["entries"][1]["postings"]] == ["B", "A"]
    assert c["balances"] == {}


def test_first_diff_orders_fields_and_names_paths():
    a = canonicalize(snap(entries=[txn(3, posting("A", "1"), posting("B", "-1"))]))
    b = canonicalize(snap(entries=[txn(3, posting("A", "2"), posting("B", "-1"))]))
    d = first_diff(a, b)
    assert (d.field, d.path, d.kind, d.line, d.subject) == (
        "entries",
        "postings.units.number",
        "transaction",
        3,
        "A",
    )
    order = canonicalize(snap(entries=[txn(3, posting("B", "-1"), posting("A", "1"))]))
    assert first_diff(a, order).path == "postings.order"
    err = canonicalize(
        snap(
            entries=b["entries"],
            errors=[{"file": "main.beancount", "line": 3, "code": "E", "msg": ""}],
        )
    )
    # The error comes first: it usually explains the rest.
    assert first_diff(a, err).field == "errors"
    assert first_diff(a, err).path == "impl-more"
    assert [d.field for d in diffs(a, err)] == ["errors", "entries"]


def test_errors_by_location_set_or_count():
    one = [{"file": "m", "line": 3, "code": "A", "msg": ""}]
    two = [*one, {"file": "m", "line": 3, "code": "B", "msg": ""}]
    a, b = canonicalize(snap(errors=one)), canonicalize(snap(errors=two))
    assert first_diff(a, b) is None
    assert first_diff(a, b, error_mode="counts").path == "impl-more"


def test_balances_units_or_lots():
    lot = {"number": "10", "currency": "USD", "date": "2024-01-01", "label": None}
    a = canonicalize(
        snap(balances={"S": [{"units": {"number": "2", "currency": "X"}, "cost": lot}]})
    )
    b = canonicalize(
        snap(
            balances={
                "S": [{"units": {"number": "2", "currency": "X"}, "cost": {**lot, "number": "11"}}]
            }
        )
    )
    c = canonicalize(
        snap(balances={"S": [{"units": {"number": "3", "currency": "X"}, "cost": lot}]})
    )
    assert first_diff(a, b).path == "lots"
    assert first_diff(a, c).path == "units"
    assert first_diff(a, canonicalize(snap())).path == "missing-in-impl"


def test_unreported_option_is_not_compared():
    a = canonicalize(snap(options={"booking_method": "STRICT", "tolerance_multiplier": "0.5"}))
    b = canonicalize(snap(options={"booking_method": "STRICT"}))
    assert first_diff(a, b) is None
    c = canonicalize(snap(options={"booking_method": "FIFO"}))
    assert first_diff(a, c).path == "booking_method"


def test_ledger_ids():
    assert ledger_id(Ledger("x")) == content_id("x")
    assert ledger_id(Ledger("x", {"a": "1"})) != ledger_id(Ledger("x", {"a": "2"}))
    led = Ledger("x", {"b": "2", "a": "1"})
    assert Ledger.from_json(json.loads(json.dumps(led.to_json("i", "main")))) == led


def test_schema_names_every_snapshot_field():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert schema["title"] == "ptadiff-snapshot/1"
    assert set(schema["required"]) == {"errors", "entries", "balances", "options"}
