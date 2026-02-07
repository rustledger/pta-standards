# Commodity Directive

The `commodity` directive declares a commodity and its display format.

## Syntax

```hledger
commodity AMOUNT
```

Or with subdirectives:

```hledger
commodity SYMBOL
    format AMOUNT
```

## Basic Declaration

```hledger
commodity $1,000.00
commodity 1.000,00 EUR
commodity 1000.00000000 BTC
```

## Format Specification

The amount in the directive specifies:

1. **Symbol position** - Before or after quantity
2. **Symbol spacing** - Space between symbol and number
3. **Thousand separator** - Character grouping thousands
4. **Decimal separator** - Character for decimals
5. **Decimal precision** - Number of decimal places

### Examples

```hledger
; US Dollar: symbol before, comma thousands, period decimal, 2 places
commodity $1,000.00

; Euro (German): symbol after, period thousands, comma decimal, 2 places
commodity 1.000,00 EUR

; Japanese Yen: symbol before, comma thousands, no decimals
commodity ¥1,000

; Bitcoin: symbol after, no thousands, period decimal, 8 places
commodity 1.00000000 BTC

; Stock shares: no symbol, no decimals
commodity 1000 AAPL
```

## Subdirective Format

More explicit style:

```hledger
commodity USD
    format $1,000.00

commodity EUR
    format 1.000,00 EUR

commodity BTC
    format 1.00000000 BTC
```

## Multiple Commodities

```hledger
; Primary currencies
commodity $1,000.00
commodity 1.000,00 EUR
commodity £1,000.00

; Cryptocurrencies
commodity 1.00000000 BTC
commodity 1.000000000000000000 ETH

; Stocks
commodity 1 AAPL
commodity 1 GOOG
```

## Format Inference

Without declaration, hledger infers format from first use:

```hledger
; First use defines format
2024-01-01 Opening
    Assets:Bank    $1,234.56
    Equity:Opening

; Subsequent amounts use same format
2024-01-02 Income
    Assets:Bank    $100.00    ; Formatted as $100.00
    Income:Salary
```

## Quoted Commodities

For commodities with special characters:

```hledger
commodity 1.00 "gold oz"
commodity 1 "airline miles"
commodity 1.000000 "ACME Corp"
```

## Display Rounding

The declared precision affects display rounding:

```hledger
commodity $1.00

2024-01-15 Third split
    Expenses:A    $33.33
    Expenses:B    $33.33
    Expenses:C    $33.34    ; Rounded for display
    Assets:Checking    $-100.00
```

## Decimal Mark Directive

Alternative way to specify decimal separator:

```hledger
decimal-mark ,

; Now commas are decimal separators
2024-01-15 European
    Expenses:Food    50,00 EUR
    Assets:Bank
```

## Best Practices

1. **Declare commodities** at file start
2. **Use consistent formatting** throughout
3. **Match local conventions** (US vs European)
4. **Specify appropriate precision** for each type

## Complete Example

```hledger
; ===== Commodity Declarations =====

; Currencies
commodity $1,000.00
commodity 1.000,00 EUR
commodity £1,000.00
commodity ¥1,000
commodity CHF 1'000.00

; Cryptocurrencies
commodity 1.00000000 BTC
commodity 1.000000000000000000 ETH

; Investment commodities
commodity 1.0000 AAPL
commodity 1.0000 GOOG
commodity 1.0000 VTSAX

; Physical commodities
commodity 1.000 "oz gold"
commodity 1.000 "oz silver"

; ===== Transactions =====

2024-01-15 Salary
    Assets:Checking    $5,000.00
    Income:Salary

2024-01-15 Convert to EUR
    Assets:EUR    900,00 EUR @@ $1,000.00
    Assets:Checking    $-1,000.00

2024-01-15 Buy Bitcoin
    Assets:Crypto    0.02500000 BTC @ $40,000.00
    Assets:Checking    $-1,000.00
```

## Command Line

```bash
# List all commodities
hledger commodities

# Show commodity totals
hledger bal -B    # Cost basis
hledger bal -V    # Market value
hledger bal -X $  # Convert to USD
```

## See Also

- [Decimal-Mark Directive](decimal-mark.md)
- [Amounts Specification](../amounts.md)
- [Account Directive](account.md)
