# Primitive Types

This document provides an overview of the primitive types used in plain text accounting specifications.

## Overview

Plain text accounting systems build on a small set of primitive types. These types are format-agnostic and define the foundational data representations.

## Type Catalog

| Type | Document | Description |
|------|----------|-------------|
| Decimal | [decimal.md](decimal.md) | Exact decimal numbers for financial calculations |
| Date | [date.md](date.md) | Calendar dates for directive ordering |
| String | [string.md](string.md) | Text values for narrations, payees, metadata |
| Unicode | [unicode.md](unicode.md) | Character encoding and normalization |

## Type Hierarchy

```
Value
├── Scalar
│   ├── Number
│   │   └── Decimal
│   ├── Date
│   ├── String
│   └── Boolean
└── Composite
    ├── Amount (Decimal + Commodity)
    ├── Position (Amount + optional Cost)
    └── Posting (Account + Position + ...)
```

## Common Properties

### Immutability

All primitive values are immutable. Operations create new values rather than modifying existing ones:

```python
# Good: create new value
new_amount = Amount(old_amount.number + 10, old_amount.commodity)

# Bad: mutation (not supported)
old_amount.number += 10  # Error
```

### Equality

Each type defines equality semantics:

| Type | Equality Rule |
|------|---------------|
| Decimal | Numeric value equality (100 == 100.00) |
| Date | Same calendar day |
| String | Byte-for-byte equality after normalization |
| Boolean | Logical equality |

### Ordering

Types that support ordering:

| Type | Ordering |
|------|----------|
| Decimal | Numeric ordering |
| Date | Chronological ordering |
| String | Lexicographic (implementation-defined) |
| Boolean | FALSE < TRUE |

### Serialization

All types have defined text representations:

| Type | Example |
|------|---------|
| Decimal | `123.45` |
| Date | `2024-01-15` |
| String | `"Hello World"` |
| Boolean | `TRUE` / `FALSE` |

## Type Coercion

### Implicit Coercion

Limited implicit coercion is allowed:

| From | To | Rule |
|------|----|------|
| Integer | Decimal | Always allowed |
| Decimal | String | For display only |

### Explicit Coercion

Other conversions require explicit operations:

```python
# String to Decimal
decimal = parse_decimal("123.45")

# Date to String
string = date.isoformat()
```

## Null Values

### No Implicit Nulls

Types do not have implicit null values. Optional fields use explicit optionality:

```python
# Optional payee
payee: Optional[String]  # None or String

# Required narration
narration: String  # Always present
```

### Omission vs. Empty

| Concept | Representation |
|---------|----------------|
| Omitted | Field not present |
| Empty string | `""` |
| Zero | `0` or `0.00` |

## Validation

### Type Validation

Each type has validation rules:

| Type | Validation |
|------|------------|
| Decimal | Finite, within precision limits |
| Date | Valid calendar date |
| String | Valid encoding, no control characters |
| Boolean | TRUE or FALSE only |

### Error Messages

Type errors include the expected type:

```
ERROR: Invalid type
  --> ledger.beancount:42:15
   |
42 |   quantity: "not a number"
   |             ^^^^^^^^^^^^^^
   |
   = expected: Decimal
   = got: String
```

## Implementation Notes

### Memory Representation

Implementations SHOULD use efficient representations:

| Type | Suggested Implementation |
|------|-------------------------|
| Decimal | Fixed-point or arbitrary-precision decimal |
| Date | Integer (days since epoch) or struct |
| String | UTF-8 bytes with interning |
| Boolean | Single byte or bit |

### Interning

Frequently-used strings (account names, commodities) SHOULD be interned for memory efficiency and fast comparison.

## See Also

- [Numerics](../numerics/README.md) - Arithmetic operations and rounding
- [I18n](../i18n/README.md) - Internationalization of formatting
- [Model](../model/README.md) - Composite types built from primitives
