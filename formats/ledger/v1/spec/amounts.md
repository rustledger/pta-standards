# Amount Specification

Amounts in Ledger represent quantities of commodities (currencies, stocks, etc.).

## Basic Format

An amount consists of a value and a commodity:

```
[SIGN] COMMODITY_SYMBOL VALUE
[SIGN] VALUE COMMODITY_CODE
```

## Examples

```ledger
$100.00          ; Dollar symbol prefix
100.00 USD       ; Currency code suffix
€50.00           ; Euro symbol prefix
50.00 EUR        ; Euro code suffix
-$25.00          ; Negative with symbol
-25.00 GBP       ; Negative with code
10 AAPL          ; Stock shares
0.5 BTC          ; Cryptocurrency
```

## Components

### Sign

| Sign | Meaning |
|------|---------|
| (none) | Positive |
| `-` | Negative |
| `+` | Explicitly positive |

```ledger
$100.00      ; Positive
-$50.00      ; Negative
+$25.00      ; Explicitly positive (rare)
```

### Commodity

Commodities can be specified as symbols or codes:

#### Symbols (Prefix)

Common currency symbols placed before the value:

| Symbol | Currency |
|--------|----------|
| `$` | US Dollar |
| `€` | Euro |
| `£` | British Pound |
| `¥` | Yen/Yuan |
| `₹` | Indian Rupee |
| `₿` | Bitcoin |

```ledger
$100.00
€50.00
£75.00
```

#### Codes (Suffix)

Three-letter codes placed after the value:

```ledger
100.00 USD
50.00 EUR
75.00 GBP
1000.00 JPY
```

#### Quoted Commodities

For commodities with spaces or special characters:

```ledger
10 "MUTUAL FUND A"
5 "My Company Stock"
```

### Value

The numeric portion with optional formatting:

#### Decimal Separator

```ledger
$1234.56     ; Period (US/UK)
1234,56 EUR  ; Comma (Europe)
```

#### Thousand Separators

```ledger
$1,234.56        ; US format
1.234,56 EUR     ; European format
$1 234.56        ; Space separator
```

#### Scientific Notation

Not typically used but supported:

```ledger
1.5e6 USD    ; 1,500,000 USD
```

## Precision

### Display Precision

Derived from commodity format directive or usage:

```ledger
commodity $
    format $1,000.00

; All USD amounts display with 2 decimal places
2024/01/15 Transaction
    Expenses:Food  $50.00
    Assets:Checking
```

### Internal Precision

Ledger maintains higher internal precision:

```ledger
2024/01/15 Split
    Expenses:A  ($100 / 3)   ; Displays as $33.33
    Expenses:B  ($100 / 3)   ; Displays as $33.33
    Expenses:C               ; Balances to $33.34
    Assets:Checking  $-100
```

### Precision in Calculations

```ledger
; Input: 1/3
; Internal: 0.333333333...
; Display: 0.33 (based on commodity format)
```

## Price Annotations

### Per-unit Price (@)

Specifies the price per unit:

```ledger
10 AAPL @ $150.00
; 10 shares at $150 each = $1500 total

100 EUR @ $1.10
; 100 EUR at $1.10 per EUR = $110 total
```

### Total Price (@@)

Specifies the total price for all units:

```ledger
10 AAPL @@ $1500.00
; 10 shares for $1500 total = $150 each

100 EUR @@ $110.00
; 100 EUR for $110 total
```

## Cost Specifications

### Per-unit Cost ({})

Records acquisition cost:

```ledger
10 AAPL {$150.00}
; Cost basis: $150 per share
```

### Total Cost ({{}})

Records total acquisition cost:

```ledger
10 AAPL {{$1500.00}}
; Total cost: $1500 for all shares
```

### Cost with Date

```ledger
10 AAPL {$150.00} [2024/01/15]
; Cost $150, acquired on 2024/01/15
```

### Cost with Lot Label

```ledger
10 AAPL {$150.00} (lot1)
; Cost $150, labeled "lot1"
```

## Value Expressions

Amounts can include arithmetic:

```ledger
($100 + $50)         ; Addition
($100 - $25)         ; Subtraction
($100 * 2)           ; Multiplication
($100 / 4)           ; Division
($100 * 0.0825)      ; Tax calculation
```

### Expression Functions

```ledger
(abs(-$50))          ; Absolute value
(round($33.333))     ; Rounding
(floor($33.9))       ; Floor
(ceiling($33.1))     ; Ceiling
```

## Commodity Formatting

### Format Directive

```ledger
commodity $
    format $1,000.00
    note US Dollar
    default

commodity EUR
    format 1.000,00 EUR
    note Euro
```

### Display Format Specification

| Format | Description |
|--------|-------------|
| `$1,000.00` | Symbol prefix, comma thousands, period decimal |
| `1.000,00 EUR` | Code suffix, period thousands, comma decimal |
| `1 000,00 €` | Symbol suffix, space thousands |

## Null/Zero Amounts

```ledger
0 USD                ; Explicit zero
$0.00                ; With symbol
; (empty)            ; Elided amount (calculated)
```

## Amount Comparison

Amounts of different commodities cannot be directly compared:

```ledger
; Cannot compare $50 with 50 EUR directly
; Must use price conversion
```

## Validation Rules

1. **Commodity required**: Every amount must have a commodity
2. **Consistent formatting**: Use consistent decimal/thousand separators
3. **Valid characters**: Only digits, separators, and sign
4. **Precision limits**: Implementation-dependent maximum precision

## Examples

### Currency Amounts

```ledger
$1,234.56            ; US Dollar
€1.234,56            ; Euro (European format)
£999.99              ; British Pound
¥10,000              ; Japanese Yen
```

### Investment Amounts

```ledger
100 AAPL             ; 100 shares
0.5 BTC              ; Half a bitcoin
10 VTSAX @ $100.00   ; Mutual fund with price
```

### Complex Amounts

```ledger
10 AAPL {$150.00} [2024/01/15] @ $180.00
; 10 shares, cost $150 each, acquired 2024/01/15, current price $180
```

## See Also

- [Commodity Directive](directives/commodity.md)
- [Posting Specification](posting.md)
- [Value Expressions](../expressions/spec.md)
