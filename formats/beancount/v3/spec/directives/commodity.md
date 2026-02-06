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
- All uppercase letters
- 1-24 characters
- May contain letters, digits, apostrophe, period, underscore, dash

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
usd     ; lowercase not allowed
US D    ; spaces not allowed
$USD    ; special characters at start
123     ; must start with letter
ABCDEFGHIJKLMNOPQRSTUVWXYZ  ; too long (>24 chars)
```

## Strict Mode

When strict mode is enabled, all currencies must be declared:

```beancount
option "strict" "TRUE"

2024-01-01 commodity USD
2024-01-01 commodity EUR

2024-01-15 * "Valid"
  Assets:Cash  100 USD    ; OK - USD declared
  Expenses:Food

2024-01-16 * "Invalid"
  Assets:Cash  100 GBP    ; ERROR - GBP not declared
  Expenses:Food
```

## Validation

| Error | Condition |
|-------|-----------|
| E5001 | Currency not declared (strict mode only) |

In non-strict mode (default), undeclared currencies are allowed but may generate warnings.

## Multiple Declarations

Multiple declarations of the same commodity merge their metadata:

```beancount
; Initial declaration
2024-01-01 commodity AAPL
  name: "Apple Inc."

; Later addition of metadata
2024-06-01 commodity AAPL
  split: "4:1"
  split-date: 2020-08-31
```

The later declaration adds to (or overrides) the earlier metadata.

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

1. Commodity declarations are optional in default mode
2. Store metadata for later retrieval
3. Merge metadata from multiple declarations
4. In strict mode, validate all currency uses
5. Date is informational (doesn't affect validation)
