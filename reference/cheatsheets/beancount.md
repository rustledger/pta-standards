# Beancount Cheat Sheet

Quick reference for Beancount syntax.

## Directives

### Transaction

```beancount
YYYY-MM-DD * "Payee" "Narration"
  Account:One    100.00 USD
  Account:Two   -100.00 USD

YYYY-MM-DD ! "Pending transaction"
  Account:One    100.00 USD
  Account:Two
```

### Open / Close Account

```beancount
YYYY-MM-DD open Account:Name [Currency,...] ["BookingMethod"]
YYYY-MM-DD close Account:Name
```

### Balance Assertion

```beancount
YYYY-MM-DD balance Account:Name  Amount Currency
YYYY-MM-DD balance Account:Name  Amount Currency ~ Tolerance
```

### Pad

```beancount
YYYY-MM-DD pad Account:Target Account:Source
```

### Price

```beancount
YYYY-MM-DD price COMMODITY  Amount Currency
```

### Note / Document / Event

```beancount
YYYY-MM-DD note Account:Name "Description"
YYYY-MM-DD document Account:Name "/path/to/file.pdf"
YYYY-MM-DD event "event-type" "value"
```

### Commodity / Query / Custom

```beancount
YYYY-MM-DD commodity CURRENCY
YYYY-MM-DD query "name" "SELECT ..."
YYYY-MM-DD custom "type" value1 value2
```

## Global Directives

```beancount
option "name" "value"
plugin "module.name" "config"
include "path/to/file.beancount"
pushtag #tag-name
poptag #tag-name
```

## Account Names

```
Assets:Bank:Checking
Liabilities:CreditCard:Chase
Equity:Opening-Balances
Income:Salary:Employer
Expenses:Food:Groceries
```

Root types: `Assets`, `Liabilities`, `Equity`, `Income`, `Expenses`

## Amounts

```beancount
100.00 USD           ; Simple amount
-50 EUR              ; Negative
1,234.56 CAD         ; With grouping
(100 / 3) USD        ; Expression
```

## Cost Specifications

```beancount
{100.00 USD}                    ; Per-unit cost
{100.00 USD, 2024-01-15}        ; With date
{100.00 USD, "lot-id"}          ; With label
{100.00 + 9.95 USD}             ; With commission
{{1000.00 USD}}                 ; Total cost
{*}                             ; Average cost merge
{}                              ; Match any lot
```

## Price Annotations

```beancount
@ 1.20 CAD           ; Per-unit price
@@ 120.00 CAD        ; Total price
```

## Complete Posting Examples

```beancount
; Simple
Assets:Cash  100.00 USD

; With cost (buy)
Assets:Stock  10 AAPL {150.00 USD}

; With cost and price (sell)
Assets:Stock  -10 AAPL {150.00 USD} @ 180.00 USD

; With cost, date, label
Assets:Stock  10 AAPL {150.00 USD, 2024-01-15, "lot-1"}

; Elided amount (auto-calculated)
Expenses:Food
```

## Tags and Links

```beancount
2024-01-15 * "Transaction" #tag1 #tag2 ^link-id
  ...
```

## Metadata

```beancount
2024-01-15 * "Transaction"
  key: "string value"
  number: 123.45
  date: 2024-01-15
  Assets:Cash  100.00 USD
    posting-meta: "value"
```

## Comments

```beancount
; Full line comment
2024-01-15 * "Transaction"  ; Inline comment
  Assets:Cash  100.00 USD   ; Posting comment
```

## Booking Methods

| Method | Behavior |
|--------|----------|
| `STRICT` | Error on ambiguous match (default) |
| `FIFO` | First-in, first-out |
| `LIFO` | Last-in, first-out |
| `AVERAGE` | Weighted average cost |
| `AVERAGE_ONLY` | Average on both buy and sell |
| `NONE` | No lot matching |

## Common Options

```beancount
option "title" "My Ledger"
option "operating_currency" "USD"
option "booking_method" "FIFO"
option "inferred_tolerance_default" "USD:0.005"
```

## BQL Quick Reference

```sql
; Select postings
SELECT date, account, position WHERE account ~ "Expenses:"

; Aggregate
SELECT account, SUM(position) GROUP BY account

; Filter transactions
SELECT * FROM year = 2024 WHERE account ~ "Assets:"

; Balance sheet
SELECT account, SUM(position)
FROM OPEN ON 2024-01-01 CLOSE ON 2024-12-31 CLEAR
WHERE account ~ "^(Assets|Liabilities)"
GROUP BY 1

; Shortcuts
JOURNAL "Assets:Checking"
BALANCES
PRINT
```

## File Organization

```
main.beancount
├── accounts.beancount      ; Account definitions
├── prices.beancount        ; Price history
├── 2024/
│   ├── 01-january.beancount
│   ├── 02-february.beancount
│   └── ...
└── importers/
    └── bank-statements/
```
