# Balance Validation Specification

This document specifies balance checking and validation rules in Ledger.

## Overview

Balance validation ensures:
- Transactions sum to zero (double-entry principle)
- Balance assertions match actual balances
- Commodity conversions are properly priced

## Transaction Balancing

### Basic Rule

Each transaction must balance to zero across all commodities:

```ledger
2024/01/15 Valid Transaction
    Expenses:Food    $50.00
    Assets:Checking  $-50.00
    ; Sum: $50 + $-50 = $0 ✓
```

### Unbalanced Error

```ledger
2024/01/15 Invalid Transaction
    Expenses:Food    $50.00
    Assets:Checking  $-40.00
    ; Sum: $50 + $-40 = $10 ✗
```

Error:
```
V-001: Transaction does not balance
  Line 1-3: 2024/01/15 Invalid Transaction
    Difference: $10.00
    All commodity totals must equal zero
```

## Multi-Commodity Transactions

### With Exchange Rate

```ledger
2024/01/15 Currency Exchange
    Assets:EUR    100 EUR @@ $110
    Assets:USD   $110
    ; EUR converts to USD, balances ✓
```

### Separate Commodity Groups

Each commodity group must balance independently when no conversion:

```ledger
2024/01/15 Multi-Commodity
    Assets:EUR    100 EUR
    Assets:USD    $110
    ; ERROR: Neither EUR nor USD balance
```

### With Price Annotation

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL @ $150
    Assets:Cash        $-1500
    ; AAPL converts at $150/unit, balances ✓
```

## Balance Assertions

### Syntax

```ledger
posting = account amount ["=" balance]
```

### Basic Assertion

```ledger
2024/01/15 Deposit
    Assets:Checking    $500 = $1500
    Income:Salary
```

The account balance after this posting must equal $1500.

### Assertion Failure

```
V-003: Balance assertion failed
  Line 2:     Assets:Checking    $500 = $1500
  Expected: $1500.00
  Actual:   $1200.00
```

### Running Balance

Assertions check the cumulative balance:

```ledger
2024/01/01 Opening
    Assets:Checking    $1000 = $1000
    Equity:Opening

2024/01/15 Deposit
    Assets:Checking    $500 = $1500
    Income:Salary

2024/01/20 Expense
    Expenses:Food      $50
    Assets:Checking   $-50 = $1450
```

## Assertion Types

### Total Balance

Default assertion checks total balance:

```ledger
    Assets:Checking    $100 = $1500
    ; Checks total of all postings to Assets:Checking
```

### Subaccount Balance

Assertions apply to the specific account:

```ledger
    Assets:Bank:Checking    $100 = $500
    Assets:Bank:Savings     $100 = $1000
    ; Each account checked independently
```

### Wildcard Assertions

Check sum of all subaccounts:

```ledger
    Assets:Bank    $0 = $1500
    ; Checks total of Assets:Bank:* = $1500
```

## Virtual Posting Balance

### Unbalanced Virtual (Parentheses)

Unbalanced virtual postings don't affect real balance:

```ledger
2024/01/15 Expense
    Expenses:Food       $50
    (Budget:Food)      $-50    ; Virtual, no balance requirement
    Assets:Checking    $-50
    ; Real postings: $50 + $-50 = $0 ✓
```

### Balanced Virtual (Brackets)

Balanced virtual postings must sum to zero among themselves:

```ledger
2024/01/15 Budget Transfer
    [Budget:Food]        $50
    [Budget:Available]  $-50
    ; Virtual postings: $50 + $-50 = $0 ✓
```

### Mixed Validation

```ledger
2024/01/15 Expense with Budget
    Expenses:Food        $50
    Assets:Checking     $-50
    ; Real: $50 + $-50 = $0 ✓

    [Budget:Food]        $50
    [Budget:Available]  $-50
    ; Virtual: $50 + $-50 = $0 ✓

    (Tracking:Groceries)  1
    ; Unbalanced virtual, no check
```

### Virtual Balance Error

```
V-012: Balanced virtual postings don't balance
  Line 5-6:
    [Budget:A]    $50
    [Budget:B]    $30
  Difference: $20.00
