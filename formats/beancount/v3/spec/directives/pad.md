# Pad Directive

## Overview

The `pad` directive automatically inserts a balancing transaction to make a subsequent `balance` assertion true. It is used for reconciling accounts when the exact transactions are unknown.

## Syntax

```ebnf
pad = date WHITESPACE "pad" WHITESPACE account WHITESPACE pad_account
      (NEWLINE metadata)*

account     = target account to pad
pad_account = source account for padding amount
```

## Components

### Date

The date of the padding transaction. Must be before the corresponding balance assertion.

### Target Account

The account whose balance will be adjusted.

### Pad Account

The account that will receive the opposite posting (typically an equity or expense account).

## Semantics

### How Padding Works

1. Parser sees `pad` directive on date D1
2. Parser sees `balance` assertion on date D2 (where D2 > D1)
3. System computes actual balance at D2
4. If balance differs from assertion, a transaction is inserted at D1 to make up the difference

### Generated Transaction

The padding generates a transaction with flag `P`:

```beancount
; Input
2024-01-01 pad Assets:Checking Equity:Opening-Balances
2024-01-15 balance Assets:Checking  1000 USD

; Generated (if account was empty)
2024-01-01 P "Padding for balance assertion"
  Assets:Checking          1000 USD
  Equity:Opening-Balances -1000 USD
```

## Examples

### Opening Balance

```beancount
; Set up initial balance without knowing transaction history
2024-01-01 open Assets:Checking USD
2024-01-01 open Equity:Opening-Balances

2024-01-01 pad Assets:Checking Equity:Opening-Balances
2024-01-02 balance Assets:Checking  5432.10 USD
```

### Reconciliation Gap

```beancount
; Account exists with known transactions
2024-01-01 open Assets:Checking USD

2024-01-15 * "Known deposit"
  Assets:Checking  1000 USD
  Income:Salary

; Some transactions missing, reconcile with bank
2024-02-01 pad Assets:Checking Expenses:Reconciliation
2024-02-02 balance Assets:Checking  850 USD

; Padding generates -150 USD to Expenses:Reconciliation
```

### Cash Account

```beancount
2024-01-01 open Assets:Cash USD
2024-01-01 open Expenses:Cash:Unknown

; Track cash spending without receipts
2024-01-01 * "ATM"
  Assets:Cash  200 USD
  Assets:Checking

; Reconcile weekly
2024-01-08 pad Assets:Cash Expenses:Cash:Unknown
2024-01-08 balance Assets:Cash  50 USD

; Generated: 150 USD expense for untracked spending
```

## Currency Matching

The pad directive works per-currency. The balance assertion determines which currency is padded:

```beancount
2024-01-01 open Assets:Multi USD,EUR

2024-01-01 pad Assets:Multi Equity:Opening

; Only pads USD
2024-01-02 balance Assets:Multi  100 USD

; Separately pads EUR
2024-01-02 balance Assets:Multi  50 EUR
```

## Validation

The following conditions produce errors:

| Condition | Error Type |
|-----------|------------|
| Pad without subsequent balance assertion | `PadError` ("Unused Pad entry") |
| Multiple pads for same account/currency before one balance | `PadError` |
| Target or pad account not opened | `ValidationError` |

### Error Examples

```beancount
; PadError: Pad without balance
2024-01-01 pad Assets:Checking Equity:Opening
; No balance assertion follows!

; PadError: Multiple pads before one balance
2024-01-01 pad Assets:Checking Equity:Opening
2024-01-05 pad Assets:Checking Equity:Opening  ; ERROR: Unused Pad entry
2024-01-10 balance Assets:Checking  1000 USD
```

## Constraints

### One Pad Per Balance

Only one `pad` directive can precede each `balance` assertion for a given account and currency:

```beancount
; Valid: one pad per balance
2024-01-01 pad Assets:Checking Equity:Opening
2024-01-15 balance Assets:Checking  1000 USD
2024-01-16 pad Assets:Checking Expenses:Unknown
2024-02-01 balance Assets:Checking  800 USD

; Invalid: two pads before one balance
2024-01-01 pad Assets:Checking Equity:Opening
2024-01-10 pad Assets:Checking Expenses:Unknown  ; ERROR
2024-01-15 balance Assets:Checking  1000 USD
```

### Pad Always Requires Balance Difference

A pad directive that doesn't result in any padding (because the balance already matches) produces a `PadError`:

```beancount
2024-01-01 open Assets:Checking USD
2024-01-01 open Equity:Opening USD

2024-01-15 * "Exact deposit"
  Assets:Checking  1000 USD
  Equity:Opening

2024-01-01 pad Assets:Checking Equity:Opening
2024-01-16 balance Assets:Checking  1000 USD

; PadError: Unused Pad entry (balance already matches, pad not needed)
```

Only use `pad` when you expect a balance difference to be filled. If the balance already matches, omit the pad directive.

## Typical Pad Accounts

| Use Case | Recommended Pad Account |
|----------|------------------------|
| Opening balances | `Equity:Opening-Balances` |
| Unknown expenses | `Expenses:Unknown` or `Expenses:Reconciliation` |
| Rounding errors | `Expenses:Rounding` |
| Conversion gains | `Income:Conversion` |

## Interaction with Booking

Pad directives create simple postings without cost specification. For accounts with lot tracking, padding adds units at zero cost:

```beancount
2024-01-01 open Assets:Stock AAPL "FIFO"

2024-01-01 pad Assets:Stock Equity:Opening
2024-01-02 balance Assets:Stock  10 AAPL

; Generated: 10 AAPL at zero cost basis
; This may not be desired for investment accounts
```

For investment accounts, prefer explicit transactions with proper cost basis.

## Implementation Notes

1. Track pad directives per account/currency
2. When processing balance, look for preceding pad
3. Compute difference and generate transaction if needed
4. Mark generated transaction with `P` flag
5. Include automatic metadata (lineno of pad directive)
