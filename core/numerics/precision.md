# Precision and Arithmetic

This document specifies precision rules for decimal arithmetic operations.

## Arithmetic Operations

### Addition and Subtraction

The result scale is the maximum of operand scales:

```
100.00 + 0.5 = 100.50   // scale 2
1.1 - 0.111 = 0.989     // scale 3
```

### Multiplication

The result scale is the sum of operand scales (then normalized):

```
10.00 × 5.5 = 55.000    // scale 2+1 = 3
```

Implementations MAY normalize trailing zeros.

### Division

Division MAY produce non-terminating decimals.
Implementations MUST:

1. Use sufficient internal precision (at least 12 decimal places)
2. Apply consistent rounding

## Rounding

### Banker's Rounding (RECOMMENDED)

Implementations SHOULD use banker's rounding (round half to even) as the default:

| Value | Rounded |
|-------|---------|
| 0.5 | 0 (even) |
| 1.5 | 2 (even) |
| 2.5 | 2 (even) |
| 3.5 | 4 (even) |
| 0.25 | 0.2 (at scale 1) |
| 0.35 | 0.4 (at scale 1) |

Banker's rounding reduces cumulative bias in large datasets.

### When Rounding Occurs

1. **Division**: Internal divisions rounded to implementation-defined precision
2. **Display**: Numbers formatted to original scale
3. **Never for storage**: Full precision MUST be preserved in memory

## Expression Evaluation

Plain text accounting formats MAY support arithmetic expressions in amounts:

```
(100.00 / 3) USD   // = 33.333... USD
```

Division in expressions follows the same rounding rules.

## Precision Limits

### Very Large Numbers

Implementations MUST support amounts up to at least 10^28:

```
28,000,000,000,000.00 USD   // National-scale amounts
```

### Very Small Numbers

Implementations MUST support at least 28 decimal places:

```
0.00000001 BTC   // Satoshis
```

### Repeating Decimals

Plain text accounting does NOT automatically handle repeating decimals.
Users MUST manually round:

```
2024-01-01 * "Split three ways"
  Expenses:Dinner  33.33 USD
  Expenses:Dinner  33.33 USD
  Expenses:Dinner  33.34 USD   // Manual adjustment
  Assets:Cash     -100.00 USD
```

## Implementation Notes

### Recommended Libraries

| Language | Library |
|----------|---------|
| Rust | `rust_decimal` |
| Python | `decimal.Decimal` |
| JavaScript | `decimal.js` or `big.js` |
| Go | `shopspring/decimal` |
| Java | `java.math.BigDecimal` |

### Parsing

1. Remove grouping separators (commas)
2. Parse as decimal with preserved scale
3. Validate range and precision limits
