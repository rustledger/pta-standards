# Amounts

This document specifies the amount model for plain text accounting systems.

## Definition

An **Amount** is a pair consisting of a decimal number and a commodity. It represents a quantity of something measurable.

```
Amount = (Number, Commodity)
```

## Components

### Number

The numeric component is a decimal value with arbitrary precision:

| Property | Description |
|----------|-------------|
| Sign | Positive, negative, or zero |
| Magnitude | Absolute value |
| Precision | Decimal places used |

### Commodity

The commodity identifies what is being measured:

| Type | Examples |
|------|----------|
| Currency | USD, EUR, GBP |
| Stock | AAPL, GOOG, TSLA |
| Cryptocurrency | BTC, ETH |
| Units | HOURS, MILES, ITEMS |

## Notation

### Standard Form

```
<number> <commodity>
```

Examples:
```
100.00 USD
-50.25 EUR
1.5 BTC
10 AAPL
```

### Symbol Prefix (Format-Specific)

Some formats allow symbol prefixes:

```
$100.00        ; USD
€50.25         ; EUR
£30.00         ; GBP
```

## Number Format

### Decimal Representation

Numbers use decimal notation with:

| Element | Character | Required |
|---------|-----------|----------|
| Sign | `-` | No (positive default) |
| Integer part | `0-9` | Yes (at least one digit) |
| Decimal point | `.` | No |
| Fractional part | `0-9` | No |

### Valid Numbers

```
0
1
-1
123
-456
0.5
-0.5
123.456
-789.012
0.00001
1000000
```

### Invalid Numbers

```
.5           ; Missing integer part (format-specific)
1.           ; Trailing decimal (format-specific)
1,000.00     ; Thousands separator (format-specific)
1e10         ; Scientific notation (format-specific)
```

### Thousands Separators

Some formats support grouping:

```
1,000,000.00 USD    ; Comma separator
1.000.000,00 EUR    ; European format
1_000_000.00 USD    ; Underscore separator
```

Separators are stripped during parsing.

## Commodity Format

### Identifier Rules

Commodities are identifiers following format-specific rules:

| Rule | Beancount | Ledger | hledger |
|------|-----------|--------|---------|
| Case | Uppercase | Any | Any |
| Characters | `A-Z0-9'._-` | Any | Any |
| Length | 1-24 | Any | Any |
| Start | Letter | Any | Any |

### Examples

```
USD          ; US Dollar
EUR          ; Euro
AAPL         ; Apple stock
BTC          ; Bitcoin
VTSAX        ; Vanguard fund
"COMP A"     ; Quoted commodity with space
```

## Amount Arithmetic

### Addition

Amounts with the same commodity can be added:

```
100 USD + 50 USD = 150 USD
```

Different commodities cannot be directly added:

```
100 USD + 50 EUR = ERROR (incommensurable)
```

### Subtraction

```
100 USD - 30 USD = 70 USD
```

### Multiplication (by scalar)

```
100 USD × 3 = 300 USD
```

### Division (by scalar)

```
100 USD ÷ 4 = 25 USD
```

### Sign Inversion

```
-(100 USD) = -100 USD
-(-50 EUR) = 50 EUR
```

## Amount Comparison

### Equality

Amounts are equal if both number and commodity match:

```
100 USD == 100 USD     ; true
100 USD == 100.00 USD  ; true (same value)
100 USD == 100 EUR     ; false (different commodity)
100 USD == 99 USD      ; false (different value)
```

### Ordering

Amounts with the same commodity can be ordered:

```
50 USD < 100 USD       ; true
-10 USD < 0 USD        ; true
```

Different commodities cannot be compared:

```
50 USD < 100 EUR       ; undefined
```

## Precision and Rounding

### Display Precision

The precision used in the source determines display:

```
100 USD        ; 0 decimal places
100.0 USD      ; 1 decimal place
100.00 USD     ; 2 decimal places
```

### Internal Precision

Implementations SHOULD maintain full precision internally:

```
Input:  33.33 USD × 3
Stored: 99.99 USD  (not 100.00)
```

### Rounding Modes

When rounding is necessary:

| Mode | 1.5 → | -1.5 → |
|------|-------|--------|
| Half-even (banker's) | 2 | -2 |
| Half-up | 2 | -1 |
| Half-down | 1 | -2 |
| Truncate | 1 | -1 |

## Zero Amounts

### Explicit Zero

```
0 USD
0.00 EUR
-0 USD         ; Equivalent to 0 USD
```

### Zero Detection

```python
amount.is_zero() → bool  # True if number == 0
```

### Zero Commodity

Zero amount retains its commodity:

```
0 USD ≠ 0 EUR  ; Different commodities
```

## Negative Amounts

### Representation

```
-100 USD       ; Explicit negative
(-100 USD)     ; Parenthesized
100 USD-       ; Suffix (rare)
```

### Semantics

Negative amounts represent:
- Outflows (expenses, payments)
- Credits to asset accounts
- Debits to liability accounts

## Amount in Postings

### Single Amount

```
Assets:Checking  100.00 USD
```

### Inferred Amount

When omitted, amount is inferred from transaction balance:

```
2024-01-15 * "Purchase"
  Expenses:Food    25.00 USD
  Assets:Checking              ; Inferred: -25.00 USD
```

### Multiple Commodities

A posting has exactly one amount. Multiple commodities require multiple postings:

```
2024-01-15 * "Exchange"
  Assets:USD   100 USD
  Assets:EUR   -85 EUR
```

## Amount Collections

### Inventory

An inventory is a collection of amounts, one per commodity:

```python
Inventory = Dict[Commodity, Number]

# Example
{
    "USD": Decimal("1000.00"),
    "EUR": Decimal("500.00"),
    "AAPL": Decimal("10")
}
```

### Balance

Account balances are inventories:

```
Assets:Investment
  100.00 USD
  50 AAPL {150.00 USD}
  0.5 BTC
```

## Weight vs. Units

### Units

The raw amount in the posting:

```
10 AAPL        ; 10 units of AAPL
```

### Weight

The value used for balance checking:

```
10 AAPL {150 USD}    ; Weight: 1500 USD (10 × 150)
10 AAPL @ 160 USD    ; Weight: 1600 USD (10 × 160)
10 AAPL              ; Weight: 10 AAPL (no conversion)
```

## Serialization

### Text Format

```
123.45 USD
```

### JSON Format

```json
{
  "number": "123.45",
  "commodity": "USD"
}
```

### Protocol Buffers

```protobuf
message Amount {
  string number = 1;      // Decimal as string
  string commodity = 2;   // Commodity identifier
}
```

## Implementation Model

```python
@dataclass(frozen=True)
class Amount:
    number: Decimal
    commodity: str

    def __add__(self, other: 'Amount') -> 'Amount':
        if self.commodity != other.commodity:
            raise ValueError("Cannot add different commodities")
        return Amount(self.number + other.number, self.commodity)

    def __neg__(self) -> 'Amount':
        return Amount(-self.number, self.commodity)

    def __mul__(self, scalar: Decimal) -> 'Amount':
        return Amount(self.number * scalar, self.commodity)

    def is_zero(self) -> bool:
        return self.number == 0
```

## Validation

### Invalid Amounts

```
ERROR: Invalid amount format
  --> ledger.beancount:42:15
   |
42 |   Assets:Cash  100$
   |                ^^^^
   |
   = expected: <number> <commodity>
```

### Missing Commodity

```
ERROR: Missing commodity
  --> ledger.beancount:42:15
   |
42 |   Assets:Cash  100
   |                ^^^
   |
   = hint: add commodity (e.g., 100 USD)
```
