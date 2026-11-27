import hashlib
import json

import pytest
from conftest import require_beancount

from ptadiff import get_format
from ptadiff.snapshot import ledger_id

FMT = get_format("beancount")

#: Consumers pin counts measured over these samples: a generator change
#: must be deliberate, and re-pinned here and by them.
DIGESTS = {
    "s1": "89d2ab7b1202b6d2",
    "s2": "dec575b7afbc6ba2",
    "s3": "92abab8edafa6e84",
    "s4": "51bfa05de6dfc46a",
    "smix": "a3ab679dbb2e091a",
}


def digest(ledgers):
    h = hashlib.sha256()
    for led in ledgers:
        h.update(json.dumps(led.to_json(ledger_id(led), "main.beancount"), sort_keys=True).encode())
    return h.hexdigest()[:16]


@pytest.mark.parametrize("name", sorted(DIGESTS))
def test_generator_is_deterministic_and_pinned(name):
    gen = FMT.semantic_generators[name]
    a, b = gen(7, 40), gen(7, 40)
    assert a == b
    assert len({ledger_id(x) for x in a}) == 40
    assert [ledger_id(x) for x in a] == sorted(ledger_id(x) for x in a)
    assert digest(a) == DIGESTS[name]


def test_s3_is_multi_file():
    assert all(led.files for led in FMT.semantic_generators["s3"](3, 20))


@pytest.mark.parametrize("name", ["s1", "s2", "s3", "s4"])
def test_generated_ledgers_are_well_formed(name):
    """Every generated ledger parses cleanly in beancount: the generators
    exercise semantics, and a syntax error would make it a parse test."""
    require_beancount()
    oracle = FMT.semantic_oracle()
    ledgers = FMT.semantic_generators[name](11, 60)
    snaps = oracle.snapshot([(str(n), led) for n, led in enumerate(ledgers)], jobs=4)
    from ptadiff.snapshot import canonicalize

    bad = [n for n, s in snaps.items() if not FMT.well_formed(canonicalize(s))]
    assert not bad, [ledgers[int(n)].render("main.beancount") for n in bad[:1]]
    # Most are valid; a share carries a fault.
    errored = sum(1 for s in snaps.values() if s["errors"])
    assert errored < len(ledgers) * 0.5
