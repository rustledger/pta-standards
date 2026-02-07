/*
 * HIFO Booking Method - Highest In, First Out
 *
 * Lots with the highest cost basis are consumed first.
 * This minimizes realized gains (or maximizes losses).
 */

module core/formal/booking/hifo

open core/formal/inventory
open util/ordering[Time]

-- HIFO reduction: use highest cost lots first
pred HIFOReduce[inv, inv': Inventory, c: Commodity, units: Int] {
  units > 0
  let lotsForCommodity = { lot: inv.lots | lot.commodity = c } |
  some lotsUsed: set Lot |
    -- All used lots are from this commodity
    lotsUsed in lotsForCommodity and

    -- Units sum to requested amount
    (sum lot: lotsUsed | lot.units) = units and

    -- HIFO constraint: used lots have higher cost than unused lots
    (all used: lotsUsed, unused: (lotsForCommodity - lotsUsed) |
      gte[used.costPerUnit, unused.costPerUnit]) and

    -- Update inventory
    inv'.lots = inv.lots - lotsUsed
}

-- HIFO selects the highest cost lots
pred HIFOSelectsHighestCost[inv: Inventory, c: Commodity, units: Int, selected: set Lot] {
  let available = { lot: inv.lots | lot.commodity = c } |
  selected in available and
  (sum lot: selected | lot.units) = units and
  -- No unselected lot has higher cost than any selected lot
  (all sel: selected, unsel: (available - selected) |
    gte[sel.costPerUnit, unsel.costPerUnit])
}

-- Example: HIFO with varying costs
pred HIFOExample {
  some inv: Inventory, c: Commodity, cur: Currency |
  some disj lot1, lot2, lot3: Lot |
  some disj t1, t2, t3: Time |
    lt[t1, t2] and lt[t2, t3] and
    -- Three lots at different prices
    lot1.commodity = c and lot1.units = 50 and lot1.costPerUnit = 10 and lot1.acquisitionDate = t1 and
    lot2.commodity = c and lot2.units = 50 and lot2.costPerUnit = 25 and lot2.acquisitionDate = t2 and
    lot3.commodity = c and lot3.units = 50 and lot3.costPerUnit = 15 and lot3.acquisitionDate = t3 and
    inv.lots = lot1 + lot2 + lot3 and
    -- HIFO should select lot2 (cost=25) first when reducing
    some hifoLots: set Lot |
      HIFOSelectsHighestCost[inv, c, 50, hifoLots] and
      hifoLots = lot2
}

-- HIFO minimizes gain (maximizes cost basis used)
pred HIFOMinimizesGain[inv: Inventory, c: Commodity, units: Int, salePrice: Int] {
  some hifoLots: set Lot |
    HIFOSelectsHighestCost[inv, c, units, hifoLots] and
    -- Cost basis is maximized
    let hifoCost = (sum lot: hifoLots | mul[lot.units, lot.costPerUnit]) |
    -- Compare to any other selection
    (all otherLots: set Lot |
      (otherLots in inv.lots and
       all lot: otherLots | lot.commodity = c and
       (sum lot: otherLots | lot.units) = units) implies
      (sum lot: otherLots | mul[lot.units, lot.costPerUnit]) <= hifoCost)
}

-- Gain calculation: sale proceeds - cost basis
fun calculateGain[saleProceeds: Int, costBasis: Int]: Int {
  sub[saleProceeds, costBasis]
}

-- Assertions
assert HIFOMaximizesCostBasis {
  all inv: Inventory, c: Commodity, u: Int |
    u > 0 and (sum lot: inv.lots | lot.commodity = c implies lot.units else 0) >= u implies
    HIFOMinimizesGain[inv, c, u, 100]
}

assert HIFOUsesHighestCostFirst {
  all inv, inv': Inventory, c: Commodity, u: Int |
    HIFOReduce[inv, inv', c, u] implies
    -- The remaining lots have lower costs
    (all remaining: inv'.lots, removed: (inv.lots - inv'.lots) |
      remaining.commodity = c and removed.commodity = c implies
      lte[remaining.costPerUnit, removed.costPerUnit])
}

check HIFOUsesHighestCostFirst for 5

run HIFOExample for 5
