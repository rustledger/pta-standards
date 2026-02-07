# Close Directive

## Overview

The `close` directive marks an account as inactive, preventing further postings after the close date.

## Syntax

```ebnf
close = date WHITESPACE "close" WHITESPACE account
        (NEWLINE metadata)*
```

## Components

### Date

The date the account becomes inactive.

> **UNDEFINED**: Close date semantics (whether posting ON the close date is allowed) is pending clarification. See [issue-drafts/002-close-date-semantics.md](../../conformance/issue-drafts/002-close-date-semantics.md).

### Account

The account to close. MUST have been previously opened.

## Examples

### Basic Close

```beancount
2020-01-01 open Assets:OldChecking USD
; ... transactions ...
2024-06-30 close Assets:OldChecking
```

### With Metadata

```beancount
2024-06-30 close Assets:OldChecking
  reason: "Account migrated to new bank"
  closed-by: "online banking"
```

### Typical Account Lifecycle

```beancount
; Open the account
2020-01-01 open Assets:Savings:EmergencyFund USD

; Use it over time
2020-02-15 * "Deposit"
  Assets:Savings:EmergencyFund  1000 USD
  Assets:Checking

2021-06-01 * "Withdrawal"
  Assets:Savings:EmergencyFund  -500 USD
  Assets:Checking

; Close when no longer needed
2024-01-01 close Assets:Savings:EmergencyFund
```

## Balance at Close

> **UNDEFINED**: Whether closing an account with non-zero balance should produce an error is pending clarification. See [issue-drafts/003-close-with-balance.md](../../conformance/issue-drafts/003-close-with-balance.md).

```beancount
2024-01-01 open Assets:Checking USD

2024-06-01 * "Deposit"
  Assets:Checking  100 USD
  Income:Gift

; What should happen when closing with 100 USD balance?
2024-12-31 close Assets:Checking
```

### Best Practice: Zero Before Close

It is recommended to zero the account before closing for cleaner bookkeeping:

```beancount
; Transfer remaining balance
2024-12-30 * "Transfer to new account"
  Assets:Checking      -100 USD
  Assets:NewChecking    100 USD

; Now safe to close
2024-12-31 close Assets:Checking
```

## Validation

The following conditions produce errors:

| Condition | Error Type |
|-----------|------------|
| Account was never opened | `ValidationError` ("Unopened account ... is being closed") |
| Posting after close date | `ValidationError` ("Invalid reference to inactive account") |

### Error Examples

```beancount
; Close without open - ValidationError
2024-01-01 close Assets:NeverOpened

; Posting after close - ValidationError
2024-01-01 open Assets:Account
2024-06-30 close Assets:Account
2024-07-01 * "Late transaction"  ; ERROR: inactive account
  Assets:Account  100 USD
  Income:Salary
```

## Multiple Currencies

If an account holds multiple currencies, all must be zero to close without warning:

```beancount
2024-01-01 open Assets:MultiCurrency USD,EUR

2024-06-01 * "Deposit USD"
  Assets:MultiCurrency  100 USD
  Income:Gift

2024-06-02 * "Deposit EUR"
  Assets:MultiCurrency  50 EUR
  Income:Gift

; Must zero both currencies
2024-12-29 * "Zero USD"
  Assets:MultiCurrency  -100 USD
  Expenses:Transfer

2024-12-30 * "Zero EUR"
  Assets:MultiCurrency  -50 EUR
  Expenses:Transfer

2024-12-31 close Assets:MultiCurrency
```

## Closing with Lots

For accounts with cost basis tracking, all lots must be disposed:

```beancount
2024-01-01 open Assets:Brokerage USD,AAPL "FIFO"

2024-03-01 * "Buy"
  Assets:Brokerage  10 AAPL {150 USD}
  Assets:Cash

; Must sell all shares before closing
2024-12-15 * "Sell all"
  Assets:Brokerage  -10 AAPL {150 USD} @ 180 USD
  Assets:Cash
  Income:CapitalGains

2024-12-31 close Assets:Brokerage
```

## Reopening Accounts

Accounts **cannot** be reopened after being closed. A second `open` directive for a closed account produces a duplicate open error:

```beancount
2020-01-01 open Assets:Checking
2022-12-31 close Assets:Checking

; ERROR: Duplicate open directive
2024-01-01 open Assets:Checking
```

To continue using an account after closure, use a new account name instead.

## Implementation Notes

1. Track close date per account
2. Validate all postings against close date
3. Close date semantics (inclusive vs exclusive) is UNDEFINED - see issue drafts
4. Balance at close behavior is UNDEFINED - see issue drafts
