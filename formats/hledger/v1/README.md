# hledger Format v1 Specification

This directory contains the complete specification for hledger journal format version 1.

## Overview

hledger v1 format is the current stable format used by hledger. It is largely compatible with Ledger while adding stricter parsing and additional features.

## Specification Structure

```
v1/
├── README.md           # This overview
├── spec/               # Detailed specifications
│   ├── syntax.md       # Grammar and syntax
│   ├── lexical.md      # Tokens and whitespace
│   ├── amounts.md      # Amount format
│   ├── posting.md      # Posting structure
│   ├── costs.md        # Cost handling
│   ├── tags.md         # Tag syntax
│   ├── metadata.md     # Metadata attachment
│   ├── includes.md     # File inclusion
│   ├── directives/     # Directive specifications
│   │   ├── account.md
│   │   ├── commodity.md
│   │   ├── include.md
│   │   └── ...
│   └── advanced/       # Advanced features
│       ├── assertions.md
│       ├── auto-postings.md
│       └── forecasting.md
├── tree-sitter/        # Grammar definitions
│   └── grammar.js
└── schema/             # JSON schemas
    └── ast.json
```

## Quick Reference

### Transaction Syntax

```hledger
DATE [STATUS] [CODE] DESCRIPTION
    ACCOUNT    AMOUNT [@ PRICE]
    ACCOUNT    [AMOUNT]
```

### Example

```hledger
2024-01-15 * (123) Whole Foods
    ; :groceries:
    expenses:food:groceries    $75.50
    assets:bank:checking
```

## Key Features

### Dates

Three separator styles supported:
- `2024-01-15` (preferred)
- `2024/01/15`
- `2024.01.15`

### Status Markers

| Marker | Meaning |
|--------|---------|
| (none) | Unmarked |
| `!` | Pending |
| `*` | Cleared |

### Account Types

```hledger
account assets:bank
    ; type: Asset

account liabilities:credit
    ; type: Liability
```

### Amount Format

```hledger
$1,000.00           ; Symbol prefix
1.000,00 EUR        ; Symbol suffix
10 AAPL @ $150      ; With price
10 AAPL {$150}      ; With cost
```

## Differences from Ledger

| Feature | hledger | Ledger |
|---------|---------|--------|
| Date format | Stricter | More flexible |
| Account types | Explicit | Inferred |
| Error messages | Detailed | Terse |
| Default mode | Strict | Permissive |

## Compatibility

### hledger Versions

This specification covers:
- hledger 1.32.x (reference)
- hledger 1.x series (compatible)

### Other Tools

- **Ledger**: High compatibility
- **Beancount**: Requires conversion

## Validation

### Syntax Check

```bash
hledger -f journal.hledger check
```

### Balance Check

```bash
hledger -f journal.hledger bal
```

## See Also

- [hledger Manual](https://hledger.org/hledger.html)
- [Syntax Specification](spec/syntax.md)
- [Ledger Differences](../../ledger/)