```

## Tolerance and Precision

### Floating Point Tolerance

Small differences due to rounding are tolerated:

```ledger
2024/01/15 Split
    Expenses:A    $33.33
    Expenses:B    $33.33
    Expenses:C    $33.34
    Assets:Cash  $-100.00
    ; Sum: $0.00 (within tolerance) ✓
```

### Precision Settings

```bash
ledger --decimal-comma --precision 2
```

### Commodity-Specific Precision

```ledger
commodity $
    format $1,000.00    ; 2 decimal places

commodity BTC
    format 0.00000000 BTC    ; 8 decimal places
```

## Cost and Price Validation

### Cost Consistency

When cost is specified, verify calculation:

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL {$150}    ; Total: $1500
    Assets:Cash        $-1500
    ; Verifies: 10 × $150 = $1500 ✓
```

### Total Cost Notation

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL {{$1500}}    ; Total cost
    Assets:Cash        $-1500
    ; Per-unit: $1500 / 10 = $150 ✓
```

### Price Annotation

```ledger
2024/01/15 Sell
    Assets:Cash         $1800
    Assets:Brokerage   -10 AAPL @ $180
    Income:Gains        ; Balances to $0
```

## Elision Validation

### Single Elision

One posting per commodity can omit amount:

```ledger
2024/01/15 Purchase
    Expenses:Food    $50
    Assets:Checking      ; Elided: $-50
```

### Multiple Elision Error

```
V-002: Multiple elided amounts for same commodity
  Line 1-3: 2024/01/15 Bad
    Only one posting per commodity can omit amount
```

## Validation Modes

### Normal Mode

- Errors abort processing
- Warnings are reported
- Balance must be exact (within tolerance)

### Permissive Mode

```bash
ledger --permissive
```

- Some errors become warnings
- Processing continues

### Strict Mode

```bash
ledger --strict
```

- Warnings become errors
- Stricter precision checking
- Requires account/commodity declarations

## Examples

### Correct Multi-Way Split

```ledger
2024/01/15 Costco
    Expenses:Food        $150.00
    Expenses:Household    $75.00
    Expenses:Gas          $50.00
    Assets:Checking     $-275.00
    ; Sum: $150 + $75 + $50 + $-275 = $0 ✓
```

### Currency Conversion

```ledger
2024/01/15 Exchange
    Assets:USD     $110.00
    Assets:EUR    -100 EUR @ $1.10
    ; 100 EUR × $1.10 = $110, balances ✓
```

### Complex Investment

```ledger
2024/01/15 Buy with Fee
    Assets:Brokerage    10 AAPL {$150} @ $152
    Expenses:Fees        $7.00
    Assets:Cash       $-1527.00
    ; Stock: 10 × $152 = $1520
    ; Fee: $7
    ; Cash: $-1527
    ; Sum: $1520 + $7 + $-1527 = $0 ✓
```

### Balance Assertion Chain

```ledger
2024/01/01 Opening
    Assets:Checking    $1000 = $1000
    Equity:Opening

2024/01/15 Income
    Assets:Checking     $500 = $1500
    Income:Salary

2024/01/20 Rent
    Expenses:Rent       $800
    Assets:Checking    $-800 = $700

2024/01/25 Groceries
    Expenses:Food        $50
    Assets:Checking     $-50 = $650
```

## Error Messages

### V-001: Transaction does not balance

```
V-001: Transaction does not balance
  Line 5-7: 2024/01/15 Purchase
    Expenses:Food        $50.00
    Assets:Checking     $-40.00
  Difference: $10.00
  All commodity totals must equal zero
```

### V-003: Balance assertion failed

```
V-003: Balance assertion failed
  Line 7:     Assets:Checking    $100 = $1500
  Expected: $1500.00
  Actual:   $1200.00
  Previous balance: $1100.00
```

### V-012: Virtual imbalance

```
V-012: Balanced virtual postings don't balance
  Line 10-11:
    [Budget:Food]      $500
    [Budget:Available] $-400
  Difference: $100.00
```

## Best Practices

1. **Regular assertions** - Add balance assertions monthly
2. **Reconcile often** - Match with bank statements
3. **Use strict mode** - For production journals
4. **Check complex transactions** - Verify multi-commodity balances
5. **Document conversions** - Add notes for exchange rates

## See Also

- [Posting Specification](../posting.md)
- [Amount Specification](../amounts.md)
- [Error Codes](../errors.md)
