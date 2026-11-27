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
sig Label {}

-- A lot represents a specific acquisition of a commodity
sig Lot {
  commodity: Commodity,
  units: Int,
  costPerUnit: Int,
  costCurrency: Currency,
  acquisitionDate: Time,
  label: lone Label
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

-- Two lots share a booking key when they agree on every attribute but units
-- (core/model/lot.md: positions merge only when ALL attributes match).
pred SameKey[a, b: Lot] {
  a.commodity = b.commodity
  a.costPerUnit = b.costPerUnit
  a.costCurrency = b.costCurrency
  a.acquisitionDate = b.acquisitionDate
  a.label = b.label
}

-- Selecting n units of c to reduce: the `full` lots are consumed whole and
-- `k` units are taken from at most one further `part` lot (0 < k < its
-- units). One partially consumed lot is enough for every method that walks
-- lots in an order (FIFO, LIFO, HIFO): the walk splits only the lot at the
-- boundary. A total match (lot.md) is the case with no `part`.
pred SelectUnits[inv: Inventory, c: Commodity, n: Int, full: set Lot, part: lone Lot, k: Int] {
  n > 0
  all lot: full + part | lot in inv.lots and lot.commodity = c
  no full & part
  some part implies (k > 0 and k < part.units) else k = 0
  add[(sum lot: full | lot.units), k] = n
}

-- Units a selection takes from one lot.
fun unitsTaken[lot: Lot, full: set Lot, part: lone Lot, k: Int]: Int {
  lot in full implies lot.units else (lot in part implies k else 0)
}

-- Cost basis a selection realises, in one cost currency.
fun selectionCostBasis[full: set Lot, part: lone Lot, k: Int, cur: Currency]: Int {
  sum lot: full + part |
    lot.costCurrency = cur implies mul[unitsTaken[lot, full, part, k], lot.costPerUnit] else 0
}

-- Reducing units. Lots are immutable atoms, so a partial reduction removes
-- the `part` lot and adds a fresh `rest` lot with the same key (cost, date,
-- label) carrying the remaining units, like a UTXO change output. `rest`
-- must be fresh: if it could be a lot already in the inventory, set union
-- would absorb it and units would be lost.
pred ReduceUnits[inv, invAfter: Inventory, c: Commodity, n: Int,
                 full: set Lot, part: lone Lot, rest: lone Lot] {
  some part iff some rest
  SelectUnits[inv, c, n, full, part, (some part implies sub[part.units, rest.units] else 0)]
  some part implies {
    rest not in inv.lots
    SameKey[rest, part]
  }
  invAfter.lots = ((inv.lots - full) - part) + rest
}

-- Lots of c that a selection leaves untouched.
fun untouched[inv: Inventory, c: Commodity, full: set Lot, part: lone Lot]: set Lot {
  { lot: inv.lots | lot.commodity = c } - full - part
}

-- Method orders over a selection: every consumed lot comes no later in the
-- method's order than any untouched lot, and the split lot comes last among
-- the consumed ones.
pred FIFOOrder[inv: Inventory, c: Commodity, full: set Lot, part: lone Lot] {
  all used: full + part, unused: untouched[inv, c, full, part] |
    lte[used.acquisitionDate, unused.acquisitionDate]
  all f: full, p: part | lte[f.acquisitionDate, p.acquisitionDate]
}

pred LIFOOrder[inv: Inventory, c: Commodity, full: set Lot, part: lone Lot] {
  all used: full + part, unused: untouched[inv, c, full, part] |
    gte[used.acquisitionDate, unused.acquisitionDate]
  all f: full, p: part | gte[f.acquisitionDate, p.acquisitionDate]
}

pred HIFOOrder[inv: Inventory, c: Commodity, full: set Lot, part: lone Lot] {
  all used: full + part, unused: untouched[inv, c, full, part] |
    gte[used.costPerUnit, unused.costPerUnit]
  all f: full, p: part | gte[f.costPerUnit, p.costPerUnit]
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
  all inv, invAfter: Inventory, c: Commodity, u: Int, full: set Lot, part, rest: lone Lot |
    (BoundedLots and ReduceUnits[inv, invAfter, c, u, full, part, rest]) implies
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
  some inv, invAfter: Inventory, c: Commodity, n: Int, full: set Lot, part, rest: lone Lot |
    BoundedLots and some inv.lots and ReduceUnits[inv, invAfter, c, n, full, part, rest]
} for 3

-- Keys are unique within an inventory (lot.md's merge rule).
pred KeysUnique[inv: Inventory] {
  all disj a, b: inv.lots | not SameKey[a, b]
}

-- A reduction never invents a key: every lot after is either untouched or
-- the residual of the partially reduced lot.
assert ReductionPreservesKeys {
  all inv, invAfter: Inventory, c: Commodity, n: Int, full: set Lot, part, rest: lone Lot |
    ReduceUnits[inv, invAfter, c, n, full, part, rest] implies
    (all l: invAfter.lots | l in inv.lots or (some p: part | SameKey[l, p]))
}

-- ...and keeps keys unique (no duplicate residual).
assert ReductionKeepsKeysUnique {
  all inv, invAfter: Inventory, c: Commodity, n: Int, full: set Lot, part, rest: lone Lot |
    (KeysUnique[inv] and ReduceUnits[inv, invAfter, c, n, full, part, rest]) implies
    KeysUnique[invAfter]
}

-- Cost basis removed equals the basis of the units taken, lot by lot.
assert ReductionConservesCostBasis {
  all inv, invAfter: Inventory, c: Commodity, cur: Currency, n: Int, full: set Lot, part, rest: lone Lot |
    (BoundedLots and (all l: Lot | l.costPerUnit >= 0 and l.costPerUnit <= 2) and
     ReduceUnits[inv, invAfter, c, n, full, part, rest]) implies
    totalCostBasis[invAfter, c, cur] =
      sub[totalCostBasis[inv, c, cur],
          selectionCostBasis[full, part, (some part implies sub[part.units, rest.units] else 0), cur]]
}

check ReductionPreservesKeys for 4
check ReductionKeepsKeysUnique for 4
check ReductionConservesCostBasis for 3 but 5 Int

run PartialReduceExample {
  some inv, invAfter: Inventory, c: Commodity, n: Int, full: set Lot, part, rest: lone Lot |
    some part and ReduceUnits[inv, invAfter, c, n, full, part, rest]
} for 3
