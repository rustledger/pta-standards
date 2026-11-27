"""Seeded input generators for beancount syntax, G1-G3 and their `b` variants.

Each generator is a pure function of `(seed, n)`: it draws from its own
`random.Random(seed)` (whose `random`, `randint`, `randrange` and `choice` are
stable across CPython versions), collects `n` distinct inputs, and returns
them sorted. The same arguments give the same inputs on every run and
platform, so a count measured over a generator sample can be pinned in CI.

* G1: lines drawn from hand-picked lists of valid, broken, unreadable and
  indented statements, so recovery after a broken statement is exercised.
* G2: lines of random tokens from a fixed vocabulary.
* G3: windows of real ledgers (the bundled `seeds/` corpus) with statements
  inserted and words mutated.
* G1b, G2b, G3b: the same, biased toward the bytes line handling gets wrong:
  a BOM (U+FEFF) and a carriage return in odd places. Every `b` input holds at
  least one of the two.

The vocabularies are ours, written for this differential work; nothing is
taken from beancount's sources.
"""

from __future__ import annotations

import random
from functools import cache
from pathlib import Path

from ..base import Generator

BOM = "\ufeff"
SEEDS_DIR = Path(__file__).parent / "seeds"

# -- G1 ---------------------------------------------------------------------

G1_VALID = [
    "2024-01-01 open Assets:A",
    '2024-01-02 * "n"',
    'option "title" "x"',
    "pushtag #a",
    "poptag #a",
    'pushmeta kk: "v"',
    "popmeta kk:",
    "2024-01-02 close Assets:A",
    "2024-01-02 balance Assets:A 1 USD",
    '2024-01-02 note Assets:A "x"',
    'include "x.bean"',
    'plugin "p"',
    '2024-01-02 custom "x" 1',
]
G1_FAILED = [
    "pushtag #a $",
    'option "title" "x" $',
    'pushmeta kk: "v" x',
    "poptag #a $",
    "2024-01-02 open Assets:B $",
    'option "title"',
    'option "a"',
    "pushtag #a 2024-02-30",
    '2024-01-02 * "n" $',
    '2024-01-02 * "a" "b" "c"',
    '2024-01-02 open Assets:B "FOO"',
    '2024-01-02 2024-01-03 * "n"',
    '2024-01-02 2024-01-03 "n"',
    "2024-01-02 123",
    "2024-01-02 open",
    '"abc',
    '2024-01-02 * "abc',
    "pushtag",
    "poptag #a #b",
    "2024-01-02 open Assets:B 5",
    "2024-01-02 2024-01-03 open Assets:C",
    "include",
    'plugin "a" "b" "c"',
    '2024-01-02 * "n" 5',
    "pushmeta kk",
    "2024-01-02 balance Assets:A",
    "2024-02-30 open Assets:B",
    '2024-01-02 event "a"',
    'option "a" "b" "c"',
    '2024-01-02 * "n" #t x',
    "2024-01-02 note Assets:A",
    '2024-01-02 2024-13-45 "n"',
    '2024-01-02 Assets:A * "n"',
]
G1_UNREAD = [
    "$",
    "$x",
    "!",
    "*",
    "#",
    "x",
    "AB-C",
    "5",
    "Assets:A",
    '"s"',
    ":",
    '$ 2024-01-02 * "y"',
    "k: 1",
    "T",
]
G1_INDENT = [
    "  2024-02-30 5",
    "  Assets:A 1 USD",
    '  kk: "v"',
    "  x",
    '  "a"',
    "  ;c",
    "  2024-01-02 open Assets:Z",
    "  Assets:A 1 USD 2024-01-02",
    "  !",
    "  h1 Z",
    "  #tag",
    "  Assets:A",
    "  Expenses:B  1 USD",
    "  5",
    "  kk: 2024-02-30",
    "  $",
    "\t2024-02-30 5",
    "  Assets:A 1 $",
    '  option "a" "b"',
]
G1_GAP = ["", ";c", "  ", "* heading"]

