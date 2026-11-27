# ptadiff: differential testing for plain-text-accounting implementations

`ptadiff` compares an implementation's parse errors with a reference
implementation's (the *oracle*) over many inputs. It turns the mismatches into
named **categories**, shrinks each category's example to a minimal input that
still shows that same category, and reports per-category counts that CI can pin.

It is format-generic. Each format plugs in its oracle adapter, normalizers,
generators and category key. Comparing, minimizing, clustering and reporting
are shared by all formats.

| Format | Oracle | Status |
|---|---|---|
| beancount | `beancount.parser` in process (`parse_string`, `lex_iter_string`) | complete: oracle, normalizers, `shape` / `coarse` keys, generators G1-G3(b) |
| ledger | `ledger` CLI, one process per input | stub: `LedgerOracle.parse_output` to write |
| hledger | `hledger check` CLI, one process per input | stub: `HledgerOracle.parse_output` to write |

## Pipeline

```
inputs (corpora, generators)
   |                    \
   v                     v
oracle adapter        implementation (JSON-lines protocol)
   |                     |
   +--> normalizers <----+          (format plugin + consumer hooks)
              |
        compare by line and count   (ptadiff.compare)
              |
        category key per mismatch   (format plugin's key registry)
              |
     cluster  ->  minimize  ->  report (JSON + markdown)
```

* **Compare.** Two sides agree on an input when they report errors on the same
  lines, with the same number of errors on each line. Codes and messages are
  not compared. The *first* line they disagree on is the divergence that
  names the mismatch, because what follows it is usually cascade.
* **Category key.** A short `|`-separated string per mismatch. The base key
  is `coarse`: `side|who:kinds|line-kind`, where `side` is `impl-more`,
  `impl-fewer` or `eof`, `who:kinds` is the error kinds of the side that
  reports *more* on that line, and `line-kind` is `top`, `indented`, `blank`
  or `eof`. Formats add finer keys. Keys are registered by name, so a better
  key can be added without changing any stage.
* **Minimize.** Delta debugging over lines, then tokens, then characters. A
  step is kept only if the smaller input still mismatches *with the same key*,
  so the result stays an example of its own category and doesn't drift to
  whichever bug is easiest to hit.
* **Cluster.** Mismatches are grouped by key and listed largest first, each
  group with its size, sources, consumer labels and shortest example.
* **Report.** Deterministic JSON (`ptadiff-report/1`) and a markdown table,
  with no timestamps, so a nightly job can commit them and diff each night
  against the last.

## The implementation protocol

The implementation under test is a command that reads JSON lines on stdin, one
input per line, and writes one JSON line per input, in the same order:

```
in:  {"id": "3f2a9c0d1b7e", "text": "2024-01-01 open Assets:A\n"}
out: {"id": "3f2a9c0d1b7e", "errors": [{"line": 1, "code": "P0003", "msg": "..."}]}
```

`line` is 1-based, and 0 means a file-level error. `code` is the
implementation's own short code, used only to name categories. The command
must answer every input and exit 0. rustledger's
`cargo run -p rustledger-loader --example parse_error_lines -- --jsonl` is one
such command.

## beancount specifics

Oracle: `BeancountOracle(version="3.2.3")` checks the installed version and
calls `parse_string` and `lex_iter_string` as black boxes, in forked workers
(`ptadiff.pool.run_forked`). beancount's C parser segfaults on some inputs. A
worker that dies, raises or exceeds its timeout loses only that one input,
which is recorded as a crash and never judged.

Normalizers (all on by default; see `ptadiff/formats/beancount/__init__.py`):

| Name | Side | What |
|---|---|---|
| `strip-bom` | oracle input | beancount 3.2.3 rejects a byte-0 BOM, so the oracle reads the input without it |
| `eol-error-on-statement-line` | oracle | `syntax error, unexpected EOL` is reported one line late, so it is moved back to the statement's line |
| `drop-builder-errors` | oracle | option, account-name and cost-merge errors come from parser actions, not the grammar, so they are dropped |

An implementation's *deliberate* differences belong in a hooks module
(`--hooks`, see `ptadiff.pipeline.load_hooks`), or, as rustledger does, in
the consumer's own normalization before it calls `ptadiff.categorize`.

Keys:

* `shape` (default): `coarse` plus the token shape of the divergent line,
  taken from beancount's black-box `lex_iter_string` token names. That is the
  token just before the line's first invalid token (`^` at the start of the
  line) followed by `error`, or the line's first two tokens when it has no
  invalid token. Example: `impl-fewer|oracle:lex:token+syn:INDENT|indented|INDENT error`.
* `coarse`: the base key above.

Generators: `g1`, `g2`, `g3` and their `b` variants, which are biased toward
BOMs and carriage returns (see `generators.py`). Each is a pure function of
`(seed, n)` that returns `n` distinct inputs, sorted. `g3` draws windows from
the bundled `seeds/` corpus, a frozen copy of this repository's beancount
examples and fuzzing seeds. `tests/test_generators.py` pins a digest of each
generator's output, because consumers pin counts measured over generator
samples.

