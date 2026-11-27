/*
 * Average Cost Booking Method
 *
 * All lots are merged into a single average-cost lot.
 * Reductions are taken from this averaged position.
 */

module core/formal/booking/average

open core/formal/inventory
open util/integer

-- Average cost inventory maintains a single aggregated lot per commodity
sig AverageCostInventory {
  positions: set AveragePosition
}

sig AveragePosition {
  commodity: Commodity,
  totalUnits: Int,
  totalCost: Int,
  costCurrency: Currency
}

-- Compute average cost per unit
fun avgCostPerUnit[pos: AveragePosition]: Int {
  pos.totalUnits > 0 implies div[pos.totalCost, pos.totalUnits] else 0
}

-- Invariant: units and cost must be non-negative
pred ValidAveragePosition[pos: AveragePosition] {
  pos.totalUnits >= 0 and
  pos.totalCost >= 0
}

-- Acquire units: merge into average
pred AverageAcquire[inv, invAfter: AverageCostInventory, c: Commodity, n: Int, costPerUnit: Int, cur: Currency] {
  n > 0 and costPerUnit >= 0
  let existingPos = { p: inv.positions | p.commodity = c and p.costCurrency = cur } |
  some newPos: AveragePosition |
    newPos.commodity = c and
    newPos.costCurrency = cur and
    (one existingPos implies (
      -- Merge with existing position
      newPos.totalUnits = add[(existingPos.totalUnits), n] and
      newPos.totalCost = add[(existingPos.totalCost), mul[n, costPerUnit]]
    ) else (
      -- Create new position
      newPos.totalUnits = n and
      newPos.totalCost = mul[n, costPerUnit]
    )) and
    invAfter.positions = (inv.positions - existingPos) + newPos
}

-- Reduce units: proportional cost reduction
pred AverageReduce[inv, invAfter: AverageCostInventory, c: Commodity, n: Int, cur: Currency] {
  n > 0
  some pos: inv.positions |
    pos.commodity = c and
    pos.costCurrency = cur and
    pos.totalUnits >= n and
    (some newPos: AveragePosition |
      newPos.commodity = c and
      newPos.costCurrency = cur and
      newPos.totalUnits = sub[pos.totalUnits, n] and
      -- Cost reduced proportionally
      newPos.totalCost = sub[pos.totalCost, mul[n, avgCostPerUnit[pos]]] and
      invAfter.positions = (inv.positions - pos) + newPos)
}

-- Cost basis for a reduction under average method
fun averageReductionCostBasis[pos: AveragePosition, n: Int]: Int {
  mul[n, avgCostPerUnit[pos]]
}

-- Example: Average cost calculation
pred AverageExample {
  some inv1, inv2, inv3: AverageCostInventory, c: Commodity, cur: Currency |
    no inv1.positions and
    -- (scaled to fit Alloy's integers: 100 units -> 1, $10 -> 1, $20 -> 3)
    -- Buy 100 units @ $10 = $1000 total
    AverageAcquire[inv1, inv2, c, 1, 1, cur] and
    -- Buy 100 more @ $20 = $2000 total (scaled: 1 @ 3)
    -- Average is now $3000 / 200 = $15 (scaled: 4 / 2 = 2)
    (some inv2a: AverageCostInventory |
      AverageAcquire[inv2, inv2a, c, 1, 3, cur] and
      -- Sell 50 units @ average cost of $15 = $750 cost basis
      -- (scaled: sell 1 @ 2, leaving 1 unit with total cost 2)
      AverageReduce[inv2a, inv3, c, 1, cur] and
      (some pos: inv3.positions | pos.totalUnits = 1 and pos.totalCost = 2))
}

-- Average preserves total cost equation
assert AverageCostPreserved {
  all inv, invAfter: AverageCostInventory, c: Commodity, u, cost: Int, cur: Currency |
    AverageAcquire[inv, invAfter, c, u, cost, cur] implies
    -- New total cost = old total cost + new cost
    let oldPos = { p: inv.positions | p.commodity = c and p.costCurrency = cur } |
    let newPos = { p: invAfter.positions | p.commodity = c and p.costCurrency = cur } |
    (one oldPos and one newPos) implies
      newPos.totalCost = add[oldPos.totalCost, mul[u, cost]]
}

-- Average cost is weighted average of all purchases: two purchases into an
-- empty inventory leave a position whose average cost per unit is
-- (u1*c1 + u2*c2) / (u1 + u2). Quantities and costs are capped at 2 so the
-- weighted sum (at most 8) fits the 5-bit integers of the check.
assert AverageCostIsWeightedAverage {
  all inv0, inv1, inv2: AverageCostInventory, c: Commodity, cur: Currency, u1, c1, u2, c2: Int |
    (no inv0.positions and u1 <= 2 and c1 <= 2 and u2 <= 2 and c2 <= 2 and
     AverageAcquire[inv0, inv1, c, u1, c1, cur] and
     AverageAcquire[inv1, inv2, c, u2, c2, cur]) implies
    (all pos: inv2.positions | pos.commodity = c and pos.costCurrency = cur implies
      avgCostPerUnit[pos] = div[add[mul[u1, c1], mul[u2, c2]], add[u1, u2]])
}

check AverageCostPreserved for 4
check AverageCostIsWeightedAverage for 4 but 5 Int

run AverageExample for 5
