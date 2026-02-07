# hledger Forecasting Specification

This document specifies forecasting and periodic transactions in hledger.

## Overview

Forecasting projects future transactions:
- Cash flow prediction
- Budget planning
- Recurring transactions

## Periodic Transactions

### Syntax

```hledger
~ PERIOD [DESCRIPTION]
    POSTING
    POSTING
```

### Example

```hledger
~ monthly rent
    expenses:rent    $1500
    assets:checking
```

## Period Expressions

### Simple Periods

| Expression | Meaning |
|------------|---------|
| `daily` | Every day |
| `weekly` | Every week |
| `biweekly` | Every 2 weeks |
| `monthly` | Every month |
| `quarterly` | Every 3 months |
| `yearly` | Every year |

### Day of Week

```hledger
~ every monday
~ every friday
~ every 2nd tuesday
```

### Day of Month

```hledger
~ every 1st
~ every 15th
~ every last day
```

### Date Range

```hledger
~ monthly from 2024-01 to 2024-12
~ weekly from 2024-01-01
```

## Generating Forecasts

### Command

```bash
hledger bal --forecast
hledger reg --forecast
```

### With Date Range

```bash
hledger bal --forecast -e 2024-12-31
```

### Forecast Only

```bash
hledger reg --forecast tag:generated
```

## Common Patterns

### Monthly Bills

```hledger
~ monthly from 2024-01  rent
    expenses:housing:rent    $1500
    assets:bank:checking

~ monthly from 2024-01  utilities
    expenses:housing:utilities    $200
    assets:bank:checking

~ monthly from 2024-01  internet
    expenses:housing:internet    $80
    assets:bank:checking
```

### Biweekly Income

```hledger
~ biweekly from 2024-01-05  paycheck
    assets:bank:checking    $2500
    income:salary          $-3000
    expenses:taxes:federal   $400
    expenses:taxes:state     $100
```

### Annual Expenses

```hledger
~ yearly from 2024-04-15  property tax
    expenses:taxes:property    $5000
    assets:bank:checking

~ yearly from 2024-06-01  insurance
    expenses:insurance:home    $1200
    assets:bank:checking
```

## Budget Definitions

### Monthly Budget

```hledger
~ monthly  budget
    expenses:food           $600
    expenses:entertainment  $200
    expenses:transportation $150
    expenses:personal       $100
    assets:budget
```

### Using Budget

```bash
hledger bal --budget
```

## Cash Flow Projection

### Setup

```hledger
; Income
~ biweekly from 2024-01-05  salary
    assets:checking    $2500
    income:salary

; Fixed expenses
~ monthly from 2024-01-01  rent
    expenses:rent    $1500
    assets:checking

~ monthly from 2024-01-05  utilities
    expenses:utilities    $200
    assets:checking

; Variable estimates
~ weekly  groceries estimate
    expenses:food    $150
    assets:checking
```

### Projection

```bash
hledger reg assets:checking --forecast -e 2024-06-30
```

## Combining with Actuals

Forecasts fill gaps between actual transactions:

```hledger
; Actual transaction
2024-01-05 Rent Payment
    expenses:rent    $1500
    assets:checking

; Forecast for future
~ monthly from 2024-02  rent
    expenses:rent    $1500
    assets:checking
```

## Forecast Tags

Generated transactions include:

```hledger
; _generated-transaction:
```

### Filter Generated

```bash
hledger reg tag:_generated
hledger reg not:tag:_generated  ; Actuals only
```

## Examples

### Personal Budget

```hledger
; ===== Income =====

~ biweekly from 2024-01-05  salary
    assets:checking    $3500
    income:salary     $-4500
    expenses:taxes     $1000

; ===== Fixed Expenses =====

~ monthly from 2024-01-01  housing
    expenses:rent        $1800
    expenses:utilities    $150
    expenses:internet     $80
    assets:checking

; ===== Variable Expenses =====

~ weekly  groceries
    expenses:food:groceries    $175
    assets:checking

~ monthly  dining out
    expenses:food:restaurants    $200
    assets:checking

; ===== Savings =====

~ monthly from 2024-01-01  savings
    assets:savings:emergency    $500
    assets:checking
```

### Business Planning

```hledger
; Revenue projection
~ monthly  expected revenue
    assets:receivables    $10000
    income:sales

; Payroll
~ biweekly  payroll
    expenses:salaries    $8000
    expenses:benefits    $2000
    assets:checking

; Operations
~ monthly  office
    expenses:office:rent      $2000
    expenses:office:supplies   $200
    assets:checking

; Quarterly tax
~ quarterly from 2024-03-31  estimated tax
    expenses:taxes:federal    $5000
    assets:checking
```

## Reporting

### Budget vs Actual

```bash
hledger bal --budget -M
```

### Forecast Balance

```bash
hledger bal --forecast -e 2024-12-31 assets
```

### Cash Runway

```bash
hledger reg assets:checking --forecast -e 2025-01-01
```

## Best Practices

1. **Separate file** - Keep forecasts in forecast.journal
2. **Conservative estimates** - Don't overestimate income
3. **Review regularly** - Update as actuals come in
4. **Date ranges** - Set end dates for temporary items
5. **Document assumptions** - Note estimation basis

## See Also

- [Auto Postings](auto-postings.md)
- [Balance Assertions](assertions.md)
