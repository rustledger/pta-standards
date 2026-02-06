# Rounding

This document specifies rounding modes and rules for plain text accounting systems.

## Overview

Rounding converts a number to fewer decimal places. The rounding mode determines how to handle the discarded digits.

## When Rounding Occurs

### Explicit Rounding

User-requested rounding for display or calculation:

```
round(123.456, 2) = 123.46
```

### Implicit Rounding

System-performed rounding due to precision limits:

```
1/3 = 0.333... → 0.33333333... (truncated at precision limit)
```

### Division Results

Division may produce non-terminating decimals:

```
100 / 3 = 33.333...
```

## Rounding Modes

### HALF_EVEN (Banker's Rounding)

Round to nearest; if equidistant, round to even. **This is the recommended default.**

| Input | Rounded (1 decimal) |
|-------|-------------------|
| 1.25 | 1.2 (round down to even) |
| 1.35 | 1.4 (round up to even) |
| 1.45 | 1.4 (round down to even) |
| 1.55 | 1.6 (round up to even) |

**Rationale:** Minimizes cumulative bias over many operations.

### HALF_UP

Round to nearest; if equidistant, round away from zero.

| Input | Rounded (1 decimal) |
|-------|-------------------|
| 1.25 | 1.3 |
| 1.35 | 1.4 |
| -1.25 | -1.3 |
| -1.35 | -1.4 |

### HALF_DOWN

Round to nearest; if equidistant, round toward zero.

| Input | Rounded (1 decimal) |
|-------|-------------------|
| 1.25 | 1.2 |
| 1.35 | 1.3 |
| -1.25 | -1.2 |
| -1.35 | -1.3 |

### CEILING (Round Up)

Always round toward positive infinity.

| Input | Rounded (1 decimal) |
|-------|-------------------|
| 1.21 | 1.3 |
| 1.29 | 1.3 |
| -1.21 | -1.2 |
| -1.29 | -1.2 |

### FLOOR (Round Down)

Always round toward negative infinity.

| Input | Rounded (1 decimal) |
|-------|-------------------|
| 1.21 | 1.2 |
| 1.29 | 1.2 |
| -1.21 | -1.3 |
| -1.29 | -1.3 |

### TRUNCATE (Toward Zero)

Discard digits beyond precision (round toward zero).

| Input | Rounded (1 decimal) |
|-------|-------------------|
| 1.29 | 1.2 |
| -1.29 | -1.2 |

### AWAY_FROM_ZERO

Round away from zero.

| Input | Rounded (1 decimal) |
|-------|-------------------|
| 1.21 | 1.3 |
| -1.21 | -1.3 |

## Rounding Mode Summary

| Mode | 0.5 rounds to | -0.5 rounds to | Bias |
|------|---------------|----------------|------|
| HALF_EVEN | 0 (even) | 0 (even) | None |
| HALF_UP | 1 | -1 | Slight up |
| HALF_DOWN | 0 | 0 | Slight down |
| CEILING | 1 | 0 | Up |
| FLOOR | 0 | -1 | Down |
| TRUNCATE | 0 | 0 | Toward zero |

## Default Rounding Mode

Implementations SHOULD use **HALF_EVEN** as the default:

- Widely used in financial systems
- Minimizes statistical bias
- IEEE 754 default
- Recommended by regulatory bodies

## Context-Specific Rounding

### Display Rounding

For reports and output:

```
1234.567 → 1234.57  (display with 2 decimals)
```

Original precision preserved internally.

### Currency Rounding

Round to currency's minor unit:

| Currency | Decimals | Example |
|----------|----------|---------|
| USD | 2 | 1.234 → 1.23 |
| JPY | 0 | 1.5 → 2 |
| KWD | 3 | 1.2345 → 1.235 |

### Cost Basis Rounding

For lot cost calculations:

```
1000 USD / 3 shares = 333.333... USD per share

; Rounded:
= 333.33 USD per share (HALF_EVEN)

; Remainder handling may be needed
```

### Tax Calculations

