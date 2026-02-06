# Date Type

This document specifies the date type used for temporal ordering in plain text accounting.

## Definition

A **Date** represents a calendar date without time-of-day information. Dates are used to order directives chronologically and to timestamp financial events.

## Date Model

### Components

| Component | Range | Description |
|-----------|-------|-------------|
| Year | 0001-9999 | Four-digit year |
| Month | 01-12 | Two-digit month |
| Day | 01-31 | Two-digit day (valid for month) |

### No Time Component

Dates represent whole calendar days. There is no time-of-day component:

```
2024-01-15          ; Represents the entire day
; NOT 2024-01-15T14:30:00
```

For intraday ordering, use metadata:

```
2024-01-15 * "Morning purchase"
  time: "09:30"
  ...
```

### No Timezone

Dates are timezone-naive. The interpretation of "2024-01-15" is local to the user's context.

## Syntax

### ISO 8601 Format (Primary)

```
YYYY-MM-DD
```

Examples:
```
2024-01-15
2024-12-31
2000-01-01
```

### Alternative Formats

Some formats accept alternative separators:

```
2024/01/15          ; Slash separator
2024.01.15          ; Dot separator
```

Implementations SHOULD accept at least `YYYY-MM-DD` and `YYYY/MM/DD`.

### Leading Zeros

Month and day MUST include leading zeros:

```
2024-01-05          ; Valid
2024-1-5            ; Invalid (missing leading zeros)
```

## Validation

### Valid Dates

Dates MUST represent valid calendar days:

```
2024-02-29          ; Valid (2024 is a leap year)
2023-02-29          ; Invalid (2023 is not a leap year)
2024-04-31          ; Invalid (April has 30 days)
2024-13-01          ; Invalid (no month 13)
```

### Year Range

Implementations SHOULD support years 0001-9999:

```
0001-01-01          ; Minimum date
9999-12-31          ; Maximum date
```

Years outside this range MAY be rejected.

### Leap Year Rules

A year is a leap year if:

1. Divisible by 4, AND
2. NOT divisible by 100, OR divisible by 400

```
2024 → Leap year (divisible by 4)
2100 → Not leap year (divisible by 100, not 400)
2000 → Leap year (divisible by 400)
```

## Ordering

### Chronological Order

Dates are ordered chronologically:

```
2024-01-01 < 2024-01-02 < 2024-02-01 < 2025-01-01
```

### Comparison

```python
date1 < date2   # date1 is before date2
date1 > date2   # date1 is after date2
date1 == date2  # Same calendar day
date1 <= date2  # date1 is on or before date2
```

### Directive Ordering

Directives are sorted by date. Same-date directives use secondary ordering.

See [Ordering](../model/ordering.md).

## Date Arithmetic

### Day Offset

```python
2024-01-15 + 1 day  = 2024-01-16
2024-01-15 + 30 days = 2024-02-14
2024-01-15 - 1 day  = 2024-01-14
```

### Month Offset

```python
2024-01-31 + 1 month = 2024-02-29  ; Clamped to valid day
2024-03-31 - 1 month = 2024-02-29  ; Clamped to valid day
```

### Day Difference

```python
2024-01-15 - 2024-01-10 = 5 days
2024-02-01 - 2024-01-01 = 31 days
```

## Special Dates

### Today

Some formats support a "today" placeholder:

```
today               ; Resolved at parse time
```

Implementations MAY support this for interactive use.

### Fiscal Dates

Fiscal year boundaries are user-defined:

```
option "fiscal_year_start" "04-01"  ; April 1
```

## Date Ranges

### Period Specification

Date ranges for queries:

```sql
SELECT * WHERE date >= 2024-01-01 AND date < 2025-01-01
```

### Open Ranges

```
date >= 2024-01-01  ; From date onwards
date < 2024-01-01   ; Before date
```

## Date in Directives

### Transaction Date

When the transaction occurred:

```
2024-01-15 * "Purchase"
  ...
```

### Auxiliary Dates

Some formats support auxiliary dates:

```
2024-01-15=2024-01-17 * "Purchase"  ; Transaction=Settlement
```

Or via metadata:

```
2024-01-15 * "Purchase"
  settlement-date: 2024-01-17
  ...
```

### Open/Close Dates

Account lifecycle:

```
2024-01-01 open Assets:Checking
2024-12-31 close Assets:Checking
```

### Balance Assertion Date

Point-in-time assertion:

```
2024-01-15 balance Assets:Checking 1000 USD
; Asserts balance at START of 2024-01-15
```

## Serialization

### Text Format

ISO 8601:

```
2024-01-15
```

### JSON Format

String in ISO 8601:

```json
{
  "date": "2024-01-15"
}
```

### Binary Format

Days since epoch (e.g., Unix epoch 1970-01-01):

```
date = 19738  ; 2024-01-15 as days since 1970-01-01
```

## Implementation

### Memory Model

```python
@dataclass(frozen=True)
class Date:
    year: int
    month: int
    day: int

    def __post_init__(self):
        # Validate
        if not (1 <= self.month <= 12):
            raise ValueError(f"Invalid month: {self.month}")
        if not (1 <= self.day <= days_in_month(self.year, self.month)):
            raise ValueError(f"Invalid day: {self.day}")

    def __lt__(self, other: 'Date') -> bool:
        return (self.year, self.month, self.day) < \
               (other.year, other.month, other.day)

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
```

### Efficient Representation

Dates can be stored as a single integer (days since epoch) for efficient comparison and arithmetic:

```python
class Date:
    _days: int  # Days since 0001-01-01

    def to_days(self) -> int:
        return self._days

    @classmethod
    def from_days(cls, days: int) -> 'Date':
        ...
```

## Validation Errors

### Invalid Format

```
ERROR: Invalid date format
  --> ledger.beancount:42:1
   |
42 | 24-01-15 * "Purchase"
   | ^^^^^^^^
   |
   = expected: YYYY-MM-DD
```

### Invalid Date

```
ERROR: Invalid date
  --> ledger.beancount:42:1
   |
42 | 2024-02-30 * "Purchase"
   | ^^^^^^^^^^
   |
   = February 2024 has only 29 days
```

### Future Date Warning

```
WARNING: Future date
  --> ledger.beancount:42:1
   |
42 | 2099-01-15 * "Purchase"
   | ^^^^^^^^^^
   |
   = date is far in the future
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Primary format | `YYYY-MM-DD` | `YYYY/MM/DD` | `YYYY-MM-DD` |
| Slash separator | Yes | Yes | Yes |
| Dot separator | No | Yes | Yes |
| Auxiliary dates | Metadata | `=` syntax | `=` syntax |
| Today keyword | No | Yes | Yes |
