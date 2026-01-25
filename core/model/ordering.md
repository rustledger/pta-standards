# Directive Ordering

This document specifies the exact ordering rules for directives.

## Overview

Directives are sorted chronologically by date.
When dates are equal, a secondary ordering determines the sequence.

## Primary Sort: Date

All directives are sorted by date ascending:

```
2024-01-01 ... (first)
2024-01-02 ...
2024-01-03 ... (last)
```

## Secondary Sort: Directive Type Priority

When dates are equal, directives are ordered by type priority.
Lower numbers sort first.

| Priority | Directive Type | Rationale |
|----------|---------------|-----------|
| 0 | `open` | Accounts MUST exist before use |
| 1 | `commodity` | Commodities declared before use |
| 2 | `pad` | Padding before balance assertions |
| 3 | `balance` | Assertions checked at start of day |
| 4 | `transaction` | Main entries |
| 5 | `note` | Annotations after transactions |
| 6 | `document` | Attachments after transactions |
| 7 | `event` | State changes |
| 8 | `query` | Queries defined after data |
| 9 | `price` | Prices at end of day |
| 10 | `close` | Accounts closed after all activity |
| 11 | `custom` | User extensions last |

## Tertiary Sort: File Order

When date and type are equal, directives appear in file order (line number):

```
; Same date, same type - file order preserved
2024-01-01 * "First transaction"
  ...

2024-01-01 * "Second transaction"
  ...
```

## Balance Assertion Timing

Balance assertions check the balance at the **beginning of the day** (midnight).

```
2024-01-15 * "Deposit"
  Assets:Checking  100 USD
  Income:Salary

2024-01-15 balance Assets:Checking  100 USD  ; Checks BEFORE the deposit!
```

This assertion checks the balance **before** any transactions on 2024-01-15.

To check the balance **after** the deposit, use the next day:

```
2024-01-15 * "Deposit"
  Assets:Checking  100 USD
  Income:Salary

2024-01-16 balance Assets:Checking  100 USD  ; Checks AFTER the deposit
```

## Pad and Balance Interaction

Pad directives MUST come before their corresponding balance assertion:

```
2024-01-01 pad Assets:Checking Equity:Opening-Balances
2024-01-01 balance Assets:Checking  1000 USD
```

The pad is processed first (priority 2), then the balance assertion (priority 3).

## Open and Close Timing

- `open` is effective at the **start** of the day
- `close` is effective at the **end** of the day

```
2024-01-01 open Assets:Checking

2024-01-01 * "Same day deposit is OK"
  Assets:Checking  100 USD
  Income:Salary

2024-12-31 * "Same day withdrawal is OK"
  Assets:Checking  -100 USD
  Expenses:Final

2024-12-31 close Assets:Checking
```

## Stable Sort Requirement

The sort MUST be **stable** to preserve file order for directives with equal date and type.

Implementations MUST NOT use unstable sorting algorithms.

## Include File Ordering

When files are included, directives are merged and sorted globally:

```
; main.beancount
include "2024-01.beancount"
include "2024-02.beancount"

; All directives from all files are sorted together
; File inclusion order does NOT affect final sort
```

## Edge Cases

### Same-Date Transactions

There is no sub-day ordering mechanism.
Transactions on the same date are ordered by:

1. Type priority (transactions are all priority 4)
2. File line number

```
; Line 10
2024-01-15 * "First"
  ...

; Line 20
2024-01-15 * "Second"
  ...

; "First" comes before "Second" due to line number
```

### Multiple Files, Same Date

When multiple files have directives on the same date:

1. Sort by date
2. Sort by type priority
3. Within same file: sort by line number
4. Across files: order by file processing sequence

For deterministic ordering, use source location from the merged source map.

## Implementation Notes

Implementations SHOULD:

1. Preserve original source locations for error reporting
2. Use stable sort algorithms
3. Maintain a source map for included files
4. Support querying directives by date range efficiently
