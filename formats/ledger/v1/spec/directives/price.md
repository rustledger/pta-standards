# Price Directive

The `P` directive records historical market prices for commodities.

## Syntax

```
P DATE COMMODITY PRICE
```

## Examples

### Basic Price

```ledger
P 2024/01/15 AAPL $150.00
```

### Currency Exchange Rate

```ledger
P 2024/01/15 EUR $1.10
P 2024/01/15 GBP $1.27
```

### Cryptocurrency

```ledger
P 2024/01/15 BTC $42000.00
```

### Multiple Prices

```ledger
P 2024/01/15 AAPL $150.00
P 2024/01/16 AAPL $152.50
P 2024/01/17 AAPL $148.75
```

## Components

### Date

Standard Ledger date format:

```ledger
P 2024/01/15 AAPL $150.00
P 2024-01-15 AAPL $150.00
```

### Time (Optional)

Time can be included:

```ledger
P 2024/01/15 12:30:00 AAPL $150.00
```

### Commodity

The commodity being priced:

```ledger
P 2024/01/15 AAPL $150.00
;            ^^^^ commodity
```

### Price

The price in another commodity:

```ledger
P 2024/01/15 AAPL $150.00
;                 ^^^^^^^ price (150 USD per share)
```

## Price Database

Ledger builds an internal price database:

```ledger
; Price history
P 2024/01/01 AAPL $145.00
P 2024/01/15 AAPL $150.00
P 2024/02/01 AAPL $155.00

; Position at cost
2024/01/15 Buy Apple
    Assets:Brokerage    10 AAPL @ $150.00
    Assets:Checking    $-1500.00
```

## Market Value Reporting

With `-V` flag, Ledger uses prices for valuation:

```bash
ledger -V balance Assets:Brokerage
```

Uses most recent price before report date.

## Exchange Rates

Prices define exchange rates between commodities:

```ledger
P 2024/01/15 EUR $1.10
P 2024/01/15 GBP $1.27
P 2024/01/15 JPY $0.0067

; Ledger can convert between any currencies
```

## Inverse Prices

Ledger automatically calculates inverses:

```ledger
P 2024/01/15 EUR $1.10
; Implies: 1 USD = 0.909 EUR
```

## Transitive Prices

Ledger calculates transitive conversions:

```ledger
P 2024/01/15 EUR $1.10
P 2024/01/15 GBP £0.85

; Ledger can convert EUR to GBP via USD
```

## Price Sources

### Manual Entry

```ledger
P 2024/01/15 AAPL $150.00
```

### From Transactions

Prices are also derived from transactions:

```ledger
2024/01/15 Buy at market
    Assets:Brokerage    10 AAPL @ $150.00
    Assets:Checking
; Implies: P 2024/01/15 AAPL $150.00
```

### External Price Files

```ledger
include prices.dat
```

## Reporting Options

### Current Value (-V)

```bash
ledger -V balance
```

Uses most recent prices.

### Historical Value (--historical)

```bash
ledger --historical -V balance
```

Uses prices as of each transaction date.

### Specific Date (--now)

```bash
ledger --now 2024/06/30 -V balance
```

Uses prices as of specified date.

## Example: Investment Tracking

```ledger
; Price history
P 2024/01/01 AAPL $145.00
P 2024/02/01 AAPL $155.00
P 2024/03/01 AAPL $160.00

; Transactions
2024/01/15 Buy Apple
    Assets:Brokerage    10 AAPL @ $148.00
    Assets:Checking    $-1480.00

2024/02/15 Buy More
    Assets:Brokerage    5 AAPL @ $157.00
    Assets:Checking    $-785.00

; Report market value
; ledger -V balance Assets:Brokerage
; Shows: 15 AAPL = $2400.00 (at $160/share)
```

## See Also

- [Commodity Directive](commodity.md)
- [Amounts Specification](../amounts.md)
- [Lot Tracking](../lots.md)
