# Tag Directive

The `tag` directive declares and documents tags used in the ledger.

## Syntax

```
tag NAME
    [SUBDIRECTIVE...]
```

## Examples

### Basic Declaration

```ledger
tag project
```

### With Subdirectives

```ledger
tag project
    check value =~ /^[a-z]+$/
    note Project code for work tracking
```

## Using Tags

### In Transactions

```ledger
2024/01/15 Business Lunch
    ; :business:meals:
    Expenses:Food    $45.00
    Assets:Checking
```

### Tag Syntax

Tags are enclosed in colons:

```ledger
; :tag1:tag2:tag3:
```

Multiple tags can be on one line:

```ledger
2024/01/15 Conference Trip
    ; :travel:business:tax-deductible:
    Expenses:Travel    $500.00
    Assets:Checking
```

## Subdirectives

### check

Validate tag values:

```ledger
tag project
    check value =~ /^[A-Z]{3}-[0-9]+$/

; Valid usage
2024/01/15 Work
    ; project: ABC-123
    Expenses:Office    $50
    Assets:Checking
```

### assert

Require valid tag values:

```ledger
tag priority
    assert value =~ /^(low|medium|high)$/
```

### note

Document the tag:

```ledger
tag reimbursable
    note Expenses to be reimbursed by employer
```

## Tag Values

### Simple Tags

```ledger
; :vacation:
```

### Tags with Values

```ledger
; project: alpha
; client: acme
; billable-hours: 8
```

## Tag Queries

Use tags in reports:

```bash
# Find all transactions with tag
ledger -f journal.ledger reg %business

# Expenses tagged 'reimbursable'
ledger reg Expenses and %reimbursable
```

## Metadata vs Tags

### Tags (Categories)

```ledger
2024/01/15 Transaction
    ; :travel:business:
    Expenses:Travel    $500
    Assets:Checking
```

### Metadata (Key-Value)

```ledger
2024/01/15 Transaction
    ; project: alpha
    ; client: Acme Corp
    Expenses:Travel    $500
    Assets:Checking
```

Both can be used together:

```ledger
2024/01/15 Transaction
    ; :travel:business:
    ; project: alpha
    ; approved-by: John
    Expenses:Travel    $500
    Assets:Checking
```

## Common Tags

### Expense Categories

```ledger
tag tax-deductible
    note Deductible on tax return

tag reimbursable
    note Company will reimburse

tag personal
    note Personal expense

tag business
    note Business expense
```

### Project Tracking

```ledger
tag project
    check value =~ /^[a-z-]+$/
    note Project identifier

tag client
    note Client name
```

### Status Tags

```ledger
tag pending
    note Awaiting action

tag approved
    note Approved by manager

tag reconciled
    note Matched with bank statement
```

## Querying Tags

### By Tag Presence

```bash
ledger reg %travel
```

### By Tag Value

```bash
ledger reg %(project=alpha)
```

### Combining with Accounts

```bash
ledger reg Expenses and %business
```

### Negation

```bash
ledger reg Expenses and not %personal
```

## Posting-Level Tags

Tags on individual postings:

```ledger
2024/01/15 Mixed Expense
    Expenses:Food    $30.00
        ; :personal:
    Expenses:Office    $50.00
        ; :business:
    Assets:Checking
```

## Automatic Tags

Using automated transactions:

```ledger
= Expenses:Travel
    ; :travel:
    ; :tax-deductible:
```

## Best Practices

1. **Declare all tags** at the top of ledger
2. **Use consistent naming** (lowercase, hyphens)
3. **Document tag purposes**
4. **Add validation rules** where appropriate
5. **Keep tag count manageable**

## Example: Complete Tag System

```ledger
; ===== Tag Declarations =====

tag personal
    note Personal (non-business) expense

tag business
    note Business expense

tag tax-deductible
    note Deductible on tax return

tag reimbursable
    note To be reimbursed by employer

tag project
    check value =~ /^[a-z][a-z0-9-]*$/
    note Project identifier

tag client
    note Client or customer name

; ===== Transactions =====

2024/01/15 Office Supplies
    ; :business:tax-deductible:
    ; project: website-redesign
    ; client: Acme Corp
    Expenses:Office    $75.00
    Assets:Checking

2024/01/20 Lunch
    ; :personal:
    Expenses:Food    $15.00
    Assets:Checking

2024/01/25 Client Dinner
    ; :business:reimbursable:
    ; client: Acme Corp
    Expenses:Food:Business    $120.00
    Assets:Checking
```

## See Also

- [Metadata Specification](../metadata.md)
- [Transaction Directive](transaction.md)
- [Payee Directive](payee.md)
