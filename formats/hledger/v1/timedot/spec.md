# Timedot Format Specification

Timedot is a simplified format for time logging, designed for quick entry.

## Overview

Timedot provides a minimal syntax for logging time spent on activities:

```timedot
2024-01-15
work:project1    ....
work:project2    ..
break            .
```

## File Extension

- `.timedot`

## Basic Syntax

### Date Line

```timedot
2024-01-15
2024/01/15
2024.01.15
```

### Activity Lines

```timedot
ACCOUNT  DOTS [; COMMENT]
```

Where:
- `ACCOUNT` - Activity/project name (account format)
- `DOTS` - Quantity indicators (dots, numbers, or time)
- `COMMENT` - Optional description

## Dot Notation

Each dot represents a unit of time (typically 15 minutes or 0.25 hours):

```timedot
2024-01-15
work:coding    ....    ; 1 hour (4 × 0.25)
work:meeting   ..      ; 30 min (2 × 0.25)
break          .       ; 15 min
```

### Dot Values

| Dots | Hours | Minutes |
|------|-------|---------|
| `.` | 0.25 | 15 |
| `..` | 0.50 | 30 |
| `...` | 0.75 | 45 |
| `....` | 1.00 | 60 |

## Numeric Notation

Explicit numbers for quantity:

```timedot
2024-01-15
work:project    4      ; 4 hours
work:meeting    1.5    ; 1.5 hours
break           0.25   ; 15 minutes
```

## Time Notation

Explicit time format:

```timedot
2024-01-15
work:project    9:00-12:00    ; 3 hours
work:meeting    14:00-15:30   ; 1.5 hours
```

## Mixed Notation

Combine different notations in one file:

```timedot
2024-01-15
work:coding    ....
work:meeting   1.5
work:call      0:30

2024-01-16
work:coding    8
work:review    ..
```

## Account Names

Standard hledger account format:

```timedot
work:client1:project-a    ....
work:client2:maintenance  ..
personal:study            .
```

## Comments

### Line Comments

```timedot
; Full line comment
# Also a comment
* Org-mode style

2024-01-15
work:coding    ....  ; End of line comment
```

### Multi-Line Descriptions

```timedot
2024-01-15
work:coding    ....
  ; Implemented new feature
  ; Fixed bug #123
```

## Empty Days

Days with no activities can be omitted:

```timedot
2024-01-15
work:coding    ....

; 2024-01-16 was a day off (just omit it)

2024-01-17
work:coding    ....
```

## Full Example

```timedot
; Time log for week of 2024-01-15

2024-01-15
work:client-a:development    ....
work:client-a:meetings       ..
work:internal:planning       .
break                        .

2024-01-16
work:client-b:maintenance    ......
work:internal:email          .
break                        ..

2024-01-17
work:client-a:development    ........  ; All day coding
break                        ..

2024-01-18
work:client-b:support        ....
work:client-a:review         ....
break                        ..

2024-01-19
work:internal:documentation  ....
work:training                ....
break                        ..
```

## Conversion to Journal

Timedot entries convert to hledger transactions:

```timedot
2024-01-15
work:coding    ....
```

Becomes:

```hledger
2024-01-15
    (work:coding)    1.00h
```

## Command Usage

```bash
# Read timedot file
hledger -f time.timedot bal

# Convert to journal
hledger -f time.timedot print

# Report by week
hledger -f time.timedot bal -W
```

## Time Units

Default unit is hours. Configure with:

```bash
# Hours (default)
hledger -f time.timedot bal

# Convert to different commodity
hledger -f time.timedot bal --value='H @ $100'
```

## Combining with Journal

Include timedot in main journal:

```hledger
; main.journal
include accounts.journal
include time.timedot
```

## Best Practices

1. **One file per period** (week/month)
2. **Consistent account names** for reporting
3. **Add comments** for notable activities
4. **Regular review** for accuracy

## Limitations

- No transaction amounts (time only)
- No balance assertions
- No multi-posting transactions
- Limited metadata support

## See Also

- [Timeclock Format](../timeclock/spec.md)
- [hledger Syntax](../spec/syntax.md)
