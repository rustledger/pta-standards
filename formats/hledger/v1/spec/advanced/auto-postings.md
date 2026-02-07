# hledger Auto Postings Specification

This document specifies automatic posting rules in hledger.

## Overview

Auto postings generate additional postings based on matching rules:
- Budget tracking
- Tax calculations
- Automated allocations

## Syntax

```hledger
= QUERY
    ACCOUNT    AMOUNT
```

## Basic Auto Posting

```hledger
= expenses:food
    (budget:food)    *-1

2024-01-15 Grocery
    expenses:food    $50
    assets:cash
; Auto-adds: (budget:food) $-50
```

## Query Patterns

### Account Match

```hledger
= expenses:food
    (budget:food)    *-1
```

### Description Match

```hledger
= desc:grocery
    (tracking:groceries)    *1
```

### Multiple Conditions

```hledger
= expenses: amt:>100
    (review:large)    *1
```

## Amount Expressions

### Multiplier

```hledger
= expenses:food
    (budget:food)    *-1     ; Same amount, negated
    (stats:count)    *0      ; Zero
```

### Fraction

```hledger
= income:salary
    (taxes:federal)    *0.22   ; 22%
    (taxes:state)      *0.05   ; 5%
```

### Fixed Amount

```hledger
= expenses:
    (tracking:expense-count)    1
```

## Common Use Cases

### Budget Tracking

```hledger
= expenses:food
    (budget:food)    *-1

= expenses:entertainment
    (budget:entertainment)    *-1
```

### Tax Estimation

```hledger
= income:salary
    (taxes:federal)    *0.22
    (taxes:state)      *0.05
    (taxes:fica)       *0.0765
```

### Savings Allocation

```hledger
= income:salary
    (savings:emergency)    *0.10
    (savings:vacation)     *0.05
```

### Category Tracking

```hledger
= expenses:
    (tracking:all-expenses)    *1
```

## Virtual Postings

### Unbalanced (Parentheses)

Most common for tracking:

```hledger
= expenses:food
    (budget:food)    *-1
```

### Balanced (Brackets)

For envelope budgeting:

```hledger
= expenses:food
    [budget:food:spent]        *1
    [budget:food:available]    *-1
```

## Multiple Rules

Rules apply in order:

```hledger
= expenses:food
    (budget:food)    *-1

= expenses:
    (tracking:expenses)    *1

2024-01-15 Grocery
    expenses:food    $50
    assets:cash
; Matches both rules
; (budget:food) $-50
; (tracking:expenses) $50
```

## Conditional Rules

### Amount-Based

```hledger
= expenses: amt:>500
    (review:large-expense)    *1
```

### Tag-Based

```hledger
= tag:reimbursable
    (receivables:pending)    *1
```

## Examples

### Complete Budget System

```hledger
; Budget auto-postings
= expenses:food
    [budget:food:spent]        *1
    [budget:food:available]    *-1

= expenses:entertainment
    [budget:fun:spent]         *1
    [budget:fun:available]     *-1

; Monthly budget allocation
2024-01-01 Budget Setup
    [budget:food:available]    $500
    [budget:fun:available]     $200
    [equity:budget]

; Transaction with auto-postings
2024-01-15 Grocery Store
    expenses:food    $100
    assets:checking
; Auto-adds:
;   [budget:food:spent]        $100
;   [budget:food:available]    $-100
```

### Tax Withholding

```hledger
= income:salary
    (taxes:federal:estimate)    *0.22
    (taxes:state:estimate)      *0.05
    (taxes:fica:estimate)       *0.0765

2024-01-15 Paycheck
    assets:checking    $3000
    income:salary
```

### Project Allocation

```hledger
= tag:project
    (projects:tracked)    *1

2024-01-15 Contractor
    ; project: Alpha
    expenses:contractors    $1000
    assets:checking
```

## Reporting

### View Auto Postings

```bash
hledger print --auto
```

### Ignore Auto Postings

```bash
hledger bal --no-auto
```

## Best Practices

1. **Document rules** - Comment purpose
2. **Use virtual postings** - Don't affect real balance
3. **Test incrementally** - Add one rule at a time
4. **Review regularly** - Check auto-generated data
5. **Order matters** - More specific rules first

## See Also

- [Forecasting](forecasting.md)
- [Balance Assertions](assertions.md)
- [Ledger Automated Transactions](../../../../ledger/v1/spec/advanced/automated.md)
