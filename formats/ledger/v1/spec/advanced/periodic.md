# Periodic Transactions Specification

This document specifies periodic (scheduled) transactions in Ledger.

## Overview

Periodic transactions define recurring entries for:
- Budget definitions
- Scheduled transactions
- Forecasting
- Cash flow projections

## Syntax

```
periodic_txn = "~" period [payee] newline posting+

period = period_expression
```

## Basic Periodic Transaction

### Monthly

```ledger
~ Monthly
    Expenses:Rent    $1500
    Assets:Checking
```

### With Description

```ledger
~ Monthly  Rent Payment
    Expenses:Rent    $1500
    Assets:Checking
```

## Period Expressions

### Simple Periods

| Expression | Meaning |
|------------|---------|
| `Daily` | Every day |
| `Weekly` | Every week |
| `Biweekly` | Every 2 weeks |
| `Monthly` | Every month |
| `Bimonthly` | Every 2 months |
| `Quarterly` | Every 3 months |
| `Yearly` | Every year |

### Day of Week

```ledger
~ Every Monday
    Income:Allowance    $50
    Assets:Wallet

~ Every Friday
    Expenses:Entertainment    $100
    Assets:Checking
```

### Day of Month

```ledger
~ Every 1st
    Expenses:Rent    $1500
    Assets:Checking

~ Every 15th
    Income:Salary    $3000
    Assets:Checking
```

### Specific Dates

```ledger
~ 2024/01/15
    Expenses:Insurance    $500
    Assets:Checking
```

### Range

```ledger
~ Monthly from 2024/01 to 2024/12
    Expenses:Rent    $1500
    Assets:Checking
```

## Budget Definitions

### Monthly Budget

```ledger
~ Monthly  Budget
    Expenses:Food           $500
    Expenses:Entertainment  $200
    Expenses:Transportation $300
    Expenses:Utilities      $150
    Assets:Checking
```

### Quarterly Budget

```ledger
~ Quarterly  Quarterly Review
    Expenses:Insurance    $300
    Expenses:Maintenance  $200
    Assets:Checking
```

### Annual Budget

```ledger
~ Yearly  Annual Expenses
    Expenses:Property-Tax    $5000
    Expenses:Insurance:Home  $1200
    Assets:Checking
```

## Forecasting

### Generate Forecast

```bash
ledger --forecast "d<[2024/12/31]" reg
```

### Example

```ledger
~ Monthly  Salary
    Assets:Checking    $5000
    Income:Salary

~ Monthly  Rent
    Expenses:Rent      $1500
    Assets:Checking

~ Weekly  Groceries
    Expenses:Food      $150
    Assets:Checking
```

Running forecast:
```bash
ledger --forecast "d<[2024/03/01]" reg ^Expenses
```

## Cash Flow Projection

### Income Schedule

```ledger
~ Every 1st  Salary
    Assets:Checking    $3000
    Income:Salary

~ Every 15th  Salary
    Assets:Checking    $3000
    Income:Salary
```

### Expense Schedule

```ledger
~ Every 1st  Rent
    Expenses:Rent       $1500
    Assets:Checking

~ Every 5th  Utilities
    Expenses:Utilities  $200
    Assets:Checking

~ Every 15th  Insurance
    Expenses:Insurance  $150
    Assets:Checking
```

## Conditional Periods

### Day of Week in Month

```ledger
~ Every 2nd Tuesday
    Expenses:Haircut    $30
    Assets:Cash
```

### Last Day of Month

```ledger
~ Every last day
    Expenses:Subscriptions    $50
    Assets:Checking
```

### Business Days

```ledger
~ Every weekday
    (Tracking:Workdays)    1
```

## Multiple Periods

### Biweekly Paycheck

```ledger
~ Biweekly from 2024/01/05
    Assets:Checking    $2000
    Income:Salary     $-2000
    (Taxes:Federal)    $400
    (Taxes:State)      $100
```

### Semi-Monthly

```ledger
~ Every 1st
    Assets:Checking    $2500
    Income:Salary

~ Every 15th
    Assets:Checking    $2500
    Income:Salary
```

## With Metadata

```ledger
~ Monthly  Rent Payment
    ; Landlord: ABC Properties
    ; Due: 1st of month
    Expenses:Housing:Rent    $1500
    Assets:Checking
```

## Budget vs Actual

### Define Budget

```ledger
~ Monthly  Food Budget
    Expenses:Food    $500
    Assets:Checking
```

### Compare

```bash
ledger --budget bal ^Expenses
```

Output:
```
              $-50  Expenses:Food    (50 remaining of $500 budget)
```

## Examples

### Personal Budget

```ledger
; ===== Income =====

~ Every 1st  Salary
    Assets:Checking    $5000
    Income:Salary

; ===== Fixed Expenses =====

~ Monthly  Housing
    Expenses:Rent        $1500
    Expenses:Utilities    $200
    Expenses:Internet     $80
    Assets:Checking

; ===== Variable Expenses =====

~ Monthly  Variable Budget
    Expenses:Food           $600
    Expenses:Entertainment  $200
    Expenses:Transportation $150
    Expenses:Personal       $100
    Assets:Checking

; ===== Savings =====

~ Monthly  Savings
    Assets:Savings:Emergency    $500
    Assets:Savings:Vacation     $200
    Assets:Checking
```

### Business Budget

```ledger
; ===== Revenue =====

~ Monthly  Expected Revenue
    Assets:Receivables    $10000
    Income:Sales

; ===== Payroll =====

~ Biweekly  Payroll
    Expenses:Salaries    $8000
    Expenses:Benefits    $2000
    Assets:Checking

; ===== Operating =====

~ Monthly  Operations
    Expenses:Office:Rent      $2000
    Expenses:Office:Supplies   $200
    Expenses:Software          $500
    Assets:Checking

; ===== Quarterly =====

~ Quarterly  Taxes
    Expenses:Taxes:Estimated    $5000
    Assets:Checking
```

### Year Planning

```ledger
; ===== Regular Monthly =====

~ Monthly
    Expenses:Rent           $1500
    Expenses:Utilities       $200
    Expenses:Food            $500
    Assets:Checking

; ===== Annual Events =====

~ 2024/01/15  Insurance Renewal
    Expenses:Insurance    $1200
    Assets:Checking

~ 2024/04/15  Tax Payment
    Expenses:Taxes    $3000
    Assets:Checking

~ 2024/07/01  Vacation
    Expenses:Travel    $2000
    Assets:Savings

~ 2024/12/25  Holiday Gifts
    Expenses:Gifts    $500
    Assets:Checking
```

## Interaction with Reports

### Budget Report

```bash
ledger --budget --monthly bal
```

### Forecast Register

```bash
ledger --forecast "d<[2024/06/30]" reg
```

### Pending Forecast

```bash
ledger --forecast-while "amount > 0" reg Assets:Checking
```

## Best Practices

1. **Separate file** - Keep periodic transactions in budget.ledger
2. **Document assumptions** - Note expected amounts and timing
3. **Review regularly** - Update for changes
4. **Use for planning** - Not just tracking
5. **Compare to actual** - Monthly budget reviews
6. **Include all expenses** - Don't forget annual/quarterly items

## See Also

- [Automated Transactions](automated.md)
- [Value Expressions](expressions.md)
- [Reporting Commands](../../README.md)