### License boundary

Nothing in this package is derived from beancount's grammar, lexer rules or
generated parser tables (beancount is GPL-2.0-only). The oracle only *calls*
beancount's public Python API. Token names come from what `lex_iter_string`
returns at run time.

## A parser-state key (planned)

The most precise way to name a syntax-error mismatch is by the reference
grammar's LR state when the error occurs. That needs parser tables, and only a
clean-room grammar's tables may be used here. Once the MIT grammar in this
repository has generated tables, the key plugs in like this:

```python
from ptadiff.formats import get_format

fmt = get_format("beancount")

def state_key(m):
    state = clean_room_parser.state_at_error(m.text, m.divergence.line)
    return fmt.coarse_key(m) + f"|state:{state}"

fmt.keys["state"] = state_key        # then: Differ(fmt, ..., key="state")
```

No other stage changes. Consumers that pin counts per key (rustledger's
parity manifest pins the key's name) re-pin once.

## The semantic differential

The parse differential compares syntax errors. The semantic differential
(`ptadiff.semantic`) compares what two implementations make of a
WELL-FORMED ledger after a full load: booking, interpolation, pads, balance
assertions, options and includes, plugins. Both sides describe each ledger
with a snapshot (`ptadiff-snapshot/1`: errors, booked entries, final
balances, effective options), specified in [SNAPSHOT.md](SNAPSHOT.md) with
its canonical form, comparison rules and verdicts.

It reuses every stage above. The implementation speaks the same JSON-lines
protocol in semantic mode (an input may span several files; the answer is
a snapshot). The oracle runs in the same forked, crash-isolated workers.
The minimizer is the same key-preserving one, shrinking each file by lines
and then whole words, and it keeps only candidates the oracle still reads as
well-formed. Clusters and reports are the same, with a deviation count added.
A format plugs in the same kinds of parts, in their own registries:

| Part | beancount |
|---|---|
| `semantic_oracle` | `loader.load_file` over the input written to a temporary directory (`semantic.py`) |
| `semantic_normalizers` | `error-at-directive`, `drop-errored-entries`, `placeholder-locations`, `load-errors-at-directive`, `errored-transaction-balances`, `tolerance-fallback`, `drop-zero-tolerances` (`semkey.py`) |
| `semantic_keys` | `sem` (default): `field\|path\|kind\|booking\|features`; `field`: `field\|path\|kind` |
| `semantic_generators` | `s1` lots and booking, `s2` pads, balances and tolerances, `s3` multi-file, `s4` built-in plugins, `smix` (`semgen.py`) |
| `oracle_unjudged` | a third-party plugin beancount cannot import where it runs |

An implementation's DELIBERATE differences go in its hooks module: a
representation difference as `normalize_impl_snapshot` /
`normalize_oracle_snapshot`, a difference in meaning as a
`ptadiff.semantic.Deviation` in `DEVIATIONS`, each pointing at where the
implementation documents it. A ledger a deviation explains is counted as
that deviation, not as a mismatch.

```sh
python -m ptadiff generate --semantic --format beancount --generator s1 --seed 1 --n 100 -o s1.jsonl
python -m ptadiff run --semantic --format beancount --impl "semantic_snapshot" \
    --gen s1:1:5000 --gen s3:1:5000 --input ledgers/ --hooks hooks.py \
    --minimize 10 --json report.json --markdown report.md --results results.jsonl
python -m ptadiff minimize --semantic --format beancount --impl "semantic_snapshot" \
    results.jsonl --line 3
```

rustledger's `cargo run -p rustledger-loader --example semantic_snapshot` is
such an implementation, and its `scripts/semantic_parity_hooks.py` such a
hooks module. The nightly `semantic-differential` workflow runs a large
sample against rustledger's main branch.

## Usage

```sh
pip install "./tooling/differential[beancount]"     # or add it to PYTHONPATH

# A generator sample, as protocol input lines:
python -m ptadiff generate --format beancount --generator g1 --seed 1 --n 1000 -o g1.jsonl

# Compare, categorize, minimize the 10 largest categories, report:
python -m ptadiff run --format beancount --impl "parse_error_lines --jsonl" \
    --input path/to/ledgers --input g1.jsonl --gen g2:1:1000 \
    --minimize 10 --json report.json --markdown report.md --results results.jsonl

# Minimize one input, keeping its category:
python -m ptadiff minimize --format beancount --impl "parse_error_lines --jsonl" case.beancount
```

As a library, see `ptadiff/__init__.py`. The usual entry points are
`Differ.evaluate` (verdicts and keys), `categorize` (a key from errors you
normalized yourself), `minimize`, `cluster` and `build_report` /
`render_markdown`.

## Tests

```sh
cd tooling/differential
python -m pytest -q tests
```

The beancount tests skip when beancount is not importable. CI sets
`PTADIFF_REQUIRE_BEANCOUNT=1`, which turns those skips into failures, so the
tests can't pass by skipping everywhere.
