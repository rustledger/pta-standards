# Tolerance

This document specifies how tolerance is calculated and used for comparing decimal values.

## Purpose

Tolerance determines when values are "close enough" to be considered equal.
This is essential for:

- Transaction balancing
- Balance assertion verification
- Rounding error accommodation

## Inferred Tolerance

Tolerance is inferred from the **scale** (decimal places) of amounts in a transaction.

### Calculation

For a number with scale `s`, the tolerance is:

```
tolerance = 0.5 × 10^(-s)
```

| Scale | Tolerance |
|-------|-----------|
| 0 (integer) | 0.5 |
| 1 | 0.05 |
| 2 | 0.005 |
| 3 | 0.0005 |

### Per-Currency Tolerance

Each currency in a transaction has its own tolerance, based on the least precise amount for that currency:

```
2024-01-01 * "Purchase"
  Assets:Cash     -100.00 USD   // scale 2 → tolerance 0.005
  Assets:Cash     -50.5 EUR     // scale 1 → tolerance 0.05
  Expenses:Food
```

USD tolerance: 0.005
EUR tolerance: 0.05

## Tolerance Multiplier

Implementations MAY provide a configurable multiplier:

```
effective_tolerance = base_tolerance × multiplier
```

The default multiplier SHOULD be 0.5 (resulting in half-penny tolerance for 2-decimal currencies).

## Tolerance from Cost

When a posting includes a cost specification, the cost's precision MAY expand the tolerance:

```
2024-01-01 * "Buy"
  Assets:Stock  10 AAPL {150.00 USD}   // USD gets tolerance from 150.00
  Assets:Cash  -1500.00 USD
```

The 2-decimal-place cost (150.00) contributes 0.005 tolerance to USD.

This is typically configurable (e.g., `infer_tolerance_from_cost` option).

## Explicit Tolerance

Balance assertions MAY specify explicit tolerance:

```
2024-01-01 balance Assets:Checking  1000.00 USD ~ 0.01
```

The `~` operator overrides inferred tolerance.

## Near-Equality Check

Two values are near-equal if:

```
|a - b| ≤ tolerance
```

This is used for:

1. **Transaction balancing**: Sum of weights must be within tolerance of zero
2. **Balance assertions**: Actual balance must be within tolerance of expected

## Default Tolerance

When tolerance cannot be inferred (no amounts to base it on), implementations SHOULD use:

```
default_tolerance = 0.005   // Half a cent for 2-decimal currencies
```

This MAY be configurable per currency:

```
option "inferred_tolerance_default" "CHF:0.01"
option "inferred_tolerance_default" "JPY:1"
```

## Edge Cases

### Zero Tolerance

A tolerance of exactly zero requires exact equality.
This is rarely practical due to rounding in divisions.

### Negative Tolerance

Negative tolerance values are invalid.
Implementations MUST reject or ignore them.

### Very Small Tolerances

Tolerances smaller than the decimal type's precision are effectively zero.
Implementations SHOULD warn if specified tolerance exceeds available precision.

## Transaction Balancing Example

```
2024-01-01 * "Currency exchange"
  Assets:USD   -100.00 USD    // scale 2
  Assets:EUR    91.50 EUR     // scale 2
  Expenses:Fees  0.50 EUR

; USD tolerance: 0.005
; EUR tolerance: 0.005
; Transaction balances if:
;   - Sum of USD weights within 0.005 of zero
;   - Sum of EUR weights within 0.005 of zero
```

## Balance Assertion Example

```
2024-01-15 balance Assets:Checking  1000.00 USD

; Inferred tolerance: 0.005
; Passes if actual balance is in [999.995, 1000.005]
```

With explicit tolerance:

```
2024-01-15 balance Assets:Checking  1000.00 USD ~ 0.10

; Explicit tolerance: 0.10
; Passes if actual balance is in [999.90, 1000.10]
```
