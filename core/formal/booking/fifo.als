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
pred FIFOReduce[inv, invAfter: Inventory, c: Commodity, n: Int] {
  n > 0
  let lotsForCommodity = { lot: inv.lots | lot.commodity = c } |
  some lotsUsed: set Lot |
    -- All used lots are from this commodity
    lotsUsed in lotsForCommodity and

    -- Units sum to requested amount
    (sum lot: lotsUsed | lot.units) = n and

    -- FIFO constraint: if lot A is used and lot B is not used,
    -- then A was acquired before or at same time as B
    (all used: lotsUsed, unused: (lotsForCommodity - lotsUsed) |
      lt[used.acquisitionDate, unused.acquisitionDate] or
      used.acquisitionDate = unused.acquisitionDate) and

    -- Update inventory
    invAfter.lots = inv.lots - lotsUsed
}

-- FIFO selects the chronologically earliest lots
pred FIFOSelectsEarliest[inv: Inventory, c: Commodity, n: Int, selected: set Lot] {
  let available = { lot: inv.lots | lot.commodity = c } |
  selected in available and
  (sum lot: selected | lot.units) = n and
  -- No unselected lot is older than any selected lot
  (all sel: selected, unsel: (available - selected) |
    not gt[sel.acquisitionDate, unsel.acquisitionDate] or
    -- Unless we needed the newer lot to reach the unit count
    (sum older: { l: available | lt[l.acquisitionDate, sel.acquisitionDate] } | older.units) < n)
}

-- Example: FIFO with two lots.
-- Amounts are scaled by 1/10 (costs 10 and 15 become 2 and 3) to fit Alloy's
-- integers. This example reduces part of a lot, which FIFOReduce cannot
-- express (it consumes whole lots only), so it has no instance: see
-- scripts/alloy-known-failures.txt. FIFOWholeLotExample below is the
-- whole-lot case the model does cover.
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
      FIFOReduce[inv2a, inv3, c, 8])
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

-- FIFO property: cost basis reflects oldest purchases
-- When reducing, the cost realized comes from earliest lots
pred FIFOCostBasisProperty[inv: Inventory, c: Commodity, n: Int, cur: Currency] {
  let sortedLots = { lot: inv.lots | lot.commodity = c } |
  some usedLots: set Lot |
    FIFOSelectsEarliest[inv, c, n, usedLots] and
    -- The cost basis is sum of (units * cost) for used lots
    (sum lot: usedLots | mul[lot.units, lot.costPerUnit]) >= 0
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
