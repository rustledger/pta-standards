import sys
from pathlib import Path

import pytest
from conftest import require_beancount

from ptadiff import JsonlImplementation, get_format
from ptadiff.semantic import SemanticDiffer
from ptadiff.snapshot import Ledger

FAKE = Path(__file__).resolve().parent / "fake_semantic_impl.py"

BASE = """\
2024-01-01 open Assets:Cash
2024-01-01 open Assets:Stock "FIFO"
2024-01-01 open Income:Gains
2024-01-02 * "buy"
  Assets:Stock  2 HOOL {10.00 USD}
  Assets:Cash
2024-01-03 * "sell"
  Assets:Stock  -1 HOOL {} @ 12.00 USD
  Assets:Cash  12.00 USD
  Income:Gains
"""


@pytest.fixture
def differ():
    require_beancount()
    fmt = get_format("beancount")
    impl = JsonlImplementation([sys.executable, str(FAKE)], name="fake")
    return SemanticDiffer(fmt, fmt.semantic_oracle(), impl, jobs=2)


def test_oracle_snapshot_shape():
    require_beancount()
    fmt = get_format("beancount")
    snap = fmt.semantic_oracle().snapshot([("a", Ledger(BASE))])["a"]
    sell = next(e for e in snap["entries"] if e.get("narration") == "sell")
    # The interpolated gain and the lot's resolved cost are there.
    assert sell["postings"][2]["units"] == {"number": "-2.00", "currency": "USD"}
    assert sell["postings"][0]["cost"]["date"] == "2024-01-02"
    assert snap["balances"]["Assets:Stock"][0]["units"]["number"] == "1"
    assert snap["options"]["booking_method"] == "STRICT"


def test_match_mismatch_crash(differ):
    led = {
        "same": Ledger(BASE),
        "error": Ledger(BASE.replace('"buy"', '"buy" ; PERTURB-ERROR')),
        "units": Ledger(BASE + "; PERTURB-UNITS\n"),
        "crash": Ledger(BASE + "; PERTURB-CRASH\n"),
    }
    v = differ.evaluate(list(led.items()))
    assert v["same"].status == "match"
    assert v["error"].status == "mismatch"
    assert v["error"].key.startswith("errors|impl-more|impl:X1|transaction")
    assert v["units"].key.startswith("entries|postings.units.number|transaction")
    assert v["crash"].key == "impl-crash|panicked"


def test_multi_file_ledger_matches(differ):
    led = Ledger(
        'option "operating_currency" "USD"\ninclude "sub/a.beancount"\n',
        {"sub/a.beancount": BASE},
    )
    assert differ.evaluate([("m", led)])["m"].status == "match"


def test_minimize_keeps_key_and_well_formedness(differ):
    led = Ledger(BASE.replace('"buy"', '"buy" ; PERTURB-ERROR'))
    key = differ.keys_of([led])[0]
    r = differ.minimize(led, key)
    assert r.key == key
    assert "PERTURB-ERROR" in r.ledger.text
    assert len(r.ledger.text) < len(led.text)
    assert differ.keys_of([r.ledger])[0] == key


def test_deviation_is_counted_apart(differ):
    from ptadiff.semantic import Deviation

    differ.deviations = [Deviation("units", "here", lambda m: "units" in m.diff.path)]
    v = differ.evaluate([("u", Ledger(BASE + "; PERTURB-UNITS\n"))])["u"]
    assert (v.status, v.deviation, v.key) == ("deviation", "units", "deviation:units")
