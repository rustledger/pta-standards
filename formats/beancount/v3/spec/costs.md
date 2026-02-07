# Cost Specifications

## Overview

Cost specifications record the acquisition price of commodities, enabling cost basis tracking, capital gains calculation, and lot identification.

## Syntax

```ebnf
cost_spec = "{" cost_comp_list "}"      ; Per-unit cost
          | "{{" cost_comp_list "}}"    ; Total cost

cost_comp_list = cost_comp ("," cost_comp)*

cost_comp = amount          ; Cost per unit or total
          | date            ; Acquisition date
          | string          ; Lot label
          | "*"             ; Merge cost (average)
```

## Cost Types

### Per-Unit Cost `{...}`

Specifies the cost per unit of the commodity:

```beancount
; 10 shares at $150 each = $1500 total cost
Assets:Stock  10 AAPL {150 USD}
```

The weight for balancing is: `units × cost = 10 × 150 = 1500 USD`

### Total Cost `{{...}}`

Specifies the total cost for all units:

```beancount
; 10 shares for $1500 total = $150 each
Assets:Stock  10 AAPL {{1500 USD}}
```

The weight for balancing is the total cost: `1500 USD`

Per-unit cost is computed as: `1500 / 10 = 150 USD`

## Cost Components

### Amount (Required for Acquisitions)

The cost basis in another currency:

```beancount
Assets:Stock  10 AAPL {150.00 USD}
Assets:Stock  10 AAPL {150 USD, 2024-01-15}
```

### Date (Optional)

The acquisition date for lot identification:

```beancount
; Explicit acquisition date
Assets:Stock  10 AAPL {150 USD, 2024-01-15}

; Date only (for reductions matching by date)
Assets:Stock  -5 AAPL {2024-01-15}
```

If omitted on acquisition, the transaction date is used.

### Label (Optional)

A string identifier for the lot:

```beancount
; Named lot
Assets:Stock  10 AAPL {150 USD, "lot-A"}

; Full specification
Assets:Stock  10 AAPL {150 USD, 2024-01-15, "retirement-fund"}
```

Labels enable explicit lot selection:

```beancount
; Sell from specific lot
Assets:Stock  -5 AAPL {"lot-A"}
```

### Merge Cost `*`

Merges all lots of a commodity into a single average-cost lot:

```beancount
; Before: lot1 (10 @ 150), lot2 (10 @ 160)
Assets:Stock  0 AAPL {*}
; After: single lot (20 @ 155)
```

The average cost is computed as: `total_cost / total_units`

Used with AVERAGE booking method for explicit lot merging.

> **Note:** See [conformance/python-beancount.md](../conformance/python-beancount.md) for implementation status.

## Component Order

Components may appear in any order:

```beancount
; All equivalent
Assets:Stock  10 AAPL {150 USD, 2024-01-15, "lot1"}
Assets:Stock  10 AAPL {2024-01-15, 150 USD, "lot1"}
Assets:Stock  10 AAPL {"lot1", 150 USD, 2024-01-15}
```

## Acquisitions vs. Reductions

### Acquisitions (Positive Units)

Create new lots in inventory:

```beancount
; New lot: 10 AAPL at 150 USD, dated 2024-01-15
Assets:Stock  10 AAPL {150 USD, 2024-01-15}
```

Amount is required for acquisitions.

### Reductions (Negative Units)

Match and reduce existing lots:

```beancount
; Match lot by cost
Assets:Stock  -5 AAPL {150 USD}

; Match by date
Assets:Stock  -5 AAPL {2024-01-15}

; Match by label
Assets:Stock  -5 AAPL {"lot1"}

; Match by cost and date
Assets:Stock  -5 AAPL {150 USD, 2024-01-15}

; Let booking method decide
Assets:Stock  -5 AAPL {}
```

## Empty Cost `{}`

An empty cost specification defers to the account's booking method:

```beancount
2024-01-01 open Assets:Stock AAPL "FIFO"

; FIFO selects oldest lot
Assets:Stock  -5 AAPL {}
```

