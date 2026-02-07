# Bucket Directive

The `bucket` directive sets the default account for balancing transactions.

## Syntax

```
bucket ACCOUNT
```

Alternative syntax:

```
A ACCOUNT
```

## Examples

### Basic Usage

```ledger
bucket Assets:Checking

2024/01/15 Grocery Store
    Expenses:Food    $50.00
    ; Automatically balanced to Assets:Checking
```

### Short Form

```ledger
A Assets:Checking

2024/01/15 Coffee Shop
    Expenses:Food:Coffee    $5.00
```

## Behavior

When a bucket is set, transactions with a single posting are automatically balanced:

```ledger
bucket Assets:Checking

; This transaction:
2024/01/15 Store
    Expenses:Food    $50.00

; Is equivalent to:
2024/01/15 Store
    Expenses:Food    $50.00
    Assets:Checking  $-50.00
```

## Changing the Bucket

The bucket can be changed mid-file:

```ledger
bucket Assets:Checking

2024/01/15 Expense from checking
    Expenses:Food    $50.00

bucket Liabilities:CreditCard

2024/01/16 Expense on credit card
    Expenses:Shopping    $100.00
```

## Clearing the Bucket

Use an empty bucket to disable:

```ledger
bucket Assets:Checking

2024/01/15 Auto-balanced
    Expenses:Food    $50.00

bucket
; or: A

2024/01/16 Must be explicit
    Expenses:Food    $50.00
    Assets:Cash             ; Required now
```

## Use Cases

### Personal Finance

```ledger
bucket Assets:Bank:Checking

; Most expenses come from checking
2024/01/15 Groceries
    Expenses:Food    $150.00

2024/01/15 Gas
    Expenses:Transportation    $45.00

2024/01/15 Rent
    Expenses:Housing:Rent    $1500.00
```

### Credit Card Tracking

```ledger
bucket Liabilities:CreditCard:Visa

; All purchases go on Visa
2024/01/15 Amazon
    Expenses:Shopping    $75.00

2024/01/15 Restaurant
    Expenses:Food:Dining    $45.00
```

### Import Processing

Useful when importing bank statements:

```ledger
; Set bucket for bank import
bucket Assets:Checking

; Imported transactions only need category
2024/01/15 WHOLEFDS #1234
    Expenses:Food:Groceries    $87.50

2024/01/16 SHELL OIL
    Expenses:Transportation:Gas    $42.00
```

## Multiple Postings

Bucket only applies when exactly one posting is given:

```ledger
bucket Assets:Checking

; Bucket used - one posting
2024/01/15 Simple
    Expenses:Food    $50.00

; Bucket NOT used - multiple postings
2024/01/15 Split
    Expenses:Food    $30.00
    Expenses:Household    $20.00
    Assets:Cash             ; Must be explicit
```

## Interaction with Aliases

Works with account aliases:

```ledger
alias checking = Assets:Bank:Checking
bucket checking

2024/01/15 Store
    Expenses:Food    $50.00
    ; Balanced to Assets:Bank:Checking
```

## Warnings

### Unexpected Balancing

Be careful with bucket when you intend multi-posting transactions:

```ledger
bucket Assets:Checking

; Oops - wanted to split but forgot second posting
2024/01/15 Split expense
    Expenses:Food    $50.00
    ; Unintentionally balanced to Checking
```

### File Organization

Reset bucket at section boundaries:

```ledger
; === Checking Account Transactions ===
bucket Assets:Checking
include transactions/checking/*.ledger

; === Credit Card Transactions ===
bucket Liabilities:CreditCard
include transactions/creditcard/*.ledger

; === Manual Entries ===
bucket
include transactions/manual.ledger
```

## Account Default Subdirective

Alternative approach using account directive:

```ledger
account Assets:Checking
    default

; Same effect as 'bucket Assets:Checking'
```

## Best Practices

1. **Set bucket per section** for clarity
2. **Reset bucket** when switching contexts
3. **Document bucket usage** in comments
4. **Be explicit** for complex transactions
5. **Review auto-balanced** transactions

## Example: Complete Workflow

```ledger
; Main checking account for most expenses
bucket Assets:Bank:Checking

; January expenses
2024/01/02 Netflix
    Expenses:Entertainment:Streaming    $15.99

2024/01/05 Grocery Store
    Expenses:Food:Groceries    $125.00

2024/01/10 Electric Company
    Expenses:Housing:Utilities:Electric    $85.00

; Credit card section
bucket Liabilities:CreditCard:Visa

2024/01/15 Amazon
    Expenses:Shopping    $50.00

2024/01/20 Restaurant
    Expenses:Food:Dining    $35.00

; Manual/complex transactions - no bucket
bucket

2024/01/25 Paycheck
    Assets:Bank:Checking    $3000.00
    Income:Salary
```

## See Also

- [Account Directive](account.md)
- [Alias Directive](alias.md)
- [Transaction Directive](transaction.md)
