# Beancount to Ledger Conversion

This specification defines how to convert Beancount files to Ledger format.

## Overview

Beancount and Ledger share core double-entry concepts but differ in syntax and features. This conversion prioritizes semantic preservation over syntactic similarity.

## Directive Mapping

### Transactions

**Beancount:**
```beancount
2024-01-15 * "Whole Foods" "Weekly groceries"
  #food
  Assets:Checking  -50.00 USD
  Expenses:Food:Groceries
```

**Ledger:**
```ledger
2024/01/15 * Whole Foods | Weekly groceries
  ; :food:
  Assets:Checking  $-50.00
  Expenses:Food:Groceries
```

### Conversion Rules

| Beancount | Ledger |
|-----------|--------|
| `2024-01-15` | `2024/01/15` |
| `"Payee" "Narration"` | `Payee \| Narration` |
| `#tag` | `:tag:` |
| `^link` | `; link: ^value` (metadata) |
| `key: "value"` | `; key: value` |

### Open Directive

**Beancount:**
```beancount
2020-01-01 open Assets:Checking USD
```

**Ledger:**
```ledger
; Account opened: 2020-01-01
account Assets:Checking
  ; currency: USD
```

### Close Directive

**Beancount:**
```beancount
2024-12-31 close Assets:OldAccount
```

**Ledger:**
```ledger
; Account closed: 2024-12-31
; account Assets:OldAccount
```

### Balance Directive

**Beancount:**
```beancount
2024-01-31 balance Assets:Checking 1000.00 USD
```

**Ledger:**
```ledger
2024/01/30 * Balance assertion
  Assets:Checking  $0 = $1000.00
```

Note: Beancount checks balance at start of day; Ledger checks after posting. Use previous day.

### Commodity Directive

**Beancount:**
```beancount
2020-01-01 commodity USD
  name: "US Dollar"
```

**Ledger:**
```ledger
commodity $
  format $1,000.00
  ; name: US Dollar
```

### Price Directive

**Beancount:**
```beancount
2024-01-15 price AAPL 185.00 USD
```

**Ledger:**
```ledger
P 2024/01/15 AAPL $185.00
```

### Pad Directive

**Beancount:**
```beancount
2024-01-01 pad Assets:Checking Equity:Opening
2024-01-02 balance Assets:Checking 1000.00 USD
```

**Ledger:** (expand to explicit transaction)
```ledger
2024/01/01 * Padding transaction
  ; Converted from beancount pad directive
  Assets:Checking  $1000.00
  Equity:Opening  $-1000.00

2024/01/01 * Balance assertion
  Assets:Checking  $0 = $1000.00
```

### Non-Convertible Directives

These have no Ledger equivalent and become comments:

```ledger
; BEANCOUNT document 2024-01-15 Assets:Checking "/path/to/statement.pdf"
; BEANCOUNT event 2024-01-15 "location" "New York"
; BEANCOUNT note 2024-01-15 Assets:Checking "Account note"
; BEANCOUNT query 2024-01-15 "myquery" "SELECT ..."
; BEANCOUNT custom 2024-01-15 "budget" Assets:Food 500 USD
```

## Amount Formatting

### Currency Position

**Beancount** (always suffix):
```beancount
100.00 USD
```

**Ledger** (prefix or suffix):
```ledger
$100.00
; or
100.00 USD
```

### Cost Basis

**Beancount:**
```beancount
10 AAPL {185.00 USD}
10 AAPL {185.00 USD, 2024-01-15}
```

**Ledger:**
```ledger
10 AAPL {$185.00}
10 AAPL {$185.00} [2024/01/15]
```

### Price Annotation

**Beancount:**
```beancount
10 AAPL @ 185.00 USD
10 AAPL @@ 1850.00 USD
```

**Ledger:**
```ledger
10 AAPL @ $185.00
10 AAPL @@ $1850.00
```

## Metadata

### Transaction Metadata

**Beancount:**
```beancount
2024-01-15 * "Payee"
  category: "food"
  receipt: "/path/to/receipt.pdf"
  Assets:Checking  -50.00 USD
```

**Ledger:**
```ledger
2024/01/15 * Payee
  ; category: food
  ; receipt: /path/to/receipt.pdf
  Assets:Checking  $-50.00
```

### Posting Metadata

**Beancount:**
```beancount
2024-01-15 * "Payee"
  Assets:Checking  -50.00 USD
    note: "ATM withdrawal"
```

**Ledger:**
```ledger
2024/01/15 * Payee
  Assets:Checking  $-50.00
    ; note: ATM withdrawal
```

## Tags and Links

### Tags

**Beancount:**
```beancount
2024-01-15 * "Payee" #travel #business
  Assets:Checking  -500.00 USD
```

**Ledger:**
```ledger
2024/01/15 * Payee
  ; :travel:business:
  Assets:Checking  $-500.00
```

### Links

**Beancount:**
```beancount
2024-01-15 * "Payee" ^invoice-123
  Assets:Checking  -500.00 USD
```

**Ledger:**
```ledger
2024/01/15 * Payee
  ; link: invoice-123
  Assets:Checking  $-500.00
```

## Includes

**Beancount:**
```beancount
include "accounts.beancount"
```

**Ledger:**
```ledger
include accounts.ledger
```

## Plugin Handling

Beancount plugins must be executed before conversion. The converter should:

1. Load the Beancount file with plugins
2. Get the resulting directive stream
3. Convert the post-plugin directives

## Algorithm

```
1. Parse Beancount file (with plugins)
2. For each directive:
   a. Map date format (- to /)
   b. Convert directive type
   c. Transform amounts and currencies
   d. Convert metadata syntax
   e. Handle tags and links
3. Generate Ledger output
4. Emit warnings for non-convertible features
```

## See Also

- [Edge Cases](edge-cases.md)
- [Loss Matrix](../loss-matrix.md)
