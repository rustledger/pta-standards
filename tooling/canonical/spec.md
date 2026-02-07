# Canonical Output Specification

This document specifies canonical output formats for PTA tools.

## Overview

Canonical output provides:
- Consistent formatting across tools
- Reproducible output
- Diff-friendly representation
- Standard interchange format

## Design Goals

1. **Deterministic**: Same input → same output
2. **Readable**: Human-friendly formatting
3. **Parseable**: Machine-parseable
4. **Lossless**: Preserve all information

## Transaction Format

### Structure

```
DATE [STATUS] [CODE] DESCRIPTION
    ACCOUNT    AMOUNT [PRICE] [ASSERTION]
    ACCOUNT    [AMOUNT]
```

### Example

```
2024-01-15 * "Grocery Store"
    Expenses:Food:Groceries    50.00 USD
    Assets:Bank:Checking      -50.00 USD
```

## Formatting Rules

### Dates

Always use ISO 8601:

```
2024-01-15    ; Not 2024/01/15 or 01/15/2024
```

### Amounts

```
123.45 USD        ; Number space commodity
-123.45 USD       ; Negative sign on number
1,234.56 USD      ; Grouping optional but consistent
```

### Accounts

```
Assets:Bank:Checking    ; Colon separator
Expenses:Food           ; Title case segments
```

### Alignment

```
    Account:Short         10.00 USD
    Account:Very:Long   -100.00 USD
                        ─────────────
```

Right-align amounts at consistent column.

### Indentation

- 4 spaces for postings
- 2 additional spaces for metadata
- No tabs

## Directive Ordering

1. Options/settings
2. Account declarations
3. Commodity declarations
4. Price directives
5. Transactions (chronological)

## Metadata Format

```
    Account    100.00 USD
      ; key: value
      ; tag:
```

## Comments

```
; Line comment
    Account    100.00 USD  ; Inline comment
```

## JSON Canonical Format

```json
{
  "version": "1.0",
  "entries": [
    {
      "type": "transaction",
      "date": "2024-01-15",
      "status": "cleared",
      "payee": "Grocery Store",
      "postings": [
        {
          "account": "Expenses:Food",
          "amount": {
            "number": "50.00",
            "commodity": "USD"
          }
        }
      ]
    }
  ]
}
```

## Normalization Rules

### Amount Normalization

1. Remove trailing zeros (optional)
2. Consistent decimal places per commodity
3. Standard grouping per locale

### Account Normalization

1. Trim whitespace
2. Consistent casing
3. Standard separator (`:`)

### Date Normalization

1. ISO 8601 format
2. Full year (YYYY)
3. Zero-padded month/day

## Validation

Canonical output MUST:

1. Parse without errors
2. Balance correctly
3. Preserve all data
4. Match source semantics

## Tools

### Canonicalize Command

```bash
pta canonicalize input.journal > output.journal
```

### Verify Canonical

```bash
pta verify-canonical file.journal
```

## See Also

- [Ledger Canonical](ledger.md)
- [hledger Canonical](hledger.md)
- [Beancount Canonical](beancount.md)
