/*
 * LIFO Booking Method - Last In, First Out
 *
 * Lots are consumed in reverse chronological order.
 * The newest lots are used first when reducing a position.
 */

module core/formal/booking/lifo

open core/formal/inventory
open util/ordering[Time]

-- LIFO reduction: use newest lots first
pred LIFOReduce[inv, invAfter: Inventory, c: Commodity, n: Int] {
  n > 0
  let lotsForCommodity = { lot: inv.lots | lot.commodity = c } |
  some lotsUsed: set Lot |
    -- All used lots are from this commodity
    lotsUsed in lotsForCommodity and

    -- Units sum to requested amount
    (sum lot: lotsUsed | lot.units) = n and

    -- LIFO constraint: if lot A is used and lot B is not used,
    -- then A was acquired after or at same time as B
    (all used: lotsUsed, unused: (lotsForCommodity - lotsUsed) |
      gt[used.acquisitionDate, unused.acquisitionDate] or
      used.acquisitionDate = unused.acquisitionDate) and

    -- Update inventory
    invAfter.lots = inv.lots - lotsUsed
}

-- LIFO selects the chronologically latest lots
pred LIFOSelectsLatest[inv: Inventory, c: Commodity, n: Int, selected: set Lot] {
  let available = { lot: inv.lots | lot.commodity = c } |
  selected in available and
  (sum lot: selected | lot.units) = n and
  -- No unselected lot is newer than any selected lot
  (all sel: selected, unsel: (available - selected) |
    not lt[sel.acquisitionDate, unsel.acquisitionDate] or
    -- Unless we needed the older lot to reach the unit count
    (sum newer: { l: available | gt[l.acquisitionDate, sel.acquisitionDate] } | newer.units) < n)
}

-- Example: LIFO with two lots.
-- Amounts are scaled by 1/10 (costs 10 and 15 become 2 and 3) to fit Alloy's
-- integers. This example reduces part of a lot, which LIFOReduce cannot
-- express (it consumes whole lots only), so it has no instance: see
-- scripts/alloy-known-failures.txt. LIFOWholeLotExample below is the
-- whole-lot case the model does cover.
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
      LIFOReduce[inv2a, inv3, c, 4])
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
  some usedLots: set Lot |
    LIFOSelectsLatest[inv, c, n, usedLots]
}

-- LIFO vs FIFO: different cost basis for same reduction
pred LIFODifferentFromFIFO {
  some inv: Inventory, c: Commodity, cur: Currency |
  some disj lot1, lot2: Lot |
  some disj t1, t2: Time |
    lt[t1, t2] and
    -- (units scaled by 1/50 and costs by 1/10 to fit Alloy's integers)
    lot1.commodity = c and lot1.units = 2 and lot1.costPerUnit = 1 and lot1.acquisitionDate = t1 and
    lot2.commodity = c and lot2.units = 1 and lot2.costPerUnit = 2 and lot2.acquisitionDate = t2 and
    inv.lots = lot1 + lot2 and
    -- Reducing 50 units:
    -- LIFO uses lot2 (cost basis = 50 * 20 = 1000)
    -- FIFO uses lot1 (cost basis = 50 * 10 = 500); FIFO's half of lot1 is a
    -- partial-lot reduction, which this whole-lot model cannot express, so
    -- only the LIFO side is constrained here.
    some lifoLots: set Lot |
      LIFOSelectsLatest[inv, c, 1, lifoLots] and
      lifoLots = lot2
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
