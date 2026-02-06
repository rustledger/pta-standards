# Balance Directive

## Overview

The `balance` directive asserts that an account has a specific balance at the beginning of the given date. If the actual balance differs, a validation error is produced.

## Syntax

```ebnf
balance = date WHITESPACE "balance" WHITESPACE account WHITESPACE amount
          ["~" tolerance]
          (NEWLINE metadata)*

tolerance = number
```

## Components

### Date

The date of the assertion. The balance is checked at the **beginning** of this date (after all directives from previous dates).

### Account

The account whose balance to check.

### Amount

The expected balance (number and currency).

### Tolerance (Optional)

An explicit tolerance for fuzzy matching:

```beancount
2024-01-15 balance Assets:Checking  1000.00 ~ 0.01 USD
```

## Semantics

### Timing

Balance assertions check the balance at the **start** of the given date:

```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 * "Deposit"
  Assets:Checking  100 USD
  Income:Salary

; Checks balance BEFORE any 2024-01-16 transactions
2024-01-16 balance Assets:Checking  100 USD

2024-01-16 * "Purchase"
  Assets:Checking  -20 USD
  Expenses:Food

; After the purchase
2024-01-17 balance Assets:Checking  80 USD
```

### Currency Specificity

Balance assertions check ONE currency at a time:

```beancount
2024-01-01 open Assets:Multi USD,EUR

2024-01-15 * "Deposits"
  Assets:Multi  100 USD
  Assets:Multi   50 EUR
  Income:Gift

; Check each currency separately
2024-01-16 balance Assets:Multi  100 USD
2024-01-16 balance Assets:Multi   50 EUR
```

## Tolerance

### Default Tolerance

Balance checking uses a default tolerance based on the currency's smallest unit:

| Currency Format | Default Tolerance |
|-----------------|-------------------|
| 2 decimal places | 0.005 |
| 3 decimal places | 0.0005 |
| No decimals | 0.5 |

The tolerance is half of the last significant digit.

### Explicit Tolerance

Override with the `~` operator:

```beancount
; Allow 1 cent variance
2024-01-15 balance Assets:Checking  1000.00 ~ 0.01 USD

; Allow 5 dollar variance (for rounding errors)
2024-01-15 balance Assets:Checking  1000.00 ~ 5.00 USD

; Exact match required
2024-01-15 balance Assets:Checking  1000.00 ~ 0 USD
```

### Tolerance Calculation

A balance assertion passes if:

```
|actual - expected| <= tolerance
```

## Examples

### Simple Balance Check

```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 * "Paycheck"
  Assets:Checking  2500.00 USD
  Income:Salary

2024-01-16 balance Assets:Checking  2500.00 USD
```

### Monthly Reconciliation

```beancount
; Check balance matches bank statement
2024-02-01 balance Assets:Checking  3456.78 USD
  statement-date: "2024-01-31"
  source: "bank-statement.pdf"
```

### Investment Account

```beancount
2024-01-01 open Assets:Brokerage USD,AAPL

2024-06-01 * "Buy"
  Assets:Brokerage  10 AAPL {150 USD}
  Assets:Brokerage  -1500 USD

; Check share count
2024-06-02 balance Assets:Brokerage  10 AAPL

; Check cash balance
2024-06-02 balance Assets:Brokerage  -1500 USD
```

## Validation

| Error | Condition |
|-------|-----------|
| E2001 | Balance assertion failed |
| E2002 | Balance within default tolerance but exceeds explicit tolerance |
| E1001 | Account not opened |

### Error Output

```
error: Balance assertion failed
  --> ledger.beancount:25:1
   |
25 | 2024-01-16 balance Assets:Checking  1000.00 USD
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ expected 1000.00, got 950.00
   |
   = difference: -50.00 USD
   = tolerance: 0.005 USD
```

## Partial Balances

Balance assertions check only the specified currency. Other currencies in the account are not affected:

```beancount
2024-01-01 open Assets:Multi

2024-01-15 * "Multi-currency"
  Assets:Multi  100 USD
  Assets:Multi   50 EUR
  Assets:Multi   25 GBP
  Income:Various

; Only checks USD balance
2024-01-16 balance Assets:Multi  100 USD
; EUR and GBP balances not checked
```

## With Cost Basis

For accounts with lots, balance assertions check the total units regardless of cost:

```beancount
2024-01-01 open Assets:Stock AAPL "FIFO"

2024-03-01 * "Buy lot 1"
  Assets:Stock  10 AAPL {150 USD}
  Assets:Cash

2024-04-01 * "Buy lot 2"
  Assets:Stock  10 AAPL {160 USD}
  Assets:Cash

; Check total shares (ignoring cost basis)
2024-04-02 balance Assets:Stock  20 AAPL
```

## Best Practices

1. **Regular assertions**: Add balance assertions monthly or after bank reconciliation
2. **Multiple currencies**: Add one assertion per currency
3. **Before major changes**: Assert balance before large transactions
4. **Use metadata**: Document the source of the expected balance

```beancount
2024-02-01 balance Assets:Checking  5432.10 USD
  source: "January statement"
  verified-date: 2024-02-05
```

## Implementation Notes

1. Balance assertions execute at start of day
2. Sort balance directives before transactions on same date
3. Apply tolerance rules for comparison
4. Report actual vs expected with difference
