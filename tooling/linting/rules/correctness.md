# Correctness Linting Rules

This document defines correctness-related linting rules.

## CORRECT-001: Unbalanced Transaction

### Description
Transaction postings must sum to zero.

### Severity
error

### Examples

```beancount
; Error
2024-01-15 * "Test"
    Expenses:Food     50.00 USD
    Assets:Cash      -40.00 USD  ; Off by 10.00

; OK
2024-01-15 * "Test"
    Expenses:Food     50.00 USD
    Assets:Cash      -50.00 USD
```

## CORRECT-002: Account Not Opened

### Description
Accounts should be opened before use (Beancount).

### Severity
error

### Examples

```beancount
; Error
2024-01-15 * "Test"
    Expenses:NewAccount  50.00 USD  ; Not opened
    Assets:Cash

; OK
2024-01-01 open Expenses:NewAccount
2024-01-15 * "Test"
    Expenses:NewAccount  50.00 USD
    Assets:Cash
```

## CORRECT-003: Invalid Date

### Description
Dates must be valid calendar dates.

### Severity
error

### Examples

```beancount
; Error
2024-02-30 * "Invalid"  ; Feb 30 doesn't exist
    Expenses  50.00 USD

; OK
2024-02-28 * "Valid"
    Expenses  50.00 USD
```

## CORRECT-004: Balance Assertion Failed

### Description
Balance assertions must match actual balance.

### Severity
error

### Examples

```beancount
; Error
2024-01-15 balance Assets:Bank  1000.00 USD  ; Actual: 900.00

; OK (if actual is 1000.00)
2024-01-15 balance Assets:Bank  1000.00 USD
```

## CORRECT-005: Duplicate Transaction

### Description
Potential duplicate transactions detected.

### Severity
warning

### Configuration
```yaml
CORRECT-005:
  check_same_day: true
  check_same_amount: true
  check_same_payee: true
```

### Examples

```beancount
; Warning: potential duplicate
2024-01-15 * "Store"
    Expenses:Food  50.00 USD
    Assets:Cash

2024-01-15 * "Store"
    Expenses:Food  50.00 USD
    Assets:Cash
```

## CORRECT-006: Invalid Commodity

### Description
Commodity symbol contains invalid characters.

### Severity
error

### Examples

```beancount
; Error
    Account  50.00 $USD  ; Invalid symbol

; OK
    Account  50.00 USD
```

## CORRECT-007: Negative Balance

### Description
Asset account has negative balance.

### Severity
warning

### Configuration
```yaml
CORRECT-007:
  accounts:
    - "Assets:*"
    - "!Assets:Credit"  # Exclude
```

### Examples

```beancount
; Warning
Assets:Bank:Checking  -500.00 USD

; OK
Liabilities:Credit   -500.00 USD
```

## CORRECT-008: Future Date

### Description
Transaction date is in the future.

### Severity
warning

### Examples

```beancount
; Warning (if today is 2024-01-15)
2024-12-31 * "Future"
    Expenses  50.00 USD
```

## CORRECT-009: Missing Commodity

### Description
Amount without commodity specification.

### Severity
error (Beancount), warning (Ledger)

### Examples

```beancount
; Error
    Account  50.00  ; No commodity

; OK
    Account  50.00 USD
```

## CORRECT-010: Orphaned Posting

### Description
Posting outside of transaction.

### Severity
error

### Examples

```beancount
; Error
    Expenses:Food  50.00 USD  ; No transaction header

; OK
2024-01-15 * "Test"
    Expenses:Food  50.00 USD
```

## CORRECT-011: Circular Include

### Description
File includes create circular reference.

### Severity
error

### Examples

```
; a.journal includes b.journal
; b.journal includes a.journal
; Error: circular include
```

## CORRECT-012: Invalid Account Name

### Description
Account name contains invalid characters.

### Severity
error

### Examples

```beancount
; Error
    Assets:Bank@Home  50.00 USD

; OK
    Assets:Bank:Home  50.00 USD
```

## Severity Summary

| Rule | Default Severity |
|------|------------------|
| CORRECT-001 | error |
| CORRECT-002 | error |
| CORRECT-003 | error |
| CORRECT-004 | error |
| CORRECT-005 | warning |
| CORRECT-006 | error |
| CORRECT-007 | warning |
| CORRECT-008 | warning |
| CORRECT-009 | varies |
| CORRECT-010 | error |
| CORRECT-011 | error |
| CORRECT-012 | error |

## See Also

- [Linting Specification](../spec.md)
- [Style Rules](style.md)
- [Consistency Rules](consistency.md)
