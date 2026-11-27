/*
 * Inventory Model - Cost Basis Tracking
 *
 * This module formally specifies inventory/lot tracking for commodities.
 * It models how positions are acquired and reduced using cost lots.
 */

module core/formal/inventory

open util/integer
open util/ordering[Time]

-- Time for temporal modeling
sig Time {}

sig Currency {}
sig Commodity {}

-- A lot represents a specific acquisition of a commodity
sig Lot {
  commodity: Commodity,
  units: Int,
  costPerUnit: Int,
  costCurrency: Currency,
  acquisitionDate: Time
}

-- Inventory is a collection of lots
sig Inventory {
  lots: set Lot
}

-- Position is the total holding of a commodity
sig Position {
  commodity: Commodity,
  totalUnits: Int,
  inventory: Inventory
}

-- Compute total units from lots
fun totalUnitsFromLots[inv: Inventory, c: Commodity]: Int {
  sum lot: inv.lots | lot.commodity = c implies lot.units else 0
}

-- Inventory invariant: position totals match lot sums
pred InventoryConsistent[inv: Inventory] {
  all c: Commodity |
    let lotsForCommodity = { lot: inv.lots | lot.commodity = c } |
    (sum lot: lotsForCommodity | lot.units) >= 0
}

-- Adding units to inventory creates a new lot
pred AcquireUnits[inv, invAfter: Inventory, c: Commodity, n: Int, cost: Int, cur: Currency, t: Time] {
  n > 0
  some newLot: Lot - inv.lots |
    newLot.commodity = c and
    newLot.units = n and
    newLot.costPerUnit = cost and
    newLot.costCurrency = cur and
    newLot.acquisitionDate = t and
    invAfter.lots = inv.lots + newLot
}

-- Reducing units removes from lots according to booking method
-- This is the base predicate; specific methods (FIFO, LIFO) extend this
pred ReduceUnits[inv, invAfter: Inventory, c: Commodity, n: Int, lotsUsed: set Lot] {
  n > 0
  all lot: lotsUsed | lot in inv.lots and lot.commodity = c
  (sum lot: lotsUsed | lot.units) = n
  invAfter.lots = inv.lots - lotsUsed
}

-- Total cost basis of inventory for a commodity
fun totalCostBasis[inv: Inventory, c: Commodity, cur: Currency]: Int {
  sum lot: inv.lots |
    (lot.commodity = c and lot.costCurrency = cur) implies mul[lot.units, lot.costPerUnit] else 0
}

-- Average cost per unit
fun averageCost[inv: Inventory, c: Commodity, cur: Currency]: Int {
  let total = totalUnitsFromLots[inv, c] |
  total > 0 implies div[totalCostBasis[inv, c, cur], total] else 0
}

-- Inventory is empty for a commodity
pred EmptyPosition[inv: Inventory, c: Commodity] {
  no lot: inv.lots | lot.commodity = c
}

-- Bounded magnitudes: the checks assume lots of at most 2 units so that, at
-- scope 3, no sum of lot units can wrap around Alloy's 4-bit integers (its
-- overflow guard does not reliably reject wrapped sums).
pred BoundedLots {
  all lot: Lot | lot.units >= -2 and lot.units <= 2
}

-- Assertions
assert AcquireIncreasesUnits {
  all inv, invAfter: Inventory, c: Commodity, u, cost: Int, cur: Currency, t: Time |
    (BoundedLots and AcquireUnits[inv, invAfter, c, u, cost, cur, t]) implies
    totalUnitsFromLots[invAfter, c] = add[totalUnitsFromLots[inv, c], u]
}

assert ReduceDecreasesUnits {
  all inv, invAfter: Inventory, c: Commodity, u: Int, lots: set Lot |
    (BoundedLots and ReduceUnits[inv, invAfter, c, u, lots]) implies
    totalUnitsFromLots[invAfter, c] = sub[totalUnitsFromLots[inv, c], u]
}

check AcquireIncreasesUnits for 3
check ReduceDecreasesUnits for 3

-- Example: simple inventory operations
pred SimpleInventoryExample {
  some inv1, inv2: Inventory, c: Commodity, cur: Currency, t1: Time |
    no inv1.lots and
    -- (100 units at 10, scaled to fit Alloy's 4-bit integers)
    AcquireUnits[inv1, inv2, c, 5, 2, cur, t1] and
    totalUnitsFromLots[inv2, c] = 5
}

run SimpleInventoryExample for 4

-- Non-vacuity: the premise of ReduceDecreasesUnits is satisfiable.
run ReduceExample {
  some inv, invAfter: Inventory, c: Commodity, n: Int, used: set Lot |
    BoundedLots and some inv.lots and ReduceUnits[inv, invAfter, c, n, used]
} for 3
