#!/usr/bin/env python3
"""Next-token exploration: compare viable prefixes of the grammar and beancount.

An LALR parser never shifts a token that cannot continue a valid input
(the *viable-prefix property*), so the token at which a syntax error is
detected depends only on the set of viable prefixes of the language.  This
tool measures that set directly instead of hoping a corpus covers it.

It performs random walks over beancount's language, one token at a time.
At every step it renders the current token prefix as text, appends every
candidate token and asks beancount (black box, ``parse_string``) whether a
syntax error is reported *at the candidate*.  The resulting acceptance set
is compared with the one computed from the grammar's LALR tables.  For
rejected candidates the two ``syntax error, unexpected ...`` messages are
also compared (informational: it checks that the expected-token lists, and
hence the LR states, agree).

Usage::

    explore.py [--grammar beancount.y] [--walks N] [--steps N] [--seed S] [--jobs N]

Each walk is printed only when it diverges.  Exit status is 1 if any
acceptance set diverged.
"""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import pickle
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lalr import Parser, compile_grammar  # noqa: E402

# One sample spelling per token kind.  KEY can only be lexed in front of a
# colon, so its sample produces KEY COLON.
SAMPLES = {
    "DATE": "2024-01-01", "OPEN": "open", "CLOSE": "close", "COMMODITY": "commodity", "PAD": "pad",
    "BALANCE": "balance", "PRICE": "price", "EVENT": "event", "QUERY": "query", "NOTE": "note",
    "DOCUMENT": "document", "CUSTOM": "custom", "OPTION": "option", "PLUGIN": "plugin",
    "INCLUDE": "include", "PUSHTAG": "pushtag", "POPTAG": "poptag", "PUSHMETA": "pushmeta",
    "POPMETA": "popmeta", "TXN": "txn", "BOOL": "TRUE", "NONE": "NULL", "COMMA": ",", "MINUS": "-",
    "PLUS": "+", "SLASH": "/", "AT": "@", "ATAT": "@@", "LCURL": "{", "RCURL": "}", "LCURLCURL": "{{",
    "RCURLCURL": "}}", "TILDE": "~", "LPAREN": "(", "RPAREN": ")", "PIPE": "|", "STRING": '"s"',
    "TAG": "#t", "LINK": "^l", "KEY": "kk:", "COLON": ":", "ACCOUNT": "Assets:A", "CURRENCY": "USD",
    "CAPITAL": "P", "NUMBER": "1", "ASTERISK": "*", "FLAG": "!", "HASH": "#", "EOL": "\n",
    "INDENT": "  ",
}
TOKENS = list(SAMPLES)


def expand(toks):
    out = []
    for t in toks:
        out.append(t)
        if t == "KEY":
            out.append("COLON")
    return out


def render(toks) -> bytes:
    out = []
    prev = "EOL"
    for i, t in enumerate(toks):
        s = SAMPLES[t]
        if t == "EOL" and prev == "INDENT":
            out.append(";c" + s)  # an INDENT is only lexed on a non-blank line
        elif t == "EOL" or prev in ("EOL", "INDENT") or i == 0:
            out.append(s)
        else:
            out.append(" " + s)
        prev = t
    # Some tokens (e.g. CAPITAL) need a following character; a comment keeps
    # a trailing INDENT alive.
    out.append(";c" if prev == "INDENT" else " ")
    return "".join(out).encode()


class Oracle:
    def __init__(self):
        from beancount.parser import lexer, parser
        self.lexer, self.parser = lexer, parser

    def lex(self, src):
        return [(t[0], t[1]) for t in self.lexer.lex_iter_string(src)]

    def syntax_errors(self, src):
        if b"/" in src:
            # A division by zero (e.g. `1 / (1 - 1)`) crashes beancount 3.2.3
            # or corrupts its next token; evaluate such inputs in a forked
            # child and skip the candidate if the child dies or reports the
            # quirk.
            return self._forked(src)
        return self._direct(src)

    def _direct(self, src):
        try:
            _, errs, _ = self.parser.parse_string(src)
        except Exception:  # beancount raised outside the parser proper
            return None
        if any("exception set" in e.message for e in errs):
            return None
        return [(e.source.get("lineno"), e.message) for e in errs if e.message.startswith("syntax error")]

    def _forked(self, src):
        r, w = os.pipe()
        pid = os.fork()
        if pid == 0:  # child
            os.close(r)
            try:
                data = pickle.dumps(self._direct(src))
            except BaseException:
                data = pickle.dumps(None)
            with os.fdopen(w, "wb") as f:
                f.write(data)
            os._exit(0)
        os.close(w)
        with os.fdopen(r, "rb") as f:
            data = f.read()
        os.waitpid(pid, 0)
        return pickle.loads(data) if data else None


def first_error_at_last(errors, toks_lexed, last_n):
    """Message of the first error if it is reported at one of the last ``last_n`` tokens."""
    if not errors:
        return None
    msg = errors[0][1]
    for name, _ in toks_lexed[-last_n:]:
        if msg.startswith(f"syntax error, unexpected {name}") and (
                len(msg) == len(f"syntax error, unexpected {name}") or msg[len(f"syntax error, unexpected {name}")] == ","):
            return msg
    return None


