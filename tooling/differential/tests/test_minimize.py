from ptadiff.formats.base import FormatPlugin
from ptadiff.minimize import minimize

units = FormatPlugin().shrink_units


def key_of(text):
    """A toy category: `AB` when both an `A` line and a `B` token are
    present, `A` when only the first; `None` (a match) otherwise."""
    has_a = any(line.startswith("A") for line in text.split("\n"))
    if not has_a:
        return None
    return "AB" if "B" in text.split() else "A"


def keys_of(texts):
    return [key_of(t) for t in texts]


def test_minimize_reaches_the_minimal_input_with_the_key():
    text = "x y\nA one two\nfoo B bar\nz\nA again\n"
    r = minimize(text, "AB", keys_of, units)
    assert r.complete
    assert key_of(r.text) == "AB"
    assert r.text == "A B"  # three characters: nothing smaller has the key


def test_minimize_never_switches_category():
    # Dropping the `B` would leave a smaller input that still mismatches
    # (key `A`); a key-preserving minimizer must not take it.
    text = "A\nB\n"
    r = minimize(text, "AB", keys_of, units)
    assert key_of(r.text) == "AB"


def test_minimize_returns_input_when_key_differs():
    r = minimize("A\n", "AB", keys_of, units)
    assert r.text == "A\n" and not r.complete


def test_minimize_budget_keeps_progress():
    text = "\n".join(["noise"] * 50 + ["A B"] + ["noise"] * 50)
    r = minimize(text, "AB", keys_of, units, max_evaluations=12)
    assert not r.complete
    assert key_of(r.text) == "AB" and len(r.text) < len(text)
    assert r.evaluations <= 12


def test_minimize_is_deterministic():
    text = "q\nA 1 2 3\nB\nA B C\nr B\n"
    a = minimize(text, "AB", keys_of, units)
    b = minimize(text, "AB", keys_of, units)
    assert a == b


def test_shrink_units_concatenate_back():
    text = "a  b\t c\r\n  \nd"
    for level in ("lines", "tokens", "chars"):
        assert "".join(units(text, level)) == text
