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
pred SpecificReduce[inv, inv': Inventory, c: Commodity, selectedLots: set IdentifiedLot] {
  -- All selected lots are for this commodity
  all lot: selectedLots | lot.commodity = c

  -- All selected lots exist in inventory
  selectedLots in inv.lots

  -- Remove selected lots from inventory
  inv'.lots = inv.lots - selectedLots
}

-- Partial lot reduction: reduce part of a specific lot
pred SpecificPartialReduce[inv, inv': Inventory, lot: IdentifiedLot, units: Int] {
  units > 0
  units < lot.units
  lot in inv.lots

  -- Create reduced lot
  some reducedLot: IdentifiedLot |
    reducedLot.id = lot.id and
    reducedLot.commodity = lot.commodity and
    reducedLot.units = sub[lot.units, units] and
    reducedLot.costPerUnit = lot.costPerUnit and
    reducedLot.costCurrency = lot.costCurrency and
    reducedLot.acquisitionDate = lot.acquisitionDate and
    inv'.lots = (inv.lots - lot) + reducedLot
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

-- Specific identification with specifier
pred SpecificReduceWithSpec[inv, inv': Inventory, c: Commodity, units: Int, spec: LotSpecifier] {
  let matching = matchingLots[inv, c, spec] |
  some selectedLots: set Lot |
    selectedLots in matching and
    (sum lot: selectedLots | lot.units) = units and
    inv'.lots = inv.lots - selectedLots
}

-- Example: specific lot selection
pred SpecificExample {
  some inv: Inventory, c: Commodity, cur: Currency |
  some disj lot1, lot2: IdentifiedLot |
  some disj t1, t2: Time |
  some disj id1, id2: LotId |
    lt[t1, t2] and
    lot1.id = id1 and lot1.commodity = c and lot1.units = 100 and lot1.costPerUnit = 10 and lot1.acquisitionDate = t1 and
    lot2.id = id2 and lot2.commodity = c and lot2.units = 100 and lot2.costPerUnit = 20 and lot2.acquisitionDate = t2 and
    inv.lots = lot1 + lot2 and
    -- Specifically select lot2 (the more expensive one)
    some inv': Inventory |
      SpecificReduce[inv, inv', c, lot2] and
      inv'.lots = lot1
}

-- Specific identification can achieve any valid reduction
assert SpecificCanMatchAnyMethod {
  all inv, inv': Inventory, c: Commodity, lotsToRemove: set Lot |
    (lotsToRemove in inv.lots and all lot: lotsToRemove | lot.commodity = c) implies
    (lotsToRemove in IdentifiedLot implies SpecificReduce[inv, inv', c, lotsToRemove])
}

-- Tax lot identification rules
-- Long-term vs short-term based on holding period
pred LongTermHolding[lot: Lot, saleDate: Time] {
  -- Held for more than 1 year (simplified as ordering)
  lt[lot.acquisitionDate, saleDate]
}

-- Select lots for tax optimization
pred TaxOptimizedSelection[inv: Inventory, c: Commodity, units: Int, saleDate: Time, salePrice: Int, selected: set Lot] {
  selected in { lot: inv.lots | lot.commodity = c }
  (sum lot: selected | lot.units) = units
  -- Prefer: 1) losses over gains, 2) long-term over short-term
}

check SpecificCanMatchAnyMethod for 4

run SpecificExample for 5
