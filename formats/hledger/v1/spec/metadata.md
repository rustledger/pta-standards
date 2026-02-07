# hledger Metadata Specification

This document specifies metadata attachment in hledger.

## Overview

Metadata provides key-value data for:
- Documentation
- Linking external resources
- Custom attributes
- Reporting dimensions

## Syntax

### Format

```hledger
; key: value
```

Metadata appears in comments following transactions or postings.

## Transaction Metadata

```hledger
2024-01-15 Office Supplies
    ; Receipt: scan-2024-01-15.pdf
    ; Vendor: Office Depot
    expenses:office    $100
    assets:checking
```

## Posting Metadata

```hledger
2024-01-15 Purchase
    expenses:office    $100
        ; Department: Engineering
        ; Approved-by: Jane Smith
    assets:checking
```

## Key Naming

### Valid Keys

```
Receipt
receipt
tax-category
project_code
PO123
```

### Conventions

- Capitalize first letter (Title Case)
- Use dashes for multi-word
- Keep concise

## Value Types

### Text

```hledger
; Project: Website Redesign
; Note: Annual subscription
```

### Paths

```hledger
; Receipt: /documents/receipts/2024/scan-001.pdf
; Invoice: invoices/INV-2024-001.pdf
```

### Dates

```hledger
; Due-date: 2024-02-15
; Submitted: 2024-01-20
```

### Numbers

```hledger
; Miles: 150
; Quantity: 3
```

## Common Metadata

### Documents

```hledger
; Receipt: file.pdf
; Invoice: INV-001
; Statement: 2024-01.pdf
```

### References

```hledger
; Check: 1234
; Confirmation: ABC123
; Order: ORD-2024-001
```

### Workflow

```hledger
; Submitted: 2024-01-15
; Approved-by: Manager
; Paid: 2024-01-20
```

### Tax

```hledger
; Tax-category: Business Expense
; Deductible: yes
; Form: Schedule C
```

## Inheritance

### Transaction to Posting

```hledger
2024-01-15 Purchase
    ; Project: Alpha
    expenses:a    $50    ; Inherits Project: Alpha
    expenses:b    $50    ; Inherits Project: Alpha
    assets:cash
```

### Posting Override

```hledger
2024-01-15 Purchase
    ; Project: Alpha
    expenses:a    $50
        ; Project: Beta    ; Overrides
    expenses:b    $50       ; Uses Alpha
    assets:cash
```

## Querying

### By Metadata

```bash
hledger reg tag:Project
hledger bal tag:Project=Alpha
```

### Display Metadata

```bash
hledger print --show-tags
```

## Examples

### Expense Report

```hledger
2024-01-15 * Office Depot
    ; Receipt: receipts/2024/office-depot-0115.pdf
    ; Purpose: Office supplies for Q1
    ; Paid-via: Company Card
    expenses:office:supplies    $150.00
        ; Items: Paper, pens, folders
    expenses:office:equipment   $200.00
        ; Items: Desk lamp
        ; Asset-tag: EQ-2024-001
    liabilities:company-card
```

### Travel Expense

```hledger
2024-01-20 * United Airlines
    ; Trip: Client Visit - Acme Corp
    ; Confirmation: ABC123
    ; Travelers: John Smith
    expenses:travel:airfare    $450.00
        ; Flight: SFO-JFK
        ; Booking: UA-123456
    assets:checking
```

### Reimbursable Expense

```hledger
2024-01-15 Client Dinner
    ; Client: Acme Corporation
    ; Attendees: 4
    ; Purpose: Project kickoff dinner
    ; Reimbursable: yes
    ; Submitted: 2024-01-16
    ; Reimbursed: 2024-02-01
    expenses:travel:meals    $175.00
    assets:personal-card
```

## Metadata vs Tags

### Use Metadata For

- Key-value pairs
- Document references
- Specific attributes
- Complex data

### Use Tags For

- Boolean flags
- Simple categories
- Quick filtering

### Combined

```hledger
2024-01-15 Purchase
    ; business:, reimbursable:     ; Tags
    ; Client: Acme Corp             ; Metadata
    ; Receipt: scan.pdf             ; Metadata
    expenses:meals    $100
    assets:card
```

## Best Practices

1. **Consistent keys** - Same names across journal
2. **Document schema** - List used metadata keys
3. **Link documents** - Reference receipts/invoices
4. **Don't duplicate** - Avoid redundant data
5. **Use for reporting** - Design for your needs

## See Also

- [Tags Specification](tags.md)
- [Comments](lexical.md#comments)
