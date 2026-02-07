# Balance Validation

## Overview

Balance validation ensures transactions balance (debits equal credits) and balance assertions match actual account balances.

## Transaction Balancing

### Transaction Not Balanced

Every transaction MUST balance: the sum of posting weights MUST equal zero for each currency. Violations produce a `ValidationError`.

**Weight Calculation:**

| Posting Type | Weight |
|--------------|--------|
| Simple amount | The amount |
| With cost `{cost}` | units × cost |
| With total cost `{{cost}}` | The total cost |
| With price `@ price` | units × price |
| With total price `@@ price` | The total price |

**Example - Unbalanced:**
```beancount
2024-01-15 * "Unbalanced"
  Assets:Checking   100 USD
  Expenses:Food      50 USD    ; ValidationError: Sum is 150 USD, not 0
```

**Example - Balanced:**
```beancount
2024-01-15 * "Balanced"
  Assets:Checking  -100 USD
  Expenses:Food      50 USD
  Expenses:Coffee    50 USD
  ; Sum: -100 + 50 + 50 = 0 ✓
```

### Multi-Currency Transactions

Each currency must independently balance:

```beancount
2024-01-15 * "Multi-currency"
  Assets:EUR        100 EUR    ; EUR: +100
  Assets:USD        110 USD    ; USD: +110
  Income:Gift:EUR  -100 EUR    ; EUR: -100
  Income:Gift:USD  -110 USD    ; USD: -110
  ; EUR sum: 0 ✓
  ; USD sum: 0 ✓
```

### Currency Conversion

Price annotations enable cross-currency balancing:

```beancount
2024-01-15 * "Exchange"
  Assets:EUR   100 EUR @ 1.10 USD    ; Weight: 110 USD
  Assets:USD  -110 USD               ; Weight: -110 USD
  ; USD sum: 110 - 110 = 0 ✓
```

### Tolerance

Small residuals are allowed within tolerance:

```beancount
2024-01-15 * "Split"
  Expenses:A   (100/3) USD    ; 33.333...
  Expenses:B   (100/3) USD    ; 33.333...
  Expenses:C   (100/3) USD    ; 33.333...
  Assets:Cash  -100 USD
  ; Residual: ~0.000001 (within tolerance)
```

See [tolerances.md](../tolerances.md) for tolerance rules.

## Amount Interpolation

### Multiple Missing Amounts

> **UNDEFINED**: The exact elision rule is pending clarification.
> See: [Pending Issue - Amount Elision Rule](https://github.com/beancount/beancount/issues/TBD)

**Option A (One per currency):**
At most one posting per currency MAY omit its amount.

**Option B (One total):**
At most one posting total MAY omit its amount.

**Always Invalid:**
```beancount
2024-01-15 * "Two missing for same currency"
  Assets:Checking   100 USD
  Expenses:Food              ; ERROR: ambiguous
  Expenses:Coffee            ; Which gets how much?
```

### Interpolation Algorithm

1. Group postings by currency
2. For each currency, count postings with missing amounts
3. If count > 1 for same currency: produce error
4. Compute missing amounts to balance each currency
5. Proceed to balance check

## Balance Assertions

### Balance Assertion Failed

Balance assertions verify account balances at a point in time. Failures produce a `BalanceError`.

**Timing:** Checked at the START of the assertion date (after all previous dates).

```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 * "Deposit"
  Assets:Checking  100 USD
  Income:Salary

2024-01-16 balance Assets:Checking  100 USD    ; ✓ Checks balance before 2024-01-16

2024-01-16 * "Purchase"
  Assets:Checking  -20 USD
  Expenses:Food

2024-01-17 balance Assets:Checking  80 USD     ; ✓ After purchase
```

**Failed Assertion:**
```beancount
2024-01-16 balance Assets:Checking  200 USD
; BalanceError: Expected 200, got 100 (difference: -100)
```

### Tolerance Exceeded

Balance assertion fails if difference exceeds tolerance. The same `BalanceError` is produced.

```beancount
2024-01-16 balance Assets:Checking  100.00 ~ 0.01 USD
; Actual: 99.98 USD
; Difference: 0.02 USD
; BalanceError: Exceeds tolerance of 0.01
```

### Currency Specificity

Balance assertions check one currency at a time:

```beancount
2024-01-01 open Assets:Multi

2024-01-15 * "Deposits"
  Assets:Multi  100 USD
  Assets:Multi   50 EUR
  Income:Various

; Check each separately
2024-01-16 balance Assets:Multi  100 USD    ; Only USD
2024-01-16 balance Assets:Multi   50 EUR    ; Only EUR
```

## Pad Validation

### Pad Without Balance

A `pad` directive MUST have a subsequent `balance` assertion for the same account and currency. Missing balance produces a `PadError`.

```beancount
2024-01-01 pad Assets:Checking Equity:Opening
; PadError: No balance assertion follows for Assets:Checking
```

**Valid:**
```beancount
2024-01-01 pad Assets:Checking Equity:Opening
2024-01-02 balance Assets:Checking  1000 USD    ; ✓
```

### Multiple Pads

Only one `pad` may precede each `balance` for a given account/currency. Multiple pads produce a `PadError`.

```beancount
2024-01-01 pad Assets:Checking Equity:Opening
2024-01-05 pad Assets:Checking Expenses:Unknown    ; PadError
2024-01-10 balance Assets:Checking  1000 USD
```

## Transaction Structure

### No Postings

> **UNDEFINED**: Whether transactions with no postings should produce an error is pending clarification.
> See: [Pending Issue - Empty Transactions](https://github.com/beancount/beancount/issues/TBD)

```beancount
2024-01-15 * "Empty transaction"
; Should this be an error?
```

### Single Posting

Transactions with only one non-zero posting cannot balance and produce a `ValidationError`:

```beancount
2024-01-15 * "Single posting"
  Assets:Checking  100 USD
; ValidationError: Transaction does not balance: (100 USD)
```

## Validation Order

Balance validation occurs in phases:

1. **Parse** - Build directive list
2. **Interpolate** - Compute missing amounts (`ValidationError` for ambiguous)
3. **Balance** - Check transaction sums (`ValidationError` for imbalanced)
4. **Assert** - Check balance assertions (`BalanceError`)
5. **Pad** - Validate pad/balance relationships (`PadError`)

## Error Messages

### Transaction Balance Error
```
ValidationError: Transaction does not balance within tolerance:
  residual: 50 USD
  tolerance: 0.005 USD
```

### Balance Assertion Error
```
BalanceError: Balance failed for 'Assets:Checking':
  expected: 200 USD
  actual: 100 USD
  difference: -100 USD
```

## Implementation Notes

1. Compute posting weights using cost/price rules
2. Group by currency for balance checking
3. Apply tolerance after summing
4. Process balance assertions chronologically
5. Track running balances per account/currency
6. Generate padding transactions before final balance check
