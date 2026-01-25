# Decimal Type

This document specifies the decimal number type used for all financial calculations.

## Rationale: Why Decimals, Not Floats

Financial calculations MUST use exact decimal arithmetic.
Floating point (IEEE 754) cannot exactly represent values like `0.1`:

```
0.1 + 0.2 = 0.30000000000000004  // IEEE 754 float
0.1 + 0.2 = 0.3                   // Decimal
```

Implementations MUST use a decimal type that provides exact representation of base-10 fractions.

## Representation

A decimal number consists of:

- **Mantissa**: The significant digits (integer)
- **Scale**: The number of decimal places
- **Sign**: Positive or negative

The value is: `mantissa / 10^scale`

### Minimum Requirements

Implementations MUST support:

- **Precision**: At least 28 significant digits
- **Scale**: 0-28 decimal places
- **Range**: At least ±10^28

## Syntax

### Number Format

```
number      = integer | decimal
integer     = ["-"] digits
decimal     = ["-"] digits "." digits
            | ["-"] "." digits
digits      = digit+
            | digit{1,3} ("," digit{3})+
digit       = "0" | "1" | ... | "9"
```

### Examples

| Input | Mantissa | Scale | Value |
|-------|----------|-------|-------|
| `100` | 100 | 0 | 100 |
| `100.00` | 10000 | 2 | 100.00 |
| `0.123456789` | 123456789 | 9 | 0.123456789 |
| `1,234,567.89` | 123456789 | 2 | 1234567.89 |
| `.50` | 50 | 2 | 0.50 |
| `-.50` | -50 | 2 | -0.50 |

### Grouping Separators

Implementations MUST accept comma `,` as a thousands grouping separator.
Implementations SHOULD ignore grouping separators during parsing.

### Decimal Separator

The period `.` is the REQUIRED decimal separator.
Implementations MUST NOT accept comma as decimal separator.

## Scale Inference

The scale of a number is inferred from its textual representation:

| Input | Scale |
|-------|-------|
| `100` | 0 |
| `100.0` | 1 |
| `100.00` | 2 |
| `0.001` | 3 |

Scale is significant for tolerance calculation.
See [Tolerance](../numerics/tolerance.md).

## Equality

Two decimals are equal if their values are identical, regardless of scale:

```
100 == 100.00  // true (same value)
100.0 == 100   // true (same value)
```

## Ordering

Standard numeric ordering applies.
Scale does not affect ordering:

```
100 < 100.01   // true
99.99 < 100    // true
```

## Serialization

When serializing decimals (for storage, caching, or API boundaries), implementations SHOULD preserve scale by using string representation:

```json
{"amount": "100.00", "currency": "USD"}
```

This ensures `100.00` and `100` remain distinguishable for tolerance purposes.
