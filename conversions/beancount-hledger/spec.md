# Beancount to hledger Conversion

This specification defines how to convert Beancount files to hledger format.

## Overview

Beancount and hledger have high syntactic compatibility. The main differences are in directives and metadata syntax.

## Directive Mapping

### Transactions

**Beancount:**
```beancount
2024-01-15 * "Whole Foods" "Weekly groceries"
  #food
  Assets:Checking  -50.00 USD
  Expenses:Food:Groceries
```

**hledger:**
```hledger
2024-01-15 * Whole Foods | Weekly groceries
  ; food:
  Assets:Checking  -50.00 USD
  Expenses:Food:Groceries
```

### Conversion Rules

| Beancount | hledger |
|-----------|---------|
| `2024-01-15` | `2024-01-15` (same) |
| `"Payee" "Narration"` | `Payee \| Narration` |
| `#tag` | `tag:` |
| `^link` | `; link: value` |
| `key: "value"` | `; key: value` |

### Open Directive

**Beancount:**
```beancount
2020-01-01 open Assets:Checking USD
```

**hledger:**
```hledger
; Opened: 2020-01-01
account Assets:Checking
  ; currency: USD
```

### Close Directive

**Beancount:**
```beancount
2024-12-31 close Assets:OldAccount
```

**hledger:**
```hledger
; Closed: 2024-12-31
; account Assets:OldAccount
```

### Balance Directive

**Beancount:**
```beancount
2024-01-31 balance Assets:Checking 1000.00 USD
```

**hledger:**
```hledger
2024-01-30 * Balance assertion
  Assets:Checking  0 = 1000.00 USD
```

Note: Date adjustment for timing difference (Beancount: start of day, hledger: after posting).

### Commodity Directive

**Beancount:**
```beancount
2020-01-01 commodity USD
  name: "US Dollar"
```

**hledger:**
```hledger
commodity 1,000.00 USD
  ; name: US Dollar
```

### Price Directive

**Beancount:**
```beancount
2024-01-15 price AAPL 185.00 USD
```

**hledger:**
```hledger
P 2024-01-15 AAPL 185.00 USD
```

### Pad Directive

**Beancount:**
```beancount
2024-01-01 pad Assets:Checking Equity:Opening
2024-01-02 balance Assets:Checking 1000.00 USD
```

**hledger:** (expand to explicit transaction)
```hledger
2024-01-01 * Padding transaction
  ; Converted from beancount pad directive
  Assets:Checking  1000.00 USD
  Equity:Opening

2024-01-01 * Balance assertion
  Assets:Checking  0 = 1000.00 USD
```

### Non-Convertible Directives

```hledger
; BEANCOUNT document 2024-01-15 Assets:Checking "/path/to/statement.pdf"
; BEANCOUNT event 2024-01-15 "location" "New York"
; BEANCOUNT note 2024-01-15 Assets:Checking "Account note"
; BEANCOUNT query 2024-01-15 "myquery" "SELECT ..."
; BEANCOUNT custom 2024-01-15 "budget" Assets:Food 500 USD
```

## Amount Formatting

### Currency Position

Both formats support suffix position. hledger also supports prefix.

**Beancount:**
```beancount
100.00 USD
```

**hledger:**
```hledger
100.00 USD
; or
USD 100.00
```

### Cost Basis

**Beancount:**
```beancount
10 AAPL {185.00 USD}
10 AAPL {185.00 USD, 2024-01-15}
```

**hledger:**
```hledger
10 AAPL @ 185.00 USD
10 AAPL @ 185.00 USD
  ; lot-date: 2024-01-15
```

Note: hledger's lot syntax differs from Beancount's.

### Price Annotation

**Beancount:**
```beancount
10 AAPL @ 185.00 USD
10 AAPL @@ 1850.00 USD
```

**hledger:**
```hledger
10 AAPL @ 185.00 USD
10 AAPL @@ 1850.00 USD
```

## Metadata

### Transaction Metadata

**Beancount:**
```beancount
2024-01-15 * "Payee"
  category: "food"
  Assets:Checking  -50.00 USD
```

**hledger:**
```hledger
2024-01-15 * Payee
  ; category: food
  Assets:Checking  -50.00 USD
```

### Posting Metadata

**Beancount:**
```beancount
2024-01-15 * "Payee"
  Assets:Checking  -50.00 USD
    note: "ATM withdrawal"
```

**hledger:**
```hledger
2024-01-15 * Payee
  Assets:Checking  -50.00 USD
    ; note: ATM withdrawal
```

## Tags and Links

### Tags

**Beancount:**
```beancount
2024-01-15 * "Payee" #travel #business
  Assets:Checking  -500.00 USD
```

**hledger:**
```hledger
2024-01-15 * Payee
  ; travel:, business:
  Assets:Checking  -500.00 USD
```

### Links

**Beancount:**
```beancount
2024-01-15 * "Payee" ^invoice-123
  Assets:Checking  -500.00 USD
```

**hledger:**
```hledger
2024-01-15 * Payee
  ; link: invoice-123
  Assets:Checking  -500.00 USD
```

## Balance Assertions

### Simple Assertion

**Beancount:**
```beancount
2024-01-31 balance Assets:Checking 1000.00 USD
```

**hledger:**
```hledger
2024-01-30 Balance check
  Assets:Checking  0 = 1000.00 USD
```

### Multi-Currency

**Beancount:**
```beancount
2024-01-31 balance Assets:Checking 1000.00 USD
2024-01-31 balance Assets:Checking 500.00 EUR
```

**hledger:**
```hledger
2024-01-30 Balance check USD
  Assets:Checking  0 USD = 1000.00 USD

2024-01-30 Balance check EUR
  Assets:Checking  0 EUR = 500.00 EUR
```

## Includes

**Beancount:**
```beancount
include "accounts.beancount"
```

**hledger:**
```hledger
include accounts.journal
```

## Algorithm

```
1. Parse Beancount file (with plugins)
2. For each directive:
   a. Keep date format (ISO 8601)
   b. Convert directive type
   c. Adjust currency position if needed
   d. Convert metadata syntax
   e. Transform tags
3. Generate hledger output
4. Emit warnings for non-convertible features
```

## See Also

- [Edge Cases](edge-cases.md)
- [Loss Matrix](../loss-matrix.md)
