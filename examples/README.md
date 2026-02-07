# Example Ledgers

This directory contains example ledger files demonstrating each PTA format.

## Formats

| Directory | Format | Description |
|-----------|--------|-------------|
| [beancount/](beancount/) | Beancount v3 | Python-based double-entry accounting |
| [hledger/](hledger/) | hledger | Haskell plain text accounting |
| [ledger/](ledger/) | Ledger | The original plain text accounting |

## Examples Overview

Each format directory contains:

| File | Description |
|------|-------------|
| `personal.{bean,journal,ledger}` | Personal finance example |
| `business.{bean,journal,ledger}` | Small business example |
| `investments.{bean,journal,ledger}` | Investment tracking example |

## Running Examples

### Beancount

```bash
bean-check examples/beancount/personal.beancount
bean-report examples/beancount/personal.beancount balances
bean-query examples/beancount/personal.beancount "SELECT account, sum(position)"
```

### hledger

```bash
hledger -f examples/hledger/personal.journal check
hledger -f examples/hledger/personal.journal balance
hledger -f examples/hledger/personal.journal register
```

### Ledger

```bash
ledger -f examples/ledger/personal.ledger balance
ledger -f examples/ledger/personal.ledger register
ledger -f examples/ledger/personal.ledger stats
```

## Cross-Format Comparison

These examples demonstrate equivalent functionality across formats:

| Feature | Beancount | hledger | Ledger |
|---------|-----------|---------|--------|
| Account declaration | `open` directive | Optional | Optional |
| Balance assertion | `balance` directive | `= AMOUNT` | `= AMOUNT` |
| Transaction flag | `*` or `!` | `*` or `!` | `*` or `!` |
| Metadata | `key: "value"` | `; key: value` | `; :tag:` |
| Comments | `; comment` | `; comment` | `; comment` |

## Validation

Run validation across all examples:

```bash
# Beancount
for f in examples/beancount/*.beancount; do bean-check "$f"; done

# hledger
for f in examples/hledger/*.journal; do hledger -f "$f" check; done

# Ledger
for f in examples/ledger/*.ledger; do ledger -f "$f" balance > /dev/null; done
```
