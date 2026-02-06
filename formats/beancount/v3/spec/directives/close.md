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

The date the account becomes inactive. Postings on or after this date will produce validation errors.

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

By default, closing an account with a non-zero balance produces a warning:

```beancount
2024-01-01 open Assets:Checking USD

2024-06-01 * "Deposit"
  Assets:Checking  100 USD
  Income:Gift

; Warning: closing with 100 USD balance
2024-12-31 close Assets:Checking
```

### Zeroing Before Close

Best practice is to zero the account before closing:

```beancount
; Transfer remaining balance
2024-12-30 * "Transfer to new account"
  Assets:Checking      -100 USD
  Assets:NewChecking    100 USD

; Now safe to close
2024-12-31 close Assets:Checking
```

### Configuration

The warning behavior can be configured:

```beancount
; Treat non-zero close as error (strict mode)
option "close_non_zero" "error"

; Allow non-zero close silently
option "close_non_zero" "ignore"
```

## Validation

| Error | Condition |
|-------|-----------|
| E1001 | Account was never opened |
| E1003 | Posting after close date |
| E1004 | Account has non-zero balance (warning by default) |

### Error Examples

```beancount
; E1001: Close without open
2024-01-01 close Assets:NeverOpened

; E1003: Posting after close
2024-01-01 open Assets:Account
2024-06-30 close Assets:Account
2024-07-01 * "Late transaction"  ; ERROR
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

An account can be reopened after being closed:

```beancount
2020-01-01 open Assets:Checking
2022-12-31 close Assets:Checking

; Reopen the same account
2024-01-01 open Assets:Checking
```

This creates a new lifecycle for the account. Transactions between the close and reopen are still invalid.

## Implementation Notes

1. Track close date per account
2. Validate all postings against close date
3. Compute balance at close for warning
4. Allow reopen (new open after close)
5. Close date is exclusive (posting ON close date is invalid)
