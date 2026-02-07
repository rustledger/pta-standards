# Tag Directive

The `tag` directive declares a tag name for validation.

## Syntax

```hledger
tag NAME
```

## Basic Declaration

```hledger
tag project
tag category
tag location
```

## Purpose

Tag declarations enable:

1. **Validation** - Warn on unknown tags
2. **Documentation** - List expected tags
3. **Completion** - Editor autocomplete

## Tag Names

### Valid Names

```hledger
tag project
tag category
tag vendor
tag receipt
tag approved-by
tag tax_year
```

### Naming Rules

- Letters, numbers, hyphens, underscores
- Case-sensitive
- No spaces

## Usage in Transactions

Tags appear in comments with `name:value` format:

```hledger
tag project
tag location

2024-01-15 Office supplies  ; project:renovation, location:hq
    Expenses:Office    $100
    Assets:Checking
```

## Tag Placement

### Transaction-Level Tags

```hledger
2024-01-15 Conference travel
    ; project:annual-conf
    ; approved-by:manager
    Expenses:Travel    $500
    Assets:Checking
```

### Posting-Level Tags

```hledger
2024-01-15 Split expense
    Expenses:Food    $50    ; project:team-lunch
    Expenses:Travel  $100   ; project:client-visit
    Assets:Checking
```

### Inline Tags

```hledger
2024-01-15 Purchase  ; vendor:Amazon, category:electronics
    Expenses:Electronics    $200
    Assets:Checking
```

## Tag Values

Tags can have values:

```hledger
; project:renovation     ; Tag with value
; approved:              ; Tag without value (empty)
; verified               ; Just a word (not a proper tag)
```

## Multiple Tags

```hledger
tag project
tag location
tag department
tag approved-by

2024-01-15 Office renovation
    ; project:hq-renovation
    ; location:building-a
    ; department:facilities
    ; approved-by:john-smith
    Expenses:Renovation    $5000
    Assets:Checking
```

## Validation Mode

With `--strict` or strict checking:

```hledger
tag project
tag approved

2024-01-15 Expense  ; project:alpha, priority:high
    ; Warning: unknown tag 'priority'
    Expenses:Misc    $100
    Assets:Checking
```

## Querying by Tag

```bash
# Find transactions with tag
hledger reg tag:project

# Find specific tag value
hledger reg tag:project=renovation

# Multiple tag conditions
hledger reg tag:project=alpha tag:approved
```

## Use Cases

### Project Tracking

```hledger
tag project

2024-01-15 Materials  ; project:kitchen-remodel
    Expenses:Materials    $500
    Assets:Checking

2024-01-16 Labor  ; project:kitchen-remodel
    Expenses:Labor    $1000
    Assets:Checking
```

### Expense Categories

```hledger
tag category
tag vendor
tag receipt

2024-01-15 Office supplies  ; category:office, vendor:Staples, receipt:IMG_001.jpg
    Expenses:Office    $75
    Assets:Checking
```

### Approval Workflow

```hledger
tag status
tag approved-by
tag approved-date

2024-01-15 Large purchase
    ; status:pending
    ; approved-by:manager
    ; approved-date:2024-01-16
    Expenses:Equipment    $5000
    Assets:Checking
```

### Tax Tracking

```hledger
tag tax-year
tag deductible
tag category

2024-01-15 Business lunch
    ; tax-year:2024
    ; deductible:yes
    ; category:meals
    Expenses:Meals    $50
    Assets:Checking
```

## Tag Conventions

| Tag | Purpose |
|-----|---------|
| `project` | Project allocation |
| `vendor` | Supplier/merchant |
| `receipt` | Receipt file reference |
| `category` | Classification |
| `approved-by` | Approver name |
| `note` | Additional notes |
| `date` | Override posting date |

## Complete Example

```hledger
; ===== Tag Declarations =====

; Project tracking
tag project
tag phase
tag billable

; Documentation
tag receipt
tag invoice
tag contract

; Workflow
tag status
tag approved-by
tag reviewed-by

; Classification
tag category
tag department
tag cost-center

; ===== Transactions =====

2024-01-15 Client meeting lunch
    ; project:alpha
    ; phase:discovery
    ; billable:yes
    ; receipt:receipts/2024/01/IMG_0123.jpg
    Expenses:Meals:Client    $75.00
    Assets:Checking

2024-01-20 Office equipment
    ; category:equipment
    ; department:engineering
    ; cost-center:R&D
    ; approved-by:director
    ; invoice:INV-2024-001
    Expenses:Equipment    $2500.00
    Assets:Checking

2024-01-25 Software subscription
    ; category:software
    ; billable:no
    ; status:auto-renewed
    Expenses:Software    $50.00
    Liabilities:Credit Card
```

## Command Line

```bash
# List all tags
hledger tags

# Show tag values
hledger tags project

# Check for unknown tags
hledger check tags
```

## See Also

- [Transaction Directive](transaction.md)
- [Account Directive](account.md)
- [Payee Directive](payee.md)
