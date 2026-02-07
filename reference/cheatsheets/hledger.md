# hledger Cheatsheet

Quick reference for hledger syntax.

## Basic Transaction

```hledger
2024-01-15 * Payee | Description
    Expenses:Food:Groceries    $50.00
    Assets:Checking
```

## Date Formats

```
2024-01-15    ; ISO format (preferred)
2024/01/15    ; Slash-separated
2024.01.15    ; Dot-separated
```

## Transaction Flags

| Flag | Meaning |
|------|---------|
| `*` | Cleared |
| `!` | Pending |
| (none) | Uncleared |

## Amount Formats

```hledger
$100.00           ; Currency prefix
100.00 USD        ; Currency suffix
1,234.56 EUR      ; Thousands separator
-$50.00           ; Negative
```

## Postings

```hledger
2024-01-15 * Transaction
    Account:Name           $100.00    ; Amount
    Account:Name          $-100.00    ; Negative
    Account:Name                      ; Elided (auto-balanced)
    Account:Name           $0 = $500  ; Balance assertion
```

## Account Directive

```hledger
account Assets:Checking
    alias checking
    ; type: A
```

## Commodity Directive

```hledger
commodity $1,000.00
commodity 1.000,00 EUR
```

## Decimal Mark

```hledger
decimal-mark ,
; Allows 1.000,00 format
```

## Price Directive

```hledger
P 2024-01-15 AAPL $185.00
P 2024-01-15 EUR $1.08
```

## Include

```hledger
include accounts.journal
include ~/finance/*.journal
```

## Comments

```hledger
; Line comment
# Also a comment

2024-01-15 * Payee
    ; Posting comment
    Expenses:Food    $10
```

## Tags

```hledger
2024-01-15 * Payee
    ; project:work, client:acme
    Expenses:Travel    $100
```

Alternative syntax:
```hledger
2024-01-15 * Payee  ; project:work
    Expenses:Travel    $100
```

## Metadata

```hledger
2024-01-15 * Payee
    ; key: value
    ; invoice: INV-001
    Expenses:Services    $500
```

## Balance Assertions

```hledger
; Single commodity
Assets:Checking    $0 = $1,000

; Total balance (all commodities)
Assets:Checking    $0 == $1,000

; Including subaccounts
Assets    $0 =* $5,000

; Total including subaccounts
Assets    $0 ==* $5,000
```

## Virtual Postings

```hledger
2024-01-15 * Payee
    Expenses:Food           $50.00
    Assets:Checking
    (Budget:Food)           $50.00    ; Unbalanced virtual
    [Budget:Spent]          $50.00    ; Balanced virtual
    [Budget:Available]     $-50.00
```

## Auto Postings

```hledger
= /Expenses:Food/
    (Budget:Food)    *1
    (Budget:Total)   *-1
```

## Periodic Transactions

```hledger
~ monthly from 2024-01
    Expenses:Rent    $1,500.00
    Assets:Checking

~ every 2 weeks
    Income:Salary    $2,500.00
    Assets:Checking
```

## Forecasting

```hledger
; With --forecast flag
~ monthly from 2024-01 to 2024-12
    Expenses:Subscriptions    $10
    Assets:Checking
```

## Lot/Cost Basis

```hledger
2024-01-15 * Buy stock
    Assets:Brokerage    10 AAPL @ $185.00
    Assets:Checking    $-1,850.00

2024-03-15 * Sell stock
    Assets:Brokerage   -10 AAPL @ $185.00
    Assets:Checking    $2,000.00
    Income:Gains      $-150.00
```

## Secondary/Effective Dates

```hledger
2024-01-15=2024-01-20 * Payee
    ; Posted: 2024-01-15
    ; Effective: 2024-01-20
    Expenses:Food    $50.00
    Assets:Checking
```

## Timedot Format

```timedot
2024-01-15
project1    2.5
project2    1.25
break       .5
```

## Common Commands

```bash
# Balance report
hledger balance
hledger bal assets liabilities

# Register
hledger register
hledger reg expenses

# Income statement
hledger incomestatement
hledger is

# Balance sheet
hledger balancesheet
hledger bs

# Check journal
hledger check

# With specific file
hledger -f file.journal balance

# Date range
hledger -b 2024-01-01 -e 2024-02-01 balance

# Monthly
hledger balance -M

# Output formats
hledger balance -O csv
hledger balance -O json
```

## Command Flags

| Flag | Description |
|------|-------------|
| `-f FILE` | Use specific file |
| `-b DATE` | Begin date |
| `-e DATE` | End date |
| `-p PERIOD` | Period expression |
| `-C` | Only cleared |
| `-P` | Only pending |
| `-U` | Only uncleared |
| `-S FIELD` | Sort by field |
| `--flat` | Flat account list |
| `-M` | Monthly |
| `-Q` | Quarterly |
| `-Y` | Yearly |
| `-O FORMAT` | Output format |
| `--forecast` | Include forecast |

## Period Expressions

```bash
hledger -p "monthly"
hledger -p "2024"
hledger -p "2024Q1"
hledger -p "jan-mar"
hledger -p "last month"
hledger -p "this year"
```

## See Also

- [Full hledger Manual](https://hledger.org/hledger.html)
- [Ledger Cheatsheet](ledger.md)
- [Beancount Cheatsheet](beancount.md)
