# Consistency Linting Rules

This document defines consistency-related linting rules.

## CONSIST-001: Date Format Consistency

### Description
All dates should use the same format throughout the journal.

### Severity
warning

### Examples

```beancount
; Warning: inconsistent date formats
2024-01-15 * "One"
2024/01/16 * "Two"
2024.01.17 * "Three"

; OK: consistent format
2024-01-15 * "One"
2024-01-16 * "Two"
2024-01-17 * "Three"
```

## CONSIST-002: Account Naming Convention

### Description
Account segments should follow consistent naming pattern.

### Configuration
```yaml
CONSIST-002:
  pattern: "TitleCase"  # or "lowercase", "UPPERCASE"
```

### Examples

```beancount
; Warning: inconsistent naming
Assets:Bank:checking
Expenses:food

; OK: consistent naming
Assets:Bank:Checking
Expenses:Food
```

## CONSIST-003: Commodity Format

### Description
Same commodity should be formatted consistently.

### Examples

```beancount
; Warning: inconsistent
    Account  $50.00
    Account  50.00 USD
    Account  USD 50

; OK: consistent
    Account  50.00 USD
    Account  100.00 USD
```

## CONSIST-004: Decimal Places

### Description
Same commodity should use consistent decimal places.

### Examples

```beancount
; Warning: inconsistent
    Account  50 USD
    Account  50.00 USD
    Account  50.000 USD

; OK: consistent
    Account  50.00 USD
    Account  100.00 USD
```

## CONSIST-005: Payee Spelling

### Description
Same payee should be spelled consistently.

### Examples

```beancount
; Warning: inconsistent
2024-01-15 * "Whole Foods"
2024-01-16 * "WholeFoods"
2024-01-17 * "Whole foods"

; OK: consistent
2024-01-15 * "Whole Foods"
2024-01-16 * "Whole Foods"
```

## CONSIST-006: Tag Naming

### Description
Tags should follow consistent naming pattern.

### Configuration
```yaml
CONSIST-006:
  pattern: "lowercase-dashes"  # or "camelCase"
```

### Examples

```beancount
; Warning: inconsistent
    ; personal:
    ; Business:
    ; URGENT:

; OK: consistent
    ; personal:
    ; business:
    ; urgent:
```

## CONSIST-007: Metadata Keys

### Description
Metadata keys should follow consistent naming.

### Examples

```beancount
; Warning: inconsistent
    ; Receipt: file.pdf
    ; receipt: other.pdf
    ; RECEIPT: another.pdf

; OK: consistent
    ; receipt: file.pdf
    ; receipt: other.pdf
```

## CONSIST-008: Transaction Ordering

### Description
Transactions should be in chronological order.

### Severity
info

### Examples

```beancount
; Warning: out of order
2024-01-20 * "Later"
2024-01-15 * "Earlier"

; OK: chronological
2024-01-15 * "Earlier"
2024-01-20 * "Later"
```

## CONSIST-009: Posting Order

### Description
Postings should follow consistent ordering pattern.

### Configuration
```yaml
CONSIST-009:
  order: "debits-first"  # or "credits-first", "alphabetical"
```

### Examples

```beancount
; Mixed ordering
2024-01-15 * "Test"
    Assets:Cash      -50.00 USD
    Expenses:Food     50.00 USD

2024-01-16 * "Test"
    Expenses:Food     50.00 USD
    Assets:Cash      -50.00 USD

; Consistent (debits first)
2024-01-15 * "Test"
    Expenses:Food     50.00 USD
    Assets:Cash      -50.00 USD

2024-01-16 * "Test"
    Expenses:Food     50.00 USD
    Assets:Cash      -50.00 USD
```

## CONSIST-010: Comment Marker

### Description
Use same comment marker throughout.

### Examples

```beancount
; Warning: inconsistent
; Semicolon comment
# Hash comment

; OK: consistent
; All semicolon comments
; Another comment
```

## CONSIST-011: Status Usage

### Description
Transaction status markers should be used consistently.

### Examples

```beancount
; Warning: some cleared, some not
2024-01-15 * "Cleared"
2024-01-16 "Not marked"

; OK: consistent usage
2024-01-15 * "Cleared"
2024-01-16 * "Also cleared"
```

## CONSIST-012: File Organization

### Description
Similar transactions should be grouped consistently.

### Configuration
```yaml
CONSIST-012:
  grouping: "by-month"  # or "by-account", "by-payee"
```

## Severity Summary

| Rule | Default Severity |
|------|------------------|
| CONSIST-001 | warning |
| CONSIST-002 | warning |
| CONSIST-003 | info |
| CONSIST-004 | info |
| CONSIST-005 | info |
| CONSIST-006 | info |
| CONSIST-007 | info |
| CONSIST-008 | info |
| CONSIST-009 | hint |
| CONSIST-010 | hint |
| CONSIST-011 | hint |
| CONSIST-012 | hint |

## See Also

- [Linting Specification](../spec.md)
- [Style Rules](style.md)
- [Correctness Rules](correctness.md)
