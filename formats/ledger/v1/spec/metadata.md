# Metadata Specification

This document specifies metadata attachment in Ledger.

## Overview

Metadata allows attaching structured key-value data to transactions and postings. This enables:
- Receipt and document linking
- Categorization beyond accounts
- Workflow tracking
- Custom reporting

## Syntax

```
metadata = key ":" [value]
key      = (letter | digit | "-" | "_")+
value    = text (to end of line)
```

Metadata appears in comments with special formatting.

## Transaction Metadata

### Basic Syntax

```ledger
2024/01/15 * Office Supplies
    ; Key: Value
    Expenses:Office    $100.00
    Assets:Checking
```

### Multiple Metadata

```ledger
2024/01/15 * Office Supplies
    ; Receipt: scan-001.pdf
    ; Category: office
    ; Project: Alpha
    Expenses:Office    $100.00
    Assets:Checking
```

## Posting Metadata

Metadata can attach to specific postings:

```ledger
2024/01/15 * Office Supplies
    Expenses:Office    $100.00
        ; Department: Engineering
        ; Approved-By: Jane Smith
    Assets:Checking
```

## Metadata Keys

### Naming Conventions

```
Valid:
  Receipt
  receipt
  tax-category
  project_code
  ID123

Invalid:
  has space
  key:colon
  @symbol
```

### Reserved Keys

Some keys have special meaning:

| Key | Purpose |
|-----|---------|
| `Payee` | Override transaction payee |
| `Date` | Override effective date |
| `Note` | Additional notes |
| `UUID` | Unique identifier |

## Metadata Values

### Text Values

```ledger
; Project: Website Redesign 2024
```

### Numeric Values

```ledger
; Miles: 150
; Amount: 99.50
```

### Date Values

```ledger
; Due-Date: 2024/02/15
```

### Path Values

```ledger
; Receipt: /documents/receipts/2024/jan/scan-001.pdf
; Invoice: invoices/INV-2024-001.pdf
```

### Empty Values

A key without value acts as a boolean flag:

```ledger
; Reviewed:
; Tax-Deductible:
```

## Inheritance

### Transaction to Posting

Transaction metadata is inherited by all postings:

```ledger
2024/01/15 * Purchase
    ; Project: Alpha    ; Applies to all postings
    Expenses:A    $50
    Expenses:B    $50
    Assets:Cash
```

### Posting Override

Postings can override transaction metadata:

```ledger
2024/01/15 * Purchase
    ; Project: Alpha
    Expenses:A    $50
        ; Project: Beta    ; Override for this posting
    Expenses:B    $50       ; Inherits Project: Alpha
    Assets:Cash
```

## Querying Metadata

### Filter by Key

```bash
ledger reg --meta Project
```

### Filter by Value

```bash
ledger reg --meta Project=Alpha
```

### Display Metadata

```bash
ledger reg --format "%(meta(\"Project\"))"
```

## Common Use Cases

### Receipt Tracking

```ledger
2024/01/15 * Staples
    ; Receipt: receipts/2024-01-15-staples.pdf
    ; Receipt-Date: 2024/01/15
    Expenses:Office    $50.00
    Assets:Checking
```

### Reimbursement Tracking

```ledger
2024/01/15 * Client Lunch
    ; Reimbursable:
    ; Client: Acme Corp
    ; Submitted: 2024/01/20
    ; Reimbursed: 2024/02/01
    Expenses:Travel:Meals    $75.00
    Assets:Personal-Card
```

### Project Accounting

```ledger
2024/01/15 * Contractor Payment
    ; Project: Website-Redesign
    ; Invoice: INV-2024-001
    ; Milestone: Phase 2
    Expenses:Contractors    $5000.00
    Assets:Checking
```

### Tax Documentation

```ledger
2024/01/15 * Charitable Donation
    ; Tax-Deductible:
    ; Receipt: charity-receipt-2024.pdf
    ; EIN: 12-3456789
    Expenses:Donations    $500.00
    Assets:Checking
```

### Approval Workflow

```ledger
2024/01/15 * Large Purchase
    ; Requested-By: John
    ; Approved-By: Jane
    ; Approved-Date: 2024/01/14
    ; PO-Number: PO-2024-0042
    Expenses:Equipment    $2500.00
    Assets:Checking
```

## Metadata in Reports

### Group by Metadata

```bash
ledger bal Expenses --group-by "meta(\"Project\")"
```

### Sum by Metadata

```bash
ledger reg --meta Project=Alpha --total
```

### Metadata Statistics

```bash
ledger stats --meta Project
```

## Examples

### Complete Transaction

```ledger
2024/01/15 * (#1234) Office Depot
    ; Receipt: receipts/office-depot-2024-01-15.pdf
    ; Paid-Via: Company Card
    ; Tax-Category: Business Expense
    ; UUID: 550e8400-e29b-41d4-a716-446655440000
    Expenses:Office:Supplies    $150.00
        ; Items: Paper, pens, folders
        ; Quantity: 3 boxes
    Expenses:Office:Equipment   $200.00
        ; Items: Desk lamp
        ; Asset-Tag: LAMP-001
    Liabilities:Company-Card   $-350.00
```

### Multi-Currency with Metadata

```ledger
2024/01/15 * International Conference
    ; Event: PyCon 2024
    ; Location: Pittsburgh, PA
    ; Purpose: Speaking engagement
    Expenses:Travel:Conference    500 EUR @ $1.10
        ; Registration: 200 EUR
        ; Accommodation: 300 EUR
    Assets:Euro-Account          -500 EUR
```

## Best Practices

1. **Consistent key naming** - Use the same keys across transactions
2. **Document your schema** - Keep a list of used metadata keys
3. **Link receipts** - Always attach receipt paths for expenses
4. **Use for filtering** - Design metadata for your reporting needs
5. **Avoid redundancy** - Don't duplicate account hierarchy info
6. **Keep values simple** - Avoid complex nested data

## See Also

- [Tags Specification](tags.md)
- [Transaction Directive](directives/transaction.md)
- [Posting Specification](posting.md)
