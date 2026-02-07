# Syntax Comparison

Side-by-side syntax comparison of Beancount, Ledger, and hledger.

## File Structure

### Beancount
```beancount
option "title" "My Ledger"
option "operating_currency" "USD"

include "accounts.beancount"

2020-01-01 open Assets:Checking USD

2024-01-15 * "Payee" "Description"
  Assets:Checking  -50.00 USD
  Expenses:Food
```

### Ledger
```ledger
; -*- ledger -*-
; My Ledger

include accounts.ledger

account Assets:Checking

2024/01/15 * Payee
    ; Description
    Assets:Checking    $-50.00
    Expenses:Food
```

### hledger
```hledger
; My Ledger

include accounts.journal

account Assets:Checking

2024-01-15 * Payee | Description
    Assets:Checking    $-50.00
    Expenses:Food
```

## Transactions

### Date Format

| Format | Beancount | Ledger | hledger |
|--------|-----------|--------|---------|
| ISO | `2024-01-15` | `2024-01-15` | `2024-01-15` |
| Slashes | ❌ | `2024/01/15` | `2024/01/15` |
| Dots | ❌ | `2024.01.15` | `2024.01.15` |

### Transaction Header

**Beancount:**
```beancount
2024-01-15 * "Payee Name" "Transaction description"
2024-01-15 ! "Pending payee"
2024-01-15 txn "Just description"
```

**Ledger:**
```ledger
2024/01/15 * Payee Name
    ; Transaction description
2024/01/15 ! Pending payee
2024/01/15 Unmarked payee
```

**hledger:**
```hledger
2024-01-15 * Payee Name | Transaction description
2024-01-15 ! Pending payee
2024-01-15 Unmarked payee
```

### Postings

**Beancount:**
```beancount
  Assets:Checking  -100.00 USD
  Assets:Checking  -100.00 USD  ; comment
  Expenses:Food  ; elided amount
```

**Ledger:**
```ledger
    Assets:Checking    $-100.00
    Assets:Checking    $-100.00  ; comment
    Expenses:Food
```

**hledger:**
```hledger
    Assets:Checking    $-100.00
    Assets:Checking    $-100.00  ; comment
    Expenses:Food
```

## Amounts

### Currency Position

| Example | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Prefix | ❌ | `$100` | `$100` |
| Suffix | `100 USD` | `100 USD` | `100 USD` |

### Negative Amounts

```
Beancount:  -100.00 USD
Ledger:     $-100.00  or  -$100.00
hledger:    $-100.00  or  -$100.00
```

### Decimal Precision

All three preserve arbitrary precision:
```
100.123456789 USD
```

## Accounts

### Declaration

**Beancount:** (required)
```beancount
2020-01-01 open Assets:Checking USD
2020-01-01 open Assets:Checking USD, EUR
```

**Ledger:** (optional)
```ledger
account Assets:Checking
    note My checking account
    alias checking
```

**hledger:** (optional)
```hledger
account Assets:Checking  ; type: A
    alias checking
```

### Account Types

| Type | Beancount | Ledger | hledger |
|------|-----------|--------|---------|
| Asset | `Assets:*` prefix | directive | directive/type |
| Liability | `Liabilities:*` | directive | directive/type |
| Equity | `Equity:*` | directive | directive/type |
| Income | `Income:*` | directive | directive/type |
| Expense | `Expenses:*` | directive | directive/type |

## Metadata

### Transaction Level

**Beancount:**
```beancount
2024-01-15 * "Payee"
  category: "groceries"
  receipt: "/path/to/file"
```

**Ledger/hledger:**
```ledger
2024/01/15 * Payee
    ; category: groceries
    ; receipt: /path/to/file
```

### Posting Level

**Beancount:**
```beancount
  Expenses:Food  50.00 USD
    memo: "snacks"
```

**Ledger/hledger:**
```ledger
    Expenses:Food    $50.00
      ; memo: snacks
```

## Tags

**Beancount:**
```beancount
2024-01-15 * "Payee" #travel #business
  ^invoice-123
```

**Ledger:**
```ledger
2024/01/15 * Payee
    ; :travel:business:
    ; link: invoice-123
```

**hledger:**
```hledger
2024-01-15 * Payee  ; travel:, business:
    ; link: invoice-123
```

## Comments

**All three:**
```
; Single line comment
# Also works in Ledger/hledger

2024-01-15 * Payee
    ; Inline comment
    Account  $100  ; End of line
```

**Block comments:**
- Beancount: Use `;` on each line
- Ledger: `comment ... end comment`
- hledger: Use `;` on each line

## Balance Assertions

**Beancount:**
```beancount
2024-01-31 balance Assets:Checking 1000.00 USD
```

**Ledger:**
```ledger
2024/01/31 * Balance check
    Assets:Checking    $0 = $1000.00
```

**hledger:**
```hledger
2024-01-31 * Balance check
    Assets:Checking    $0 = $1000.00
    ; Also: == for total, =* for subaccounts
```

## Prices

### Price Directive

**Beancount:**
```beancount
2024-01-15 price AAPL 185.00 USD
```

**Ledger/hledger:**
```
P 2024/01/15 AAPL $185.00
```

### Inline Price

**All three:**
```
10 AAPL @ 185.00 USD    ; Unit price
10 AAPL @@ 1850.00 USD  ; Total price
```

## Cost Basis

**Beancount:**
```beancount
10 AAPL {185.00 USD}
10 AAPL {185.00 USD, 2024-01-15}
10 AAPL {185.00 USD, 2024-01-15, "mylot"}
```

**Ledger:**
```ledger
10 AAPL {$185.00}
10 AAPL {$185.00} [2024/01/15]
10 AAPL {$185.00} [2024/01/15] (mylot)
```

**hledger:**
```hledger
10 AAPL @ $185.00
    ; lot-date: 2024-01-15
```

## Includes

**Beancount:**
```beancount
include "subdir/file.beancount"
```

**Ledger:**
```ledger
include subdir/file.ledger
include ~/ledger/*.ledger
```

**hledger:**
```hledger
include subdir/file.journal
```

## See Also

- [Feature Comparison](features.md)
- [Philosophy Comparison](philosophy.md)