def step_sets(oracle, parser, prefix):
    acc_o, acc_g, msgs = set(), set(), {}
    for t in TOKENS:
        p2 = prefix + [t]
        src = render(p2)
        lexed = oracle.lex(src)
        if [n for n, _ in lexed] != expand(p2):
            continue  # not renderable here (e.g. lexer context)
        last_n = 2 if t == "KEY" else 1
        ref = oracle.syntax_errors(src)
        if ref is None:
            continue
        mo = first_error_at_last(ref, lexed, last_n)
        got = [(e.line, e.message) for e in parser.run(lexed)]
        mg = first_error_at_last(got, lexed, last_n)
        if mo is None:
            acc_o.add(t)
        if mg is None:
            acc_g.add(t)
        if mo is not None and mg is not None:
            msgs[t] = (mo, mg)
    return acc_o, acc_g, msgs


# Walks start from these prefixes in turn so that every directive kind and
# the deeper sub-languages (costs, prices, expressions) are reached often.
STARTS = [
    "", "DATE", "DATE ASTERISK", "DATE ASTERISK EOL INDENT", "DATE FLAG STRING EOL INDENT ACCOUNT",
    "DATE TXN EOL INDENT ACCOUNT NUMBER", "DATE ASTERISK EOL INDENT ACCOUNT LCURL",
    "DATE ASTERISK EOL INDENT ACCOUNT LCURLCURL", "DATE ASTERISK EOL INDENT ACCOUNT CURRENCY AT",
    "DATE ASTERISK EOL INDENT KEY", "DATE BALANCE ACCOUNT", "DATE OPEN ACCOUNT", "DATE CLOSE ACCOUNT",
    "DATE COMMODITY CURRENCY", "DATE PAD ACCOUNT", "DATE PRICE CURRENCY", "DATE EVENT STRING",
    "DATE QUERY STRING", "DATE NOTE ACCOUNT", "DATE DOCUMENT ACCOUNT", "DATE CUSTOM STRING",
    "DATE OPEN ACCOUNT EOL INDENT", "PUSHMETA", "POPMETA", "OPTION", "PLUGIN", "INCLUDE", "PUSHTAG",
    "POPTAG",
]

_G = {}


def _init(grammar):
    _G["parser"] = Parser(compile_grammar(grammar))
    _G["oracle"] = Oracle()


def walk(args):
    seed, steps, start = args
    r = random.Random(seed)
    parser, oracle = _G["parser"], _G["oracle"]
    prefix: list[str] = start.split()
    msg_diffs = []
    checked = 0
    for _ in range(steps):
        acc_o, acc_g, msgs = step_sets(oracle, parser, prefix)
        checked += 1
        for t, (mo, mg) in msgs.items():
            if mo != mg:
                msg_diffs.append((list(prefix), t, mo, mg))
        if acc_o != acc_g:
            return {"seed": seed, "prefix": prefix, "text": render(prefix).decode(),
                    "only_beancount": sorted(acc_o - acc_g), "only_grammar": sorted(acc_g - acc_o),
                    "msg_diffs": msg_diffs[:50], "steps": checked, "n_msg_diffs": len(msg_diffs)}
        choices = sorted(acc_o)
        if not choices:
            break
        weights = [0.15 if c == "EOL" else 1.0 for c in choices]
        prefix = prefix + [r.choices(choices, weights)[0]]
    return {"seed": seed, "ok": True, "steps": checked, "msg_diffs": msg_diffs[:50], "n_msg_diffs": len(msg_diffs)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grammar", default=os.path.join(HERE, "..", "beancount.y"))
    ap.add_argument("--walks", type=int, default=200)
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--show-messages", type=int, default=0, help="print up to N message differences")
    args = ap.parse_args()

    tasks = [(args.seed * 100003 + i, args.steps, STARTS[i % len(STARTS)]) for i in range(args.walks)]
    bad = 0
    steps = 0
    nmsg = 0
    shown = 0
    with mp.Pool(args.jobs, initializer=_init, initargs=(args.grammar,)) as pool:
        for res in pool.imap_unordered(walk, tasks):
            steps += res["steps"]
            nmsg += res["n_msg_diffs"]
            if not res.get("ok"):
                bad += 1
                print(f"DIVERGE seed={res['seed']} prefix={' '.join(res['prefix'])}")
                print(f"    text={res['text']!r}")
                print(f"    only beancount accepts: {res['only_beancount']}  only grammar accepts: {res['only_grammar']}")
            for d in res["msg_diffs"]:
                if shown < args.show_messages:
                    shown += 1
                    print(f"MSG prefix={' '.join(d[0])} + {d[1]}\n    beancount: {d[2]}\n    grammar:   {d[3]}")
    print(f"walks: {args.walks}  steps checked: {steps}  diverging walks: {bad}  "
          f"rejection-message differences: {nmsg}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
