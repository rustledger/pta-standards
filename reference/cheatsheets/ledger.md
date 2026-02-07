# Ledger Cheatsheet

Quick reference for Ledger CLI syntax.

## Basic Transaction

```ledger
2024/01/15 * Payee description
    Expenses:Food:Groceries    $50.00
    Assets:Checking
```

## Date Formats

```
2024/01/15    ; Slash-separated
2024-01-15    ; ISO format
2024.01.15    ; Dot-separated
```

## Transaction Flags

| Flag | Meaning |
|------|---------|
| `*` | Cleared |
| `!` | Pending |
| (none) | Uncleared |

## Amount Formats

```ledger
$100.00           ; Currency prefix
100.00 USD        ; Currency suffix
1,234.56 EUR      ; Thousands separator
-$50.00           ; Negative
```

## Postings

```ledger
2024/01/15 * Transaction
    Account:Name           $100.00    ; Amount
    Account:Name          $-100.00    ; Negative
    Account:Name                      ; Elided (auto-balanced)
    Account:Name           $0 = $500  ; Balance assertion
```

## Account Directives

```ledger
account Assets:Checking
    alias checking
    note My main account
    assert amount >= 0
    default
```

## Commodity Directive

```ledger
commodity $
    format $1,000.00
    nomarket
    default
```

## Price Directive

```ledger
P 2024/01/15 AAPL $185.00
P 2024/01/15 EUR $1.08
```

## Include

```ledger
include accounts.ledger
include ~/ledger/*.ledger
```

## Comments

```ledger
; Line comment
# Also a comment
* Org-mode header

2024/01/15 * Payee
    ; Posting comment
    Expenses:Food    $10
```

## Tags

```ledger
2024/01/15 * Payee
    ; :tag1:tag2:tag3:
    Expenses:Food    $10
```

## Metadata

```ledger
2024/01/15 * Payee
    ; key: value
    ; UUID: 12345
    Expenses:Food    $10
```

## Virtual Postings

```ledger
2024/01/15 * Payee
    Expenses:Food           $50.00
    Assets:Checking
    (Budget:Food)           $50.00    ; Unbalanced virtual
    [Budget:Spent]          $50.00    ; Balanced virtual
    [Budget:Available]     $-50.00
```

## Automated Transactions

```ledger
= /Expenses:Food/
    (Budget:Food)    (amount)
    (Budget:Total)   (-amount)

= expr payee =~ /Grocery/
    Expenses:Tax    (amount * 0.08)
```

## Periodic Transactions

```ledger
~ Monthly
    Expenses:Rent    $1,500.00
    Assets:Checking

~ Every 2 weeks
    Income:Salary    $2,500.00
    Assets:Checking
```

## Lot/Cost Basis

```ledger
2024/01/15 * Buy stock
    Assets:Brokerage    10 AAPL {$185.00}
    Assets:Checking    $-1,850.00

2024/03/15 * Sell stock
    Assets:Brokerage   -10 AAPL {$185.00} @ $200.00
    Assets:Checking    $2,000.00
    Income:Gains      $-150.00
```

## Effective Dates

```ledger
2024/01/15=2024/01/20 * Payee
    ; Primary date: 2024/01/15
    ; Effective date: 2024/01/20
    Expenses:Food    $50.00
    Assets:Checking
```

## Expressions

```ledger
2024/01/15 * Payee
    Expenses:Food    ($100 * 0.5)
    Assets:Checking

= expr account =~ /Expenses/ and amount > 100
    Liabilities:Tax    (amount * 0.1)
```

## Balance Assertions

```ledger
2024/01/15 * Payee
    Assets:Checking    $0 = $1,000.00
```

## Common Commands

```bash
# Balance report
ledger balance
ledger bal Assets Liabilities

# Register
ledger register
ledger reg Expenses

# Statistics
ledger stats

# Specific file
ledger -f file.ledger balance

# Date range
ledger -b 2024/01/01 -e 2024/02/01 balance

# Clear status
ledger cleared
```

## Command Flags

| Flag | Description |
|------|-------------|
| `-f FILE` | Use specific file |
| `-b DATE` | Begin date |
| `-e DATE` | End date |
| `-p PERIOD` | Period expression |
| `--cleared` | Only cleared |
| `--pending` | Only pending |
| `--uncleared` | Only uncleared |
| `-S EXPR` | Sort by expression |
| `--flat` | Flat account list |
| `-M` | Monthly |
| `-Y` | Yearly |

## See Also

- [Full Ledger Manual](https://ledger-cli.org/doc/ledger3.html)
- [hledger Cheatsheet](hledger.md)
- [Beancount Cheatsheet](beancount.md)
