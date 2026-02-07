# Virtual Postings Specification

This document specifies virtual posting behavior in Ledger.

## Overview

Virtual postings are special postings that:
- Track information without affecting real balances
- Enable budget tracking
- Support envelope budgeting
- Allow auxiliary calculations

## Types of Virtual Postings

### Unbalanced Virtual (Parentheses)

```ledger
(Account:Name)    amount
```

- Do NOT need to balance
- Used for tracking and notes
- Excluded from real balance checks

### Balanced Virtual (Brackets)

```ledger
[Account:Name]    amount
```

- MUST balance among themselves
- Used for envelope budgeting
- Separate balance check from real postings

## Unbalanced Virtual

### Basic Syntax

```ledger
2024/01/15 Expense
    Expenses:Food       $50
    Assets:Checking    $-50
    (Budget:Food)      $-50    ; Tracks budget usage
```

### No Balance Requirement

```ledger
2024/01/15 Track Something
    Expenses:Food       $50
    Assets:Checking    $-50
    (Tracking:Count)     1     ; Just counts, no balance needed
```

### Common Uses

#### Budget Tracking

```ledger
2024/01/15 Grocery
    Expenses:Food       $100
    Assets:Checking    $-100
    (Budget:Food)      $-100   ; Decrements food budget
```

#### Counting

```ledger
2024/01/15 Coffee
    Expenses:Food:Coffee    $5
    Assets:Wallet          $-5
    (Stats:Coffees)          1   ; Count coffee purchases
```

#### Parallel Tracking

```ledger
2024/01/15 Business Lunch
    Expenses:Meals      $75
    Assets:Card        $-75
    (Reimbursable)      $75   ; Track for reimbursement
```

## Balanced Virtual

### Basic Syntax

```ledger
2024/01/15 Budget Transfer
    [Budget:Food]        $100
    [Budget:Available]  $-100
    ; Must sum to zero among brackets
```

### Balance Requirement

Balanced virtual postings form their own group:

```ledger
2024/01/15 Complex Transaction
    ; Real postings - must balance
    Expenses:Food       $50
    Assets:Checking    $-50

    ; Balanced virtual - must balance separately
    [Budget:Food:Spent]       $50
    [Budget:Food:Available]  $-50

    ; Unbalanced virtual - no requirement
    (Stats:Transactions)       1
```

### Envelope Budgeting

```ledger
; Allocate budget at start of month
2024/01/01 Monthly Budget Allocation
    [Budget:Food:Available]        $500
    [Budget:Entertainment:Available]  $200
    [Budget:Transportation:Available] $300
    [Budget:Reserve]              $-1000

; Spending reduces envelope
2024/01/15 Grocery
    Expenses:Food                   $100
    Assets:Checking                $-100
    [Budget:Food:Available]        $-100
    [Budget:Food:Spent]             $100
```

## Mixed Usage

### Real + Both Virtual Types

```ledger
2024/01/15 Full Example
    ; === Real Postings ===
    Expenses:Food          $50
    Assets:Checking       $-50
    ; Sum: $0 ✓

    ; === Balanced Virtual ===
    [Envelope:Food:Spent]      $50
    [Envelope:Food:Available] $-50
    ; Sum: $0 ✓

    ; === Unbalanced Virtual ===
    (Tracking:Food)            $50
    (Stats:Count)                1
    ; No balance check
```

## Querying Virtual Postings

### Include Virtual

```bash
ledger --real bal              # Exclude all virtual
ledger --real reg              # Only real postings
```

### Only Virtual

```bash
ledger bal ^Budget             # Accounts starting with Budget
ledger reg "(Budget"           # Parentheses accounts
```

### All Postings

```bash
ledger bal                     # Includes everything
```

## Account Naming Conventions

### Common Patterns

```ledger
; Budget envelopes (balanced)
[Budget:Food]
[Budget:Entertainment]
[Budget:Savings]

; Tracking (unbalanced)
(Tracking:Expenses)
(Tracking:Income)
(Stats:Count)

; Reimbursements
(Reimbursable:Client-A)
(Reimbursable:Employer)

; Notes
(Memo:Project-Alpha)
(Note:Tax-Deductible)
```

## Budget System Example

