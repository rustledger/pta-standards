import dataclasses

from conftest import require_beancount

from ptadiff.compare import Divergence
from ptadiff.formats import get_format
from ptadiff.formats.base import Mismatch
from ptadiff.formats.beancount import error_kind, line_shape
from ptadiff.model import Error, Token
from ptadiff.pipeline import Differ
from ptadiff.protocol import JsonlImplementation


def test_error_kind_names():
    assert error_kind(Error(1, "LexerError", "Invalid token: '$'")) == "lex:token"
    assert error_kind(Error(1, "LexerError", "ValueError: month must be in 1..12")) == "lex:date"
    assert error_kind(Error(1, "LexerError", "ValueError: Invalid number format: '1,50'")) == (
        "lex:number"
    )
    assert error_kind(Error(1, "ParserSyntaxError", "syntax error, unexpected INDENT")) == (
        "syn:INDENT"
    )
    msg = "syntax error, unexpected EOL, expecting STRING"
    assert error_kind(Error(1, "ParserSyntaxError", msg)) == "syn:EOL"
    assert error_kind(Error(1, "ParserSyntaxError", "syntax error, unexpected end of file")) == (
        "syn:end_of_file"
    )
    assert error_kind(Error(0, "ParserError", "Unbalanced pushed tag: 'a'")) == "ParserError"


def test_line_shape_anchors_on_first_invalid_token():
    toks = [
        Token("DATE", 1, "2024-01-01"),
        Token("OPEN", 1, "open"),
        Token("ACCOUNT", 1, "Assets:A"),
        Token("error", 1, "$x"),
        Token("error", 1, "$"),
        Token("EOL", 2, "\n"),
        Token("INDENT", 2, "  "),
        Token("ACCOUNT", 2, "Assets:A"),
        Token("NUMBER", 2, "1"),
        Token("CURRENCY", 2, "USD"),
    ]
    assert line_shape(toks, 1) == "ACCOUNT error"
    assert line_shape(toks, 2) == "INDENT ACCOUNT"
    assert line_shape(toks, 3) == "-"
    assert line_shape([Token("error", 1, "$")] * 3, 1) == "^ error"


def test_normalizers_defaults():
    fmt = get_format("beancount")
    assert fmt.oracle_input("\ufeffx\ufeff") == "x\ufeff"
    errs = [
        Error(3, "ParserSyntaxError", "syntax error, unexpected EOL, expecting STRING"),
        Error(1, "ParserSyntaxError", "syntax error, unexpected EOL"),
        Error(2, "ParserSyntaxError", "syntax error, unexpected end of file"),
        Error(4, "ParserError", "Invalid option: 'x'"),
        Error(5, "ParserError", "Cost merging is not supported yet"),
    ]
    assert [e.line for e in fmt.normalize("oracle", "", errs)] == [2, 1, 2]
    fmt.normalizer("eol-error-on-statement-line").enabled = False
    assert [e.line for e in fmt.normalize("oracle", "", errs)] == [3, 1, 2]


def test_shape_key_fields():
    fmt = get_format("beancount")
    m = Mismatch(
        text="x\n  $\n",
        oracle=(Error(2, "ParserSyntaxError", "syntax error, unexpected INDENT"),),
        impl=(Error(2, "P0012", "a"), Error(2, "P0012", "b")),
        divergence=Divergence(2, 1, 2),
        tokens=(Token("INDENT", 2, "  "), Token("error", 2, "$")),
    )
    assert fmt.key("shape")(m) == "impl-more|impl:P0012|indented|INDENT error"
    assert fmt.key("coarse")(m) == "impl-more|impl:P0012|indented"
    # Fewer: the oracle's surplus names it.
    fewer = dataclasses.replace(m, impl=(), divergence=Divergence(2, 1, 0))
    assert fmt.key("coarse")(fewer) == "impl-fewer|oracle:syn:INDENT|indented"
    assert fmt.key("shape")(dataclasses.replace(m, tokens=None)).endswith("|indented|?")
    eof = Mismatch("", (Error(0, "ParserError", "u"),), (), Divergence(0, 1, 0), ())
    assert fmt.key("shape")(eof) == "eof|oracle:ParserError|eof|-"


def test_beancount_oracle_parse_and_lex():
    require_beancount()
    oracle = get_format("beancount").oracle(version=None)
    items = [("a", "2024-01-01 open Assets:A\n  $\n"), ("b", "2024-01-01 open Assets:A\n")]
    got = oracle.parse(items, jobs=2)
    assert got["b"].ok and got["b"].errors == ()
    assert [e.line for e in got["a"].errors] == [2]
    toks = oracle.lex(items[:1])["a"]
    assert [t.kind for t in toks] == ["DATE", "OPEN", "ACCOUNT", "EOL", "INDENT", "error", "EOL"]
    assert toks[5] == Token("error", 2, "$")


def test_differ_end_to_end_with_fake_impl(fake_impl_argv):
    require_beancount()
    fmt = get_format("beancount")
    differ = Differ(fmt, fmt.oracle(version=None), JsonlImplementation(fake_impl_argv), jobs=2)
    items = [
        ("ok", "2024-01-01 open Assets:A\n"),
        # beancount: an invalid token on line 2; the fake reports nothing.
        ("miss", "2024-01-01 open Assets:A\n  $\n"),
        # beancount: nothing; the fake reports line 1 twice.
        ("extra", "; BAD2\n"),
    ]
    v = differ.evaluate(items)
    assert v["ok"].status == "match"
    assert v["miss"].status == "mismatch"
    assert v["miss"].key == "impl-fewer|oracle:lex:token|indented|INDENT error"
    assert v["extra"].key == "impl-more|impl:X2|top|-"
    assert differ.keys_of(["2024-01-01 open Assets:A\n"]) == [None]
