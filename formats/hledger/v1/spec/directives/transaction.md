# Transaction Directive

Transactions are the primary entries in an hledger journal, recording financial movements between accounts.

## Syntax

```hledger
DATE [=DATE2] [STATUS] [CODE] DESCRIPTION
    POSTING
    POSTING
    ...
```

## Components

### Date (Required)

```hledger
2024-01-15 Transaction with dashes
2024/01/15 Transaction with slashes
2024.01.15 Transaction with dots
```

### Secondary Date (Optional)

The `=` separates primary and secondary dates:

```hledger
2024-01-15=2024-01-20 Payment with effective date
    Expenses:Bill    $100
    Assets:Checking
```

- Primary date: Transaction entry date
- Secondary date: Effective/posting date

### Status (Optional)

```hledger
2024-01-15 Unmarked transaction
    ...

2024-01-15 ! Pending transaction
    ...

2024-01-15 * Cleared transaction
    ...
```

| Marker | Meaning | Description |
|--------|---------|-------------|
| (none) | Unmarked | Not yet reviewed |
| `!` | Pending | Entered but awaiting confirmation |
| `*` | Cleared | Verified/reconciled |

### Code (Optional)

Check number or reference in parentheses:

```hledger
2024-01-15 (#1234) Check payment
    Expenses:Rent    $1500
    Assets:Checking

2024-01-15 (INV-001) Invoice payment
    Assets:Receivable    $500
    Income:Sales
```

### Description (Required)

Free-form text describing the transaction:

```hledger
2024-01-15 Grocery shopping at Whole Foods
    Expenses:Food    $75
    Assets:Checking

2024-01-15 Monthly rent payment
    Expenses:Housing:Rent    $1500
    Assets:Checking
```

### Postings (Required)

At least one posting required. See [Posting Specification](../posting.md).

## Minimum Transaction

```hledger
2024-01-15 Description
    Account:One    $50
    Account:Two
```

## Complete Example

```hledger
2024-01-15=2024-01-20 * (#1234) Monthly rent payment
    ; tag:housing, recurring:monthly
    Expenses:Housing:Rent    $1500.00
        ; landlord:ABC Properties
    Assets:Checking    $-1500.00 = $3500.00
        ; check:cleared
```

## Transaction Comments

### Header Comment

```hledger
2024-01-15 Transaction  ; This is a header comment
    Expenses:Food    $50
    Assets:Checking
```

### Transaction-Level Tags

After description or on next indented comment line:

```hledger
2024-01-15 Office supplies  ; project:renovation, dept:ops
    Expenses:Office    $100
    Assets:Checking

2024-01-15 Conference travel
    ; trip:annual-conf
    ; approved-by:manager
    Expenses:Travel    $500
    Assets:Checking
```

## Multi-Posting Transactions

```hledger
2024-01-15 Split expense
    Expenses:Food:Groceries    $50.00
    Expenses:Food:Snacks       $10.00
    Expenses:Household         $25.00
    Assets:Checking           $-85.00
```

## Balancing Rules

1. **Sum to zero**: All posting amounts must sum to zero
2. **One elision per commodity**: One posting per commodity can omit amount
3. **Automatic balancing**: Elided posting gets calculated amount

### Valid

```hledger
2024-01-15 Balanced explicitly
    Expenses:Food    $50.00
    Assets:Checking  $-50.00

2024-01-15 Balanced with elision
    Expenses:Food    $50.00
    Assets:Checking          ; Inferred: $-50.00
```

### Invalid

```hledger
; ERROR: Does not balance
2024-01-15 Unbalanced
    Expenses:Food    $50.00
    Assets:Checking  $-40.00
```

## Multi-Currency Transactions

```hledger
2024-01-15 Currency exchange
    Assets:USD    $-100.00
    Assets:EUR    90.00 EUR @@ $100.00

2024-01-15 International purchase
    Expenses:Shopping    100.00 EUR @ $1.10
    Assets:Checking    $-110.00
```

## Virtual Postings

```hledger
2024-01-15 Expense with budget tracking
    Expenses:Food        $50.00     ; Real posting
    (Budget:Food)       $-50.00     ; Virtual unbalanced
    Assets:Checking     $-50.00     ; Real posting
```

## Periodic Transactions

Template for forecasting (with `~`):

```hledger
~ monthly from 2024-01-01
    Expenses:Rent    $1500
    Assets:Checking
```

## Transaction Modifiers

Auto-posting rules (with `=`):

```hledger
= expenses:food
    (Budget:Food)    *-1

; Applied to matching transactions
2024-01-15 Groceries
    Expenses:Food    $50
    Assets:Checking
; Auto-adds: (Budget:Food) $-50
```

## Status Inheritance

Transaction status can apply to postings:

```hledger
2024-01-15 * Cleared transaction
    Expenses:Food    $50       ; Inherits cleared
    Assets:Checking  $-50      ; Inherits cleared

2024-01-15 Mixed status
    * Expenses:Food    $30     ; Explicitly cleared
    ! Expenses:Drink   $20     ; Explicitly pending
    Assets:Checking            ; No status
```

## Date Ordering

Transactions should be in chronological order:

```hledger
2024-01-14 Earlier
    ...

2024-01-15 Later
    ...
```

hledger will warn if dates are out of order (with `--strict`).

## Best Practices

1. **Use consistent date format** (prefer YYYY-MM-DD)
2. **Include descriptive text** for all transactions
3. **Mark status** as transactions are reconciled
4. **Add relevant tags** for reporting
5. **Keep transactions in date order**
6. **Use balance assertions** regularly

## Examples

### Simple Purchase

```hledger
2024-01-15 Coffee shop
    Expenses:Food:Coffee    $5.00
    Assets:Cash
```

### Paycheck with Withholdings

```hledger
2024-01-15 * Paycheck  ; employer:ACME Corp
    Assets:Checking           $3,500.00
    Expenses:Tax:Federal        $700.00
    Expenses:Tax:State          $200.00
    Expenses:Tax:FICA           $300.00
    Expenses:Benefits:Health    $100.00
    Income:Salary            $-4,800.00
```

### Investment Purchase

```hledger
2024-01-15 Buy Apple stock
    Assets:Brokerage:AAPL    10 AAPL @ $150.00
    Expenses:Fees    $9.99
    Assets:Brokerage:Cash    $-1509.99
```

### Transfer Between Accounts

```hledger
2024-01-15 * Transfer to savings
    Assets:Savings    $500.00
    Assets:Checking   $-500.00
```

## See Also

- [Posting Specification](../posting.md)
- [Amounts Specification](../amounts.md)
- [Syntax Specification](../syntax.md)
