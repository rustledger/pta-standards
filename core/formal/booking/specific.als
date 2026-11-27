/*
 * Specific Identification Booking Method
 *
 * The user explicitly specifies which lot(s) to use when reducing a position.
 * This provides maximum flexibility for tax optimization.
 */

module core/formal/booking/specific

open core/formal/inventory
open util/ordering[Time]

-- A lot identifier for specific selection
sig LotId {}

-- Extended lot with identifier
sig IdentifiedLot extends Lot {
  id: LotId
}

-- Specific reduction: user selects exact lots
pred SpecificReduce[inv, invAfter: Inventory, c: Commodity, selectedLots: set IdentifiedLot] {
  -- All selected lots are for this commodity
  all lot: selectedLots | lot.commodity = c

  -- All selected lots exist in inventory
  selectedLots in inv.lots

  -- Remove selected lots from inventory
  invAfter.lots = inv.lots - selectedLots
}

-- Partial lot reduction: reduce part of a specific lot. This is the shared
-- ReduceUnits with the chosen lot as its split lot: the residual is a fresh
-- lot (not already in the inventory) with the same key and identifier.
pred SpecificPartialReduce[inv, invAfter: Inventory, lot: IdentifiedLot, n: Int] {
  n < lot.units
  some rest: IdentifiedLot |
    rest.id = lot.id and
    ReduceUnits[inv, invAfter, lot.commodity, n, none, lot, rest]
}

-- Lot specification syntax (as in beancount)
-- {2023-05-15}  - match by date
-- {100.00 USD}  - match by cost
-- {FIFO}        - use FIFO method
-- {}            - match any

abstract sig LotSpecifier {}
sig DateSpec extends LotSpecifier { specDate: Time }
sig CostSpec extends LotSpecifier { specCost: Int, specCurrency: Currency }

-- Match lot against specifier
pred LotMatchesSpec[lot: Lot, spec: LotSpecifier] {
  spec in DateSpec implies lot.acquisitionDate = spec.specDate
  spec in CostSpec implies (lot.costPerUnit = spec.specCost and lot.costCurrency = spec.specCurrency)
}

-- Find lots matching a specifier
fun matchingLots[inv: Inventory, c: Commodity, spec: LotSpecifier]: set Lot {
  { lot: inv.lots | lot.commodity = c and LotMatchesSpec[lot, spec] }
}

-- Specific identification with specifier: the matching lots are reduced,
-- whole or (at most one of them) in part.
pred SpecificReduceWithSpec[inv, invAfter: Inventory, c: Commodity, n: Int, spec: LotSpecifier] {
  some full: set Lot, part, rest: lone Lot |
    full + part in matchingLots[inv, c, spec] and
    ReduceUnits[inv, invAfter, c, n, full, part, rest]
}

-- Example: specific lot selection
pred SpecificExample {
  some inv: Inventory, c: Commodity, cur: Currency |
  some disj lot1, lot2: IdentifiedLot |
  some disj t1, t2: Time |
  some disj id1, id2: LotId |
    lt[t1, t2] and
    -- (units scaled by 1/100 and costs by 1/10 to fit Alloy's integers)
    lot1.id = id1 and lot1.commodity = c and lot1.units = 1 and lot1.costPerUnit = 1 and lot1.acquisitionDate = t1 and
    lot2.id = id2 and lot2.commodity = c and lot2.units = 1 and lot2.costPerUnit = 2 and lot2.acquisitionDate = t2 and
    inv.lots = lot1 + lot2 and
    -- Specifically select lot2 (the more expensive one)
    some invAfter: Inventory |
      SpecificReduce[inv, invAfter, c, lot2] and
      invAfter.lots = lot1
}

-- Specific identification can achieve any valid reduction: whatever set of
-- identified lots of the commodity another method (FIFO, LIFO, HIFO, ...)
-- would remove, SpecificReduce accepts that same selection and produces the
-- same resulting inventory. (`invAfter` is the inventory with exactly those
-- lots removed; quantifying over an arbitrary `invAfter` would be false.)
assert SpecificCanMatchAnyMethod {
  all inv, invAfter: Inventory, c: Commodity, lotsToRemove: set Lot |
    (lotsToRemove in inv.lots and all lot: lotsToRemove | lot.commodity = c) implies
    ((lotsToRemove in IdentifiedLot and invAfter.lots = inv.lots - lotsToRemove)
      implies SpecificReduce[inv, invAfter, c, lotsToRemove])
}

-- Tax lot identification rules
-- Long-term vs short-term based on holding period
pred LongTermHolding[lot: Lot, saleDate: Time] {
  -- Held for more than 1 year (simplified as ordering)
  lt[lot.acquisitionDate, saleDate]
}

-- Select lots for tax optimization
pred TaxOptimizedSelection[inv: Inventory, c: Commodity, n: Int, saleDate: Time, salePrice: Int, selected: set Lot] {
  selected in { lot: inv.lots | lot.commodity = c }
  (sum lot: selected | lot.units) = n
  -- Prefer: 1) losses over gains, 2) long-term over short-term
}

check SpecificCanMatchAnyMethod for 4

run SpecificExample for 5

-- A partial specific reduction removes exactly n units. (Before the residual
-- had to be fresh, it could coincide with a lot already held and be absorbed
-- by set union, losing units.)
assert SpecificPartialReduceDecreasesUnits {
  all inv, invAfter: Inventory, lot: IdentifiedLot, n: Int |
    (BoundedLots and SpecificPartialReduce[inv, invAfter, lot, n]) implies
    totalUnitsFromLots[invAfter, lot.commodity] = sub[totalUnitsFromLots[inv, lot.commodity], n]
}

check SpecificPartialReduceDecreasesUnits for 3

-- Non-vacuity: a partial specific reduction exists.
run SpecificPartialExample {
  some inv, invAfter: Inventory, lot: IdentifiedLot, n: Int |
    SpecificPartialReduce[inv, invAfter, lot, n]
} for 3