G1B_UNREAD = [*G1_UNREAD, BOM, BOM + "$", "x" + BOM, BOM + '2024-01-02 * "n"']
G1B_UNREAD += [BOM + "Assets:A", "x\r", "$\r"]
G1B_INDENT = [*G1_INDENT, "  " + BOM, "\t" + BOM + "x", "  Assets:A 1 USD\r"]
G1B_INDENT += ["  " + BOM + "Assets:A 1 USD", "  T\r", "  1,50"]
G1B_MUTATIONS = [BOM, "\r", "\r", BOM + " ", " \r"]


def _g1_line(r: random.Random, unread: list[str], indent: list[str]) -> str:
    k = r.random()
    if k < 0.12:
        return r.choice(G1_VALID)
    if k < 0.40:
        return r.choice(G1_FAILED)
    if k < 0.52:
        return r.choice(unread)
    if k < 0.82:
        return r.choice(indent)
    return r.choice(G1_GAP)


def _finish(r: random.Random, lines: list[str], crlf: float, final_newline: float = 0.85) -> str:
    nl = "\r\n" if r.random() < crlf else "\n"
    text = nl.join(lines)
    if r.random() < final_newline:
        text += nl
    return text


def g1(seed: int, n: int) -> list[str]:
    r = random.Random(seed)
    out: set[str] = set()
    while len(out) < n:
        lines = ["2024-01-01 open Assets:A"] if r.random() < 0.7 else []
        lines += [_g1_line(r, G1_UNREAD, G1_INDENT) for _ in range(r.randint(2, 6))]
        out.add(_finish(r, lines, 0.1))
    return sorted(out)


def g1b(seed: int, n: int) -> list[str]:
    r = random.Random(seed)
    out: set[str] = set()
    while len(out) < n:
        lines = ["2024-01-01 open Assets:A"] if r.random() < 0.7 else []
        lines += [_g1_line(r, G1B_UNREAD, G1B_INDENT) for _ in range(r.randint(2, 6))]
        for _ in range(r.randint(0, 2)):
            j = r.randrange(len(lines))
            if lines[j]:
                i = r.randint(0, len(lines[j]))
                lines[j] = lines[j][:i] + r.choice(G1B_MUTATIONS) + lines[j][i:]
        text = _finish(r, lines, 0.3)
        if BOM in text or "\r" in text:
            out.add(text)
    return sorted(out)


# -- G2 ---------------------------------------------------------------------

G2_TOKENS = [
    "2024-01-02", "2024-02-30", "2024/1/3", "2024-13-45", "open", "close", "balance",
    "pad", "note", "event", "price", "commodity", "custom", "document", "query", "txn",
    "pushtag", "poptag", "pushmeta", "popmeta", "option", "include", "plugin", "*", "!",
    "#", "&", "?", "%", "P", "T", "Z", "USD", "EUR", "Assets:A", "Expenses:B", "Assets:a",
    '"s"', '"a b"', '"x', "5", "1.5", "-3", "1,000", "1,50", "#t", "^l", "kk:", "k:", ":",
    "|", "@", "@@", "{", "}", "{{", "}}", ",", "~", "+", "(", ")", "/", "$", "x", "foo",
    "TRUE", "NULL", ";c",
]  # fmt: skip
G2_ODD = [BOM, "\x11", "\r", "AB-C", "/6J"]
G2B_HEAVY = [BOM, "\r", BOM, "\r", "A" + BOM, BOM + "x", BOM + "2024-01-02", "Assets:" + BOM + "A"]


def g2(seed: int, n: int) -> list[str]:
    r = random.Random(seed)
    vocab = G2_TOKENS + G2_ODD
    out: set[str] = set()
    while len(out) < n:
        lines = ["2024-01-01 open Assets:A"] if r.random() < 0.5 else []
        for _ in range(r.randint(1, 6)):
            toks = [r.choice(vocab) for _ in range(r.randint(0, 6))]
            sep = " " if r.random() < 0.8 else ""
            lines.append(r.choice(["", "", "  ", "\t", " "]) + sep.join(toks))
        out.add(_finish(r, lines, 0.1))
    return sorted(out)


