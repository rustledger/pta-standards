# Style Linting Rules

This document defines style-related linting rules.

## STYLE-001: Indentation

### Description
Postings should use consistent indentation.

### Configuration
```yaml
STYLE-001:
  indent: 4           # spaces
  use_tabs: false
```

### Examples

```beancount
; Bad
2024-01-15 * "Test"
  Account  50.00 USD    ; 2 spaces

; Good
2024-01-15 * "Test"
    Account  50.00 USD  ; 4 spaces
```

## STYLE-002: Amount Alignment

### Description
Amounts should align at a consistent column.

### Configuration
```yaml
STYLE-002:
  align_column: 48
```

### Examples

```beancount
; Bad
    Short  50.00 USD
    Very:Long:Account  100.00 USD

; Good
    Short                           50.00 USD
    Very:Long:Account              100.00 USD
```

## STYLE-003: Date Format

### Description
Dates should use consistent format.

### Configuration
```yaml
STYLE-003:
  format: "YYYY-MM-DD"  # or "YYYY/MM/DD"
```

### Examples

```beancount
; Bad (inconsistent)
2024-01-15 * "One"
2024/01/16 * "Two"

; Good
2024-01-15 * "One"
2024-01-16 * "Two"
```

## STYLE-004: Trailing Whitespace

### Description
Lines should not have trailing whitespace.

### Examples

```beancount
; Bad
2024-01-15 * "Test"   ⎵⎵
    Account  50.00 USD⎵

; Good
2024-01-15 * "Test"
    Account  50.00 USD
```

## STYLE-005: Blank Lines

### Description
Transactions should be separated by blank lines.

### Configuration
```yaml
STYLE-005:
  blank_lines: 1
```

### Examples

```beancount
; Bad
2024-01-15 * "One"
    Account  50.00 USD
2024-01-16 * "Two"
    Account  50.00 USD

; Good
2024-01-15 * "One"
    Account  50.00 USD

2024-01-16 * "Two"
    Account  50.00 USD
```

## STYLE-006: Account Case

### Description
Account names should use consistent casing.

### Configuration
```yaml
STYLE-006:
  style: "TitleCase"  # or "lowercase"
```

### Examples

```beancount
; Bad
expenses:food
ASSETS:BANK

; Good
Expenses:Food
Assets:Bank
```

## STYLE-007: Commodity Position

### Description
Commodity should appear consistently before or after amount.

### Configuration
```yaml
STYLE-007:
  position: "after"  # or "before"
```

### Examples

```beancount
; Bad (inconsistent)
    Account  USD 50.00
    Account  50.00 USD

; Good
    Account  50.00 USD
    Account  100.00 USD
```

## STYLE-008: Quote Style

### Description
Strings should use consistent quote style.

### Configuration
```yaml
STYLE-008:
  style: "double"  # or "single"
```

### Examples

```beancount
; Bad (for Beancount)
2024-01-15 * 'Payee' 'Narration'

; Good
2024-01-15 * "Payee" "Narration"
```

## STYLE-009: Metadata Alignment

### Description
Metadata should be consistently indented.

### Configuration
```yaml
STYLE-009:
  indent: 2  # additional spaces
```

### Examples

```beancount
; Bad
    Account  50.00 USD
; key: value

; Good
    Account  50.00 USD
      ; key: value
```

## STYLE-010: Comment Style

### Description
Comments should use consistent marker.

### Configuration
```yaml
STYLE-010:
  marker: ";"  # or "#"
```

### Examples

```beancount
; Bad (inconsistent)
; Comment one
# Comment two

; Good
; Comment one
; Comment two
```

## Auto-Fix Support

| Rule | Auto-fixable |
|------|--------------|
| STYLE-001 | Yes |
| STYLE-002 | Yes |
| STYLE-003 | No |
| STYLE-004 | Yes |
| STYLE-005 | Yes |
| STYLE-006 | No |
| STYLE-007 | No |
| STYLE-008 | Yes |
| STYLE-009 | Yes |
| STYLE-010 | Yes |

## See Also

- [Linting Specification](../spec.md)
- [Correctness Rules](correctness.md)
- [Consistency Rules](consistency.md)
