# Document Directive

## Overview

The `document` directive links an external file (receipt, statement, contract) to an account at a specific date. It creates a paper trail connecting financial records to supporting documentation.

## Syntax

```ebnf
document = date WHITESPACE "document" WHITESPACE account WHITESPACE path
           [WHITESPACE tags_links]*
           (NEWLINE metadata)*

path = string
```

## Components

### Date

The date the document is associated with (typically the date on the document).

### Account

The account the document relates to.

### Path

A string containing the file path to the document. Can be:
- Relative path (resolved from the ledger file's directory)
- Absolute path

### Tags and Links

Optional tags and links to categorize or connect documents.

## Examples

### Basic Document

```beancount
2024-01-01 open Assets:Checking USD

2024-01-15 document Assets:Checking "documents/2024/01/bank-statement.pdf"
```

### Receipt Attachment

```beancount
2024-01-15 document Expenses:Office "receipts/2024/01/staples-receipt.jpg"
  amount: "125.50 USD"
  vendor: "Staples"
```

### With Tags

```beancount
2024-01-15 document Assets:Checking "statements/2024-01.pdf" #statement #monthly
```

### With Links

```beancount
2024-01-15 document Liabilities:Mortgage "contracts/mortgage-agreement.pdf" ^mortgage-2024
```

### Multiple Documents

```beancount
; Monthly statements
2024-01-01 document Assets:Checking "statements/2024-01-checking.pdf"
2024-02-01 document Assets:Checking "statements/2024-02-checking.pdf"
2024-03-01 document Assets:Checking "statements/2024-03-checking.pdf"
```

## Path Resolution

### Relative Paths

Relative paths are resolved from the directory containing the ledger file:

```
/home/user/finances/
├── ledger.beancount
├── documents/
│   └── 2024/
│       └── receipt.pdf
```

```beancount
; In ledger.beancount
2024-01-15 document Expenses:Food "documents/2024/receipt.pdf"
; Resolves to: /home/user/finances/documents/2024/receipt.pdf
```

### Absolute Paths

Absolute paths are used as-is:

```beancount
2024-01-15 document Assets:Checking "/mnt/archive/statements/2024-01.pdf"
```

### Document Root

A document root can be configured:

```beancount
option "documents" "/home/user/finances/docs"

; Paths resolve relative to document root
2024-01-15 document Assets:Checking "statements/2024-01.pdf"
; Resolves to: /home/user/finances/docs/statements/2024-01.pdf
```

## Automatic Document Discovery

Some implementations scan directories for documents matching patterns:

```beancount
option "documents" "/home/user/Documents/Financial"

; Automatically discovers:
; /home/user/Documents/Financial/Assets/Checking/2024-01-15.statement.pdf
; Creates: 2024-01-15 document Assets:Checking "Assets/Checking/2024-01-15.statement.pdf"
```

Directory structure convention:
```
documents/
├── Assets/
│   └── Checking/
│       ├── 2024-01-15.statement.pdf
│       └── 2024-02-15.statement.pdf
├── Expenses/
│   └── Office/
│       └── 2024-01-20.receipt.staples.jpg
```

## Validation

| Error | Condition |
|-------|-----------|
| E8001 | Document file not found |
| E1001 | Account not opened |

### File Existence Check

By default, implementations warn if the file doesn't exist:

```
warning: Document file not found
  --> ledger.beancount:15:1
   |
15 | 2024-01-15 document Assets:Checking "missing.pdf"
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ file does not exist
   |
   = path: /home/user/finances/missing.pdf
```

This can be configured:

```beancount
option "document_check" "error"    ; Treat missing files as errors
option "document_check" "warning"  ; Warn only (default)
option "document_check" "ignore"   ; No checking
```

## Common Document Types

| Type | Extension | Use Case |
|------|-----------|----------|
| PDF | `.pdf` | Statements, contracts, invoices |
| Image | `.jpg`, `.png` | Receipts, photos of documents |
| Scan | `.tiff` | High-quality scans |
| Text | `.txt` | Notes, text exports |

## Metadata

Common metadata keys:

```beancount
2024-01-15 document Assets:Checking "statement.pdf"
  type: "bank-statement"
  period: "2024-01"
  pages: 3
  file-hash: "sha256:abc123..."
```

## Linking to Transactions

Documents can be linked to related transactions:

```beancount
2024-01-15 * "Office Supplies" ^purchase-001
  Expenses:Office  125.50 USD
  Assets:Checking

2024-01-15 document Expenses:Office "receipts/staples.pdf" ^purchase-001
```

Or using transaction metadata:

```beancount
2024-01-15 * "Office Supplies"
  document: "receipts/staples.pdf"
  Expenses:Office  125.50 USD
  Assets:Checking
```

## Use Cases

### Tax Documentation

```beancount
; Keep all tax-relevant documents
2024-12-31 document Income:Salary "tax/2024/w2.pdf" #tax-2024
2024-12-31 document Assets:Brokerage "tax/2024/1099-div.pdf" #tax-2024
2024-12-31 document Assets:Brokerage "tax/2024/1099-b.pdf" #tax-2024
```

### Contract Archive

```beancount
2024-01-01 document Liabilities:Mortgage "contracts/mortgage-note.pdf"
  signed-date: 2024-01-01
  term: "30 years"
  rate: "6.5%"
```

### Receipt Organization

```beancount
2024-01-15 document Expenses:Business:Travel "receipts/2024/flight-nyc.pdf"
2024-01-16 document Expenses:Business:Travel "receipts/2024/hotel-nyc.pdf"
2024-01-17 document Expenses:Business:Meals "receipts/2024/dinner-client.jpg"
```

## Implementation Notes

1. Store document references indexed by account and date
2. Validate file existence (configurable)
3. Support relative and absolute paths
4. Enable document discovery from configured directories
5. Documents don't affect financial calculations
