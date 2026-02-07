# Balance Tolerances

## Overview

Tolerances allow small differences when checking transaction balance and balance assertions. They accommodate rounding errors from decimal arithmetic and real-world imprecision.

## The Problem

Exact decimal arithmetic can produce residuals:

```beancount
2024-01-15 * "Three-way split"
  Expenses:A   (100 / 3) USD    ; 33.333333...
  Expenses:B   (100 / 3) USD    ; 33.333333...
  Expenses:C   (100 / 3) USD    ; 33.333333...
  Assets:Cash  -100 USD
  ; Sum: 99.999999... - 100 = -0.000...001
```

Without tolerance, this would fail to balance.

## Tolerance Calculation

### Automatic Tolerance

Tolerance is computed from the **smallest decimal precision** used for a currency in the transaction:

```
tolerance = 0.5 × 10^(-precision)
```

Examples:

| Amount | Precision | Tolerance |
|--------|-----------|-----------|
| `100.00 USD` | 2 | 0.005 |
| `100.000 USD` | 3 | 0.0005 |
| `100 USD` | 0 | 0.5 |
| `0.00000001 BTC` | 8 | 0.000000005 |

### Per-Transaction Tolerance

The tolerance for a transaction is the **maximum** tolerance across all its postings:

```beancount
2024-01-15 * "Mixed precision"
  Assets:Checking   100.00 USD      ; precision 2 → tol 0.005
  Expenses:Food      50.0 USD       ; precision 1 → tol 0.05
  Expenses:Coffee    50 USD         ; precision 0 → tol 0.5
  ; Transaction tolerance: max(0.005, 0.05, 0.5) = 0.5 USD
```

### Balance Check

A transaction balances if:

```
|sum of weights| ≤ tolerance
```

## Configuration

### Per-Currency Default Tolerance

Set default tolerance for specific currencies when it cannot be inferred:

```beancount
option "inferred_tolerance_default" "USD:0.005"
option "inferred_tolerance_default" "BTC:0.00000001"
```

### Tolerance Multiplier

Adjust the multiplier used in tolerance calculation (default is 0.5):

```beancount
option "tolerance_multiplier" "0.5"
```

### Infer Tolerance from Cost

Enable/disable automatic tolerance inference from cost currencies:

```beancount
option "infer_tolerance_from_cost" "TRUE"
```

When enabled, tolerance is also inferred from cost specifications.

## Balance Assertions

### Default Assertion Tolerance

Balance assertions use the same tolerance calculation:

```beancount
2024-01-15 balance Assets:Checking  1000.00 USD
; Passes if actual is within 1000.00 ± 0.005
```

### Explicit Tolerance

Override with the `~` operator:

```beancount
; Exact match required
2024-01-15 balance Assets:Checking  1000.00 ~ 0 USD

; Allow 1 cent variance
2024-01-15 balance Assets:Checking  1000.00 ~ 0.01 USD

; Allow 5 dollar variance
2024-01-15 balance Assets:Checking  1000.00 ~ 5.00 USD
```

### Tolerance Syntax

```ebnf
balance_with_tolerance = amount "~" tolerance_value

tolerance_value = number
```

The tolerance value uses the same currency as the amount.

## Examples

### Three-Way Split

```beancount
2024-01-15 * "Dinner split"
  Expenses:Food     33.33 USD
  Expenses:Food     33.33 USD
  Expenses:Food     33.34 USD    ; Adjusted for rounding
  Assets:Cash     -100.00 USD
  ; Sum: 0 (exact with adjustment)
```

Or with tolerance:

```beancount
2024-01-15 * "Dinner split"
  Expenses:Food     (100/3) USD
  Expenses:Food     (100/3) USD
  Expenses:Food     (100/3) USD
  Assets:Cash      -100.00 USD
  ; Sum: ~0 (within tolerance)
```

### Currency Exchange

```beancount
2024-01-15 * "Exchange"
  Assets:EUR   -100 EUR @ 1.0875 USD
  Assets:USD    108.75 USD
  ; EUR weight: 100 × 1.0875 = 108.75 USD
  ; USD weight: 108.75 USD
  ; Sum: 0
```

With rounding:

```beancount
2024-01-15 * "Exchange with rounding"
  Assets:EUR   -100 EUR @ 1.08756 USD
  Assets:USD    108.76 USD
  ; EUR weight: 108.756 USD
  ; USD weight: 108.76 USD
  ; Residual: 0.004 USD (within tolerance)
```

### Stock Purchase with Commission

```beancount
2024-01-15 * "Buy stock"
  Assets:Stock     10 AAPL {185.5325 USD}
  Expenses:Comm     9.99 USD
  Assets:Cash   -1865.31 USD
  ; Stock: 10 × 185.5325 = 1855.325 USD
  ; Comm: 9.99 USD
  ; Cash: -1865.31 USD
  ; Sum: 1855.325 + 9.99 - 1865.31 = 0.005 (within tolerance)
```

## Tolerance Accumulation

### Multiple Currencies

Each currency has independent tolerance:

```beancount
2024-01-15 * "Multi-currency"
  Assets:EUR    100 EUR
  Assets:USD    110 USD
  Income:Gift:EUR  -100 EUR    ; EUR balances exactly
  Income:Gift:USD  -110 USD    ; USD balances exactly
```

### Large Transactions

Tolerance doesn't scale with transaction size:

```beancount
; Same tolerance (0.005) for both
2024-01-15 * "Small"
  Assets:A    10.00 USD
  Assets:B   -10.00 USD

2024-01-15 * "Large"
  Assets:A    1000000.00 USD
  Assets:B   -1000000.00 USD
```

For percentage-based tolerance, use explicit configuration.

## Edge Cases

### Zero Tolerance

Require exact balance by using explicit tolerance on balance assertions:

```beancount
; Must match exactly
2024-01-15 balance Assets:Checking  1000.00 ~ 0 USD
```

### High-Precision Currencies

Cryptocurrency often needs high precision defaults:

```beancount
option "inferred_tolerance_default" "BTC:0.00000001"
option "inferred_tolerance_default" "ETH:0.000000000000000001"
```

### Shares and Units

For discrete units, set appropriate defaults:

```beancount
option "inferred_tolerance_default" "AAPL:0.0001"
option "inferred_tolerance_default" "VACHR:0.5"
```

## Validation Errors

The following conditions produce errors:

| Condition | Error Type |
|-----------|------------|
| Transaction residual exceeds tolerance | `ValidationError` ("Transaction does not balance") |
| Balance assertion outside tolerance | `BalanceError` |

### Error Messages

Transaction balance error:
```
ValidationError: Transaction does not balance: (0.50 USD)
```

Balance assertion error:
```
BalanceError: Balance failed for 'Assets:Checking': expected 1000.00 USD != accumulated 999.97 USD
```

## Implementation Notes

1. Track precision of each number parsed
2. Compute tolerance from minimum precision per currency
3. Use decimal arithmetic (not floating point)
4. Apply tolerance after summing all weights
5. Store explicit tolerance from `~` operator
6. Report residual and tolerance in error messages
