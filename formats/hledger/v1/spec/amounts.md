# Amounts Specification

This document specifies how amounts are represented in hledger.

## Overview

An amount consists of:
- Quantity (decimal number)
- Commodity (currency or unit)
- Optional price annotation

## Quantity

### Integer Quantities

```hledger
100
-50
0
1234567890
```

### Decimal Quantities

```hledger
100.00
3.14159
-0.001
.50        ; Leading zero optional
```

### Maximum Precision

hledger supports up to 255 decimal places for internal calculations.

## Commodity Symbols

### Symbol Types

```hledger
$100       ; Currency symbol
100 USD    ; Currency code
100 AAPL   ; Stock ticker
100 kg     ; Unit of measure
100 "gold coins"  ; Quoted commodity
```

### Symbol Position

```hledger
$100       ; Prefix (no space)
$ 100      ; Prefix with space
100 USD    ; Suffix with space
100USD     ; Suffix (no space)
```

### Quoted Commodities

For commodities with spaces or special characters:

```hledger
10 "gold bars"
5 "airline miles"
1 "Bitcoin (BTC)"
```

## Thousand Separators

### Common Formats

```hledger
1,234.56          ; US/UK style
1.234,56          ; European style
1 234,56          ; French style
1'234.56          ; Swiss style
```

### Separator Rules

- Maximum 3 digits between separators
- Thousands separator and decimal mark must differ
- hledger infers format from first usage

## Negative Amounts

```hledger
-$100       ; Minus before commodity
$-100       ; Minus after commodity
-100 USD    ; Minus before quantity
100 USD-    ; Minus after (unusual)
```

## Zero Amounts

```hledger
$0
0 USD
$0.00
EUR 0,00
```

## Commodity Formatting

### Display Precision

```hledger
$1.00       ; 2 decimal places
1.234 BTC   ; 3 decimal places
100 AAPL    ; 0 decimal places (shares)
```

### Format Inference

hledger infers commodity format from the first occurrence:

```hledger
; First use defines format
2024-01-01 Define USD format
    Assets:Bank    $1,234.56
    Equity:Opening

; Subsequent uses follow same format
2024-01-02 Another transaction
    Assets:Bank    $100.00
    Income:Salary
```

## Price Annotations

### Per-Unit Price (@)

```hledger
10 AAPL @ $150.00
; 10 shares at $150 each = $1500 total
```

### Total Price (@@)

```hledger
100 EUR @@ $110.00
; 100 EUR for $110 total (not $11,000)
```

### Price Direction

Price indicates market value, not cost basis:

```hledger
; Buy stock
2024-01-15 Buy Apple
    Assets:Brokerage    10 AAPL @ $150
    Assets:Checking    $-1500

; Sell at different price
2024-02-15 Sell Apple
    Assets:Checking    $1600
    Assets:Brokerage    -10 AAPL @ $160
```

## Amount Expressions

### Basic Arithmetic

```hledger
; Not natively supported in hledger
; Use external preprocessing or timedot format
```

### Calculated Amounts

Use amount inference for one posting:

```hledger
2024-01-15 Split expense
    Expenses:Food    $75.00
    Expenses:Drink   $25.00
    Assets:Checking          ; Calculated as $-100.00
```

## Multi-Commodity Transactions

```hledger
2024-01-15 Currency exchange
    Assets:USD:Checking    $-100
    Assets:EUR:Checking    EUR 90
    Expenses:Fees    $10

; With conversion price
2024-01-15 Exchange with price
    Assets:EUR:Checking    90 EUR @@ $100
    Assets:USD:Checking    $-100
```

## Amount Inference Rules

1. **One missing amount per commodity**: Automatically calculated
2. **Balance requirement**: Sum of all amounts must equal zero
3. **Multiple commodities**: Each must balance separately (or use prices)

### Valid Inference

```hledger
2024-01-15 Valid
    Expenses:Food    $50
    Assets:Checking       ; Inferred: $-50
```

### Invalid Inference

```hledger
; ERROR: Two missing amounts for same commodity
2024-01-15 Invalid
    Expenses:Food
    Expenses:Drink
    Assets:Checking
```

## Amount Validation

### Balance Check

Transaction must sum to zero:

```hledger
; Valid: sums to $0
2024-01-15 Balanced
    Expenses:Food    $50
    Assets:Checking    $-50

; Error: sums to $10
2024-01-15 Unbalanced
    Expenses:Food    $50
    Assets:Checking    $-40
```

### Precision Tolerance

Small rounding differences may be tolerated:

```hledger
; May be accepted due to rounding
2024-01-15 Rounding
    Expenses:A    $33.33
    Expenses:B    $33.33
    Expenses:C    $33.34
    Assets:Checking    $-100.00
```

## Display Options

### Command-Line Formatting

```bash
hledger bal --no-total
hledger bal -B  # Convert to cost basis
hledger bal -V  # Show market value
hledger bal -X USD  # Convert to USD
```

## Examples

### Simple Amount

```hledger
$100.00
```

### With Commodity Code

```hledger
100.00 USD
```

### European Format

```hledger
1.234,56 EUR
```

### Stock with Price

```hledger
100 AAPL @ $150.00
```

### Cryptocurrency

```hledger
0.12345678 BTC @ $40000
```

### Complex Transaction

```hledger
2024-01-15 Investment purchase
    Assets:Brokerage:AAPL    10 AAPL @ $150
    Assets:Brokerage:Cash    $-1500.00
    Expenses:Fees    $9.99
    Assets:Bank:Checking    $-1509.99
```

## See Also

- [Syntax Specification](syntax.md)
- [Posting Specification](posting.md)
- [Commodity Directive](directives/commodity.md)
