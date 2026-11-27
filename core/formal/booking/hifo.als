/*
 * HIFO Booking Method - Highest In, First Out
 *
 * Lots with the highest cost basis are consumed first.
 * This minimizes realized gains (or maximizes losses).
 */

module core/formal/booking/hifo

open core/formal/inventory
open util/ordering[Time]

-- HIFO selects the highest cost lots: whole lots dearest first, then k units
-- of the next-dearest lot.
pred HIFOSelectsHighestCost[inv: Inventory, c: Commodity, n: Int, full: set Lot, part: lone Lot, k: Int] {
  SelectUnits[inv, c, n, full, part, k]
  HIFOOrder[inv, c, full, part]
}

-- HIFO reduction: a HIFO selection applied to the inventory. The lot at the
-- boundary may be consumed partially, leaving a residual lot with the same
-- cost, date and label (see ReduceUnits in core/formal/inventory).
pred HIFOReduce[inv, invAfter: Inventory, c: Commodity, n: Int] {
  some full: set Lot, part, rest: lone Lot |
    ReduceUnits[inv, invAfter, c, n, full, part, rest] and
    HIFOOrder[inv, c, full, part]
}

-- Example: HIFO with varying costs
pred HIFOExample {
  some inv: Inventory, c: Commodity, cur: Currency |
  some disj lot1, lot2, lot3: Lot |
  some disj t1, t2, t3: Time |
    lt[t1, t2] and lt[t2, t3] and
    -- Three lots at different prices
    -- (units scaled by 1/50 and costs by 1/5 to fit Alloy's integers)
    lot1.commodity = c and lot1.units = 1 and lot1.costPerUnit = 2 and lot1.acquisitionDate = t1 and
    lot2.commodity = c and lot2.units = 1 and lot2.costPerUnit = 5 and lot2.acquisitionDate = t2 and
    lot3.commodity = c and lot3.units = 1 and lot3.costPerUnit = 3 and lot3.acquisitionDate = t3 and
    inv.lots = lot1 + lot2 + lot3 and
    -- HIFO should select lot2 (cost=25) first when reducing
    some hifoFull: set Lot, hifoPart: lone Lot, k: Int |
      HIFOSelectsHighestCost[inv, c, 1, hifoFull, hifoPart, k] and
      hifoFull = lot2 and no hifoPart
}

-- HIFO minimizes gain (maximizes cost basis used): no other selection of n
-- units, whole or partial, realises a higher cost basis.
pred HIFOMinimizesGain[inv: Inventory, c: Commodity, n: Int, cur: Currency] {
  some hifoFull: set Lot, hifoPart: lone Lot, hifoK: Int |
    HIFOSelectsHighestCost[inv, c, n, hifoFull, hifoPart, hifoK] and
    (all otherFull: set Lot, otherPart: lone Lot, otherK: Int |
      SelectUnits[inv, c, n, otherFull, otherPart, otherK] implies
      selectionCostBasis[otherFull, otherPart, otherK, cur] <=
        selectionCostBasis[hifoFull, hifoPart, hifoK, cur])
}

-- Gain calculation: sale proceeds - cost basis
fun calculateGain[saleProceeds: Int, costBasis: Int]: Int {
  sub[saleProceeds, costBasis]
}

-- Assertions

-- HIFO realises the highest cost basis of any selection of the same units
-- (stated first-order over both selections so that it can be checked; the
-- HIFOMinimizesGain form quantifies over a set inside an existential).
-- Premises: one cost currency, positive units and non-negative costs, small
-- enough that no basis can wrap around Alloy's integers.
assert HIFOMaximizesCostBasis {
  all inv: Inventory, c: Commodity, cur: Currency, n: Int,
      hifoFull, otherFull: set Lot, hifoPart, otherPart: lone Lot, hifoK, otherK: Int |
    ((all l: Lot | l.units >= 1 and l.units <= 2 and l.costPerUnit >= 0 and
                   l.costPerUnit <= 2 and l.costCurrency = cur) and
     HIFOSelectsHighestCost[inv, c, n, hifoFull, hifoPart, hifoK] and
     SelectUnits[inv, c, n, otherFull, otherPart, otherK]) implies
    selectionCostBasis[otherFull, otherPart, otherK, cur] <=
      selectionCostBasis[hifoFull, hifoPart, hifoK, cur]
}

assert HIFOUsesHighestCostFirst {
  all inv, invAfter: Inventory, c: Commodity, u: Int |
    HIFOReduce[inv, invAfter, c, u] implies
    -- The remaining lots have lower costs
    (all remaining: invAfter.lots, removed: (inv.lots - invAfter.lots) |
      remaining.commodity = c and removed.commodity = c implies
      lte[remaining.costPerUnit, removed.costPerUnit])
}

check HIFOMaximizesCostBasis for 3 but 5 Int
check HIFOUsesHighestCostFirst for 5

run HIFOExample for 5
