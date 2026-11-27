# Equivalence harness for the clean-room LALR grammar

These scripts check that [`../beancount.y`](../beancount.y) reports syntax errors exactly like beancount 3.2.3, and that [`../LEXICAL.md`](../LEXICAL.md) (executable form: `reflexer.py`) tokenises exactly like it.
beancount is used only as a black box through its public Python API.

| File | Purpose |
|------|---------|
| `lalr.py` | Runs bison on the grammar, extracts the LALR tables from the generated C, and replays them over a token list with yacc.c error recovery. No beancount dependency. |
| `oracle.py` | Worker pool around `lex_iter_string` / `parse_string`. Each worker is a separate process, because some inputs crash beancount. |
| `equivalence.py` | Compares syntax-error count, lines and messages on a set of inputs; optionally compares the reference lexer too. |
| `explore.py` | Random walks over beancount's language comparing, at every step, the set of tokens each side accepts next and the rejection messages. Needs no corpus. |
| `reflexer.py` | The lexical rule table of `LEXICAL.md` as code. |

## Requirements

- bison >= 3.6 on `PATH` (or `$BISON`);
- a Python with `beancount==3.2.3` importable (or point `$BEANCOUNT_PYTHON` at one for the oracle workers).

With nix:

```bash
nix shell nixpkgs#bison --impure --expr \
  'let p = import (builtins.getFlake "nixpkgs") {}; in p.python3.withPackages (ps: [ ps.beancount ])' \
  -c python3 equivalence.py --random 2000 --check-lexer
```

## Usage

```bash
# Random inputs plus the conformance tests' inline sources
python3 equivalence.py --random 5000 --inline-tests ../../../../../tests --check-lexer

# A corpus directory (files are read as bytes); cache oracle results between runs
python3 equivalence.py --cache /tmp/bc-cache.tsv --dir /path/to/fuzz-corpus \
    --dir '/path/to/rustledger/tests/compatibility::*.beancount' \
    --mismatches /tmp/mismatches.jsonl

# Viable-prefix exploration
python3 explore.py --walks 500 --steps 40
```

An input **matches** when the number of syntax errors and the line of each agree.
The stricter "exact message" metric also requires identical `syntax error, unexpected X, expecting ...` texts.

Inputs are excluded from the rates when beancount itself fails:

- **crash**: the interpreter dies (segfault);
- **exception**: `parse_string` raises (seen with unbalanced `pushmeta` whose value is not a string);
- **divide-by-zero quirk**: an arithmetic expression divides by zero; beancount then replaces the next token with a lexer error (`SystemError: ... returned a result with an exception set`), so the parser no longer sees the token stream `lex_iter_string` reports.

Only errors whose message starts with `syntax error` are compared.
Errors raised by beancount's semantic actions (`Pipe symbol is deprecated.`, too many strings, invalid option, ...) are not syntax errors and are not modelled.

## Why the token stream is beancount's

The harness feeds the grammar beancount's own token stream, so the grammar comparison is independent of the lexer.
The lexer is checked separately (`--check-lexer`) against the same stream.

## Results

Against beancount 3.2.3, at the time of writing:

| Input set | Inputs | Compared | Count + lines | Exact messages | Reference lexer |
|-----------|-------:|---------:|--------------:|---------------:|----------------:|
| rustledger `fuzz-corpus` @ `9bc79f4f` (all targets) | 71,784 | see PR | 100% | 100% | see PR |
| rustledger `tests/compatibility/**/*.beancount` | 731 | see PR | 100% | 100% | see PR |
| G1–G3 generators (6 × 3,000) | 18,000 | 17,998 | 100% | 100% | see PR |
| `--random 5000` + conformance inline tests | 5,480 | 5,479 | 100% | 100% | 100% |
