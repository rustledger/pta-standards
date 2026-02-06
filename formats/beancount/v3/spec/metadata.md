# Metadata

## Overview

Metadata provides a key-value mechanism for attaching arbitrary data to directives and postings. It enables custom categorization, external references, and tool-specific information.

## Syntax

```ebnf
metadata = INDENT key ":" value

key   = lowercase (alphanumeric | "-" | "_")*
value = string | number | date | account | currency | tag | amount | boolean
```

## Location

### Directive Metadata

Attached to any directive with single indentation:

```beancount
2024-01-15 * "Purchase"
  receipt: "scan.pdf"
  category: "office-supplies"
  Assets:Checking  -100 USD
  Expenses:Office
```

### Posting Metadata

Attached to specific postings with double indentation:

```beancount
2024-01-15 * "Purchase"
  Assets:Checking  -100 USD
    bank-ref: "TXN123456"
    cleared: TRUE
  Expenses:Office   100 USD
    tax-category: "deductible"
```

### Mixed Metadata

Both directive and posting metadata in one transaction:

```beancount
2024-01-15 * "Office supplies"
  vendor: "Staples"                    ; Directive metadata
  invoice: "INV-2024-001"
  Assets:Checking  -156.78 USD
    bank-ref: "CHK-9876"               ; Posting metadata
  Expenses:Office   156.78 USD
    receipt: "receipts/2024/staples.pdf"
```

## Key Format

### Rules

- MUST start with lowercase letter
- MAY contain letters, digits, hyphens, underscores
- Case-sensitive

### Valid Keys

```
receipt
invoice-number
tax_category
ref123
my-custom-key
```

### Invalid Keys

```
Receipt          ; Starts with uppercase
123ref           ; Starts with digit
invoice number   ; Contains space
invoice.number   ; Contains period
```

## Value Types

### String

```beancount
  description: "Monthly subscription"
  filename: "/path/to/file.pdf"
```

### Number

```beancount
  quantity: 5
  rate: 0.0825
  year: 2024
```

### Date

```beancount
  due-date: 2024-02-15
  filed: 2024-04-15
```

### Account

```beancount
  source-account: Assets:Checking
  destination: Expenses:Travel
```

### Currency

```beancount
  base-currency: USD
  commodity: AAPL
```

### Tag

```beancount
  project: #website-redesign
  category: #tax-deductible
```

### Amount

```beancount
  original-amount: 100 EUR
  fee: 2.50 USD
```

### Boolean

```beancount
  reconciled: TRUE
  pending: FALSE
```

## Automatic Metadata

All directives automatically receive:

| Key | Type | Description |
|-----|------|-------------|
| `filename` | String | Source file path |
| `lineno` | Number | Line number in source |

```beancount
; Automatically added by parser:
; filename: "ledger.beancount"
; lineno: 42
```

## Common Metadata Keys

### Financial

| Key | Type | Purpose |
|-----|------|---------|
| `receipt` | String | Receipt file path |
| `invoice` | String | Invoice reference |
| `check` | Number | Check number |
| `bank-ref` | String | Bank reference |
| `confirmation` | String | Confirmation number |

### Categorization

| Key | Type | Purpose |
|-----|------|---------|
| `category` | String | Classification |
| `project` | Tag | Project association |
| `department` | String | Cost center |
| `tax-category` | String | Tax classification |

### Status

| Key | Type | Purpose |
|-----|------|---------|
| `reconciled` | Boolean | Bank reconciled |
| `reviewed` | Boolean | Human reviewed |
| `pending` | Boolean | Awaiting action |
| `approved-by` | String | Approver name |

### External Systems

| Key | Type | Purpose |
|-----|------|---------|
| `quickbooks-id` | String | QB sync ID |
| `stripe-id` | String | Stripe transaction |
| `plaid-id` | String | Plaid transaction |

## Duplicate Keys

Duplicate metadata keys on the same directive produce a warning:

```beancount
2024-01-15 * "Purchase"
  category: "office"
  category: "supplies"    ; Warning: duplicate key
  Assets:Checking  -100 USD
  Expenses:Office
```

Implementations typically use the last value.

## Metadata Inheritance

Posting metadata does NOT inherit from directive metadata:

```beancount
2024-01-15 * "Purchase"
  category: "office"              ; Only on transaction
  Assets:Checking  -100 USD       ; Does NOT have category
  Expenses:Office
    category: "supplies"          ; Separate from transaction
```

## Metadata Stack

### pushmeta / popmeta

Apply metadata to multiple directives:

```beancount
pushmeta project: #q1-initiative

2024-01-15 * "Expense 1"
  ; Automatically has project: #q1-initiative
  Expenses:Marketing  500 USD
  Assets:Checking

2024-01-20 * "Expense 2"
  ; Also has project: #q1-initiative
  Expenses:Marketing  300 USD
  Assets:Checking

popmeta project:
```

### Stack Behavior

```beancount
pushmeta location: "NYC"
pushmeta department: "Sales"

2024-01-15 * "Meeting"
  ; Has both location and department
  Expenses:Meals  50 USD
  Assets:Cash

popmeta department:

2024-01-16 * "Travel"
  ; Has only location
  Expenses:Transport  25 USD
  Assets:Cash

popmeta location:
```

## Querying Metadata

### In BQL

```sql
SELECT date, narration, meta("category")
FROM transactions
WHERE meta("tax-category") = "deductible"
```

### Filtering

```sql
SELECT * FROM postings
WHERE "receipt" IN meta
```

## Metadata on Non-Transaction Directives

### Open

```beancount
2024-01-01 open Assets:Checking USD
  institution: "Bank of America"
  account-number: "****1234"
  routing: "****5678"
```

### Commodity

```beancount
2024-01-01 commodity AAPL
  name: "Apple Inc."
  isin: "US0378331005"
  exchange: "NASDAQ"
```

### Balance

```beancount
2024-02-01 balance Assets:Checking  5000 USD
  source: "bank-statement"
  statement-date: 2024-01-31
```

## Validation

| Warning | Condition |
|---------|-----------|
| E6001 | Duplicate metadata key |
| E6002 | Invalid metadata value type |

Metadata validation is typically lenient—unknown keys are allowed.

## Implementation Notes

1. Parse key as lowercase identifier
2. Parse value based on syntax (quotes → string, etc.)
3. Store as key-value map per directive/posting
4. Inject automatic metadata (filename, lineno)
5. Support metadata stack (pushmeta/popmeta)
6. Enable metadata queries in BQL
