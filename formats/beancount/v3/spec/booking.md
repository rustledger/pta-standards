# Booking Methods

## Overview

Booking determines how lot reductions are matched to existing positions when selling or disposing of commodities that have cost basis tracking.

## The Problem

When you hold multiple lots of the same commodity purchased at different prices, a reduction (sale) must be matched to specific lots:

```beancount
; Multiple lots acquired
2024-01-01 * "Buy lot 1"
  Assets:Stock  10 AAPL {150 USD, 2024-01-01, "lot1"}
  Assets:Cash

2024-02-01 * "Buy lot 2"
  Assets:Stock  10 AAPL {160 USD, 2024-02-01, "lot2"}
  Assets:Cash

; Which lot does this reduce?
2024-03-01 * "Sell"
  Assets:Stock  -5 AAPL {}   ; ← Booking determines this
  Assets:Cash
```

## Booking Methods

### STRICT (Default)

Requires explicit lot specification. Ambiguous reductions are errors.

```beancount
2024-01-01 open Assets:Stock AAPL "STRICT"

; Must specify which lot
2024-03-01 * "Sell from lot 1"
  Assets:Stock  -5 AAPL {150 USD, 2024-01-01}  ; Explicit
  Assets:Cash

; ERROR: Ambiguous - multiple lots match
2024-03-01 * "Ambiguous sell"
  Assets:Stock  -5 AAPL {}  ; Error!
  Assets:Cash
```

### FIFO (First-In, First-Out)

Reduces oldest lots first, ordered by acquisition date.

```beancount
2024-01-01 open Assets:Stock AAPL "FIFO"

; Reduces lot1 first (oldest)
2024-03-01 * "Sell FIFO"
  Assets:Stock  -5 AAPL {}
  Assets:Cash

; Equivalent to:
; Assets:Stock  -5 AAPL {150 USD, 2024-01-01}
```

### LIFO (Last-In, First-Out)

Reduces newest lots first, ordered by acquisition date (descending).

```beancount
2024-01-01 open Assets:Stock AAPL "LIFO"

; Reduces lot2 first (newest)
2024-03-01 * "Sell LIFO"
  Assets:Stock  -5 AAPL {}
  Assets:Cash

; Equivalent to:
; Assets:Stock  -5 AAPL {160 USD, 2024-02-01}
```

### HIFO (Highest-In, First-Out)

Reduces highest-cost lots first. Minimizes capital gains.

```beancount
2024-01-01 open Assets:Stock AAPL "HIFO"

; Reduces lot2 first (highest cost: 160 USD)
2024-03-01 * "Sell HIFO"
  Assets:Stock  -5 AAPL {}
  Assets:Cash
```

### NONE

Allows reductions without lot tracking. Creates negative positions if needed.

```beancount
2024-01-01 open Assets:Stock AAPL "NONE"

; Can sell more than you own
2024-03-01 * "Short sell"
  Assets:Stock  -100 AAPL {}  ; Creates -100 AAPL position
  Assets:Cash
```

### AVERAGE

Uses average cost basis. All lots are merged conceptually into a single position with average cost.

```beancount
2024-01-01 open Assets:Stock AAPL "AVERAGE"

; lot1: 10 @ 150 = 1500
; lot2: 10 @ 160 = 1600
; Average: 3100 / 20 = 155 USD

2024-03-01 * "Sell average"
  Assets:Stock  -5 AAPL {}  ; Cost basis: 5 × 155 = 775 USD
  Assets:Cash
```

The average cost is recomputed after each acquisition.

> **Note:** See [conformance/python-beancount.md](../conformance/python-beancount.md) for implementation status.

### STRICT_WITH_SIZE

Like STRICT, but also requires the reduction size to match exactly.

```beancount
2024-01-01 open Assets:Stock AAPL "STRICT_WITH_SIZE"

; Must specify exact cost AND size must match lot
2024-03-01 * "Sell"
  Assets:Stock  -10 AAPL {150 USD}  ; Must sell entire lot
  Assets:Cash
```

## Lot Matching

### Cost Specification

Reduce by matching cost:

```beancount
; Match by exact cost
Assets:Stock  -5 AAPL {150 USD}

; Match by cost and date
Assets:Stock  -5 AAPL {150 USD, 2024-01-01}

; Match by cost, date, and label
Assets:Stock  -5 AAPL {150 USD, 2024-01-01, "lot1"}
```

### Date Only

Reduce by acquisition date:

