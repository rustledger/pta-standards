# Commodity Directive

## Overview

The `commodity` directive declares a currency or commodity and attaches metadata to it. While currencies can be used without declaration, this directive enables documentation and validation.

## Syntax

```ebnf
commodity = date WHITESPACE "commodity" WHITESPACE currency
            (NEWLINE metadata)*
```

## Components

### Date

The date the commodity is declared. Typically the date it first appears in the ledger or when it was created/issued.

### Currency

The commodity symbol following currency naming rules:
- MUST start with uppercase letter (A-Z)
- MUST end with uppercase letter or digit (A-Z, 0-9)
- Middle characters may include: uppercase letters, digits, apostrophe, period, underscore, dash
- No enforced maximum length (docs mention 24 chars but not enforced)

## Examples

### Basic Declaration

```beancount
2024-01-01 commodity USD
2024-01-01 commodity EUR
2024-01-01 commodity AAPL
```

### With Metadata

```beancount
2024-01-01 commodity USD
  name: "United States Dollar"
  asset-class: "currency"

2024-01-01 commodity AAPL
  name: "Apple Inc."
  asset-class: "stock"
  exchange: "NASDAQ"
  isin: "US0378331005"

2024-01-01 commodity BTC
  name: "Bitcoin"
  asset-class: "cryptocurrency"
  precision: 8
```

### Display Formatting

```beancount
2024-01-01 commodity USD
  name: "US Dollar"
  symbol: "$"
  symbol-position: "prefix"
  precision: 2
  decimal-separator: "."
  group-separator: ","

2024-01-01 commodity EUR
  name: "Euro"
  symbol: "€"
  symbol-position: "suffix"
  precision: 2
```

## Common Metadata Keys

| Key | Type | Description |
|-----|------|-------------|
| `name` | String | Human-readable name |
| `asset-class` | String | Category (currency, stock, crypto, etc.) |
| `precision` | Number | Decimal places for display |
| `symbol` | String | Display symbol ($, €, etc.) |
| `symbol-position` | String | "prefix" or "suffix" |
| `exchange` | String | Trading exchange |
| `isin` | String | International Securities ID |
| `cusip` | String | CUSIP identifier |
| `ticker` | String | Exchange ticker symbol |
| `quote` | Currency | Currency for price quotes |

## Currency Naming

### Valid Names

```
USD     ; US Dollar
EUR     ; Euro
GBP     ; British Pound
AAPL    ; Apple stock
BTC     ; Bitcoin
ETH     ; Ethereum
VTSAX   ; Vanguard fund
VACHR   ; Custom (vacation hours)
AU      ; Gold
AG      ; Silver
```

### Invalid Names

```
usd     ; lowercase not allowed (must start with uppercase)
US D    ; spaces not allowed
$USD    ; special characters at start not allowed
123     ; must start with letter, not digit
USD-    ; cannot end with special character (must end with A-Z or 0-9)
```

## Validation

Undeclared currencies are allowed without error. The `commodity` directive is optional and primarily used for attaching metadata to currencies.

Note: There is NO "strict" option in beancount that requires currency declaration. Plugins may implement stricter currency declaration requirements if needed.

## Multiple Declarations

Multiple declarations of the same commodity produce a validation error:

```beancount
; Initial declaration
2024-01-01 commodity AAPL
  name: "Apple Inc."

; ERROR: Duplicate commodity directives for 'AAPL'
2024-06-01 commodity AAPL
  split: "4:1"
```

To add metadata, include all metadata on the single declaration:

```beancount
2024-01-01 commodity AAPL
  name: "Apple Inc."
  split: "4:1"
  split-date: 2020-08-31
```

## Use Cases

### Documentation

```beancount
2024-01-01 commodity VTSAX
  name: "Vanguard Total Stock Market Index Fund Admiral"
  asset-class: "mutual-fund"
  expense-ratio: 0.04
  benchmark: "CRSP US Total Market Index"
```

### Custom Units

```beancount
; Track vacation hours
2024-01-01 commodity VACHR
  name: "Vacation Hours"
  unit: "hours"

2024-01-01 open Assets:Vacation VACHR
2024-01-01 open Expenses:TimeOff VACHR
2024-01-01 open Income:Accrued VACHR

2024-01-15 * "Vacation accrual"
  Assets:Vacation  8 VACHR
  Income:Accrued
```

### Price Quote Configuration

```beancount
2024-01-01 commodity AAPL
  name: "Apple Inc."
  quote: USD
  price-source: "yahoo"
  ticker: "AAPL"
```

## Implementation Notes

1. Commodity declarations are optional
2. Store metadata for later retrieval
3. Reject duplicate commodity declarations with error
4. Date is informational (doesn't affect validation)
