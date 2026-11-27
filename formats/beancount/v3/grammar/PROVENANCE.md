# Provenance of the clean-room LALR grammar

This file records which sources informed `beancount.y`, `LEXICAL.md` and the harness, so that their clean-room status can be audited.

beancount is GPL-2.0-only.
These artefacts are MIT-licensed and are intended to be embeddable in GPL-3.0-only software, so none of them may be derived from beancount's code.

## Sources that were NOT used

None of the following was opened, read, searched, quoted, compiled or run through bison while writing these files:

- beancount's grammar and lexer sources: `grammar.y`, `lexer.l`, the generated `parser.c` / `lexer.c`, `tokens.c` / `tokens.h`, `grammar.py`, `lexer.py`, in any location (pip / nix store package, `reference/sources/beancount`, or any copy elsewhere);
- any file generated from them (for example bison reports or tables generated from `grammar.y`);
- rustledger's lexer and recovery code (`crates/rustledger-parser/src/cst/recovery.rs` is itself a port of `lexer.l`), or any other rustledger source.

One incidental exposure is recorded for completeness: an uncaught Python exception during a black-box run printed a traceback whose last frames named beancount's `grammar.py` (`finalize`, a line joining pushed metadata values).
Nothing in these files depends on it; the corresponding inputs are simply counted as "beancount exception" by the harness.

## Sources that were used

| Source | Kind | Used for |
|--------|------|----------|
| beancount public user documentation (language syntax), and the prose of `formats/beancount/v3/spec/` | Documentation | The initial shape of every directive in `beancount.y`; the initial token inventory in `LEXICAL.md`. Spec claims were treated as hypotheses and tested. |
| `beancount.parser.lexer.lex_iter_string` (beancount 3.2.3, called, not read) | Black-box oracle | Token *names* (the grammar's terminals); every rule in `LEXICAL.md` / `harness/reflexer.py`, by feeding chosen inputs and recording the tokens, lines and texts that come back; the token stream replayed by the equivalence harness. |
| `beancount.parser.parser.parse_string` (beancount 3.2.3, called, not read) | Black-box oracle | Whether, where (line) and how ("unexpected X, expecting A or B") syntax errors are reported, for chosen inputs. |
| `bean-check` (beancount 3.2.3) | Black-box oracle | Spot checks only. |
| Facts supplied with the task | Observations | Error recovery resumes only at top level; three tokens must shift before another error is reported (standard yacc); lexer errors reach the parser as an error token. All three were re-confirmed by experiment. |
| GNU bison 3.8 documentation and behaviour | Tool | yacc.c error-recovery semantics (`yyerrstatus`, `YYerror` from the scanner, verbose message format with at most four expected tokens), implemented independently in `harness/lalr.py`. |
| rustledger corpora: the `fuzz-corpus` branch at `9bc79f4f`, `tests/compatibility` | Test inputs (read-only) | Inputs for the equivalence harness. Only used as data. |
| G1–G3 generators (`~/drafts/parser-research/rbc/gen*.py`, our own code) | Test-input generators | Inputs for the equivalence harness. |

## Which experiment informed which decision

| Decision | Evidence |
|----------|----------|
| Only one `error` production, at top level, of the form `declarations error` | After an error, tokens are discarded until one that can start a declaration, even in the middle of a line: `pushtag #a #b 2024-01-01 open Assets:A` reports one error and still creates the Open entry. Errors inside postings swallow all following indented lines. |
| Lexer errors as bison `YYerror` (recovery without a report) | `2024-01-01 open Assets:A $` reports only the lexer error, and the entry is dropped. |
| `eol : EOL \| YYEOF` | `option "a" "b"` without a final newline parses; `2024-01-01 open` at end of input reports `unexpected end of file, expecting ACCOUNT`; complete lines report `expecting end of file or EOL`. |
| Undated directives take no indented lines; INDENT at top level is an error | `option "a" "b"` followed by `  ;c` reports `unexpected INDENT`. |
| `INDENT tags_links eol` in transactions (and so indented comments) | After `INDENT` in a transaction, an unexpected token reports `expecting end of file or EOL or TAG or LINK` (an empty tag list was reduced first). |
| `kv_lines` allow only `KEY` or a comment after `INDENT` | `expecting end of file or EOL or KEY` after an indent under `open`. |
| Posting alternatives each end with `eol` | `expecting end of file or EOL or ATAT or AT` after an account or amount. |
| `CAPITAL` as currency and flag | `kk: P`, `1 P`, `2024-01-01 P "x"`, `  P Assets:A` are all accepted. |
| `custom` value conflict resolved by shifting (`%expect 2`) | `custom "x" 1 -2` yields one value, -1. |
| Token declaration order | All "expecting ..." lists observed (e.g. `HASH or CAPITAL or CURRENCY`, `PLUS or MINUS or LPAREN or NUMBER`, `RCURL or COMMA`, `end of file or EOL or ATAT or AT`). |
| Every remaining detail of the language | `harness/explore.py`: next-token acceptance sets and rejection messages compared at every step of random walks; then `harness/equivalence.py` over the corpora. |
| Every rule of `LEXICAL.md` | Character-by-character probes (each character after each token kind, each character in column 0, enumeration of all digit/comma strings up to 11 characters for number grouping, dates, strings and escapes, control characters, invalid UTF-8, BOM, CR), then `equivalence.py --check-lexer` over the corpora. |
