# Lot Specification

This document specifies lot tracking and identification in Ledger.

## Overview

Lots represent distinct purchases of a commodity with specific acquisition attributes. Lot tracking enables:
- FIFO/LIFO/specific identification for sales
- Capital gains calculation
- Portfolio management
- Tax lot optimization

## Lot Attributes

Each lot has these identifying attributes:

| Attribute | Syntax | Example |
|-----------|--------|---------|
| Cost | `{amount}` | `{$150.00}` |
| Date | `[date]` | `[2024/01/15]` |
| Label | `(text)` | `(lot-1)` |

## Lot Creation

### Implicit Lot Creation

Every posting with a cost creates a new lot:

```ledger
2024/01/15 Buy Stock
    Assets:Brokerage    10 AAPL {$150.00}
    Assets:Cash        $-1500.00
```

Creates lot: `10 AAPL @ $150.00, acquired 2024/01/15`

### Explicit Lot Labeling

```ledger
2024/01/15 Buy Stock - Lot 1
    Assets:Brokerage    10 AAPL {$150.00} [2024/01/15] (jan-buy)
    Assets:Cash        $-1500.00
```

Creates lot: `10 AAPL @ $150.00, acquired 2024/01/15, label "jan-buy"`

## Lot Selection

### By Cost

```ledger
2024/06/15 Sell
    Assets:Cash         $1800.00
    Assets:Brokerage   -10 AAPL {$150.00}
    Income:Capital-Gains
```

Matches lots with exactly $150.00 per-unit cost.

### By Date

```ledger
2024/06/15 Sell
    Assets:Cash         $1800.00
    Assets:Brokerage   -10 AAPL [2024/01/15]
    Income:Capital-Gains
```

Matches lots acquired on 2024/01/15.

### By Label

```ledger
2024/06/15 Sell
    Assets:Cash         $1800.00
    Assets:Brokerage   -10 AAPL (jan-buy)
    Income:Capital-Gains
```

Matches lots with label "jan-buy".

### Combined Selection

```ledger
2024/06/15 Sell specific lot
    Assets:Cash         $1800.00
    Assets:Brokerage   -10 AAPL {$150.00} [2024/01/15] (jan-buy)
    Income:Capital-Gains
```

All attributes must match.

## Automatic Selection Methods

When no lot is specified, Ledger uses a selection method:

### FIFO (First In, First Out)

```bash
ledger bal --lot-dates    # Orders by acquisition date
```

Sells oldest lots first. Default for most tax jurisdictions.

### LIFO (Last In, First Out)

Sells newest lots first. May be tax-advantageous in certain situations.

### Average Cost

```bash
ledger bal --average-lots
```

Uses weighted average cost for all units:

```
average_cost = total_cost / total_units
```

### Specific Identification

Explicitly specify which lot to sell using cost, date, or label.

## Lot Matching Rules

### Exact Match

```ledger
; Buy
2024/01/15 Buy
    Assets:Stock    10 AAPL {$150.00}
    Assets:Cash

; Sell - exact match
2024/06/15 Sell
    Assets:Cash     $1800.00
    Assets:Stock   -10 AAPL {$150.00}
    Income:Gains
```

### Partial Match

When selling fewer units than in the lot:

```ledger
; Buy 100 shares
2024/01/15 Buy
    Assets:Stock    100 AAPL {$150.00}
    Assets:Cash    $-15000.00

; Sell 30 shares from that lot
2024/06/15 Sell
    Assets:Cash      $5400.00
    Assets:Stock    -30 AAPL {$150.00}
    Income:Gains
```

Remaining: 70 AAPL @ $150.00

### Ambiguous Match

When multiple lots match:

```ledger
; Multiple lots at same cost
2024/01/15 Buy
    Assets:Stock    10 AAPL {$150.00}
    Assets:Cash

2024/02/15 Buy
    Assets:Stock    10 AAPL {$150.00}
    Assets:Cash

; Ambiguous - which lot?
2024/06/15 Sell
    Assets:Stock   -10 AAPL {$150.00}
    Assets:Cash
```

