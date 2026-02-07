# Beancount Format Specification

This directory contains the formal specification for the Beancount journal format.

## Overview

Beancount is a double-entry bookkeeping language created by Martin Blais. It emphasizes correctness, strict validation, and reproducibility.

## Design Principles

- **Correctness first**: Strict validation catches errors early
- **Explicit is better**: No implicit behavior or defaults
- **Reproducibility**: Same input always produces same output
- **Minimal syntax**: Simple, consistent grammar

## Key Features

- Strict account opening/closing
- Booking methods for inventory
- Plugin system for custom validation
- Query language (BQL)
- Web interface (Fava)

## Versions

| Version | Status | Description |
|---------|--------|-------------|
| v2 | Legacy | Beancount 2.x format |
| v3 | Current | Beancount 3.x format |

## Directory Structure

```
beancount/
├── README.md           # This file
├── compliance.md       # Compliance testing
├── CHANGELOG.md        # Version history
├── plugins/            # Plugin specifications
│   ├── spec.md
│   ├── hooks.md
│   └── sandboxing.md
├── v2/                 # Version 2 spec
└── v3/                 # Version 3 spec (current)
    ├── README.md
    ├── spec/
    └── tree-sitter/
```

## Quick Start

### Basic Transaction

```beancount
2024-01-15 * "Grocery Store" "Weekly shopping"
  Expenses:Food:Groceries    50.00 USD
  Assets:Bank:Checking      -50.00 USD
```

### Account Opening

```beancount
2024-01-01 open Assets:Bank:Checking USD
2024-01-01 open Expenses:Food:Groceries
```

### Price Declaration

```beancount
2024-01-15 price AAPL 150.00 USD
```

## Differences from Ledger/hledger

| Feature | Beancount | Ledger/hledger |
|---------|-----------|----------------|
| Account opening | Required | Optional |
| Date format | YYYY-MM-DD only | Multiple formats |
| Amount elision | No | Yes |
| Booking | Explicit methods | Implicit |
| Plugins | Yes | No |

## Related Tools

- [Fava](https://github.com/beancount/fava) - Web interface
- [beancount-import](https://github.com/jbms/beancount-import) - Import automation
- [bean-check](https://beancount.github.io/docs/running_beancount_and_generating_reports.html) - Validation

## Resources

- [Beancount Documentation](https://beancount.github.io/docs/)
- [Beancount Mailing List](https://groups.google.com/g/beancount)
- [Fava Demo](https://fava.pythonanywhere.com/)

## See Also

- [Ledger Format](../ledger/)
- [hledger Format](../hledger/)
- [Format Comparison](../README.md)
