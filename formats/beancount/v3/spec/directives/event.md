# Event Directive

## Overview

The `event` directive tracks the value of a named variable over time. Events are useful for recording non-financial information that changes throughout the ledger's timeline.

## Syntax

```ebnf
event = date WHITESPACE "event" WHITESPACE name WHITESPACE value
        (NEWLINE metadata)*

name  = string
value = string
```

## Components

### Date

The date the event occurs or the value changes.

### Name

A string identifying the type of event (the variable being tracked).

### Value

A string representing the new value of the variable.

## Examples

### Location Tracking

```beancount
2024-01-01 event "location" "New York, USA"
2024-03-15 event "location" "London, UK"
2024-06-01 event "location" "Berlin, Germany"
2024-09-01 event "location" "New York, USA"
```

### Employment Status

```beancount
2020-06-01 event "employer" "Acme Corp"
2022-09-15 event "employer" "TechStart Inc"
2024-01-01 event "employer" "BigCo"
```

### Life Events

```beancount
2023-05-20 event "status" "married"
2024-02-15 event "status" "parent"
```

### Tax Residence

```beancount
2024-01-01 event "tax-residence" "USA"
2024-07-01 event "tax-residence" "Germany"
```

### With Metadata

```beancount
2024-03-15 event "location" "London, UK"
  reason: "work assignment"
  duration: "3 months"
  visa-type: "work"
```

## Use Cases

### Travel Tracking

```beancount
; Track trips for tax or expense allocation
2024-01-01 event "location" "Home"
2024-02-10 event "location" "Conference - Las Vegas"
2024-02-14 event "location" "Home"
2024-03-01 event "location" "Client Site - Chicago"
2024-03-05 event "location" "Home"
```

### Project Tracking

```beancount
; Track active projects
2024-01-01 event "project" "Website Redesign"
2024-04-01 event "project" "Mobile App"
2024-07-01 event "project" "API Integration"
```

### Vehicle Tracking

```beancount
2020-01-15 event "car" "2020 Toyota Camry"
2024-03-01 event "car" "2024 Tesla Model 3"
```

### Address History

```beancount
2020-06-01 event "address" "123 Main St, Apt 4B, New York, NY 10001"
2023-08-15 event "address" "456 Oak Ave, Brooklyn, NY 11201"
```

## Querying Events

Events can be queried in BQL:

```sql
-- Get all location changes
SELECT date, value FROM events WHERE type = "location"

-- Get location at specific date
SELECT value FROM events
WHERE type = "location" AND date <= 2024-06-15
ORDER BY date DESC LIMIT 1
```

## Reporting

Events enable time-based reporting:

```beancount
; Expenses by location
2024-01-01 event "location" "New York"
2024-01-15 * "Lunch"
  Expenses:Food  25 USD
  Assets:Cash

2024-02-01 event "location" "London"
2024-02-15 * "Lunch"
  Expenses:Food  20 GBP
  Assets:Cash

; Report can show:
; New York: 25 USD in expenses
; London: 20 GBP in expenses
```

## Event vs. Metadata

Use events for:
- Values that change over time
- Information spanning multiple transactions
- Variables you want to query across the ledger

Use metadata for:
- Static information attached to specific directives
- Per-transaction details
- Non-temporal attributes

## Validation

Events have no specific validation errors. All fields are free-form strings.

However, implementations MAY warn about:
- Duplicate events (same name/value on same date)
- Events with empty values

## Common Event Types

| Event Name | Purpose |
|------------|---------|
| `location` | Physical location tracking |
| `employer` | Employment history |
| `address` | Residence address |
| `status` | Life status changes |
| `project` | Active project tracking |
| `tax-residence` | Tax jurisdiction |
| `vehicle` | Vehicle ownership |

## Implementation Notes

1. Store events in a timeline indexed by name
2. Enable lookup of value at any date
3. Support querying event history
4. Events don't affect financial calculations
5. Consider indexing for efficient date-range queries