```beancount
Assets:Stock  -5 AAPL {2024-01-01}
```

### Label Only

Reduce by lot label:

```beancount
Assets:Stock  -5 AAPL {"lot1"}
```

### Empty Cost

Let booking method decide:

```beancount
Assets:Stock  -5 AAPL {}
```

### Partial Match

If specification matches multiple lots, booking method breaks the tie:

```beancount
2024-01-01 open Assets:Stock AAPL "FIFO"

; If multiple lots have same cost, FIFO picks oldest
Assets:Stock  -5 AAPL {150 USD}  ; Oldest 150 USD lot
```

## Merge Cost (`*`)

The merge cost operator explicitly combines all lots into a single average-cost lot:

```beancount
; Before: lot1 (10 @ 150), lot2 (10 @ 160)
2024-03-01 * "Merge lots"
  Assets:Stock  0 AAPL {*}

; After: single lot (20 @ 155)
```

This is used with AVERAGE booking for explicit lot merging, or to convert from per-lot tracking to average cost.

> **Note:** See [conformance/python-beancount.md](../conformance/python-beancount.md) for implementation status.

## Lot Splitting

When reducing fewer units than a lot contains, the lot is split:

```beancount
; Have: 10 AAPL {150 USD}
; Sell: 3 AAPL

; After: 7 AAPL {150 USD}  ; Remainder
```

## Cross-Lot Reduction

A single reduction may span multiple lots:

```beancount
; Have: lot1 (10 @ 150), lot2 (10 @ 160)
; FIFO sell 15 shares

2024-03-01 * "Sell 15 FIFO"
  Assets:Stock  -15 AAPL {}
  Assets:Cash

; Reduces: 10 from lot1 (exhausted), 5 from lot2
; Remaining: 5 AAPL {160 USD}
```

## Capital Gains

Booking affects capital gains calculations:

```beancount
; Buy at 150, sell at 180
2024-01-01 * "Buy"
  Assets:Stock  10 AAPL {150 USD}
  Assets:Cash  -1500 USD

2024-06-01 * "Sell"
  Assets:Stock  -10 AAPL {150 USD} @ 180 USD
  Assets:Cash   1800 USD
  Income:CapitalGains  -300 USD  ; Gain: (180-150) × 10
```

## Configuration

### Per-Account

```beancount
2024-01-01 open Assets:Retirement VTSAX "FIFO"
2024-01-01 open Assets:Trading BTC "LIFO"
2024-01-01 open Assets:LongTerm AAPL "HIFO"
```

### Global Default

```beancount
option "booking_method" "STRICT"  ; Default for all accounts
```

## Validation Errors

The following conditions produce booking-related validation errors:

| Condition | Description |
|-----------|-------------|
| No matching lot | Reduction specification doesn't match any existing lot |
| Insufficient units | Not enough units available in matching lots |
| Ambiguous match | Multiple lots match in STRICT mode |
| Negative inventory | Reduction would create negative position (except NONE) |

Booking errors are reported with descriptive messages explaining why the lot matching failed. See [conformance/python-beancount.md](../conformance/python-beancount.md) for error type details.

## Examples

### FIFO Tax-Lot Accounting

```beancount
2020-01-01 open Assets:Brokerage:AAPL AAPL "FIFO"

2020-03-01 * "Buy" ^apple-2020
  Assets:Brokerage:AAPL  100 AAPL {75 USD}
  Assets:Cash

2021-06-01 * "Buy" ^apple-2021
  Assets:Brokerage:AAPL  50 AAPL {130 USD}
  Assets:Cash

2024-01-15 * "Sell (FIFO takes 2020 lot)"
  Assets:Brokerage:AAPL  -75 AAPL {} @ 185 USD
  Assets:Cash
  Income:CapitalGains:LongTerm  ; Held > 1 year
```

### Specific Lot Selection

```beancount
2020-01-01 open Assets:Brokerage:AAPL AAPL "STRICT"

2024-01-15 * "Sell specific lot"
  Assets:Brokerage:AAPL  -50 AAPL {130 USD, 2021-06-01} @ 185 USD
  Assets:Cash
  Income:CapitalGains:ShortTerm  ; 2021 lot, held < 1 year
```

## Implementation Notes

1. Track lots with (cost, date, label, units)
2. Index lots for efficient matching
3. Implement each booking method's ordering
4. Handle partial lot reductions
5. Validate against negative inventory (except NONE)
6. Preserve lot identity through splits
