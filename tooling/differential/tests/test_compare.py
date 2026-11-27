from ptadiff.compare import Divergence, agree, divergences, first_divergence
from ptadiff.model import Error


def E(line, code="c"):
    return Error(line, code, "")


def test_first_divergence_agree_returns_none():
    assert first_divergence([E(2), E(2)], [E(2, "x"), E(2, "y")]) is None
    assert agree([E(1)], [E(1, "other code")])


def test_first_divergence_line_order_puts_line_zero_last():
    d = divergences([E(0), E(5)], [E(3)])
    assert d == [Divergence(3, 0, 1), Divergence(5, 1, 0), Divergence(0, 1, 0)]
    assert first_divergence([E(0), E(5)], [E(3)]) == Divergence(3, 0, 1)


def test_first_divergence_counts_per_line():
    assert first_divergence([E(4)], [E(4), E(4)]) == Divergence(4, 1, 2)
