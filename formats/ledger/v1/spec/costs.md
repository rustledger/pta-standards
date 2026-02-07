# Cost Specification

This document specifies cost basis tracking in Ledger.

## Overview

Cost basis records the acquisition price of commodities, essential for:
- Capital gains calculation
- Portfolio tracking
- Tax reporting

## Syntax

```
cost_spec = "{" cost_components "}"
          | "{{" cost_components "}}"

cost_components = amount [date] [lot_note]
```

## Per-Unit Cost

### Basic Syntax

```ledger
    Assets:Brokerage    10 AAPL {$150.00}
    ; Cost: $150 per share
```

### Interpretation

- Total cost: 10 × $150 = $1500
- Per-unit cost: $150

## Total Cost

### Syntax

```ledger
    Assets:Brokerage    10 AAPL {{$1500.00}}
    ; Total cost: $1500 for all 10 shares
```

### Per-Unit Calculation

```
per_unit_cost = total_cost / units
$150 = $1500 / 10
```

## Cost Components

### Amount Only

```ledger
    Assets:Brokerage    10 AAPL {$150.00}
```

### With Date

```ledger
    Assets:Brokerage    10 AAPL {$150.00} [2024/01/15]
    ; Acquired on 2024/01/15
```

### With Lot Note

```ledger
    Assets:Brokerage    10 AAPL {$150.00} (lot-1)
    ; Labeled as "lot-1"
```

### Full Specification

```ledger
    Assets:Brokerage    10 AAPL {$150.00} [2024/01/15] (lot-1)
    ; Cost $150, acquired 2024/01/15, labeled "lot-1"
```

## Cost vs Price

### Cost (Acquisition)

```ledger
    Assets:Brokerage    10 AAPL {$150.00}
    ; Records what you paid
```

### Price (Current Market)

```ledger
    Assets:Brokerage    10 AAPL @ $180.00
    ; Records current market price
```

### Both Together

```ledger
    Assets:Brokerage    10 AAPL {$150.00} @ $180.00
    ; Cost $150, current price $180
```

## Lot Tracking

### Creating Lots

Each purchase with different cost creates a new lot:

```ledger
2024/01/15 Buy AAPL - Lot 1
    Assets:Brokerage    10 AAPL {$150.00} [2024/01/15] (lot-1)
    Assets:Cash        $-1500.00

2024/02/15 Buy AAPL - Lot 2
    Assets:Brokerage    10 AAPL {$160.00} [2024/02/15] (lot-2)
    Assets:Cash        $-1600.00
```

### Inventory State

After both transactions:
- Lot 1: 10 AAPL @ $150.00
- Lot 2: 10 AAPL @ $160.00
- Total: 20 AAPL, cost basis $3100

## Selling Lots

### Explicit Lot Selection

```ledger
2024/03/15 Sell AAPL - Lot 1
    Assets:Cash         $1800.00
    Assets:Brokerage   -10 AAPL {$150.00} [2024/01/15]
    Income:Capital-Gains
```

### By Cost

```ledger
    Assets:Brokerage   -10 AAPL {$150.00}
    ; Matches lot with $150 cost
```

### By Date

```ledger
    Assets:Brokerage   -10 AAPL [2024/01/15]
    ; Matches lot acquired on 2024/01/15
```

### By Label

```ledger
    Assets:Brokerage   -10 AAPL (lot-1)
    ; Matches lot labeled "lot-1"
```

## Capital Gains Calculation

### Example

```ledger
; Buy at $150
2024/01/15 Buy AAPL
    Assets:Brokerage    10 AAPL {$150.00}
    Assets:Cash        $-1500.00

; Sell at $180
2024/06/15 Sell AAPL
    Assets:Cash         $1800.00
    Assets:Brokerage   -10 AAPL {$150.00} @ $180.00
    Income:Capital-Gains    ; $300 gain
```

### Gain Calculation

```
Proceeds:    10 × $180 = $1800
Cost basis:  10 × $150 = $1500
────────────────────────────────
Capital gain:            $300
```

## Automatic Lot Selection

When lot is not specified, Ledger uses booking method:

### FIFO (First In, First Out)

```ledger
--lot-dates     ; Use FIFO ordering
```

Sells oldest lots first.

### LIFO (Last In, First Out)

Sells newest lots first.

### Average Cost

```ledger
--average-lots
```

Uses weighted average cost.

## Partial Lot Sales

### Selling Part of a Lot

```ledger
; Buy 100 shares
2024/01/15 Buy
    Assets:Brokerage    100 AAPL {$150.00}
    Assets:Cash        $-15000.00

; Sell 30 shares from that lot
2024/06/15 Sell
    Assets:Cash          $5400.00
    Assets:Brokerage    -30 AAPL {$150.00}
    Income:Capital-Gains
```

Remaining: 70 AAPL at $150.00

## Cost in Different Currency

```ledger
2024/01/15 Buy on foreign exchange
    Assets:Brokerage    100 FOREIGN.STOCK {10.00 EUR}
    Assets:EUR         -1000.00 EUR
```

## Adjusting Cost Basis

### Stock Split

```ledger
2024/06/01 Stock Split 2:1
    Assets:Brokerage    100 AAPL {$75.00}   ; New shares at half cost
    Assets:Brokerage   -100 AAPL {$150.00}  ; Remove old shares
```

### Dividend Reinvestment

```ledger
2024/03/15 Dividend Reinvestment
    Assets:Brokerage    0.5 AAPL {$160.00}
    Income:Dividends   $-80.00
```

## Reporting

### Cost Basis Report

```bash
ledger bal --lot-prices Assets:Brokerage
```

### Gains Report

```bash
ledger reg --gain Income:Capital-Gains
```

## Examples

### Complete Investment Lifecycle

```ledger
; ===== Buy Shares =====

2024/01/15 Buy AAPL
    Assets:Brokerage    50 AAPL {$150.00} [2024/01/15] (jan-buy)
    Assets:Cash        $-7500.00

2024/03/15 Buy more AAPL
    Assets:Brokerage    50 AAPL {$160.00} [2024/03/15] (mar-buy)
    Assets:Cash        $-8000.00

; ===== Sell Specific Lot =====

2024/09/15 Sell January lot
    Assets:Cash         $9000.00
    Assets:Brokerage   -50 AAPL {$150.00} [2024/01/15] @ $180.00
    Income:Capital-Gains    ; $1500 gain

; ===== Remaining Position =====
; 50 AAPL at $160 cost basis (mar-buy lot)
```

## Best Practices

1. **Always specify cost** when buying investments
2. **Use dates** for lot identification
3. **Use labels** for complex portfolios
4. **Track splits and adjustments** carefully
5. **Reconcile regularly** with brokerage statements

## See Also

- [Amounts Specification](amounts.md)
- [Posting Specification](posting.md)
- [Price Directive](directives/price.md)
