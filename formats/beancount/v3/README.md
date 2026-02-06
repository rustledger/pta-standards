# Beancount v3 Format Specification

## Overview

Beancount is a double-entry bookkeeping language designed for plain text accounting. This specification defines version 3 of the Beancount format.

## Key Features

- **Plain text** - Human-readable, version-controllable files
- **Double-entry** - Enforced balance in every transaction
- **Multi-currency** - Native support for multiple currencies and commodities
- **Cost tracking** - Lot-based inventory with multiple booking methods
- **Extensible** - Metadata, plugins, and custom directives

## Quick Example

```beancount
; Options
option "title" "Personal Finances"
option "operating_currency" "USD"

; Account structure
2024-01-01 open Assets:Checking USD
2024-01-01 open Assets:Savings USD
2024-01-01 open Expenses:Food
2024-01-01 open Income:Salary

; Transactions
2024-01-15 * "Employer" "Monthly salary"
  Assets:Checking    5000.00 USD
  Income:Salary

2024-01-16 * "Grocery Store" "Weekly groceries"
  Expenses:Food       125.50 USD
  Assets:Checking

; Balance assertion
2024-01-17 balance Assets:Checking  4874.50 USD
```

## Specification Structure

### Core Specification

| Document | Description |
|----------|-------------|
| [spec/introduction.md](spec/introduction.md) | Overview and terminology |
| [spec/lexical.md](spec/lexical.md) | Tokens, encoding, whitespace |
| [spec/syntax.md](spec/syntax.md) | Grammar and file structure |

### Directives

| Directive | Document |
|-----------|----------|
| Transaction | [spec/directives/transaction.md](spec/directives/transaction.md) |
| Open | [spec/directives/open.md](spec/directives/open.md) |
| Close | [spec/directives/close.md](spec/directives/close.md) |
| Balance | [spec/directives/balance.md](spec/directives/balance.md) |
| Pad | [spec/directives/pad.md](spec/directives/pad.md) |
| Commodity | [spec/directives/commodity.md](spec/directives/commodity.md) |
| Price | [spec/directives/price.md](spec/directives/price.md) |
| Event | [spec/directives/event.md](spec/directives/event.md) |
| Note | [spec/directives/note.md](spec/directives/note.md) |
| Document | [spec/directives/document.md](spec/directives/document.md) |
| Query | [spec/directives/query.md](spec/directives/query.md) |
| Custom | [spec/directives/custom.md](spec/directives/custom.md) |
| Option | [spec/directives/option.md](spec/directives/option.md) |
| Plugin | [spec/directives/plugin.md](spec/directives/plugin.md) |
| Include | [spec/directives/include.md](spec/directives/include.md) |

### Data Elements

| Element | Document |
|---------|----------|
| Postings | [spec/posting.md](spec/posting.md) |
| Amounts | [spec/amounts.md](spec/amounts.md) |
| Costs | [spec/costs.md](spec/costs.md) |
| Prices | [spec/prices.md](spec/prices.md) |
| Metadata | [spec/metadata.md](spec/metadata.md) |
| Tags & Links | [spec/tags-links.md](spec/tags-links.md) |

### Semantics

| Topic | Document |
|-------|----------|
| Booking Methods | [spec/booking.md](spec/booking.md) |
| Tolerances | [spec/tolerances.md](spec/tolerances.md) |
| Include Processing | [spec/includes.md](spec/includes.md) |
| Error Codes | [spec/errors.md](spec/errors.md) |

### Validation

| Topic | Document |
|-------|----------|
| Account Lifecycle | [spec/validation/accounts.md](spec/validation/accounts.md) |
| Balance Checking | [spec/validation/balance.md](spec/validation/balance.md) |
| Currency Rules | [spec/validation/commodities.md](spec/validation/commodities.md) |
| Duplicate Detection | [spec/validation/duplicates.md](spec/validation/duplicates.md) |

## Grammar

| Format | File | Description |
|--------|------|-------------|
| PEG | [grammar/beancount.peg](grammar/beancount.peg) | Parsing Expression Grammar |
| EBNF | [grammar/beancount.ebnf](grammar/beancount.ebnf) | ISO 14977 EBNF |
| ABNF | [grammar/beancount.abnf](grammar/beancount.abnf) | RFC 5234 ABNF |

## Schema

| Format | File | Description |
|--------|------|-------------|
| JSON Schema | [schema/ast.schema.json](schema/ast.schema.json) | AST validation |
| Protocol Buffers | [schema/ast.proto](schema/ast.proto) | Binary serialization |

## Editor Support

### Tree-sitter

Complete tree-sitter grammar for syntax highlighting and editor integration:

- [tree-sitter/grammar.js](tree-sitter/grammar.js) - Parser grammar
- [tree-sitter/queries/highlights.scm](tree-sitter/queries/highlights.scm) - Syntax highlighting
- [tree-sitter/queries/folds.scm](tree-sitter/queries/folds.scm) - Code folding
- [tree-sitter/queries/indents.scm](tree-sitter/queries/indents.scm) - Auto-indentation

## Query Language

Beancount includes BQL (Beancount Query Language) for querying ledger data:

- [bql/spec.md](bql/spec.md) - BQL specification
- [bql/functions.md](bql/functions.md) - Built-in functions

## Migration

- [migration/guide.md](migration/guide.md) - Migrating from v2 to v3
- [migration/breaking-changes.md](migration/breaking-changes.md) - Breaking changes list

## File Extension

Beancount files use the `.beancount` extension:

```
ledger.beancount
accounts.beancount
2024/january.beancount
```

Some tools also recognize `.bean` as an alternative.

## Implementations

| Implementation | Language | Status |
|----------------|----------|--------|
| [beancount](https://github.com/beancount/beancount) | Python | Reference |
| [rustledger](https://github.com/rustledger/rustledger) | Rust | Compatible |
| [beancount-parser](https://github.com/beancount/beancount-parser) | Rust | Parser only |

## Resources

- [Beancount Documentation](https://beancount.github.io/docs/)
- [Plain Text Accounting](https://plaintextaccounting.org/)
- [Beancount Mailing List](https://groups.google.com/g/beancount)

## License

This specification is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