Resolution: Uses configured lot selection method (FIFO by default).

## Lot State Tracking

### View Lot Details

```bash
ledger bal --lots Assets:Brokerage
```

Output:
```
        10 AAPL {$150.00} [2024/01/15]
        10 AAPL {$160.00} [2024/02/15]
        10 AAPL {$155.00} [2024/03/15]
------------------------------------
        30 AAPL  Assets:Brokerage
```

### Lot Prices

```bash
ledger bal --lot-prices Assets:Brokerage
```

Shows current market value vs cost basis.

## Lot Adjustments

### Stock Split

Adjust cost basis when shares split:

```ledger
2024/06/01 Stock Split 2:1
    ; Remove old lots
    Assets:Brokerage   -10 AAPL {$150.00} [2024/01/15]
    ; Add new lots at half cost
    Assets:Brokerage    20 AAPL {$75.00} [2024/01/15]
```

### Return of Capital

Reduce cost basis for return of capital:

```ledger
2024/06/15 Return of Capital
    Assets:Cash         $10.00
    Assets:Brokerage   -10 AAPL {$150.00}
    Assets:Brokerage    10 AAPL {$149.00}
```

### Wash Sale Adjustment

Adjust cost for wash sale rules:

```ledger
; Sell at loss
2024/01/15 Sell at Loss
    Assets:Cash         $1400.00
    Assets:Brokerage   -10 AAPL {$150.00} @ $140.00
    Income:Capital-Gains    ; $100 loss

; Repurchase within 30 days - wash sale
2024/01/20 Repurchase (Wash Sale)
    Assets:Brokerage    10 AAPL {$150.00}  ; Adjusted cost includes disallowed loss
    Assets:Cash        $-1400.00
```

## Lot Reports

### Cost Basis Report

```bash
ledger bal --basis Assets:Investments
```

### Unrealized Gains

```bash
ledger bal --gain Assets:Investments --market
```

### Tax Lot Report

```bash
ledger reg --lots --gain Income:Capital-Gains
```

## Examples

### Complete Lot Lifecycle

```ledger
; ===== Initial Purchase =====

2024/01/15 Buy AAPL - Lot A
    Assets:Brokerage    50 AAPL {$150.00} [2024/01/15] (lot-A)
    Assets:Cash        $-7500.00

; ===== Additional Purchase =====

2024/03/15 Buy AAPL - Lot B
    Assets:Brokerage    50 AAPL {$160.00} [2024/03/15] (lot-B)
    Assets:Cash        $-8000.00

; ===== Sell Using Specific ID =====

2024/09/15 Sell Lot A (Long-term gains)
    Assets:Cash         $9000.00
    Assets:Brokerage   -50 AAPL {$150.00} [2024/01/15] @ $180.00
    Income:Capital-Gains:Long    ; $1500 long-term gain

; ===== Check Remaining =====
; Lot B remains: 50 AAPL @ $160, acquired 2024/03/15
```

### Multi-Currency Lots

```ledger
2024/01/15 Buy EUR stocks
    Assets:Brokerage    100 EURO.STOCK {10.00 EUR} [2024/01/15]
    Assets:EUR         -1000.00 EUR

2024/06/15 Sell EUR stocks
    Assets:EUR          1200.00 EUR
    Assets:Brokerage   -100 EURO.STOCK {10.00 EUR} @ 12.00 EUR
    Income:Gains        -200.00 EUR
```

## Best Practices

1. **Use labels** for complex portfolios
2. **Include dates** for tax lot identification
3. **Verify lot selection** before recording sales
4. **Regular reconciliation** with brokerage statements
5. **Document wash sales** and adjustments
6. **Consistent method** - stick to FIFO/LIFO/specific ID

## See Also

- [Cost Specification](costs.md)
- [Amounts Specification](amounts.md)
- [Price Directive](directives/price.md)
