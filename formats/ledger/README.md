# Ledger Format Specification

This directory contains the formal specification for the Ledger plain text accounting format.

## Overview

Ledger is the original plain text accounting tool, created by John Wiegley. It pioneered the concept of double-entry bookkeeping in plain text files.

## Versions

| Version | Status | Description |
|---------|--------|-------------|
| [v1](v1/) | Current | Based on Ledger 3.x behavior |

## Key Features

- **Double-entry accounting** - Every transaction balances
- **Multiple commodities** - Track any currency or asset
- **Virtual postings** - Non-balancing entries for budgets
- **Value expressions** - Arithmetic and functions in amounts
- **Automated transactions** - Rule-based posting generation
- **Periodic transactions** - Recurring transaction templates
- **Rich queries** - Flexible reporting and filtering

## Quick Start

A simple Ledger file:

```ledger
; My first ledger
2024/01/15 * Grocery Store
    Expenses:Food:Groceries    $50.00
    Assets:Checking

2024/01/16 * Paycheck
    Assets:Checking           $2000.00
    Income:Salary
```

## Directory Structure

```
ledger/
├── README.md           # This file
├── compliance.md       # Compliance requirements
└── v1/
    ├── README.md       # Version overview
    ├── spec/           # Format specification
    │   ├── syntax.md   # Syntax rules
    │   ├── amounts.md  # Amount formatting
    │   ├── posting.md  # Posting rules
    │   └── directives/ # Directive specifications
    ├── expressions/    # Value expression language
    ├── schema/         # JSON schemas
    └── tree-sitter/    # Tree-sitter grammar
```

## Compared to Other Formats

| Feature | Ledger | hledger | Beancount |
|---------|--------|---------|-----------|
| Virtual postings | Yes | Yes | No |
| Value expressions | Yes | No | No |
| Automated transactions | Yes | Yes | No |
| Lot tracking | Basic | Basic | Advanced |
| Required account declaration | No | No | Yes |
| Date format | `YYYY/MM/DD` | Both | `YYYY-MM-DD` |

## Resources

- [Official Ledger Documentation](https://ledger-cli.org/doc/ledger3.html)
- [Ledger GitHub Repository](https://github.com/ledger/ledger)
- [Plain Text Accounting](https://plaintextaccounting.org/)

## Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for how to contribute to this specification.