Tax jurisdictions may mandate specific rounding:

```
; US: Generally HALF_UP for tax
; EU: Often HALF_EVEN
; Some: TRUNCATE for tax benefit calculations
```

## Rounding Functions

### Round to Decimal Places

```python
def round_decimal(value: Decimal, places: int, mode: RoundingMode) -> Decimal:
    """Round value to specified decimal places."""
    quantize_exp = Decimal(10) ** -places
    return value.quantize(quantize_exp, rounding=mode)

# Examples:
round_decimal(1.235, 2, HALF_EVEN) = 1.24
round_decimal(1.245, 2, HALF_EVEN) = 1.24  # Even preference
```

### Round to Significant Figures

```python
def round_sigfigs(value: Decimal, sigfigs: int, mode: RoundingMode) -> Decimal:
    """Round to specified significant figures."""
    ...

# Examples:
round_sigfigs(1234.5, 3, HALF_EVEN) = 1230
round_sigfigs(0.001234, 3, HALF_EVEN) = 0.00123
```

## Rounding in Calculations

### Intermediate vs. Final

**Recommended:** Round only final results, not intermediate values.

```python
# Good: Full precision intermediate
result = (a * b + c * d).round(2)

# Bad: Rounding intermediates accumulates error
result = a.round(2) * b.round(2) + c.round(2) * d.round(2)
```

### Allocation with Rounding

Distributing amounts with remainder:

```
Total: 100.00
Split: 3 ways
Each:  33.33, 33.33, 33.34  (handles remainder)
```

Algorithm:
```python
def allocate(total: Decimal, n: int) -> List[Decimal]:
    base = (total / n).quantize(Decimal('0.01'), FLOOR)
    remainder = total - base * n
    result = [base] * n
    # Distribute remainder penny by penny
    for i in range(int(remainder * 100)):
        result[i] += Decimal('0.01')
    return result
```

## Rounding Errors

### Cumulative Error

Many small roundings can accumulate:

```
sum(round(1/3, 2) for _ in range(3)) = 0.99 (not 1.00)
```

**Mitigation:** Keep full precision; round only for display.

### Balance Discrepancies

Rounding may cause tiny imbalances:

```
100 USD → split 3 ways:
  33.33 USD
  33.33 USD
  33.33 USD
  ─────────
  99.99 USD (0.01 short)
```

**Solution:** Use tolerance in balance checking or explicit remainder handling.

## Configuration

### Option Syntax

```
option "rounding_mode" "HALF_EVEN"
option "display_precision" "2"
```

### Per-Currency Precision

```
option "precision" "USD:2"
option "precision" "BTC:8"
option "precision" "JPY:0"
```

## Implementation

### Python Example

```python
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

def round_amount(amount: Decimal, places: int = 2) -> Decimal:
    exp = Decimal(10) ** -places
    return amount.quantize(exp, rounding=ROUND_HALF_EVEN)
```

### Rust Example

```rust
use rust_decimal::{Decimal, RoundingStrategy};

fn round_amount(amount: Decimal, places: u32) -> Decimal {
    amount.round_dp_with_strategy(places, RoundingStrategy::MidpointNearestEven)
}
```

## Error Messages

### Precision Loss Warning

```
WARNING: Precision loss in calculation
  --> ledger.beancount:42:15
   |
42 |   cost: 100.00 / 3
   |         ^^^^^^^^^^
   |
   = result 33.333... rounded to 33.33
```

### Rounding Mode Not Supported

```
ERROR: Unknown rounding mode
  --> ledger.beancount:5:18
   |
 5 | option "rounding_mode" "UNKNOWN"
   |                        ^^^^^^^^^
   |
   = valid modes: HALF_EVEN, HALF_UP, HALF_DOWN, CEILING, FLOOR, TRUNCATE
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Default mode | HALF_EVEN | HALF_UP | HALF_EVEN |
| Configurable | Limited | Yes | Yes |
| Display precision | Per-commodity | Per-commodity | Per-commodity |
| Allocation | Manual | Built-in | Manual |