def g2b(seed: int, n: int) -> list[str]:
    r = random.Random(seed)
    vocab = G2_TOKENS + [t for t in G2_ODD if t not in (BOM, "\r")]
    out: set[str] = set()
    while len(out) < n:
        lines = ["2024-01-01 open Assets:A"] if r.random() < 0.5 else []
        for _ in range(r.randint(1, 6)):
            toks = [
                r.choice(G2B_HEAVY) if r.random() < 0.15 else r.choice(vocab)
                for _ in range(r.randint(0, 6))
            ]
            sep = " " if r.random() < 0.8 else r.choice(["", "\r", "\t"])
            indent = r.choice(["", "", "  ", "\t", " ", BOM, "  " + BOM, "\r", "\r  "])
            lines.append(indent + sep.join(toks))
        text = _finish(r, lines, 0.3)
        if BOM in text or "\r" in text:
            out.add(text)
    return sorted(out)


# -- G3 ---------------------------------------------------------------------

G3_INSERTS = [
    "pushtag #a $", 'option "title"', '2024-01-02 2024-01-03 * "n"', "$", "!",
    "  2024-02-30 5", '"abc', "  x", "", ";c", "2024-01-02 open Assets:B $",
    '$ 2024-01-02 * "y"', '  option "a" "b"', "x", "  $", "2024-01-02 123", "AB-C",
    "  Assets:A 1 USD 5", "  kk: 5 5", '2024-01-02 * "a" "b" "c"', "k: 1", "\t2024-02-30",
    "  Assets:a 1 USD",
]  # fmt: skip
G3_MUTATIONS = ["$", "x", "2024-02-30", "5", '"', "#", "!", "k:", "Z", "1,50", "|", ""]
G3B_MUTATIONS = [BOM, "\r", BOM + "x", "x\r", *G3_MUTATIONS]


@cache
def seed_ledgers() -> tuple[tuple[str, ...], ...]:
    """The bundled seed corpus, as lists of lines, in file-name order."""
    out = []
    for path in sorted(SEEDS_DIR.glob("*.beancount")):
        text = path.read_text(encoding="utf-8")
        if text.strip():
            out.append(tuple(text.split("\n")))
    return tuple(out)


def _g3(seed: int, n: int, mutations: list[str], crlf: float, biased: bool) -> list[str]:
    r = random.Random(seed)
    ledgers = seed_ledgers()
    out: set[str] = set()
    while len(out) < n:
        lines = r.choice(ledgers)
        a = r.randrange(len(lines))
        seg = list(lines[a : a + r.randint(3, 25)])
        for _ in range(r.randint(1, 3)):
            if r.random() < 0.5:
                seg.insert(r.randint(0, len(seg)), r.choice(G3_INSERTS))
            elif seg:
                i = r.randrange(len(seg))
                words = seg[i].split(" ")
                j = r.randrange(len(words))
                if r.random() < 0.6:
                    words[j] = r.choice(mutations)
                else:
                    words[j] += r.choice(mutations)
                seg[i] = " ".join(words)
        text = "\n".join(seg)
        if r.random() < 0.9:
            text += "\n"
        if r.random() < crlf:
            text = text.replace("\n", "\r\n")
        if not biased or BOM in text or "\r" in text:
            out.add(text)
    return sorted(out)


def g3(seed: int, n: int) -> list[str]:
    return _g3(seed, n, G3_MUTATIONS, 0.05, biased=False)


def g3b(seed: int, n: int) -> list[str]:
    return _g3(seed, n, G3B_MUTATIONS, 0.3, biased=True)


GENERATORS = {
    g.name: g
    for g in [
        Generator("g1", g1, "lines from lists of valid, broken and indented statements"),
        Generator("g1b", g1b, "G1 with BOMs and carriage returns inserted"),
        Generator("g2", g2, "lines of random tokens"),
        Generator("g2b", g2b, "G2 biased toward BOMs and carriage returns"),
        Generator("g3", g3, "windows of real ledgers, with inserts and mutations"),
        Generator("g3b", g3b, "G3 biased toward BOMs and carriage returns"),
    ]
}
