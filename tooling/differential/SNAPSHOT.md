# `ptadiff-snapshot/1`: what a ledger means after a full load

The semantic differential (`ptadiff.semantic`) compares two implementations
of a plain-text-accounting format on whole ledgers: not where they report
syntax errors (that is the parse differential), but what each makes of a
ledger once it is loaded the whole way: includes and options, plugins,
booking, interpolation, pads, balance checks. Both sides describe a ledger
with a **snapshot**, one JSON object in the schema below. The machine-readable
form is [`ptadiff/schemas/snapshot-1.schema.json`](ptadiff/schemas/snapshot-1.schema.json).

The schema is format-generic. It names accounting concepts (entries,
postings, lots, inventories, tolerances), not one format's syntax, so a
ledger or hledger oracle can produce it too. A format plugin supplies the
oracle that produces the reference snapshot and the normalizers for its
known representation differences.

## Transport

Over the JSON-lines protocol (`ptadiff.protocol`), semantic mode. One input
per line, the main file in `text` and any other file in `files`, by path
relative to the main file's directory:

```json
{"id": "3f2a9c0d1b7e", "text": "include \"a.beancount\"\n...", "main": "main.beancount",
 "files": {"a.beancount": "2024-01-01 open Assets:A\n"}}
```

One answer per input, in order: the snapshot, or why there is none.

```json
{"id": "3f2a9c0d1b7e", "snapshot": {"errors": [], "entries": [], "balances": {}, "options": {}}}
{"id": "3f2a9c0d1b7e", "crash": "panicked: ..."}
```

