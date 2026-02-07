# Default Directive

The `D` or `default` directive sets the default commodity format.

## Syntax

```
D AMOUNT
```

## Examples

### US Dollar Default

```ledger
D $1,000.00

2024/01/15 Transaction
    Expenses:Food    50.00
    ; Interpreted as $50.00
    Assets:Checking
```

### Euro Default

```ledger
D 1.000,00 EUR

2024/01/15 Transaction
    Expenses:Food    50,00
    ; Interpreted as 50,00 EUR
    Assets:Checking
```

## Purpose

The default directive specifies:

1. **Default commodity** - For amounts without explicit commodity
2. **Display format** - How amounts are formatted

## Format Components

### Symbol Position

```ledger
D $1,000.00    ; Symbol prefix
D 1,000.00 USD ; Symbol suffix
```

### Thousand Separator

```ledger
D $1,000.00    ; Comma separator
D $1.000,00    ; Period separator
D $1 000.00    ; Space separator
```

### Decimal Separator

```ledger
D $1,000.00    ; Period decimal
D $1.000,00    ; Comma decimal
```

### Precision

```ledger
D $1,000.00    ; 2 decimal places
D $1,000.000   ; 3 decimal places
D $1,000.0000  ; 4 decimal places
```

## Behavior

### Without Default

```ledger
; No default - commodity required
2024/01/15 Transaction
    Expenses:Food    50.00 USD    ; Must specify
    Assets:Checking  -50.00 USD   ; Must specify
```

### With Default

```ledger
D $1,000.00

2024/01/15 Transaction
    Expenses:Food    50.00    ; Assumes USD
    Assets:Checking           ; Balances in USD
```

## Multiple Defaults

The last default wins:

```ledger
D $1,000.00

; US transactions
2024/01/15 US Store
    Expenses:Food    50.00
    Assets:USD:Checking

D 1.000,00 EUR

; European transactions
2024/01/16 EU Store
    Expenses:Food    50,00
    Assets:EUR:Checking
```

## Interaction with Commodities

### Commodity Directive

```ledger
commodity $
    format $1,000.00

D $1,000.00

; Both affect USD formatting
```

### Explicit Overrides Default

```ledger
D $1,000.00

2024/01/15 Transaction
    Expenses:Food    50.00 EUR   ; Uses EUR, not default
    Assets:Checking
```

## Use Cases

### Personal Finance (US)

```ledger
D $1,000.00

2024/01/15 Groceries
    Expenses:Food    150.00
    Assets:Checking

2024/01/15 Gas
    Expenses:Transportation    45.00
    Assets:Checking
```

### European Finance

```ledger
D 1.000,00 €

2024/01/15 Lebensmittel
    Ausgaben:Essen    50,00
    Vermögen:Girokonto
```

### Multi-Currency with Default

```ledger
D $1,000.00

; Default USD transactions
2024/01/15 Local Store
    Expenses:Food    50.00
    Assets:Checking

; Explicit foreign currency
2024/01/16 European Purchase
    Expenses:Shopping    100.00 EUR
    Assets:Euro:Account
```

## Display Format Examples

### US Dollar

```ledger
D $1,000.00

; Amount: 1234.56
; Displays: $1,234.56
```

### Euro (European)

```ledger
D 1.000,00 €

; Amount: 1234,56
; Displays: 1.234,56 €
```

### Japanese Yen

```ledger
D ¥1,000

; Amount: 1234
; Displays: ¥1,234
```

### Bitcoin

```ledger
D 1.00000000 BTC

; Amount: 0.12345678
; Displays: 0.12345678 BTC
```

## Precision Handling

```ledger
D $1,000.00

; Input with more precision is preserved internally
2024/01/15 Transaction
    Expenses:A    33.333333
    Expenses:B    33.333333
    Expenses:C    33.333334
    Assets:Checking  -100.00

; But displayed per format: $33.33
```

## Best Practices

1. **Set default early** in main file
2. **Match local currency** conventions
3. **Use consistent formatting** throughout
4. **Consider multi-currency** needs
5. **Document currency assumptions**

## Example: Regional Settings

### US Setup

```ledger
; US formatting
D $1,000.00

commodity $
    note US Dollar

commodity EUR
    format 1,000.00 EUR
    note Euro (displayed US-style)
```

### European Setup

```ledger
; European formatting
D 1.000,00 €

commodity €
    note Euro

commodity USD
    format 1.000,00 USD
    note US Dollar (displayed EU-style)
```

## Command Line Override

```bash
# Override display format
ledger -f journal.ledger --price-db prices.db balance
```

## See Also

- [Commodity Directive](commodity.md)
- [Amounts Specification](../amounts.md)
