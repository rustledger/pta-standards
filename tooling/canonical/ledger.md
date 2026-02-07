# Ledger Canonical Output

This document specifies canonical output format for Ledger journals.

## Format

### Transaction

```ledger
2024/01/15 * (code) Payee
    ; Transaction metadata
    Account:One                    $100.00
        ; Posting metadata
    Account:Two                   $-100.00
```

## Formatting Rules

### Date

```ledger
2024/01/15    ; YYYY/MM/DD (preferred)
```

### Status

```ledger
2024/01/15 * Cleared
2024/01/15 ! Pending
2024/01/15 Unmarked
```

### Code

```ledger
2024/01/15 (check-123) Payee
```

### Payee

```ledger
2024/01/15 Payee Name Here
```

No quotes required.

### Account Alignment

```ledger
    Short:Account                  $100.00
    Longer:Account:Name            $200.00
    Very:Long:Account:Name:Here   $1000.00
```

Right-align at column 48 (or consistent column).

### Amount Format

```ledger
    Account    $1,234.56
    Account    100.00 USD
    Account    10 AAPL {$150.00}
```

### Metadata

```ledger
2024/01/15 Payee
    ; Key: Value
    ; :tag1:tag2:
    Account    $100.00
        ; Posting-level: metadata
```

### Comments

```ledger
; Standalone comment

2024/01/15 Payee  ; Inline comment
    Account    $100.00  ; Amount comment
```

## Directive Order

1. Commodity directives
2. Account directives
3. Tag/payee declarations
4. Transactions (chronological)

## Example

```ledger
; Canonical Ledger output

commodity $
    format $1,000.00

account Assets:Bank:Checking
account Expenses:Food:Groceries

2024/01/01 * Opening Balance
    Assets:Bank:Checking              $5,000.00
    Equity:Opening-Balances

2024/01/15 * (123) Whole Foods
    ; :groceries:weekly:
    Expenses:Food:Groceries             $125.50
        ; Receipt: scan-2024-01-15.pdf
    Assets:Bank:Checking               $-125.50
```

## Normalization

### Input

```ledger
2024-01-15 payee
	Expenses  $50
	Assets:Cash
```

### Canonical Output

```ledger
2024/01/15 payee
    Expenses                            $50.00
    Assets:Cash                        $-50.00
```

## See Also

- [Canonical Specification](spec.md)
- [Ledger Specification](../../formats/ledger/v1/)