### Setup

```ledger
; ===== Monthly Budget Setup =====

2024/01/01 * January Budget
    ; Income allocation
    [Budget:Income:Expected]           $5000
    [Budget:Income:Received]              $0

    ; Expense envelopes
    [Budget:Housing:Available]         $1500
    [Budget:Food:Available]             $500
    [Budget:Entertainment:Available]    $200
    [Budget:Transportation:Available]   $300
    [Budget:Utilities:Available]        $200
    [Budget:Savings:Available]          $500

    ; Unallocated
    [Budget:Reserve]                   $1800
```

### Income Receipt

```ledger
2024/01/15 * Paycheck
    Assets:Checking                    $2500
    Income:Salary                     $-2500
    [Budget:Income:Received]           $2500
    [Budget:Income:Expected]          $-2500
```

### Spending

```ledger
2024/01/20 * Grocery Store
    Expenses:Food                       $120
    Assets:Checking                    $-120
    [Budget:Food:Spent]                 $120
    [Budget:Food:Available]            $-120
```

### Transfer Between Envelopes

```ledger
2024/01/25 * Budget Adjustment
    ; Move $50 from Entertainment to Food
    [Budget:Entertainment:Available]    $-50
    [Budget:Food:Available]              $50
```

## Validation

### Balanced Virtual Must Balance

```ledger
2024/01/15 Invalid
    [Budget:A]    $100
    [Budget:B]    $-50
    ; ERROR: Balanced virtual don't balance ($50 difference)
```

Error:
```
V-012: Balanced virtual postings don't balance
  Line 2-3:
    [Budget:A]    $100
    [Budget:B]    $-50
  Difference: $50.00
```

### Unbalanced Virtual Never Error

```ledger
2024/01/15 Valid
    (Anything)    $1000
    (Random)      $5000
    ; OK: Unbalanced virtual have no requirement
```

## Reporting

### Budget Status

```bash
ledger bal ^Budget --format "%(account): %(total)\n"
```

### Real vs Virtual

```bash
ledger --real bal      # Real accounts only
ledger bal "(Budget"   # Virtual budget accounts
```

### Envelope Status

```bash
ledger bal ^Budget:.*:Available
```

## Examples

### Complete Budget Flow

```ledger
; ===== Initial Setup =====

2024/01/01 Create Budget
    [Budget:Food:Available]         $500
    [Budget:Fun:Available]          $200
    [Budget:Reserve]               $-700

; ===== Regular Expense =====

2024/01/15 Grocery Store
    Expenses:Food                   $100
    Assets:Checking                $-100
    [Budget:Food:Available]        $-100
    [Budget:Food:Spent]             $100

; ===== Check Status =====
; Food: $400 available, $100 spent

; ===== Overspend =====

2024/01/20 Restaurant
    Expenses:Food                   $450
    Assets:Checking                $-450
    [Budget:Food:Available]        $-450
    [Budget:Food:Spent]             $450

; Food: $-50 available (overspent!)

; ===== Cover from Reserve =====

2024/01/21 Cover Food Overage
    [Budget:Reserve]                $-50
    [Budget:Food:Available]          $50

; Food: $0 available, Reserve: $-750
```

### Tracking with Stats

```ledger
2024/01/15 Morning Coffee
    Expenses:Food:Coffee            $5
    Assets:Wallet                  $-5
    (Stats:Coffees)                  1
    (Stats:Coffee-Spending)         $5

2024/01/16 Morning Coffee
    Expenses:Food:Coffee            $5
    Assets:Wallet                  $-5
    (Stats:Coffees)                  1
    (Stats:Coffee-Spending)         $5

; Query: ledger bal ^Stats
; Stats:Coffees           2
; Stats:Coffee-Spending  $10
```

## Best Practices

1. **Clear naming** - Distinguish virtual from real accounts
2. **Consistent brackets/parens** - Use appropriate type
3. **Document purpose** - Comment budget rules
4. **Regular review** - Check envelope balances
5. **Automate** - Use automated transactions
6. **Separate files** - Keep budget rules in budget.ledger

## See Also

- [Automated Transactions](automated.md)
- [Periodic Transactions](periodic.md)
- [Balance Validation](../validation/balance.md)
