# hledger Balance Assertions Specification

This document specifies balance assertions in hledger.

## Overview

Balance assertions verify account balances at specific points:
- Catch errors early
- Reconciliation checkpoints
- Data integrity

## Syntax

### Basic Assertion

```hledger
ACCOUNT    AMOUNT = EXPECTED_BALANCE
```

### Subaccount Assertion

```hledger
ACCOUNT    AMOUNT =* EXPECTED_BALANCE
```

## Basic Assertion

```hledger
2024-01-15 Deposit
    assets:checking    $500 = $1500
    income:salary
```

After this posting, `assets:checking` must equal $1500.

## Assertion Types

### Exact Balance

```hledger
    assets:checking    $100 = $1000
```

Checks this specific account only.

### Including Subaccounts

```hledger
    assets:bank    $0 =* $5000
```

Checks `assets:bank` plus all subaccounts.

## Assertion Timing

Assertions check the balance AFTER the posting:

```hledger
2024-01-01 Opening
    assets:checking    $1000 = $1000
    equity:opening

2024-01-15 Expense
    expenses:food      $50
    assets:checking   $-50 = $950
```

## Multi-Commodity

Each commodity is checked separately:

```hledger
    assets:brokerage    10 AAPL = 100 AAPL
    assets:brokerage    $0 = $5000
```

## Assertion Failure

When assertion fails:

```
hledger: error: balance assertion failed
  in file.journal, line 10
    assets:checking    $100 = $1000
  expected: $1000
  actual:   $900
```

## Common Patterns

### Monthly Reconciliation

```hledger
2024-01-31 * Monthly Reconciliation
    assets:checking    $0 = $2500.00
    ; Statement balance verified
```

### Opening Balance

```hledger
2024-01-01 * Opening Balance
    assets:checking    $5000 = $5000
    assets:savings     $10000 = $10000
    equity:opening
```

### Zero Balance Check

```hledger
2024-01-15 Clear Receivable
    assets:checking     $100
    assets:receivables $-100 = $0
```

### Statement Close

```hledger
2024-01-31 Statement Close
    ; Credit card statement
    liabilities:visa    $0 = $-1500
```

## Balance Assignments

Automatically calculate amount to reach balance:

```hledger
2024-01-15 Adjustment
    assets:checking    = $1000  ; Amount calculated
    equity:adjustments
```

The amount is inferred to make balance = $1000.

## Partial Assertions

Only assert when amount is provided:

```hledger
2024-01-15 Transaction
    expenses:food    $50
    assets:checking  $-50 = $950  ; Asserted
    ; or
    assets:checking       ; Not asserted
```

## Strict vs Lenient

### Strict (Default)

Assertions must pass:

```bash
hledger check assertions
```

### Ignore Assertions

```bash
hledger bal --ignore-assertions
```

## Examples

### Bank Reconciliation

```hledger
; Opening balance from bank statement
2024-01-01 * Opening
    assets:bank:checking    $5,234.56 = $5,234.56
    equity:opening

; Regular transactions
2024-01-05 Groceries
    expenses:food           $87.32
    assets:bank:checking   $-87.32

2024-01-10 Salary
    assets:bank:checking    $3,000.00
    income:salary

; Month-end reconciliation
2024-01-31 * Statement Balance
    assets:bank:checking    $0 = $8,147.24
    ; Verified against January statement
```

### Credit Card

```hledger
2024-01-05 Amazon
    expenses:shopping    $75.00
    liabilities:visa

2024-01-15 Restaurant
    expenses:food    $45.00
    liabilities:visa

; Statement close
2024-01-20 Statement Close
    liabilities:visa    $0 = $-120.00

; Payment
2024-01-25 * Payment
    liabilities:visa     $120.00 = $0
    assets:checking
```

### Investment Account

```hledger
2024-01-15 Buy Stock
    assets:brokerage    10 AAPL {$150}
    assets:brokerage   $-1500

2024-01-31 Month-end Check
    assets:brokerage    0 AAPL = 10 AAPL
    assets:brokerage    $0 = $3500
```

## Best Practices

1. **Regular assertions** - Monthly at minimum
2. **Match statements** - Use bank/card statements
3. **Opening balances** - Always assert
4. **After transfers** - Verify both accounts
5. **Document source** - Note statement reference

## Troubleshooting

### Finding Discrepancy

```bash
# Show register leading up to assertion
hledger reg assets:checking -e 2024-01-31

# Check for missing transactions
hledger bal assets:checking
```

### Common Issues

- Duplicate transactions
- Missing transactions
- Wrong date ordering
- Commodity mismatch

## See Also

- [Posting Specification](../posting.md)
- [Auto Postings](auto-postings.md)
