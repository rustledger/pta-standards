# hledger Cost Specification

This document specifies cost basis tracking in hledger.

## Overview

Cost tracking records acquisition prices for:
- Investment purchases
- Currency conversions
- Capital gains calculation

## Syntax

### Per-Unit Cost

```hledger
AMOUNT {COST}
```

### Total Cost

```hledger
AMOUNT {{TOTAL_COST}}
```

## Per-Unit Cost

### Basic Usage

```hledger
2024-01-15 Buy Stock
    assets:brokerage    10 AAPL {$150}
    assets:cash        $-1500
```

Cost: $150 per share, total $1500.

### With Date

```hledger
    assets:brokerage    10 AAPL {$150, 2024-01-15}
```

### Full Specification

```hledger
    assets:brokerage    10 AAPL {$150, 2024-01-15, "lot1"}
```

## Total Cost

```hledger
2024-01-15 Buy Stock
    assets:brokerage    10 AAPL {{$1500}}
    assets:cash        $-1500
```

Per-unit: $1500 / 10 = $150.

## Cost vs Price

### Cost (Acquisition)

Records what you paid:

```hledger
    assets:brokerage    10 AAPL {$150}
    ; Cost basis: $150/share
```

### Price (Market Value)

Records current value:

```hledger
    assets:brokerage    10 AAPL @ $180
    ; Current price: $180/share
```

### Both Together

```hledger
    assets:brokerage    10 AAPL {$150} @ $180
    ; Bought at $150, now worth $180
```

## Lot Tracking

### Creating Lots

```hledger
2024-01-15 Buy Lot 1
    assets:brokerage    10 AAPL {$150}
    assets:cash        $-1500

2024-02-15 Buy Lot 2
    assets:brokerage    10 AAPL {$160}
    assets:cash        $-1600
```

### Selling Lots

```hledger
2024-06-15 Sell Lot 1
    assets:cash         $1800
    assets:brokerage   -10 AAPL {$150} @ $180
    income:capital-gains
```

## Capital Gains

### Calculation

```hledger
2024-01-15 Buy
    assets:brokerage    10 AAPL {$150}
    assets:cash        $-1500

2024-06-15 Sell
    assets:cash         $1800
    assets:brokerage   -10 AAPL {$150} @ $180
    income:capital-gains    ; $-300 (gain)
```

Gain: ($180 - $150) × 10 = $300

## Multi-Currency

### Currency Exchange

```hledger
2024-01-15 Exchange
    assets:eur    100 EUR {$1.10}
    assets:usd   $-110
```

### Foreign Stock

```hledger
2024-01-15 Buy Foreign Stock
    assets:brokerage    100 EURO.STOCK {10.00 EUR}
    assets:eur         -1000 EUR
```

## Reports

### Cost Basis

```bash
hledger bal --cost assets:brokerage
```

### Market Value

```bash
hledger bal --value=now assets:brokerage
```

### Gains

```bash
hledger bal --gain
```

## Examples

### Investment Portfolio

```hledger
; === Purchases ===

2024-01-15 Buy AAPL
    assets:brokerage    50 AAPL {$150}
    assets:cash        $-7500

2024-03-15 Buy AAPL
    assets:brokerage    50 AAPL {$160}
    assets:cash        $-8000

; === Sale ===

2024-09-15 Sell AAPL
    assets:cash         $9000
    assets:brokerage   -50 AAPL {$150} @ $180
    income:capital-gains:long
```

### Currency Trading

```hledger
2024-01-15 Buy EUR
    assets:eur     1000 EUR {$1.10}
    assets:usd    $-1100

2024-06-15 Sell EUR
    assets:usd     $1150
    assets:eur    -1000 EUR {$1.10} @ $1.15
    income:forex
```

## Best Practices

1. **Always specify cost** for investments
2. **Use dates** for lot identification
3. **Track separately** different purchase prices
4. **Regular reconciliation** with statements
5. **Document adjustments** (splits, dividends)

## See Also

- [Amounts Specification](amounts.md)
- [Posting Specification](posting.md)
- [Ledger Costs](../../../ledger/v1/spec/costs.md)
