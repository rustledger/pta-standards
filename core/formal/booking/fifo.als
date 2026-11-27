/*
 * FIFO Booking Method - First In, First Out
 *
 * Lots are consumed in chronological order of acquisition.
 * The oldest lots are used first when reducing a position; the lot at the
 * boundary may be consumed partially, leaving a residual lot with the same
 * cost, date and label (see ReduceUnits in core/formal/inventory).
 */

module core/formal/booking/fifo

open core/formal/inventory
open util/ordering[Time]

-- FIFO selects the chronologically earliest lots: whole lots oldest first,
-- then k units of the next-oldest lot.
pred FIFOSelectsEarliest[inv: Inventory, c: Commodity, n: Int, full: set Lot, part: lone Lot, k: Int] {
  SelectUnits[inv, c, n, full, part, k]
  FIFOOrder[inv, c, full, part]
}

-- FIFO reduction: a FIFO selection applied to the inventory.
pred FIFOReduce[inv, invAfter: Inventory, c: Commodity, n: Int] {
  some full: set Lot, part, rest: lone Lot |
    ReduceUnits[inv, invAfter, c, n, full, part, rest] and
    FIFOOrder[inv, c, full, part]
}

-- Example: FIFO with two lots: buy 100 @ 10 then 50 @ 15, sell 80.
-- Amounts are scaled by 1/10 (costs 10 and 15 become 2 and 3) to fit Alloy's
-- integers. The sale consumes 80 of the first lot and leaves 20 of it, at
-- the same cost and date, beside the untouched second lot.
pred FIFOExample {
  some inv1, inv2, inv3: Inventory, c: Commodity, cur: Currency |
  some disj t1, t2: Time |
    lt[t1, t2] and
    no inv1.lots and
    -- Acquire 100 units at time t1
    AcquireUnits[inv1, inv2, c, 10, 2, cur, t1] and
    -- Acquire 50 more units at time t2
    (some inv2a: Inventory |
      AcquireUnits[inv2, inv2a, c, 5, 3, cur, t2] and
      -- Reduce 80 units using FIFO (should use t1 lot first)
      FIFOReduce[inv2a, inv3, c, 8] and
      -- 20 units of the t1 lot remain beside the untouched t2 lot
      #inv3.lots = 2 and
      (some r: inv3.lots | r.acquisitionDate = t1 and r.units = 2 and r.costPerUnit = 2) and
      (some r: inv3.lots | r.acquisitionDate = t2 and r.units = 5 and r.costPerUnit = 3))
}

-- Example: FIFO reducing exactly the oldest lot leaves the newer one.
pred FIFOWholeLotExample {
  some inv1, inv2, inv3: Inventory, c: Commodity, cur: Currency |
  some disj t1, t2: Time |
    lt[t1, t2] and
    no inv1.lots and
    AcquireUnits[inv1, inv2, c, 2, 2, cur, t1] and
    (some inv2a: Inventory |
      AcquireUnits[inv2, inv2a, c, 1, 3, cur, t2] and
      FIFOReduce[inv2a, inv3, c, 2] and
      inv3.lots.acquisitionDate = t2)
}

-- FIFO property: cost basis reflects oldest purchases.
-- When reducing, the cost realized comes from the earliest lots.
pred FIFOCostBasisProperty[inv: Inventory, c: Commodity, n: Int, cur: Currency] {
  some full: set Lot, part: lone Lot, k: Int |
    FIFOSelectsEarliest[inv, c, n, full, part, k] and
    selectionCostBasis[full, part, k, cur] >= 0
}

-- Assertions
assert FIFOUsesOldestFirst {
  all inv, invAfter: Inventory, c: Commodity, u: Int |
    FIFOReduce[inv, invAfter, c, u] implies
    -- The remaining lots are the newest ones
    (all remaining: invAfter.lots, removed: (inv.lots - invAfter.lots) |
      remaining.commodity = c and removed.commodity = c implies
      gte[remaining.acquisitionDate, removed.acquisitionDate])
}

check FIFOUsesOldestFirst for 5

run FIFOExample for 5 but 5 Int
run FIFOWholeLotExample for 5
