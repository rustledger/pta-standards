# hledger Canonical Output

This document specifies canonical output format for hledger journals.

## Format

### Transaction

```hledger
2024-01-15 * (code) Payee
    ; transaction comment
    account:one    100.00 USD
        ; posting comment
    account:two   -100.00 USD
```

## Formatting Rules

### Date

```hledger
2024-01-15    ; YYYY-MM-DD (preferred)
```

### Status

```hledger
2024-01-15 * cleared
2024-01-15 ! pending
2024-01-15 unmarked
```

### Code

```hledger
2024-01-15 (check-123) Payee
```

### Description

```hledger
2024-01-15 Payee | Description
```

Or:

```hledger
2024-01-15 Just description
```

### Account Alignment

```hledger
    short:account         100.00 USD
    longer:account:name   200.00 USD
```

### Amount Format

```hledger
    account    1,234.56 USD
    account    10 AAPL @ 150 USD
    account    10 AAPL {150 USD}
```

### Metadata

```hledger
2024-01-15 Payee
    ; key: value
    ; tag1:, tag2: value
    account    100.00 USD
        ; posting-level: metadata
```

### Comments

```hledger
; Standalone comment
# Also valid

2024-01-15 Payee  ; inline
    account    100.00 USD  ; posting inline
```

## Directive Order

1. `decimal-mark` directive
2. `commodity` directives
3. `account` directives
4. Transactions (chronological)

## Example

```hledger
; Canonical hledger output

decimal-mark .

commodity USD
    format 1,000.00 USD

account assets:bank:checking
    ; type: Asset

account expenses:food:groceries
    ; type: Expense

2024-01-01 * Opening Balance
    assets:bank:checking    5,000.00 USD
    equity:opening-balances

2024-01-15 * (123) Whole Foods
    ; groceries:, weekly:
    expenses:food:groceries    125.50 USD
        ; receipt: scan-2024-01-15.pdf
    assets:bank:checking      -125.50 USD
```

## Normalization

### Input

```hledger
2024/01/15 payee
	Expenses  $50
	Assets:Cash
```

### Canonical Output

```hledger
2024-01-15 payee
    expenses     50.00 USD
    assets:cash -50.00 USD
```

## See Also

- [Canonical Specification](spec.md)
- [hledger Specification](../../formats/hledger/v1/)
