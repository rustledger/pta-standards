# Automated Transactions Specification

This document specifies automated transaction rules in Ledger.

## Overview

Automated transactions generate postings based on pattern matching. They enable:
- Automatic tax calculations
- Budget tracking
- Allocation rules
- Classification automation

## Syntax

```
automated_txn = "=" query newline posting+

query = regex | expression
```

## Basic Automated Transaction

### Pattern Matching

```ledger
= /Grocery/
    (Budget:Food)  -1

2024/01/15 Whole Foods Grocery
    Expenses:Food    $100
    Assets:Checking
    ; Auto-adds: (Budget:Food) $-100
```

### Result

The transaction becomes:

```ledger
2024/01/15 Whole Foods Grocery
    Expenses:Food      $100
    Assets:Checking   $-100
    (Budget:Food)     $-100    ; Auto-generated
```

## Query Types

### Regex Pattern

Match payee/narration:

```ledger
= /Grocery/
    (Budget:Food)  -1

= /^Restaurant/
    (Budget:Dining)  -1
```

### Account Pattern

Match account names:

```ledger
= /Expenses:Food/
    (Budget:Food)  -1
```

### Expression Query

```ledger
= expr account =~ /Expenses/
    (Tracking:Expenses)  amount

= expr amount > 100
    (Tracking:Large)  1
```

## Amount Expressions

### Multiplier

```ledger
= /Expenses:Food/
    (Budget:Food)  -1    ; Same amount, negated
    (Stats:Count)   1    ; Literal 1
```

### Fraction

```ledger
= /Income:Salary/
    (Taxes:Federal)    0.22    ; 22% of amount
    (Taxes:State)      0.05    ; 5% of amount
    (Savings:401k)     0.10    ; 10% of amount
```

### Expression

```ledger
= expr account =~ /Income/
    (Taxes:Estimate)  (amount * 0.25)
```

## Common Use Cases

### Budget Tracking

```ledger
= /Expenses:Food/
    (Budget:Food)  -1

= /Expenses:Entertainment/
    (Budget:Entertainment)  -1

= /Expenses:Transportation/
    (Budget:Transportation)  -1
```

### Tax Estimation

```ledger
= /Income:Salary/
    (Taxes:Federal:Estimate)     (amount * 0.22)
    (Taxes:State:Estimate)       (amount * 0.05)
    (Taxes:FICA:Estimate)        (amount * 0.0765)
```

### Savings Automation

```ledger
= /Income:Salary/
    [Savings:Emergency]    (amount * 0.10)
    [Assets:Checking]      (amount * -0.10)
```

### Expense Classification

```ledger
= /Amazon/
    ; :online-shopping:

= /Whole Foods|Trader Joe|Safeway/
    ; :groceries:
```

### Reimbursement Tracking

```ledger
= expr has_tag("reimbursable")
    (Receivables:Reimbursements)  amount
```

## Multiple Rules

Rules are applied in order:

```ledger
= /Expenses:Food/
    (Budget:Food)  -1

= /Expenses/
    (Tracking:Total-Expenses)  1

2024/01/15 Grocery
    Expenses:Food    $50
    Assets:Checking
    ; Both rules match:
    ; (Budget:Food)  $-50
    ; (Tracking:Total-Expenses)  $50
```

## Conditional Application

### Tag-Based

```ledger
= expr has_tag("business")
    (Tracking:Business)  amount

= expr not has_tag("business")
    (Tracking:Personal)  amount
```

### Amount-Based

```ledger
= expr amount > 500
    ; :large-expense:
    (Review:Large)  amount
```

### Account-Based

```ledger
= expr account =~ /^Expenses/ and amount > 100
    (Budget:Discretionary)  -1
```

## Virtual Postings

### Unbalanced (Parentheses)

Most common for tracking:

```ledger
= /Expenses/
    (Tracking:All-Expenses)  amount
```

### Balanced (Brackets)

For budget transfers:

```ledger
= /Expenses:Food/
    [Budget:Food:Spent]       amount
    [Budget:Food:Available]  -amount
```

## Interaction with Real Postings

### Original Transaction

```ledger
2024/01/15 Grocery Store
    Expenses:Food:Groceries    $150
    Assets:Checking           $-150
```

### With Automation

```ledger
= /Expenses:Food/
    (Budget:Food)         -1
    (Stats:Transactions)   1

; Result:
2024/01/15 Grocery Store
    Expenses:Food:Groceries    $150
    Assets:Checking           $-150
    (Budget:Food)             $-150    ; Auto
    (Stats:Transactions)          1    ; Auto
```

## Expression Functions

### Available in Queries

| Function | Description |
|----------|-------------|
| `account` | Current account name |
| `amount` | Posting amount |
| `total` | Transaction total |
| `has_tag(name)` | Check for tag |
| `tag(name)` | Get tag value |
| `date` | Transaction date |
| `payee` | Transaction payee |

### Examples

```ledger
= expr account =~ /^Expenses/ and amount > $100
    (Large:Expenses)  amount

= expr has_tag("project") and tag("project") == "alpha"
    (Projects:Alpha)  amount

= expr date >= [2024/01/01]
    (Year:2024)  amount
```

## Execution Order

1. Parse original transaction
2. Balance original transaction
3. Find matching automated rules
4. Generate automated postings
5. Add to transaction (don't rebalance)

## Disabling Automation

### Per-Transaction

```ledger
2024/01/15 Special Case  ; noauto
    Expenses:Food    $50
    Assets:Checking
```

### Command Line

```bash
ledger --no-auto bal
```

## Examples

### Complete Budget System

```ledger
; ===== Budget Rules =====

= /Expenses:Food/
    [Budget:Food:Spent]       amount
    [Budget:Food:Available]  -amount

= /Expenses:Entertainment/
    [Budget:Fun:Spent]        amount
    [Budget:Fun:Available]   -amount

= /Expenses:Transportation/
    [Budget:Transport:Spent]      amount
    [Budget:Transport:Available] -amount

; ===== Monthly Budget =====

2024/01/01 Set January Budget
    [Budget:Food:Available]       $500
    [Budget:Fun:Available]        $200
    [Budget:Transport:Available]  $300
    [Equity:Budget]

; ===== Transactions =====

2024/01/15 Grocery Store
    Expenses:Food    $150
    Assets:Checking
    ; Auto: [Budget:Food:Spent] $150
    ; Auto: [Budget:Food:Available] $-150
```

### Tax Withholding Simulation

```ledger
= /Income:Salary/
    (Taxes:Federal:Withheld)   (amount * 0.22)
    (Taxes:State:Withheld)     (amount * 0.05)
    (Taxes:FICA:Withheld)      (amount * 0.0765)
    (Net:Income)               (amount * 0.6735)

2024/01/15 Paycheck
    Assets:Checking    $3000
    Income:Salary
```

### Project Allocation

```ledger
= expr has_tag("project")
    (Projects)  amount

2024/01/15 Contractor
    ; :project-alpha:
    Expenses:Contractors    $1000
    Assets:Checking
    ; Auto: (Projects) $1000
```

## Best Practices

1. **Document rules** - Comment automation purpose
2. **Test incrementally** - Add one rule at a time
3. **Use virtual postings** - Keep real accounts clean
4. **Order matters** - More specific rules first
5. **Review auto-postings** - Check reports regularly
6. **Don't over-automate** - Keep it maintainable

## See Also

- [Periodic Transactions](periodic.md)
- [Value Expressions](expressions.md)
- [Virtual Postings](virtual.md)
