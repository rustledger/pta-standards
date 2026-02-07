# hledger Tags Specification

This document specifies tag syntax in hledger.

## Overview

Tags attach metadata to transactions and postings for:
- Categorization
- Filtering
- Reporting
- Custom attributes

## Syntax

### Tag Format

```
tag = name [":" [value]]
```

### In Comments

```hledger
; tagname:
; tagname: value
; tag1:, tag2:, tag3:value
```

## Transaction Tags

### Basic Tag

```hledger
2024-01-15 Grocery Store
    ; food:
    expenses:food    $50
    assets:cash
```

### Tag with Value

```hledger
2024-01-15 Business Dinner
    ; client: Acme Corp
    ; project: Alpha
    expenses:meals    $100
    assets:cash
```

### Multiple Tags

```hledger
2024-01-15 Purchase
    ; personal:, groceries:, weekly:
    expenses:food    $75
    assets:checking
```

## Posting Tags

```hledger
2024-01-15 Mixed Purchase
    expenses:food    $30
        ; category: groceries
    expenses:office  $20
        ; category: supplies
    assets:checking
```

## Tag Naming

### Valid Names

```
lowercase
camelCase
with-dashes
with_underscores
numbers123
```

### Invalid Names

```
has space        ; No spaces in name
123starts        ; Can't start with digit
```

## Tag Values

### Text Values

```hledger
; project: Website Redesign
; vendor: Office Depot
```

### Empty Values (Boolean)

```hledger
; reviewed:
; approved:
```

### Comma-Separated Tags

```hledger
; tag1:, tag2: value2, tag3:
```

## Querying Tags

### Filter by Tag Name

```bash
hledger reg tag:food
hledger bal tag:project
```

### Filter by Tag Value

```bash
hledger reg tag:project=Alpha
hledger bal tag:client="Acme Corp"
```

### Not Having Tag

```bash
hledger reg not:tag:reviewed
```

## Common Tags

### Categorization

```hledger
; personal:
; business:
; reimbursable:
```

### Status

```hledger
; pending:
; approved:
; reconciled:
```

### References

```hledger
; receipt: scan-001.pdf
; invoice: INV-2024-001
; check: 1234
```

### Projects

```hledger
; project: Alpha
; client: Acme
; department: Engineering
```

## Tag Declaration

```hledger
tag project
    ; For project tracking

tag receipt
    ; Receipt file reference
```

## Inheritance

### Transaction to Posting

Transaction tags apply to all postings:

```hledger
2024-01-15 Purchase
    ; business:
    expenses:office  $50    ; Inherits business:
    assets:checking         ; Inherits business:
```

### Posting Override

Postings can add tags:

```hledger
2024-01-15 Purchase
    ; business:
    expenses:travel  $100
        ; project: Alpha    ; Also has business:
    assets:checking
```

## Examples

### Expense Tracking

```hledger
2024-01-15 Office Depot
    ; business:, receipt: office-2024-01-15.pdf
    expenses:office:supplies    $75.00
        ; item: paper, pens
    expenses:office:equipment   $150.00
        ; item: desk lamp
        ; asset-tag: LAMP-001
    liabilities:credit-card
```

### Project Accounting

```hledger
2024-01-15 Contractor Payment
    ; project: Alpha, invoice: INV-001
    expenses:contractors    $2000
    assets:checking

2024-01-20 Software License
    ; project: Beta, annual:
    expenses:software    $500
    assets:checking
```

### Reimbursement Workflow

```hledger
2024-01-15 Client Dinner
    ; reimbursable:, client: Acme, submitted:
    expenses:travel:meals    $100
    assets:personal-card

2024-02-01 Reimbursement Received
    ; reimburses: 2024-01-15
    assets:checking    $100
    income:reimbursements
```

## Reporting

### List All Tags

```bash
hledger tags
```

### Balance by Tag

```bash
hledger bal tag:project
```

### Pivot by Tag

```bash
hledger bal --pivot project
```

## Best Practices

1. **Consistent naming** - Lowercase with dashes
2. **Document tags** - Declare and describe
3. **Limited set** - Don't overuse tags
4. **Use accounts** - Primary categorization
5. **Tags for cross-cutting** - Secondary dimensions

## See Also

- [Metadata Specification](metadata.md)
- [Tag Directive](directives/tag.md)
