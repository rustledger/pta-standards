# Commodity Directive

The `commodity` directive declares a commodity and its display format.

## Syntax

```
commodity SYMBOL
    [SUBDIRECTIVE...]
```

## Examples

### Basic Declaration

```ledger
commodity $
```

### With Format

```ledger
commodity $
    format $1,000.00
```

### Full Example

```ledger
commodity USD
    format 1,000.00 USD
    note United States Dollar
    nomarket
    default
```

### Stock/Security

```ledger
commodity AAPL
    format 1,000.000 AAPL
    note Apple Inc. common stock
```

## Subdirectives

### format

Specifies how amounts should be displayed:

```ledger
commodity $
    format $1,000.00

commodity EUR
    format 1.000,00 EUR

commodity BTC
    format 1.00000000 BTC
```

Format components:
- Position of symbol (prefix or suffix)
- Thousand separator (`,` or `.` or space)
- Decimal separator (`.` or `,`)
- Decimal precision (number of places shown)

### note

Adds a description:

```ledger
commodity JPY
    note Japanese Yen
```

### nomarket

Excludes from market value calculations:

```ledger
commodity POINTS
    note Loyalty points - no market value
    nomarket
```

### default

Sets as the default commodity:

```ledger
commodity $
    format $1,000.00
    default

; Amounts without commodity use default
2024/01/15 Test
    Expenses:Food    50.00    ; Interpreted as $50.00
    Assets:Checking
```

### alias

Creates alternative names:

```ledger
commodity $
    alias USD
    alias US$
```

## Commodity Symbols

### Currency Symbols

```ledger
commodity $     ; US Dollar
commodity €     ; Euro
commodity £     ; British Pound
commodity ¥     ; Yen
commodity ₹     ; Indian Rupee
```

### Currency Codes

```ledger
commodity USD
commodity EUR
commodity GBP
commodity JPY
```

### Custom Commodities

```ledger
commodity AAPL          ; Stock
commodity "MUTUAL FUND" ; Quoted (spaces allowed)
commodity BTC           ; Cryptocurrency
commodity miles         ; Loyalty/reward
```

## Display Format Examples

### US Currency

```ledger
commodity $
    format $1,000.00
```
Displays: `$1,234.56`

### European Currency

```ledger
commodity EUR
    format 1.000,00 EUR
```
Displays: `1.234,56 EUR`

### Cryptocurrency

```ledger
commodity BTC
    format 1.00000000 BTC
```
Displays: `0.12345678 BTC`

### Shares

```ledger
commodity AAPL
    format 1,000.000 AAPL
```
Displays: `100.000 AAPL`

## Precision

The format directive controls display precision:

```ledger
commodity $
    format $1,000.00    ; 2 decimal places

; Internal: $33.333333...
; Display:  $33.33
```

## Implicit Declaration

Commodities are implicitly declared on first use:

```ledger
; USD is implicitly declared
2024/01/15 Transaction
    Expenses:Food    50.00 USD
    Assets:Checking
```

Display format is inferred from usage.

## Multiple Commodities

A journal can use many commodities:

```ledger
commodity $
    format $1,000.00

commodity EUR
    format 1.000,00 EUR

commodity AAPL
    format 1.000 AAPL

2024/01/15 Mixed transaction
    Assets:Brokerage    10 AAPL
    Assets:EUR         100 EUR
    Assets:Checking   $-1500.00
```

## See Also

- [Amounts Specification](../amounts.md)
- [Price Directive](price.md)
