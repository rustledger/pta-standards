# Numeric Operations

This document provides an overview of numeric operations in plain text accounting systems.

## Overview

Financial calculations require exact decimal arithmetic with well-defined rounding and tolerance rules. This section specifies how numbers are represented, manipulated, and compared.

## Documents

| Document | Description |
|----------|-------------|
| [Decimal Type](../types/decimal.md) | Decimal number representation |
| [Precision](precision.md) | Precision requirements and limits |
| [Rounding](rounding.md) | Rounding modes and rules |
| [Tolerance](tolerance.md) | Near-equality for balance checking |

## Core Principles

### Exact Arithmetic

All arithmetic operations MUST use exact decimal arithmetic:

```
0.1 + 0.2 = 0.3  (exactly, not 0.30000000000000004)
```

IEEE 754 floating-point MUST NOT be used for financial calculations.

### Precision Preservation

Operations preserve all significant digits up to implementation limits:

```
Input:  1.23 + 4.567
Result: 5.797  (3 decimal places preserved)
```

### Deterministic Results

Same inputs MUST produce same outputs:

```
f(a, b) = f(a, b)  (always)
```

No randomness or undefined behavior in numeric operations.

## Arithmetic Operations

### Addition and Subtraction

```
a + b = c
a - b = d

Precision: max(precision(a), precision(b))
```

Examples:
```
100.00 + 50.5 = 150.50
100.00 - 50.5 = 49.50
```

### Multiplication

```
a × b = c

Precision: precision(a) + precision(b)
```

Examples:
```
10 × 1.5 = 15.0
1.5 × 1.5 = 2.25
```

### Division

```
a ÷ b = c

Precision: implementation-defined (typically capped)
```

Examples:
```
100 ÷ 3 = 33.333... (may be truncated)
```

Division by zero is an error.

## Comparison Operations

### Exact Equality

```
a == b  (exactly equal)
a != b  (not exactly equal)
```

### Near Equality (Tolerance)

```
|a - b| ≤ tolerance  (near-equal for balance checking)
```

See [Tolerance](tolerance.md).

### Ordering

```
a < b   (less than)
a <= b  (less or equal)
a > b   (greater than)
a >= b  (greater or equal)
```

## Scale and Precision

### Scale

Number of decimal places:

| Value | Scale |
|-------|-------|
| 100 | 0 |
| 100.0 | 1 |
| 100.00 | 2 |
| 0.001 | 3 |

### Precision

Number of significant digits:

| Value | Precision |
|-------|-----------|
| 100 | 3 |
| 100.0 | 4 |
| 0.001 | 1 |
| 123.45 | 5 |

### Significance

Scale affects tolerance calculation; precision affects storage limits.

## Limits

### Minimum Requirements

| Property | Minimum |
|----------|---------|
| Precision | 28 digits |
| Scale | 0-28 |
| Range | ±10²⁸ |

### Overflow Handling

Numbers exceeding limits MUST produce errors:

```
ERROR: Numeric overflow
  --> ledger.beancount:42:15
   |
42 |   Assets:Cash  99999999999999999999999999999 USD
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

### Underflow Handling

Very small numbers MAY be rounded to zero:

```
0.00000000000000000000000000001 → 0 (below precision)
```

## Special Values

### Zero

```
0 = 0.0 = 0.00  (equal values)
-0 = 0          (negative zero equals zero)
```

### Infinity

Infinity is NOT supported. Operations that would produce infinity are errors.

### NaN

Not-a-Number is NOT supported. Invalid operations are errors.

## Currency Arithmetic

### Same Currency

Direct arithmetic:

```
100 USD + 50 USD = 150 USD
100 USD - 30 USD = 70 USD
```

### Different Currencies

Requires conversion:

```
100 USD + 50 EUR = ERROR (incommensurable)

; With price:
100 USD + (50 EUR × 1.08 USD/EUR) = 154 USD
```

### Inventory Arithmetic

Inventories track amounts per currency:

```
Inventory {
  USD: 100.00
  EUR: 50.00
}
```

## Balance Checking

### Transaction Balance

```
sum(posting.weight for posting in transaction) ≈ 0
```

Where `≈` means within tolerance.

### Balance Assertion

```
actual_balance ≈ expected_balance
```

See [Tolerance](tolerance.md) for tolerance calculation.

## Implementation Notes

### Recommended Libraries

| Language | Library |
|----------|---------|
| Python | `decimal.Decimal` |
| Rust | `rust_decimal` or `bigdecimal` |
| Java | `java.math.BigDecimal` |
| JavaScript | `decimal.js` or `bignumber.js` |
| Go | `shopspring/decimal` |

### Avoid

- IEEE 754 `float`/`double`
- Fixed-point integers without sufficient range
- String-based arithmetic (slow)

## Error Conditions

| Error | Cause |
|-------|-------|
| Overflow | Result exceeds representable range |
| Division by zero | Denominator is zero |
| Invalid operation | Undefined arithmetic |
| Precision loss | Result would lose significant digits |

## See Also

- [Types: Decimal](../types/decimal.md) - Decimal representation
- [Precision](precision.md) - Precision requirements
- [Rounding](rounding.md) - Rounding modes
- [Tolerance](tolerance.md) - Balance tolerance
