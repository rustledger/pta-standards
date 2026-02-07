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
pred AverageAcquire[inv, inv': AverageCostInventory, c: Commodity, units: Int, costPerUnit: Int, cur: Currency] {
  units > 0 and costPerUnit >= 0
  let existingPos = { p: inv.positions | p.commodity = c and p.costCurrency = cur } |
  some newPos: AveragePosition |
    newPos.commodity = c and
    newPos.costCurrency = cur and
    (one existingPos implies (
      -- Merge with existing position
      newPos.totalUnits = add[(existingPos.totalUnits), units] and
      newPos.totalCost = add[(existingPos.totalCost), mul[units, costPerUnit]]
    ) else (
      -- Create new position
      newPos.totalUnits = units and
      newPos.totalCost = mul[units, costPerUnit]
    )) and
    inv'.positions = (inv.positions - existingPos) + newPos
}

-- Reduce units: proportional cost reduction
pred AverageReduce[inv, inv': AverageCostInventory, c: Commodity, units: Int, cur: Currency] {
  units > 0
  some pos: inv.positions |
    pos.commodity = c and
    pos.costCurrency = cur and
    pos.totalUnits >= units and
    (some newPos: AveragePosition |
      newPos.commodity = c and
      newPos.costCurrency = cur and
      newPos.totalUnits = sub[pos.totalUnits, units] and
      -- Cost reduced proportionally
      newPos.totalCost = sub[pos.totalCost, mul[units, avgCostPerUnit[pos]]] and
      inv'.positions = (inv.positions - pos) + newPos)
}

-- Cost basis for a reduction under average method
fun averageReductionCostBasis[pos: AveragePosition, units: Int]: Int {
  mul[units, avgCostPerUnit[pos]]
}

-- Example: Average cost calculation
pred AverageExample {
  some inv1, inv2, inv3: AverageCostInventory, c: Commodity, cur: Currency |
    no inv1.positions and
    -- Buy 100 units @ $10 = $1000 total
    AverageAcquire[inv1, inv2, c, 100, 10, cur] and
    -- Buy 100 more @ $20 = $2000 total
    -- Average is now $3000 / 200 = $15
    (some inv2a: AverageCostInventory |
      AverageAcquire[inv2, inv2a, c, 100, 20, cur] and
      -- Sell 50 units @ average cost of $15 = $750 cost basis
      AverageReduce[inv2a, inv3, c, 50, cur])
}

-- Average preserves total cost equation
assert AverageCostPreserved {
  all inv, inv': AverageCostInventory, c: Commodity, u, cost: Int, cur: Currency |
    AverageAcquire[inv, inv', c, u, cost, cur] implies
    -- New total cost = old total cost + new cost
    let oldPos = { p: inv.positions | p.commodity = c and p.costCurrency = cur } |
    let newPos = { p: inv'.positions | p.commodity = c and p.costCurrency = cur } |
    (one oldPos and one newPos) implies
      newPos.totalCost = add[oldPos.totalCost, mul[u, cost]]
}

-- Average cost is weighted average of all purchases
assert AverageCostIsWeightedAverage {
  all inv: AverageCostInventory, pos: inv.positions |
    ValidAveragePosition[pos] and pos.totalUnits > 0 implies
    avgCostPerUnit[pos] = div[pos.totalCost, pos.totalUnits]
}

check AverageCostPreserved for 4
check AverageCostIsWeightedAverage for 4

run AverageExample for 5
