/*
 * FIFO Booking Method - First In, First Out
 *
 * Lots are consumed in chronological order of acquisition.
 * The oldest lots are used first when reducing a position.
 */

module core/formal/booking/fifo

open core/formal/inventory
open util/ordering[Time]

-- FIFO reduction: use oldest lots first
pred FIFOReduce[inv, inv': Inventory, c: Commodity, units: Int] {
  units > 0
  let lotsForCommodity = { lot: inv.lots | lot.commodity = c } |
  some lotsUsed: set Lot |
    -- All used lots are from this commodity
    lotsUsed in lotsForCommodity and

    -- Units sum to requested amount
    (sum lot: lotsUsed | lot.units) = units and

    -- FIFO constraint: if lot A is used and lot B is not used,
    -- then A was acquired before or at same time as B
    (all used: lotsUsed, unused: (lotsForCommodity - lotsUsed) |
      lt[used.acquisitionDate, unused.acquisitionDate] or
      used.acquisitionDate = unused.acquisitionDate) and

    -- Update inventory
    inv'.lots = inv.lots - lotsUsed
}

-- FIFO selects the chronologically earliest lots
pred FIFOSelectsEarliest[inv: Inventory, c: Commodity, units: Int, selected: set Lot] {
  let available = { lot: inv.lots | lot.commodity = c } |
  selected in available and
  (sum lot: selected | lot.units) = units and
  -- No unselected lot is older than any selected lot
  (all sel: selected, unsel: (available - selected) |
    not gt[sel.acquisitionDate, unsel.acquisitionDate] or
    -- Unless we needed the newer lot to reach the unit count
    (sum older: { l: available | lt[l.acquisitionDate, sel.acquisitionDate] } | older.units) < units)
}

-- Example: FIFO with two lots
pred FIFOExample {
  some inv1, inv2, inv3: Inventory, c: Commodity, cur: Currency |
  some disj t1, t2: Time |
    lt[t1, t2] and
    no inv1.lots and
    -- Acquire 100 units at time t1
    AcquireUnits[inv1, inv2, c, 100, 10, cur, t1] and
    -- Acquire 50 more units at time t2
    (some inv2a: Inventory |
      AcquireUnits[inv2, inv2a, c, 50, 15, cur, t2] and
      -- Reduce 80 units using FIFO (should use t1 lot first)
      FIFOReduce[inv2a, inv3, c, 80])
}

-- FIFO property: cost basis reflects oldest purchases
-- When reducing, the cost realized comes from earliest lots
pred FIFOCostBasisProperty[inv: Inventory, c: Commodity, units: Int, cur: Currency] {
  let sortedLots = { lot: inv.lots | lot.commodity = c } |
  some usedLots: set Lot |
    FIFOSelectsEarliest[inv, c, units, usedLots] and
    -- The cost basis is sum of (units * cost) for used lots
    (sum lot: usedLots | mul[lot.units, lot.costPerUnit]) >= 0
}

-- Assertions
assert FIFOUsesOldestFirst {
  all inv, inv': Inventory, c: Commodity, u: Int |
    FIFOReduce[inv, inv', c, u] implies
    -- The remaining lots are the newest ones
    (all remaining: inv'.lots, removed: (inv.lots - inv'.lots) |
      remaining.commodity = c and removed.commodity = c implies
      gte[remaining.acquisitionDate, removed.acquisitionDate])
}

check FIFOUsesOldestFirst for 5

run FIFOExample for 5
