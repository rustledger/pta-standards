import sys

import pytest

from ptadiff.model import Error
from ptadiff.protocol import JsonlImplementation, ProtocolError, parse_output


def test_jsonl_implementation_round_trip(fake_impl_argv):
    impl = JsonlImplementation(fake_impl_argv)
    got = impl.run([("a", "ok\nBAD\n"), ("b", "BAD2\r\nEOF!"), ("c", "")])
    assert got == {
        "a": [Error(2, "X1", "bad: BAD")],
        "b": [Error(1, "X2", "bad2"), Error(1, "X2", "bad2"), Error(0, "X0", "eof")],
        "c": [],
    }


def test_jsonl_implementation_preserves_odd_text(fake_impl_argv):
    # A NUL, a CR, U+2028 (which `str.splitlines` would split at) and a
    # non-BMP character, echoed back unescaped in the message.
    text = "\ufeffBAD\x00\r\n\u2028 \U0001f600 BAD"
    got = JsonlImplementation(fake_impl_argv).run([("i", text), ("j", "BAD")])
    assert [e.line for e in got["i"]] == [1, 2]
    assert got["i"][1].msg == "bad: \u2028 \U0001f600 BAD"
    assert got["j"] == [Error(1, "X1", "bad: BAD")]


def test_parse_output_rejects_wrong_order_and_count():
    with pytest.raises(ProtocolError, match="answered 1 of 2"):
        parse_output('{"id": "a", "errors": []}\n', ["a", "b"])
    with pytest.raises(ProtocolError, match="where 'a' was next"):
        parse_output('{"id": "b", "errors": []}\n', ["a"])
    with pytest.raises(ProtocolError, match="bad output line"):
        parse_output("not json\n", ["a"])


def test_parse_output_accepts_triples():
    assert parse_output('{"id": "a", "errors": [[3, "P1", "m"]]}', ["a"]) == {
        "a": [Error(3, "P1", "m")]
    }


def test_jsonl_implementation_nonzero_exit_is_an_error():
    impl = JsonlImplementation([sys.executable, "-c", "import sys; sys.exit(3)"])
    with pytest.raises(ProtocolError, match="exited 3"):
        impl.run([("a", "x")])
