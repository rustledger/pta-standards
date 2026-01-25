# Lots and Inventory

This document specifies the lot and inventory model for tracking positions with cost basis.

## Core Concepts

### Position

A **Position** represents units of a commodity with optional acquisition metadata:

- **Units**: The quantity and commodity (e.g., `10 AAPL`)
- **Cost**: Per-unit acquisition cost (e.g., `150.00 USD`)
- **Date**: Acquisition date (defaults to transaction date)
- **Label**: Optional user-specified identifier

### Lot

A **Lot** is a position with specific cost basis, acquisition date, and optional label.
Lots are tracked separately for tax and reporting purposes.

### Inventory

An **Inventory** is a collection of positions (lots) held in an account.
Positions are merged only when ALL attributes match exactly:
- Same commodity
- Same cost per unit
- Same cost currency
- Same acquisition date
- Same label

## Simple vs. Cost-Basis Positions

### Simple Positions

Positions without cost information track commodity quantities only:

```
Assets:Checking   100.00 USD
```

No cost basis is recorded; the position is just units + commodity.

### Positions Held at Cost

Positions with cost include acquisition details essential for tracking investments:

```
Assets:Stock   10 AAPL {150.00 USD, 2024-01-15}
```

The cost specification is preserved for the lifetime of the position.

## Augmentations and Reductions

### Augmentations (Adding to Inventory)

When adding units to an account, a new lot is created with provided specifications:

```
2024-04-01 * "Buy shares"
  Assets:Invest    25 HOOL {23.00 USD, 2024-04-01, "first-lot"}
  Assets:Cash     -575.00 USD
```

The cost specification data is attached to the position and preserved indefinitely.

Cost specifications MAY include any combination of:
- Per-unit cost and currency
- Acquisition date (overrides transaction date if provided)
- Optional label string

### Reductions (Removing from Inventory)

When removing units, the cost specification acts as a **filter** to identify which lot(s) to reduce:

```
2024-05-15 * "Sell shares"
  Assets:Invest   -12 HOOL {23.00 USD}
  Assets:Cash      276.00 USD
```

The system matches this against existing inventory positions.
Matched lots are reduced; unmatched specification elements are discarded.

## Matching and Ambiguity Resolution

### Match Categories

| Category | Description | Outcome |
|----------|-------------|---------|
| **Single match** | Exactly one position matches | Reduce that position |
| **Total match** | Multiple positions match, combined units equal reduction exactly | Reduce all matched positions |
| **No match** | No position satisfies the filter | Error |
| **Ambiguous match** | Multiple positions match with excess units | Apply booking method |

### Total Match Exception

When the sum of all matching positions' units equals the reduction request exactly, all matched positions are consumed without requiring disambiguation.

## Booking Methods

The booking method determines how to resolve ambiguous matches.

### STRICT

- MUST have unambiguous match
- Raises error when multiple lots match with excess units
- Forces explicit disambiguation in source data

### FIFO (First-In, First-Out)

Selects oldest (earliest-dated) matching lots first:

1. Sort matching positions by acquisition date ascending
2. Reduce from oldest lot
3. If lot fully consumed, move to next oldest
4. Repeat until reduction satisfied

### LIFO (Last-In, First-Out)

Selects newest (latest-dated) matching lots first:

1. Sort matching positions by acquisition date descending
2. Reduce from newest lot
3. If lot fully consumed, move to next newest
4. Repeat until reduction satisfied

### AVERAGE

Merges all units of the affected commodity and recalculates average cost:

1. Compute total units and total cost across all matching positions
2. Calculate weighted average cost = total cost / total units
3. Replace all matching positions with single position at average cost
4. Reduce from this averaged position

After AVERAGE booking:
- Date specificity is lost (averaged positions have no specific date)
- Labels are lost

### NONE

Disables booking entirely:

- Reductions are appended unconditionally without matching
- Results in mixed-sign inventories
- Only total units and total cost basis are meaningful
- Compatible with accounts where lot tracking is impractical (e.g., retirement plans)

## Cost Specifications

### Syntax

Cost specifications appear in curly braces `{}` and MAY contain (in any order):

- **Amount**: `23.00 USD` - per-unit cost
- **Date**: `2024-04-25` - acquisition date
- **Label**: `"lot-id"` - user identifier

### Examples

```
{23.00 USD}
{2024-04-25}
{"lot-id"}
{23.00 USD, 2024-04-25}
{2024-04-25, 23.00 USD, "lot-id"}
```

### For Augmentations

Provide lot data to create new position:
- Omitted date defaults to transaction date
- Omitted cost MUST be inferred from other postings (interpolation)
- Omitted label remains empty

### For Reductions

The specification filters inventory by matching stored attributes:
- Only positions matching ALL specified criteria are candidates
- Empty `{}` matches any position with cost basis
- Omitted specification matches any position (including those without cost)

## Prices vs. Cost

**Prices are NOT used by the booking algorithm.**

A posting with both cost and price uses cost for inventory matching:

```
2024-05-15 * "Sell shares"
  Assets:Stock   -12 HOOL {23.00 USD} @ 24.70 USD
  Assets:Cash     296.40 USD
```

- Cost (23.00 USD) drives inventory reduction
- Price (24.70 USD) is recorded for reference
- Capital gains = (price - cost) × quantity = (24.70 - 23.00) × 12 = 20.40 USD

## Weight Calculation

The "weight" of a posting determines its contribution to transaction balance:

| Posting Type | Weight |
|--------------|--------|
| Amount only | `units × currency` |
| With price (`@`) | `units × price` |
| With cost (`{}`) | `units × cost` |
| Cost + price | `units × cost` (price ignored) |

## Partial Lot Reduction

When a lot is partially reduced:

1. Position units decrease by reduction amount
2. Cost per unit remains unchanged
3. Date and label remain unchanged

Example:
```
Before: 25 HOOL {23.00 USD, 2024-04-01, "first-lot"}
Reduce: -12 HOOL
After:  13 HOOL {23.00 USD, 2024-04-01, "first-lot"}
```

## Multiple Commodities

Accounts MAY contain multiple commodity types simultaneously.
Postings affect only their specified commodity; other holdings remain unchanged.

Mixed inventories (positive and negative units of the same commodity) are only permitted under NONE booking.

## Error Conditions

| Error | Condition |
|-------|-----------|
| Insufficient units | Reduction exceeds available matching positions |
| No matching lots | No positions satisfy the cost specification filter |
| Ambiguous match | Multiple candidates with STRICT booking |
| Negative units | Reduction would go below zero (unless NONE booking) |
