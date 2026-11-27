import hashlib

import pytest

from ptadiff.formats.beancount.generators import BOM, GENERATORS, seed_ledgers

# The digest of each generator's (seed=1, n=200) sample. A consumer pins
# counts measured over generator samples, so ANY change to a generator's
# output must be deliberate: update the digest here and re-pin downstream.
DIGESTS = {
    "g1": "0763f17c4888ef8a",
    "g1b": "e757d73745df26ed",
    "g2": "f69bb277edfe9eca",
    "g2b": "5597cd720b31737a",
    "g3": "74f98ad3b46dc66c",
    "g3b": "51bd0462c1532991",
}


def digest(texts):
    return hashlib.sha256("\0".join(texts).encode("utf-8")).hexdigest()[:16]


@pytest.mark.parametrize("name", sorted(GENERATORS))
def test_generator_is_deterministic_sorted_and_distinct(name):
    gen = GENERATORS[name]
    a, b = gen(1, 200), gen(1, 200)
    assert a == b
    assert a == sorted(set(a)) and len(a) == 200
    assert gen(2, 200) != a


@pytest.mark.parametrize("name", sorted(GENERATORS))
def test_generator_output_is_pinned(name):
    assert digest(GENERATORS[name](1, 200)) == DIGESTS[name]


@pytest.mark.parametrize("name", ["g1b", "g2b", "g3b"])
def test_biased_generators_hold_a_bom_or_cr(name):
    assert all(BOM in t or "\r" in t for t in GENERATORS[name](3, 100))


def test_seed_corpus_is_bundled():
    assert len(seed_ledgers()) >= 5
