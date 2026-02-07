# Effective Dates Specification

This document specifies effective (auxiliary) dates in Ledger.

## Overview

Effective dates provide a secondary date for transactions or postings:
- Distinguish transaction date from settlement date
- Track when expenses actually apply
- Handle credit card posting delays
- Support accrual accounting scenarios

## Syntax

### Transaction Level

```
date = primary_date ["=" effective_date]
```

### Posting Level

```
posting = account amount ["[" "=" effective_date "]"]
```

## Transaction Effective Date

### Basic Syntax

```ledger
2024/01/15=2024/01/20 Credit Card Purchase
    Expenses:Food    $50
    Liabilities:Credit-Card
```

- Primary date: 2024/01/15 (purchase date)
- Effective date: 2024/01/20 (statement date)

### Use Cases

#### Purchase vs Statement Date

```ledger
; Purchase made Jan 15, appears on Jan 20 statement
2024/01/15=2024/01/20 Store Purchase
    Expenses:Shopping    $100
    Liabilities:Credit-Card
```

#### Payroll Accrual

```ledger
; Work done in January, paid in February
2024/01/31=2024/02/05 January Salary
    Assets:Checking     $5000
    Income:Salary
```

#### Invoice Dating

```ledger
; Invoice dated Jan 10, paid Jan 25
2024/01/10=2024/01/25 Vendor Invoice #123
    Expenses:Services    $500
    Assets:Checking
```

## Posting Effective Date

### Basic Syntax

```ledger
2024/01/15 Credit Card Payment
    Assets:Checking         $-500 [=2024/01/18]
    Liabilities:Credit-Card  $500
```

The checking debit has effective date Jan 18 (when bank processes).

### Different Dates Per Posting

```ledger
2024/01/15 Settlement
    Assets:Brokerage     10 AAPL [=2024/01/17]  ; T+2 settlement
    Assets:Cash         $-1500 [=2024/01/15]    ; Cash moves immediately
```

### Complex Example

```ledger
2024/01/15 Credit Card Statement Payment
    ; Payment initiated Jan 15
    Assets:Checking        $-1000 [=2024/01/17]  ; Bank processes Jan 17
    ; Credit applied immediately
    Liabilities:Visa        $1000               ; Uses transaction date
```

## Reporting with Dates

### Primary Date (Default)

```bash
ledger -p "jan 2024" reg
```

Uses primary date for filtering.

### Effective Date

```bash
ledger --effective -p "jan 2024" reg
```

Uses effective date for filtering.

### Both Dates

```bash
ledger --aux-date reg
```

Shows both dates in output.

## Common Patterns

### Credit Card Workflow

```ledger
; Purchase - use effective for statement period
2024/01/05=2024/01/31 Gas Station
    Expenses:Transportation:Gas    $45
    Liabilities:Credit-Card

2024/01/15=2024/01/31 Restaurant
    Expenses:Food:Dining    $75
    Liabilities:Credit-Card

; Statement closes Jan 31
; Due Feb 15

; Payment
2024/02/10=2024/02/12 Credit Card Payment
    Assets:Checking          $-120
    Liabilities:Credit-Card   $120
```

### Accrual Accounting

```ledger
; Record expense when incurred
2024/01/31 January Rent
    Expenses:Rent           $1500
    Liabilities:Accrued

; Pay when due
2024/02/01=2024/01/31 Pay January Rent
    Liabilities:Accrued      $1500
    Assets:Checking         $-1500
```

### Reimbursement Tracking

```ledger
; Expense incurred
2024/01/15 Business Dinner
    Expenses:Travel:Meals       $100
    Assets:Personal-Card       $-100

; Reimbursement received (effective = original expense date)
2024/02/01=2024/01/15 Reimbursement
    Assets:Checking             $100
    Income:Reimbursement       $-100
```

### Stock Settlement (T+2)

```ledger
; Trade date
2024/01/15 Buy AAPL
    Assets:Brokerage:Pending    10 AAPL {$150}
    Assets:Brokerage:Cash      $-1500

; Settlement date (T+2)
2024/01/17=2024/01/15 Settlement
    Assets:Brokerage:Settled    10 AAPL {$150}
    Assets:Brokerage:Pending   -10 AAPL {$150}
```

## Date Filtering

### By Primary Date

```bash
# Transactions dated in January
ledger -b 2024/01/01 -e 2024/02/01 reg
```

### By Effective Date

```bash
# Transactions effective in January
ledger --effective -b 2024/01/01 -e 2024/02/01 reg
```

### Period Reporting

```bash
# Monthly report by effective date
ledger --effective --monthly bal
```

## Interaction with Other Features

### Balance Assertions

Balance assertions use the primary date:

```ledger
2024/01/15=2024/01/20 Deposit
    Assets:Checking    $500 = $1500
    Income:Interest
```

### Automated Transactions

Automated rules match against primary date:

```ledger
= expr date >= [2024/01/01]
    (Year:2024)  amount
```

### Periodic Transactions

Generated with primary date only:

```ledger
~ Monthly  Rent
    Expenses:Rent    $1500
    Assets:Checking
```

## Examples

### Monthly Statement Reconciliation

```ledger
; ===== January Statement Period =====

; Purchases during statement period
2024/01/02=2024/01/31 Amazon
    Expenses:Shopping    $75
    Liabilities:Visa

2024/01/15=2024/01/31 Grocery
    Expenses:Food        $120
    Liabilities:Visa

2024/01/28=2024/01/31 Gas
    Expenses:Transportation    $50
    Liabilities:Visa

; Statement balance assertion
2024/01/31 Statement Close
    Liabilities:Visa    $0 = $-245
    ; Balance: $245 owed

; Payment (effective when bank processes)
2024/02/10=2024/02/12 Pay Visa
    Assets:Checking      $-245
    Liabilities:Visa      $245
```

### Payroll with Withholding

```ledger
; Pay period ends Jan 15, paycheck Jan 20
2024/01/15=2024/01/20 Paycheck
    Assets:Checking          $3500
    Expenses:Taxes:Federal   $800
    Expenses:Taxes:State     $200
    Expenses:Taxes:FICA      $300
    Expenses:Benefits        $200
    Income:Salary           $-5000
```

### Multi-Currency Settlement

```ledger
; Trade date in EUR
2024/01/15 Buy EUR
    Assets:EUR    1000 EUR @ $1.10
    Assets:USD   $-1100

; Settlement with effective date
2024/01/17=2024/01/15 EUR Settlement
    ; EUR settles T+2
    Assets:EUR:Settled     1000 EUR
    Assets:EUR:Pending    -1000 EUR
```

## Best Practices

1. **Consistent usage** - Apply effective dates uniformly
2. **Document meaning** - Note what each date represents
3. **Credit card statements** - Use for statement period alignment
4. **Reconciliation** - Match bank's posting dates
5. **Report choice** - Pick primary or effective based on need
6. **Simple when possible** - Only use when dates differ

## See Also

- [Transaction Directive](../directives/transaction.md)
- [Posting Specification](../posting.md)
- [Balance Validation](../validation/balance.md)