With STRICT booking, empty cost on reduction is an error if multiple lots exist.

## Cost and Price Together

Cost and price annotations can both appear:

```beancount
; Cost basis: 150 USD, Market price: 185 USD
Assets:Stock  -10 AAPL {150 USD} @ 185 USD
```

- **Cost** (`{150 USD}`): Used for balance calculation and capital gains
- **Price** (`@ 185 USD`): Records market value (informational)

The posting weight uses the cost, not the price.

## Lot Matching

### Exact Match

All specified components must match:

```beancount
; Must match cost AND date
Assets:Stock  -5 AAPL {150 USD, 2024-01-15}
```

### Partial Match

Unspecified components match any value:

```beancount
; Matches any lot with cost 150 USD
Assets:Stock  -5 AAPL {150 USD}

; Matches any lot from 2024-01-15
Assets:Stock  -5 AAPL {2024-01-15}
```

### Ambiguous Match

When multiple lots match and booking is STRICT:

```beancount
2024-01-01 open Assets:Stock AAPL "STRICT"

; Have: lot1 (10 @ 150), lot2 (10 @ 150)
; Both have same cost - ambiguous!
Assets:Stock  -5 AAPL {150 USD}  ; ERROR: Ambiguous
```

Resolve by adding date or label:

```beancount
Assets:Stock  -5 AAPL {150 USD, 2024-01-15}  ; OK
```

## Capital Gains

Cost basis determines capital gains:

```beancount
; Buy at 150
2024-01-15 * "Buy"
  Assets:Stock   10 AAPL {150 USD}
  Assets:Cash  -1500 USD

; Sell at 185
2024-06-15 * "Sell"
  Assets:Stock  -10 AAPL {150 USD} @ 185 USD
  Assets:Cash   1850 USD
  Income:CapitalGains  -350 USD  ; (185-150) × 10
```

## Examples

### Basic Stock Purchase

```beancount
2024-01-15 * "Buy Apple"
  Assets:Brokerage  100 AAPL {185.50 USD}
  Assets:Cash      -18550 USD
```

### With Commission

```beancount
2024-01-15 * "Buy with commission"
  Assets:Brokerage  100 AAPL {185.50 USD}
  Expenses:Commission  9.99 USD
  Assets:Cash
```

### Multiple Lots

```beancount
2024-01-15 * "Buy lot 1"
  Assets:Stock  50 AAPL {150 USD, 2024-01-15, "jan-buy"}
  Assets:Cash

2024-03-15 * "Buy lot 2"
  Assets:Stock  50 AAPL {175 USD, 2024-03-15, "mar-buy"}
  Assets:Cash
```

### Partial Sale

```beancount
2024-06-15 * "Sell from January lot"
  Assets:Stock  -30 AAPL {150 USD, "jan-buy"} @ 200 USD
  Assets:Cash   6000 USD
  Income:CapitalGains
```

### Total Cost for Odd Lots

```beancount
; 7 shares for $1234.56 total
2024-01-15 * "Odd lot purchase"
  Assets:Stock  7 AAPL {{1234.56 USD}}
  Assets:Cash  -1234.56 USD
  ; Per-unit cost: 1234.56 / 7 = 176.3657... USD
```

## Booking Errors

The following conditions produce errors during lot matching:

| Condition | Description |
|-----------|-------------|
| No matching lot | Reduction specification doesn't match any existing lot |
| Insufficient units | Not enough units available in matching lots |
| Ambiguous match | Multiple lots match in STRICT booking mode |
| Negative inventory | Reduction would create negative position (except NONE booking) |

See [conformance/python-beancount.md](../conformance/python-beancount.md) for error type details.

## Implementation Notes

1. Store lots with (units, cost, date, label)
2. Parse cost components in any order
3. Compute per-unit cost for total cost syntax
4. Match lots using all specified components
5. Apply booking method for ties/empty specs
6. Track remaining units after partial reductions