An implementation lays the files out in a fresh directory and loads the
main one from there, as its users load a ledger. Every path in the snapshot
is relative to that directory (`main.beancount`, `sub/a.beancount`). A
location that is not in the input (a plugin's placeholder, `<auto_accounts>`)
is written as the implementation names it; ptadiff places it nowhere (see
Normalization).

## The snapshot

```json
{
  "errors":   [Error, ...],
  "entries":  [Entry, ...],
  "balances": {"<account>": [Position, ...], ...},
  "options":  {...}
}
```

Each side writes what it computes, in its own order and with its own
number formatting: ptadiff canonicalizes both (below).

### `errors`

Every error the implementation's check command counts as an error
(warnings and advisories left out), after the whole load:

| Field | Type | Meaning |
|---|---|---|
| `file` | string | the file, relative; `""` or a `<placeholder>` when it has none |
| `line` | integer | 1-based; 0 when it has none |
| `code` | string | the implementation's own code or error type; names categories, never compared |
| `msg` | string | the message; never compared |

### `entries`

Every entry of the loaded ledger: as booked, plugin-rewritten, with the
entries the load generates (pad transactions, plugin-made opens, prices,
closes...) included. Every entry has:

| Field | Type | Meaning |
|---|---|---|
| `type` | string | `open`, `close`, `commodity`, `pad`, `balance`, `transaction`, `price`, `note`, `event`, `query`, `document`, `custom` |
| `date` | string | ISO 8601 |
| `file`, `line` | string, integer | where it was written; a generated entry carries its source's location, or a placeholder |

and, by type:

| Type | Fields |
|---|---|
| `open` | `account`, `currencies` (set), `booking` (the method written, or null) |
| `close` | `account` |
| `commodity` | `currency` |
| `pad` | `account`, `source_account` |
| `balance` | `account`, `amount` (Amount), `tolerance` (number or null: written only) |
| `transaction` | `flag`, `payee`, `narration`, `tags` (set), `links` (set), `postings` (list), `tolerances` (optional) |
| `price` | `currency`, `amount` (Amount) |
| `note` | `account`, `comment` |
| `event` | `event`, `description` |
| `query` | `name`, `query` |
| `document` | `account`, `filename` (relative) |
| `custom` | `custom` (its type), `values` (how many) |

A **posting**, in the order the transaction holds them:

| Field | Type | Meaning |
|---|---|---|
| `account` | string | |
| `units` | Amount or null | after interpolation: an elided amount is filled in |
| `cost` | Cost, CostSpec or null | the lot, resolved as the inventory holds it |
| `price` | Amount or null | per unit (an `@@` total is divided by the units) |
| `flag` | string or null | |

`tolerances` is a transaction's inferred tolerance per currency: what the
balance check allows for each currency the transaction names, as the
implementation infers it (from the amounts as written, before
interpolation). An implementation that does not expose it leaves the key
out, and it is then not compared.

An **Amount** is `{"number": N, "currency": C}`; either may be null on an
entry the implementation refused to book. A **Cost** is
`{"number": N, "currency": C, "date": D, "label": L}`: the per-unit cost,
its currency, the lot date (the transaction date when none was written) and
the label. A **CostSpec** is a cost booking left unresolved, on a refused
entry only: `{"spec": true, "number_per", "number_total", "currency",
"date", "label", "merge"}`. A number `N` is a decimal string (or a JSON
number).

### `balances`

Every account's final inventory, after every entry: the positions it holds,
each `{"units": Amount, "cost": Cost or null}`, lots at cost kept apart.
An entry the implementation refused (booking failed) contributes nothing.

### `options`

The options in effect, where the implementation has them:

| Key | Type | Meaning |
|---|---|---|
| `operating_currency` | set of strings | |
| `booking_method` | string | the ledger-wide default |
| `inferred_tolerance_default` | `{currency: number}` | `*` is the fallback |
| `tolerance_multiplier` | number | |
| `infer_tolerance_from_cost` | boolean | |
| `display_precision` | `{currency: {"common": int, "max": int}}` | the fractional digits the implementation would display a currency with, under the most-common and the maximum policies |

An option a side does not report is not compared.

## Canonical form

`ptadiff.snapshot.canonicalize`, applied to both sides, before and after
their normalizers:

* **Numbers** are compared by value. Each is parsed as a decimal; one with
  more than 20 significant digits (`SIGNIFICANT_DIGITS`) is rounded to 20
  (half-even); it is written without exponent or trailing zeros, `-0` as
  `0`. So `10.00` equals `10`, and two engines that disagree in the 27th
  digit of a quotient (a per-unit price from an `@@` total, say) agree.
  The scale a ledger writes is compared, where it is observable, through
  `options.display_precision`.
* **Order**: errors, entries (by date, type, file, line, then content),
  tags, links, an open's currencies, `operating_currency`, an account's
  positions and every per-currency map are sorted: their order carries no
  meaning. Postings keep theirs.
* **Zero positions** are dropped, and so is an account left with none.

## Comparison

Two canonical snapshots are compared field by field, in this order, and the
FIRST difference names the mismatch (`ptadiff.snapshot.first_diff`): an
error difference usually explains the entries after it, an entry difference
the balances.

1. `errors`: by the set of locations with an error (`error_mode="lines"`,
   the default): a location flagged on one side only is a difference; how
   many errors each side reports there is not (beancount reports an unknown
   account in a `balance` three times, an implementation may report it
   once). `error_mode="counts"` compares the count per location.
2. `entries`: each entry is paired with its counterpart by type, date, file
   and line (the n-th of several with one identity with the n-th); one
   without a counterpart is `missing-in-impl` or `extra-in-impl`; a pair
   that differs names the first differing field (`postings.cost.number`,
   `tolerances.USD`), `postings.count` when the counts differ, and
   `postings.order` when only the order does.
3. `balances`: per account: `units` when the totals per currency differ,
   `lots` when only the lots do.
4. `options`: per option.

The `FieldDiff` of the first difference records the field, the path, the
directive kind, the location and both values.

## Normalization

A normalizer is a named rewrite of one side's canonical snapshot (`oracle`,
`impl`, `both`), or of both at once (`pair`), declared by the format plugin
(`FormatPlugin.semantic_normalizers`) or by a consumer's hooks module
(`normalize_oracle_snapshot`, `normalize_impl_snapshot`). Each removes a
KNOWN difference of representation, where both sides mean the same; each
can be turned off by name (`--no-normalize`). The beancount format's are
listed in `ptadiff/formats/beancount/semkey.py`.

A difference an implementation makes ON PURPOSE (a deviation in meaning,
documented by the implementation) is not normalized away: it is declared as
a `ptadiff.semantic.Deviation` in the consumer's hooks (`DEVIATIONS`), with
a predicate over the mismatch and a reference to its documentation. A ledger
whose first difference a deviation explains is counted as that deviation,
apart from the mismatches, so the match rate measures only what is not
decided.

## Verdicts

| Status | Meaning |
|---|---|
| `match` | no difference |
| `mismatch` | a difference, named by the format's semantic key; also an implementation crash (`impl-crash\|...`) |
| `deviation` | a declared deviation explains the first difference |
| `crash` | the oracle crashed, or cannot judge the ledger where it runs (`FormatPlugin.oracle_unjudged`): not judged |
