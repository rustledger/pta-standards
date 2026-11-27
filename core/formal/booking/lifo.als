/*
 * LIFO Booking Method - Last In, First Out
 *
 * Lots are consumed in reverse chronological order.
 * The newest lots are used first when reducing a position; the lot at the
 * boundary may be consumed partially, leaving a residual lot with the same
 * cost, date and label (see ReduceUnits in core/formal/inventory).
 */

module core/formal/booking/lifo

open core/formal/inventory
open util/ordering[Time]

-- LIFO selects the chronologically latest lots: whole lots newest first,
-- then k units of the next-newest lot.
pred LIFOSelectsLatest[inv: Inventory, c: Commodity, n: Int, full: set Lot, part: lone Lot, k: Int] {
  SelectUnits[inv, c, n, full, part, k]
  LIFOOrder[inv, c, full, part]
}

-- LIFO reduction: a LIFO selection applied to the inventory.
pred LIFOReduce[inv, invAfter: Inventory, c: Commodity, n: Int] {
  some full: set Lot, part, rest: lone Lot |
    ReduceUnits[inv, invAfter, c, n, full, part, rest] and
    LIFOOrder[inv, c, full, part]
}

-- Example: LIFO with two lots: buy 100 @ 10 then 50 @ 15, sell 40.
-- Amounts are scaled by 1/10 (costs 10 and 15 become 2 and 3) to fit Alloy's
-- integers. The sale consumes 40 of the second lot and leaves 10 of it, at
-- the same cost and date, beside the untouched first lot.
pred LIFOExample {
  some inv1, inv2, inv3: Inventory, c: Commodity, cur: Currency |
  some disj t1, t2: Time |
    lt[t1, t2] and
    no inv1.lots and
    -- Acquire 100 units at time t1 @ $10
    AcquireUnits[inv1, inv2, c, 10, 2, cur, t1] and
    -- Acquire 50 more units at time t2 @ $15
    (some inv2a: Inventory |
      AcquireUnits[inv2, inv2a, c, 5, 3, cur, t2] and
      -- Reduce 40 units using LIFO (should use t2 lot first)
      LIFOReduce[inv2a, inv3, c, 4] and
      -- 10 units of the t2 lot remain beside the untouched t1 lot
      #inv3.lots = 2 and
      (some r: inv3.lots | r.acquisitionDate = t2 and r.units = 1 and r.costPerUnit = 3) and
      (some r: inv3.lots | r.acquisitionDate = t1 and r.units = 10 and r.costPerUnit = 2))
}

-- Example: LIFO reducing exactly the newest lot leaves the older one.
pred LIFOWholeLotExample {
  some inv1, inv2, inv3: Inventory, c: Commodity, cur: Currency |
  some disj t1, t2: Time |
    lt[t1, t2] and
    no inv1.lots and
    AcquireUnits[inv1, inv2, c, 2, 2, cur, t1] and
    (some inv2a: Inventory |
      AcquireUnits[inv2, inv2a, c, 1, 3, cur, t2] and
      LIFOReduce[inv2a, inv3, c, 1] and
      inv3.lots.acquisitionDate = t1)
}

-- LIFO property: cost basis reflects newest purchases
pred LIFOCostBasisProperty[inv: Inventory, c: Commodity, n: Int, cur: Currency] {
  some full: set Lot, part: lone Lot, k: Int |
    LIFOSelectsLatest[inv, c, n, full, part, k]
}

-- LIFO vs FIFO: different cost basis for the same reduction
pred LIFODifferentFromFIFO {
  some inv: Inventory, c: Commodity, cur: Currency |
  some disj lot1, lot2: Lot |
  some disj t1, t2: Time |
    lt[t1, t2] and
    -- (units scaled by 1/50 and costs by 1/10 to fit Alloy's integers)
    lot1.commodity = c and lot1.units = 2 and lot1.costPerUnit = 1 and
    lot1.costCurrency = cur and lot1.acquisitionDate = t1 and
    lot2.commodity = c and lot2.units = 1 and lot2.costPerUnit = 2 and
    lot2.costCurrency = cur and lot2.acquisitionDate = t2 and
    inv.lots = lot1 + lot2 and
    -- Reducing 50 units:
    -- LIFO uses all of lot2 (cost basis = 50 * 20 = 1000)
    (some lifoFull: set Lot, lifoPart: lone Lot, lifoK: Int |
      LIFOSelectsLatest[inv, c, 1, lifoFull, lifoPart, lifoK] and
      lifoFull = lot2 and no lifoPart and
      selectionCostBasis[lifoFull, lifoPart, lifoK, cur] = 2) and
    -- FIFO uses half of lot1 (cost basis = 50 * 10 = 500)
    (some fifoFull: set Lot, fifoPart: lone Lot, fifoK: Int |
      SelectUnits[inv, c, 1, fifoFull, fifoPart, fifoK] and FIFOOrder[inv, c, fifoFull, fifoPart] and
      no fifoFull and fifoPart = lot1 and fifoK = 1 and
      selectionCostBasis[fifoFull, fifoPart, fifoK, cur] = 1)
}

-- Assertions
assert LIFOUsesNewestFirst {
  all inv, invAfter: Inventory, c: Commodity, u: Int |
    LIFOReduce[inv, invAfter, c, u] implies
    -- The remaining lots are the oldest ones
    (all remaining: invAfter.lots, removed: (inv.lots - invAfter.lots) |
      remaining.commodity = c and removed.commodity = c implies
      lte[remaining.acquisitionDate, removed.acquisitionDate])
}

check LIFOUsesNewestFirst for 5

run LIFOExample for 5 but 5 Int
run LIFOWholeLotExample for 5
run LIFODifferentFromFIFO for 4
