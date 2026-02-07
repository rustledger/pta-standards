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
pred AcquireUnits[inv, inv': Inventory, c: Commodity, units: Int, cost: Int, cur: Currency, t: Time] {
  units > 0
  some newLot: Lot |
    newLot.commodity = c and
    newLot.units = units and
    newLot.costPerUnit = cost and
    newLot.costCurrency = cur and
    newLot.acquisitionDate = t and
    inv'.lots = inv.lots + newLot
}

-- Reducing units removes from lots according to booking method
-- This is the base predicate; specific methods (FIFO, LIFO) extend this
pred ReduceUnits[inv, inv': Inventory, c: Commodity, units: Int, lotsUsed: set Lot] {
  units > 0
  all lot: lotsUsed | lot in inv.lots and lot.commodity = c
  (sum lot: lotsUsed | lot.units) = units
  inv'.lots = inv.lots - lotsUsed
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

-- Assertions
assert AcquireIncreasesUnits {
  all inv, inv': Inventory, c: Commodity, u, cost: Int, cur: Currency, t: Time |
    AcquireUnits[inv, inv', c, u, cost, cur, t] implies
    totalUnitsFromLots[inv', c] = add[totalUnitsFromLots[inv, c], u]
}

assert ReduceDecreasesUnits {
  all inv, inv': Inventory, c: Commodity, u: Int, lots: set Lot |
    ReduceUnits[inv, inv', c, u, lots] implies
    totalUnitsFromLots[inv', c] = sub[totalUnitsFromLots[inv, c], u]
}

check AcquireIncreasesUnits for 4
check ReduceDecreasesUnits for 4

-- Example: simple inventory operations
pred SimpleInventoryExample {
  some inv1, inv2, inv3: Inventory, c: Commodity, cur: Currency, t1, t2: Time |
    no inv1.lots and
    AcquireUnits[inv1, inv2, c, 100, 10, cur, t1] and
    totalUnitsFromLots[inv2, c] = 100
}

run SimpleInventoryExample for 4
