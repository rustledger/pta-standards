#!/usr/bin/env python3
"""Equivalence harness: clean-room LALR grammar vs. beancount's parser.

For every input:

1. beancount's lexer (``lex_iter_string``) gives the token stream and
   beancount's parser (``parse_string``) gives the reference syntax errors
   (errors whose message starts with ``syntax error``);
2. the grammar is compiled with bison and its LALR tables are replayed over
   that same token stream with yacc error recovery (``lalr.py``);
3. the two lists of syntax errors are compared.

An input *matches* when the number of syntax errors and the line of each one
agree.  Exact message agreement (``unexpected X, expecting A or B``) is
reported separately as a stricter, informational metric.

Inputs on which beancount itself crashes or raises are counted separately
and excluded from the match rate.

Usage::

    equivalence.py [--grammar beancount.y] [--cache FILE] [--jobs N]
                   [--dir DIR ...] [--json FILE ...] [--file FILE ...]
                   [--sample N] [--mismatches OUT.jsonl] [--min-rate R]
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import hashlib
import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lalr import Parser, compile_grammar  # noqa: E402
from oracle import OraclePool  # noqa: E402

# A division by zero inside an arithmetic expression leaves a pending Python
# exception behind in beancount 3.2.3; the *next* token the lexer produces is
# then replaced by a lexer error carrying this text, so the parser no longer
# sees the token stream that lex_iter_string reports (when it does not simply
# segfault).  Such inputs are excluded.
DZ_MARK = "returned a result with an exception set"


def load_inputs(args) -> list[tuple[str, bytes]]:
    items: list[tuple[str, bytes]] = []
    for d in args.dir or []:
        d, _, pattern = d.partition("::")
        for root, dirs, files in os.walk(d):
            dirs[:] = sorted(x for x in dirs if x != ".git")
            for f in sorted(files):
                if pattern and not fnmatch.fnmatch(f, pattern):
                    continue
                p = os.path.join(root, f)
                with open(p, "rb") as fh:
                    items.append((p, fh.read()))
    for j in args.json or []:
        with open(j) as fh:
            for k, s in enumerate(json.load(fh)):
                items.append((f"{j}#{k}", s.encode("utf-8", "surrogatepass")))
    for p in args.file or []:
        with open(p, "rb") as fh:
            items.append((p, fh.read()))
    for d in args.inline_tests or []:
        for root, dirs, files in os.walk(d):
            dirs.sort()
            if "tests.json" in files:
                p = os.path.join(root, "tests.json")
                with open(p) as fh:
                    doc = json.load(fh)
                for t in doc.get("tests", []) if isinstance(doc, dict) else []:
                    src = (
                        t.get("input", {}).get("inline")
                        if isinstance(t.get("input"), dict)
                        else None
                    )
                    if isinstance(src, str):
                        items.append((f"{p}#{t.get('id')}", src.encode()))
    if args.random:
        items.extend(random_inputs(args.random, args.seed))
    if args.max_bytes:
        items = [it for it in items if len(it[1]) <= args.max_bytes]
    if args.sample and len(items) > args.sample:
        items = random.Random(args.seed).sample(items, args.sample)
    return items


# Pieces for random inputs: well-formed lines, broken lines and token soup.
_LINES = [
    "2024-01-01 open Assets:A USD",
    '2024-01-01 open Assets:A USD,EUR "FIFO"',
    '2024-01-02 * "p" "n" #t ^l',
    '2024-01-02 txn "n"',
    '2024-01-02 ! "n"',
    "2024-01-02 P",
    "  Assets:A  -1,000.50 USD",
    "  Assets:A 1 HOOL {10 USD}",
    '  Assets:A 1 HOOL {{10 USD, 2024-01-01, "lot"}} @ 11 USD',
    "  Assets:A 1 HOOL {1 # 2 USD} @@ 3 USD",
    "  ! Assets:B",
    '  kk: "v"',
    "  kk: 1 + 2 * (3 - 1) USD",
    "  #tag ^link",
    "  ;comment",
    "  Assets:A {}",
    "2024-01-03 balance Assets:A 1 ~ 0.01 USD",
    "2024-01-03 pad Assets:A Equity:B",
    "2024-01-03 close Assets:A",
    "2024-01-03 commodity USD",
    "2024-01-03 price HOOL 10 USD",
    '2024-01-03 event "a" "b"',
    '2024-01-03 query "a" "b"',
    '2024-01-03 note Assets:A "x" #t',
    '2024-01-03 document Assets:A "f.pdf" ^l',
    '2024-01-03 custom "x" 1 USD TRUE "s" Assets:A 2024-01-01',
    'option "title" "x"',
    'include "x.bean"',
    'plugin "p" "cfg"',
    "pushtag #a",
    "poptag #a",
    'pushmeta kk: "v"',
    "popmeta kk:",
    "* heading",
    "",
    ";c",
    "garbage line",
    "2024-02-30 open Assets:A",
    "  $",
    "1,0",
]
_SOUP = [
    "2024-01-02",
    "open",
    "close",
    "balance",
    "pad",
    "note",
    "event",
    "price",
    "commodity",
    "custom",
    "document",
    "query",
    "txn",
    "pushtag",
    "poptag",
    "pushmeta",
    "popmeta",
    "option",
    "include",
    "plugin",
    "*",
    "!",
    "#",
    "&",
    "P",
    "USD",
    "Assets:A",
    '"s"',
    "5",
    "1.5",
    "-",
    "+",
    "/",
    "#t",
    "^l",
    "kk:",
    ":",
    "|",
    "@",
    "@@",
    "{",
    "}",
    "{{",
    "}}",
    ",",
    "~",
    "(",
    ")",
    "$",
    "TRUE",
    "NULL",
    ";c",
    "x",
]


def random_inputs(n: int, seed: int) -> list[tuple[str, bytes]]:
    """Deterministic random inputs mixing valid lines, broken lines and token soup."""
    r = random.Random(seed)
    out = []
    for k in range(n):
        lines = []
        for _ in range(r.randint(1, 8)):
            if r.random() < 0.6:
                line = r.choice(_LINES)
                if r.random() < 0.3 and line:
                    ws = line.split(" ")
                    ws.insert(r.randrange(len(ws) + 1), r.choice(_SOUP))
                    line = " ".join(ws)
            else:
                line = r.choice(["", "", "  ", "\t"]) + " ".join(
                    r.choice(_SOUP) for _ in range(r.randint(1, 6))
                )
            lines.append(line)
        nl = "\r\n" if r.random() < 0.1 else "\n"
        text = nl.join(lines) + (nl if r.random() < 0.8 else "")
        out.append((f"random#{seed}:{k}", text.encode()))
    return out


class Cache:
    def __init__(self, path: str | None):
        self.path = path
        self.data: dict[str, dict] = {}
        if path and os.path.exists(path):
            with open(path) as f:
                for line in f:
                    k, v = line.split("\t", 1)
                    self.data[k] = json.loads(v)
        self.fh = open(path, "a") if path else None  # noqa: SIM115 (lives as long as the run)

    @staticmethod
    def key(b: bytes) -> str:
        return hashlib.sha1(b).hexdigest()

    def get(self, b: bytes):
        return self.data.get(self.key(b))

    def put(self, b: bytes, v: dict) -> None:
        k = self.key(b)
        self.data[k] = v
        if self.fh:
            self.fh.write(k + "\t" + json.dumps(v) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--grammar", default=os.path.join(HERE, "..", "beancount.y"))
    ap.add_argument(
        "--dir",
        action="append",
        help="directory of input files (read as bytes); DIR::PATTERN keeps only file names matching PATTERN",
    )
    ap.add_argument("--json", action="append")
    ap.add_argument("--file", action="append")
    ap.add_argument(
        "--inline-tests",
        action="append",
        help="directory searched for conformance tests.json files; their input.inline sources are used",
    )
    ap.add_argument(
        "--random",
        type=int,
        default=0,
        help="add N random token-soup inputs (see random_inputs; uses --seed)",
    )
    ap.add_argument("--cache")
    ap.add_argument("--jobs", type=int)
    ap.add_argument("--sample", type=int)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-bytes", type=int, default=0, help="skip inputs larger than this")
    ap.add_argument("--mismatches", help="write mismatching inputs here (JSON lines)")
    ap.add_argument(
        "--message-mismatches", help="write inputs whose messages differ here (JSON lines)"
    )
    ap.add_argument(
        "--min-rate",
        type=float,
        help="exit 1 if the match rate (and, with --check-lexer, the lexer rate) is below this (0-100)",
    )
    ap.add_argument(
        "--check-lexer",
        action="store_true",
        help="also compare the reference lexer (reflexer.py) with beancount's token stream",
    )
    ap.add_argument(
        "--lexer-mismatches", help="write inputs where the reference lexer differs here"
    )
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    tables = compile_grammar(args.grammar)
    parser = Parser(tables)
    items = load_inputs(args)
    cache = Cache(args.cache)

    todo = [i for i, (_, b) in enumerate(items) if cache.get(b) is None]
    if todo:
        pool = OraclePool(args.jobs)
        for done, (k, res) in enumerate(pool.map([items[i][1] for i in todo]), 1):
            cache.put(items[todo[k]][1], res)
            if not args.quiet and done % 2000 == 0:
                print(f"  oracle: {done}/{len(todo)}", file=sys.stderr)

    if args.check_lexer:
        import reflexer
    lex_out = open(args.lexer_mismatches, "w") if args.lexer_mismatches else None  # noqa: SIM115
    stats = Counter()
    kinds = Counter()
    mism_out = open(args.mismatches, "w") if args.mismatches else None  # noqa: SIM115
    msg_out = open(args.message_mismatches, "w") if args.message_mismatches else None  # noqa: SIM115
    for name, data in items:
        res = cache.get(data)
        st = res["status"]
        if st == "ok" and any(DZ_MARK in o[2] for o in res["other"]):
            st = "divzero"
        if st != "ok":
            stats[st] += 1
            continue
        stats["compared"] += 1
        if args.check_lexer:
            mine = [[t, ln] for t, ln, _ in reflexer.lex(data)]
            if mine == res["tokens"]:
                stats["lex_match"] += 1
            elif lex_out:
                lex_out.write(
                    json.dumps(
                        {
                            "name": name,
                            "input": base64.b64encode(data).decode(),
                            "beancount": res["tokens"],
                            "reflexer": mine,
                        }
                    )
                    + "\n"
                )
        ref = [(ln, msg) for ln, msg in res["syntax"]]
        got = [(e.line, e.message) for e in parser.run([tuple(t) for t in res["tokens"]])]
        if ref:
            stats["with_errors"] += 1
            stats["errors"] += len(ref)
        if [ln for ln, _ in ref] == [ln for ln, _ in got]:
            stats["match"] += 1
            if ref == got:
                stats["message_match"] += 1
            elif msg_out:
                msg_out.write(
                    json.dumps(
                        {
                            "name": name,
                            "text": data.decode("utf-8", "replace"),
                            "beancount": ref,
                            "grammar": got,
                        }
                    )
                    + "\n"
                )
            continue
        stats["mismatch"] += 1
        if len(ref) != len(got):
            kinds[f"count {len(got) - len(ref):+d}"] += 1
        else:
            kinds["line"] += 1
        if mism_out:
            mism_out.write(
                json.dumps(
                    {
                        "name": name,
                        "input": base64.b64encode(data).decode(),
                        "text": data.decode("utf-8", "replace"),
                        "beancount": ref,
                        "grammar": got,
                    }
                )
                + "\n"
            )

    c = stats["compared"]
    rate = 100.0 * stats["match"] / c if c else 100.0
    mrate = 100.0 * stats["message_match"] / c if c else 100.0
    print(
        f"inputs: {len(items)}  compared: {c}  beancount crash: {stats['crash']}  "
        f"beancount exception: {stats['exception']}  divide-by-zero quirk: {stats['divzero']}"
    )
    print(
        f"inputs with syntax errors (beancount): {stats['with_errors']}  syntax errors: {stats['errors']}"
    )
    print(f"error count+lines match: {stats['match']}/{c} = {rate:.3f}%")
    print(f"exact message match:     {stats['message_match']}/{c} = {mrate:.3f}%")
    if args.check_lexer:
        print(
            f"reference lexer tokens:  {stats['lex_match']}/{c} = {100.0 * stats['lex_match'] / max(c, 1):.3f}%"
        )
    if kinds:
        print("mismatch kinds (grammar vs beancount):", dict(kinds.most_common()))
    if args.min_rate is not None:
        if rate < args.min_rate:
            return 1
        if args.check_lexer and c and 100.0 * stats["lex_match"] / c < args.min_rate:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
