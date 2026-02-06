# Beancount v3 Specification - Introduction

## Overview

Beancount is a double-entry bookkeeping language for plain text accounting. It provides a simple, human-readable format for recording financial transactions and a set of tools for processing, validating, and querying the data.

## Purpose

This specification defines:

1. **Syntax** - The grammar of Beancount files
2. **Semantics** - The meaning of directives and their behavior
3. **Validation** - Rules for detecting errors
4. **Processing** - How files are loaded and transformed

## Design Principles

### Plain Text

All data is stored in human-readable text files:
- Version controllable (git, mercurial)
- Grep-able and scriptable
- No proprietary formats
- Long-term archival friendly

### Double-Entry Accounting

Every transaction must balance:
- Sum of debits equals sum of credits
- Enforced by the parser/validator
- Prevents common bookkeeping errors

### Declarative

Files declare facts, not procedures:
- No imperative control flow
- Order within files doesn't matter (directives are sorted by date)
- Idempotent processing

### Extensible

Support for custom data and transformations:
- Metadata on any directive
- Custom directives for arbitrary data
- Plugin system for transformations

## Document Structure

### Core Specification

| Document | Description |
|----------|-------------|
| [lexical.md](lexical.md) | Tokens, whitespace, comments, encoding |
| [syntax.md](syntax.md) | Grammar overview, file structure |
| [posting.md](posting.md) | Posting structure within transactions |
| [amounts.md](amounts.md) | Number and amount formats |
| [costs.md](costs.md) | Cost basis specification |
| [prices.md](prices.md) | Price annotations |
| [metadata.md](metadata.md) | Key-value metadata |
| [tags-links.md](tags-links.md) | Tags and links |

### Directives

| Directive | Description |
|-----------|-------------|
| [transaction.md](directives/transaction.md) | Financial exchanges |
| [open.md](directives/open.md) | Account declarations |
| [close.md](directives/close.md) | Account closures |
| [balance.md](directives/balance.md) | Balance assertions |
| [pad.md](directives/pad.md) | Automatic balancing |
| [commodity.md](directives/commodity.md) | Currency declarations |
| [price.md](directives/price.md) | Market prices |
| [event.md](directives/event.md) | Variable tracking |
| [note.md](directives/note.md) | Account notes |
| [document.md](directives/document.md) | File attachments |
| [query.md](directives/query.md) | Embedded queries |
| [custom.md](directives/custom.md) | User-defined directives |
| [option.md](directives/option.md) | Configuration |
| [plugin.md](directives/plugin.md) | Transformations |
| [include.md](directives/include.md) | File inclusion |

### Validation

| Document | Description |
|----------|-------------|
| [validation/accounts.md](validation/accounts.md) | Account lifecycle |
| [validation/balance.md](validation/balance.md) | Balance checking |
| [validation/commodities.md](validation/commodities.md) | Currency rules |
| [validation/duplicates.md](validation/duplicates.md) | Duplicate detection |
| [errors.md](errors.md) | Error codes catalog |

### Semantics

| Document | Description |
|----------|-------------|
| [booking.md](booking.md) | Lot matching methods |
| [tolerances.md](tolerances.md) | Balance tolerances |
| [includes.md](includes.md) | Include semantics |

## Terminology

### RFC 2119 Keywords

This specification uses RFC 2119 keywords:

| Keyword | Meaning |
|---------|---------|
| **MUST** | Absolute requirement |
| **MUST NOT** | Absolute prohibition |
| **SHOULD** | Recommended but not required |
| **SHOULD NOT** | Not recommended but not prohibited |
| **MAY** | Optional |

### Definitions

| Term | Definition |
|------|------------|
| **Directive** | A dated entry in the ledger |
| **Transaction** | A directive recording a financial exchange |
| **Posting** | A single line within a transaction |
| **Account** | A named container for tracking value |
| **Commodity** | A unit of measurement (currency, stock, etc.) |
| **Amount** | A number paired with a commodity |
| **Cost** | The acquisition price of a commodity |
| **Price** | The market exchange rate |
| **Lot** | A specific acquisition of a commodity |
| **Inventory** | The collection of lots in an account |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v3.0 | 2024 | Current specification |
| v2.0 | 2016 | Python 3, Unicode support |
| v1.0 | 2012 | Initial release |

## Conformance

Implementations claiming Beancount compatibility MUST:

1. Parse all valid Beancount syntax
2. Reject all invalid syntax with appropriate errors
3. Implement all required validation rules
4. Support the standard booking methods

See [conformance/](../../../../conformance/) for the conformance testing program.

## Example

A minimal Beancount file:

```beancount
; Personal Finance Ledger
option "title" "My Finances"
option "operating_currency" "USD"

; Account definitions
2024-01-01 open Assets:Checking USD
2024-01-01 open Expenses:Food
2024-01-01 open Income:Salary

; Transactions
2024-01-15 * "Employer" "Monthly salary"
  Assets:Checking    3000.00 USD
  Income:Salary

2024-01-16 * "Grocery Store" "Weekly groceries"
  Expenses:Food       85.50 USD
  Assets:Checking

; Balance assertion
2024-01-17 balance Assets:Checking  2914.50 USD
```

## References

- [Beancount Documentation](https://beancount.github.io/docs/)
- [Plain Text Accounting](https://plaintextaccounting.org/)
- [Double-Entry Bookkeeping](https://en.wikipedia.org/wiki/Double-entry_bookkeeping)
