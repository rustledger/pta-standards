# Tags Specification

This document specifies tag syntax and semantics in Ledger.

## Overview

Tags provide lightweight categorization for transactions and postings. Unlike metadata (key-value pairs), tags are simple labels useful for:
- Cross-cutting categorization
- Filtering and grouping
- Workflow states
- Quick annotations

## Syntax

### Inline Tag Format

```
tag_list = ":" tag (":" tag)* ":"
tag      = (letter | digit | "-" | "_")+
```

### Examples

```ledger
; :personal:
; :business:reimbursable:
; :tax-2024:deductible:
```

## Transaction Tags

### Single Tag

```ledger
2024/01/15 * Grocery Store
    ; :personal:
    Expenses:Food    $50.00
    Assets:Checking
```

### Multiple Tags

```ledger
2024/01/15 * Client Dinner
    ; :business:reimbursable:client-meeting:
    Expenses:Meals    $150.00
    Assets:Personal-Card
```

## Posting Tags

Tags can apply to specific postings:

```ledger
2024/01/15 * Mixed Purchase
    Expenses:Food    $30.00
        ; :personal:
    Expenses:Office  $20.00
        ; :business:
    Assets:Checking
```

## Tag Naming

### Valid Names

```
personal
business
tax-2024
project_alpha
Q1
```

### Invalid Names

```
has space       ; No spaces
with:colon      ; No colons inside
@mention        ; No special characters
123start        ; Cannot start with digit
```

### Case Sensitivity

Tags are case-sensitive:

```ledger
; :Personal:    ; Different from :personal:
; :URGENT:      ; Different from :urgent:
```

## Tag Inheritance

### Transaction to Posting

Transaction tags apply to all postings:

```ledger
2024/01/15 * Purchase
    ; :business:
    Expenses:A    $50    ; Inherits :business:
    Expenses:B    $50    ; Inherits :business:
    Assets:Cash
```

### Posting-Specific Tags

Postings can have their own tags:

```ledger
2024/01/15 * Purchase
    ; :business:
    Expenses:A    $50
        ; :project-alpha:    ; Also has :business:
    Expenses:B    $50        ; Only has :business:
    Assets:Cash
```

## Querying Tags

### Filter by Tag

```bash
ledger reg %personal
ledger bal %business
```

### Multiple Tags (AND)

```bash
ledger reg %business %reimbursable
```

### Tag Expression

```bash
ledger reg "tag(\"business\")"
```

### Exclude Tag

```bash
ledger reg not %personal
```

## Common Tag Categories

### Ownership

```ledger
; :personal:
; :business:
; :joint:
; :spouse:
```

### Workflow

```ledger
; :pending:
; :reviewed:
; :approved:
; :reconciled:
```

### Tax

```ledger
; :tax-deductible:
; :tax-exempt:
; :taxable:
; :capital-gain:
```

### Time Period

```ledger
; :Q1:
; :Q2:
; :2024:
; :FY2024:
```

### Projects

```ledger
; :project-alpha:
; :client-acme:
; :campaign-summer:
```

### Special

```ledger
; :recurring:
; :one-time:
; :reimbursable:
; :split:
```

## Tags vs Metadata

### When to Use Tags

- Simple categorization
- Boolean attributes
- Quick filtering
- Cross-cutting concerns

```ledger
; :business:reimbursable:
```

### When to Use Metadata

- Key-value data
- Specific values needed
- Complex attributes
- Linked documents

```ledger
; Client: Acme Corp
; Amount: $500.00
```

### Combined Use

```ledger
2024/01/15 * Client Lunch
    ; :business:reimbursable:
    ; Client: Acme Corp
    ; Receipt: scan-001.pdf
    Expenses:Meals    $75.00
    Assets:Personal-Card
```

## Tag Declaration

### Optional Declaration

Tags don't require declaration, but you can declare them:

```ledger
tag personal
    ; Personal expenses, not business-related

tag business
    ; Business expenses, potentially deductible

tag reimbursable
    ; Expenses to be reimbursed by employer/client
```

### Enforce Declaration

```bash
ledger --strict-tags bal
```

Only allows declared tags.

## Automated Tagging

### With Automated Transactions

```ledger
= /Grocery/
    ; :personal:food:

= /Office Depot/
    ; :business:supplies:
```

### Tag-Based Rules

```ledger
= expr has_tag("reimbursable")
    (Receivable:Reimbursements)  amount
```

## Reports and Tags

### List All Tags

```bash
ledger tags
```

### Tag Statistics

```bash
ledger stats --tag
```

### Balance by Tag

```bash
ledger bal --group-by "tag(\"project\")"
```

## Examples

### Personal Finance Tagging

```ledger
2024/01/15 * Grocery Store
    ; :personal:groceries:
    Expenses:Food:Groceries    $150.00
    Assets:Checking

2024/01/15 * Gas Station
    ; :personal:auto:
    Expenses:Transportation:Gas    $45.00
    Assets:Credit-Card

2024/01/15 * Client Dinner
    ; :business:reimbursable:client-meeting:
    Expenses:Meals:Business    $125.00
        ; Client: Acme Corp
    Assets:Personal-Card
```

### Project Tracking

```ledger
2024/01/15 * Contractor Payment
    ; :project-alpha:billable:
    Expenses:Contractors    $2000.00
    Assets:Checking

2024/01/15 * Software License
    ; :project-beta:infrastructure:
    Expenses:Software    $500.00
    Assets:Checking
```

### Workflow States

```ledger
2024/01/15 * Office Supplies
    ; :pending:needs-receipt:
    Expenses:Office    $50.00
    Assets:Checking

2024/01/15 * Travel Booking
    ; :approved:booked:
    Expenses:Travel    $500.00
    Assets:Checking
```

## Best Practices

1. **Consistent naming** - Use lowercase with hyphens
2. **Limited set** - Don't create too many tags
3. **Document tags** - Keep a tag glossary
4. **Hierarchical accounts** - Use accounts for primary categorization
5. **Tags for cross-cutting** - Use tags for secondary classification
6. **Avoid redundancy** - Don't tag what accounts already capture

## See Also

- [Metadata Specification](metadata.md)
- [Transaction Directive](directives/transaction.md)
- [Tag Directive](directives/tag.md)
