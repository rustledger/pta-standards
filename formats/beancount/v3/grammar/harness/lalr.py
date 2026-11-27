"""Compile a bison grammar and replay its LALR tables over a token stream.

This module is self-contained and has no dependency on beancount.

``compile_grammar`` runs ``bison`` on a ``.y`` file and extracts the
generated parse tables from the C output (``yypact``, ``yydefact``,
``yytable``, ``yycheck``, ...).  ``Parser.run`` replays those tables over a
list of ``(token_name, line)`` pairs with the error-recovery behaviour of
bison's ``yacc.c`` skeleton (bison >= 3.6):

* a syntax error is *reported* only when ``yyerrstatus`` is 0;
* on any error the parser pops states until one can shift ``error``,
  shifts it, and sets ``yyerrstatus`` to 3;
* while ``yyerrstatus`` is 3 an unacceptable lookahead is discarded (at end
  of input the parse is aborted instead);
* every successful token shift decrements ``yyerrstatus``;
* a token named ``error`` coming from the lexer (bison's ``YYerror``) enters
  recovery directly, without a report, and the lookahead becomes the
  "invalid token" symbol, which is then discarded like any other.

The end of input is fed as token 0 (``"end of file"``) for as long as the
parser asks for more tokens, like a flex scanner does.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field

ARRAYS = ("yypact", "yydefact", "yypgoto", "yydefgoto", "yytable", "yycheck", "yyr1", "yyr2")
DEFINES = (
    "YYFINAL",
    "YYLAST",
    "YYNTOKENS",
    "YYNNTS",
    "YYNRULES",
    "YYNSTATES",
    "YYPACT_NINF",
    "YYTABLE_NINF",
)


@dataclass
class Tables:
    names: list[str]
    arrays: dict[str, list[int]]
    defines: dict[str, int]
    table_ninf_is_error: bool
    token_index: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        ntok = self.defines["YYNTOKENS"]
        for i, n in enumerate(self.names[:ntok]):
            self.token_index[n] = i


def _unquote(name: str) -> str:
    # yytname entries for aliased tokens are C strings containing a quoted
    # string, e.g. "\"end of file\"".  bison's yytnamerr strips the quotes.
    name = name.encode().decode("unicode_escape")
    if len(name) >= 2 and name[0] == '"' and name[-1] == '"':
        return name[1:-1]
    return name


def parse_c_tables(c_source: str) -> Tables:
    arrays: dict[str, list[int]] = {}
    for a in ARRAYS:
        m = re.search(r"static const \w+ " + a + r"\[\] =\s*\{([^}]*)\}", c_source)
        if not m:
            raise ValueError(f"table {a} not found in bison output")
        arrays[a] = [int(x) for x in m.group(1).replace("\n", " ").split(",") if x.strip()]
    defines = {}
    for d in DEFINES:
        m = re.search(r"#define " + d + r"\s+\(?(-?\d+)\)?", c_source)
        if not m:
            raise ValueError(f"define {d} not found in bison output")
        defines[d] = int(m.group(1))
    m = re.search(r"static const char \*const yytname\[\] =\s*\{(.*?)YY_NULLPTR", c_source, re.S)
    if not m:
        raise ValueError("yytname not found (use %define parse.error verbose)")
    names = [_unquote(x) for x in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]
    m = re.search(r"#define yytable_value_is_error\(Yyn\)\s*\\\s*(.*)", c_source)
    ninf_err = bool(m and "YYTABLE_NINF" in m.group(1))
    return Tables(names, arrays, defines, ninf_err)


def compile_grammar(path: str, bison: str | None = None) -> Tables:
    bison = bison or os.environ.get("BISON") or shutil.which("bison")
    if not bison:
        raise RuntimeError("bison not found (set $BISON or put it on PATH)")
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "parser.c")
        subprocess.run(
            [bison, "-Wall", "-Werror=conflicts-rr", "-o", out, path],
            check=True,
            capture_output=True,
            text=True,
        )
        with open(out) as f:
            return parse_c_tables(f.read())


@dataclass
class SyntaxErrorReport:
    line: int
    message: str


class Abort(Exception):
    pass


class Parser:
    """Replays bison LALR tables with yacc.c error recovery."""

    EMPTY = -2

    def __init__(self, tables: Tables):
        self.t = tables
        a, d = tables.arrays, tables.defines
        self.pact, self.defact = a["yypact"], a["yydefact"]
        self.pgoto, self.defgoto = a["yypgoto"], a["yydefgoto"]
        self.table, self.check = a["yytable"], a["yycheck"]
        self.r1, self.r2 = a["yyr1"], a["yyr2"]
        self.final, self.last = d["YYFINAL"], d["YYLAST"]
        self.ntokens = d["YYNTOKENS"]
        self.pact_ninf, self.table_ninf = d["YYPACT_NINF"], d["YYTABLE_NINF"]
        self.ERROR = tables.token_index["error"]
        self.UNDEF = tables.token_index["invalid token"]

    def _table_is_error(self, v: int) -> bool:
        return self.t.table_ninf_is_error and v == self.table_ninf

    def expected(self, state: int) -> list[str]:
        """Tokens listed by bison's verbose message for ``state`` (all of them)."""
        res = []
        yyn = self.pact[state]
        if yyn == self.pact_ninf:
            return res
        xbegin = -yyn if yyn < 0 else 0
        checklim = self.last - yyn + 1
        xend = min(checklim, self.ntokens)
        for x in range(xbegin, xend):
            if (
                self.check[x + yyn] == x
                and x != self.ERROR
                and not self._table_is_error(self.table[x + yyn])
            ):
                res.append(self.t.names[x])
        return res

    def message(self, state: int, token: int) -> str:
        exp = self.expected(state)
        msg = "syntax error, unexpected " + self.t.names[token]
        if 0 < len(exp) <= 4:
            msg += ", expecting " + " or ".join(exp)
        return msg

    def run(self, tokens: list[tuple[str, int]], trace: bool = False) -> list[SyntaxErrorReport]:
        """Parse ``tokens`` (name, line); return the syntax errors bison would report."""
        idx = self.t.token_index
        errors: list[SyntaxErrorReport] = []
        stack = [0]
        pos = 0
        n = len(tokens)
        last_line = tokens[-1][1] if tokens else 1
        yychar = self.EMPTY  # symbol number of the lookahead, or EMPTY
        yyline = last_line
        errstatus = 0
        state = 0

        def read():
            nonlocal pos
            if pos < n:
                name, line = tokens[pos]
                pos += 1
                if name == "error":
                    return "LEXERR", line
                if name not in idx:
                    raise KeyError(f"token {name!r} is not a terminal of the grammar")
                return idx[name], line
            return 0, last_line

        while True:
            # yynewstate / yybackup
            if state == self.final:
                return errors
            yyn = self.pact[state]
            goto_errlab = False
            reduce_rule = None
            if yyn == self.pact_ninf:
                reduce_rule = self.defact[state]
                if reduce_rule == 0:
                    goto_errlab = True
            else:
                if yychar == self.EMPTY:
                    tok, yyline = read()
                    if tok == "LEXERR":
                        # Scanner returned YYerror: straight to yyerrlab1,
                        # lookahead becomes YYUNDEF.
                        yychar = self.UNDEF
                        state = self._recover(stack)
                        errstatus = 3
                        if state is None:
                            return errors
                        continue
                    yychar = tok
                k = yyn + yychar
                if 0 <= k <= self.last and self.check[k] == yychar:
                    act = self.table[k]
                    if act <= 0:
                        if self._table_is_error(act):
                            goto_errlab = True
                        else:
                            reduce_rule = -act
                    else:
                        # shift
                        if errstatus:
                            errstatus -= 1
                        if trace:
                            print(f"shift {self.t.names[yychar]} -> {act}")
                        stack.append(act)
                        state = act
                        yychar = self.EMPTY
                        continue
                else:
                    reduce_rule = self.defact[state]
                    if reduce_rule == 0:
                        goto_errlab = True
            if goto_errlab:
                if errstatus == 0:
                    tokname = yychar if yychar != self.EMPTY else None
                    msg = self.message(state, tokname) if tokname is not None else "syntax error"
                    errors.append(SyntaxErrorReport(yyline, msg))
                    if trace:
                        print(f"ERROR line {yyline}: {msg}")
                if errstatus == 3:
                    if yychar == 0:
                        return errors  # YYABORT at end of input
                    if yychar != self.EMPTY:
                        yychar = self.EMPTY  # discard lookahead
                state = self._recover(stack)
                errstatus = 3
                if state is None:
                    return errors
                continue
            # reduce
            ln = self.r2[reduce_rule]
            if ln:
                del stack[-ln:]
            lhs = self.r1[reduce_rule] - self.ntokens
            top = stack[-1]
            gi = self.pgoto[lhs] + top
            if 0 <= gi <= self.last and self.check[gi] == top:
                state = self.table[gi]
            else:
                state = self.defgoto[lhs]
            if trace:
                print(f"reduce {reduce_rule} -> {state}")
            stack.append(state)

    def _recover(self, stack: list[int]):
        """yyerrlab1: pop to a state that shifts ``error``; shift it."""
        while True:
            s = stack[-1]
            yyn = self.pact[s]
            if yyn != self.pact_ninf:
                k = yyn + self.ERROR
                if 0 <= k <= self.last and self.check[k] == self.ERROR:
                    v = self.table[k]
                    if v > 0:
                        stack.append(v)
                        return v
            if len(stack) == 1:
                return None  # YYABORT
            stack.pop()
