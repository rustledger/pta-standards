/**
 * Beancount v3 Booking Methods - Formal Specification
 *
 * This Alloy model formalizes the lot matching and booking semantics
 * for inventory reductions in Beancount.
 */

module booking

open util/ordering[Date]

-- =============================================================================
-- SIGNATURES (Data Types)
-- =============================================================================

sig Date {}

sig Decimal {
    -- Decimal values can be compared
    value: one Int
}

sig Currency {}

sig Label {}

/**
 * A Lot represents a position acquired at a specific cost.
 */
sig Lot {
    units: one Decimal,
    cost: one Decimal,
    currency: one Currency,
    acquiredOn: one Date,
    label: lone Label
}

/**
 * An Inventory is a collection of lots for one commodity in one account.
 */
sig Inventory {
    lots: set Lot,
    commodity: one Currency
}

/**
 * Booking methods determine how reductions are matched to lots.
 */
abstract sig BookingMethod {}
one sig STRICT, STRICT_WITH_SIZE, FIFO, LIFO, HIFO, NONE, AVERAGE extends BookingMethod {}

/**
 * A CostSpec specifies which lot(s) to reduce.
 */
sig CostSpec {
    specCost: lone Decimal,
    specDate: lone Date,
    specLabel: lone Label
}

/**
 * A Reduction is an attempt to remove units from inventory.
 */
sig Reduction {
    unitsToReduce: one Decimal,
    spec: one CostSpec,
    method: one BookingMethod,
    inventory: one Inventory,
    -- The lots matched by this reduction
    matchedLots: set Lot,
    -- Whether this reduction succeeded
    succeeded: one Int  -- 1 = success, 0 = failure
}

-- =============================================================================
-- HELPER PREDICATES
-- =============================================================================

/**
 * Check if a lot matches a cost specification.
 */
pred lotMatchesSpec[l: Lot, s: CostSpec] {
    -- If cost specified, must match
    (some s.specCost) implies (l.cost = s.specCost)
    -- If date specified, must match
    (some s.specDate) implies (l.acquiredOn = s.specDate)
    -- If label specified, must match
    (some s.specLabel) implies (l.label = s.specLabel)
}

/**
 * Empty cost spec matches all lots.
 */
pred isEmptySpec[s: CostSpec] {
    no s.specCost
    no s.specDate
    no s.specLabel
}

/**
 * Get all lots matching a spec in an inventory.
 */
fun matchingLots[inv: Inventory, s: CostSpec]: set Lot {
    { l: inv.lots | lotMatchesSpec[l, s] }
}

/**
 * Check if date d1 is before or equal to date d2.
 */
pred dateLeq[d1, d2: Date] {
    d1 in d2.prevs or d1 = d2
}

/**
 * Check if date d1 is strictly before date d2.
 */
pred dateLt[d1, d2: Date] {
    d1 in d2.prevs
}

-- =============================================================================
-- BOOKING METHOD SEMANTICS
-- =============================================================================

/**
 * STRICT: Requires unambiguous lot specification.
 */
pred strictBooking[r: Reduction] {
    let matches = matchingLots[r.inventory, r.spec] | {
        -- Empty spec with multiple lots is an error
        (isEmptySpec[r.spec] and #matches > 1) implies r.succeeded = 0
        -- Single match succeeds
        (#matches = 1) implies (r.matchedLots = matches and r.succeeded = 1)
        -- Non-empty spec with single match succeeds
        (not isEmptySpec[r.spec] and #matches = 1) implies (r.matchedLots = matches and r.succeeded = 1)
        -- No matches is an error
        (#matches = 0) implies r.succeeded = 0
    }
}

/**
 * FIFO: Oldest lot first (by acquisition date).
 */
pred fifoBooking[r: Reduction] {
    let matches = matchingLots[r.inventory, r.spec] | {
        (#matches = 0) implies r.succeeded = 0
        (#matches > 0) implies {
            r.succeeded = 1
            -- Select the oldest lot among matches
            some oldest: matches | {
                all other: matches - oldest | dateLt[oldest.acquiredOn, other.acquiredOn] or oldest.acquiredOn = other.acquiredOn
                oldest in r.matchedLots
            }
        }
    }
}

/**
 * LIFO: Newest lot first (by acquisition date).
 */
pred lifoBooking[r: Reduction] {
    let matches = matchingLots[r.inventory, r.spec] | {
        (#matches = 0) implies r.succeeded = 0
        (#matches > 0) implies {
            r.succeeded = 1
            -- Select the newest lot among matches
            some newest: matches | {
                all other: matches - newest | dateLt[other.acquiredOn, newest.acquiredOn] or other.acquiredOn = newest.acquiredOn
                newest in r.matchedLots
            }
        }
    }
}

/**
 * HIFO: Highest cost first.
 */
pred hifoBooking[r: Reduction] {
    let matches = matchingLots[r.inventory, r.spec] | {
        (#matches = 0) implies r.succeeded = 0
        (#matches > 0) implies {
            r.succeeded = 1
            -- Select the highest cost lot among matches
            some highest: matches | {
                all other: matches - highest | highest.cost.value >= other.cost.value
                highest in r.matchedLots
            }
        }
    }
}

/**
 * NONE: No lot tracking, allows negative inventory.
 */
pred noneBooking[r: Reduction] {
    -- Always succeeds, no lot matching required
    r.succeeded = 1
    -- Matched lots can be empty (creating negative inventory)
    r.matchedLots in r.inventory.lots
}

/**
 * AVERAGE: All lots conceptually merged to average cost.
 */
pred averageBooking[r: Reduction] {
    let matches = matchingLots[r.inventory, r.spec] | {
        -- All lots are treated as a single merged position
        r.matchedLots = matches
        (#matches > 0) implies r.succeeded = 1
        (#matches = 0) implies r.succeeded = 0
    }
}

/**
 * STRICT_WITH_SIZE: Like STRICT but units must match lot size exactly.
 */
pred strictWithSizeBooking[r: Reduction] {
    let matches = matchingLots[r.inventory, r.spec] | {
        -- Same as STRICT
        (isEmptySpec[r.spec] and #matches > 1) implies r.succeeded = 0
        (#matches = 0) implies r.succeeded = 0
        -- Additionally: reduction units must equal lot units
        (#matches = 1) implies {
            let l = matches | {
                (l.units.value = r.unitsToReduce.value) implies (r.matchedLots = matches and r.succeeded = 1)
                (l.units.value != r.unitsToReduce.value) implies r.succeeded = 0
            }
        }
    }
}

-- =============================================================================
-- MAIN BOOKING PREDICATE
-- =============================================================================

/**
 * Apply the appropriate booking method.
 */
pred applyBooking[r: Reduction] {
    r.method = STRICT implies strictBooking[r]
    r.method = STRICT_WITH_SIZE implies strictWithSizeBooking[r]
    r.method = FIFO implies fifoBooking[r]
    r.method = LIFO implies lifoBooking[r]
    r.method = HIFO implies hifoBooking[r]
    r.method = NONE implies noneBooking[r]
    r.method = AVERAGE implies averageBooking[r]

    -- Matched lots must come from the inventory
    r.matchedLots in r.inventory.lots
}

-- =============================================================================
-- INVARIANTS
-- =============================================================================

/**
 * Invariant: Matched lots are always from the reduction's inventory.
 */
fact matchedLotsFromInventory {
    all r: Reduction | r.matchedLots in r.inventory.lots
}

/**
 * Invariant: FIFO always selects the oldest matching lot.
 */
pred fifoSelectsOldest[r: Reduction] {
    (r.method = FIFO and r.succeeded = 1) implies {
        all matched: r.matchedLots |
            all other: matchingLots[r.inventory, r.spec] - matched |
                dateLeq[matched.acquiredOn, other.acquiredOn]
    }
}

/**
 * Invariant: LIFO always selects the newest matching lot.
 */
pred lifoSelectsNewest[r: Reduction] {
    (r.method = LIFO and r.succeeded = 1) implies {
        all matched: r.matchedLots |
            all other: matchingLots[r.inventory, r.spec] - matched |
                dateLeq[other.acquiredOn, matched.acquiredOn]
    }
}

/**
 * Invariant: HIFO always selects the highest cost matching lot.
 */
pred hifoSelectsHighest[r: Reduction] {
    (r.method = HIFO and r.succeeded = 1) implies {
        all matched: r.matchedLots |
            all other: matchingLots[r.inventory, r.spec] - matched |
                matched.cost.value >= other.cost.value
    }
}

-- =============================================================================
-- ASSERTIONS (Properties to Check)
-- =============================================================================

/**
 * STRICT with empty spec and multiple lots should fail.
 */
assert strictEmptySpecMultipleLotsFails {
    all r: Reduction |
        (r.method = STRICT and
         isEmptySpec[r.spec] and
         #r.inventory.lots > 1 and
         applyBooking[r])
        implies r.succeeded = 0
}

/**
 * NONE booking always succeeds.
 */
assert noneAlwaysSucceeds {
    all r: Reduction |
        (r.method = NONE and applyBooking[r])
        implies r.succeeded = 1
}

/**
 * A reduction with no matching lots fails (except NONE).
 */
assert noMatchingLotsFails {
    all r: Reduction |
        (r.method != NONE and
         #matchingLots[r.inventory, r.spec] = 0 and
         applyBooking[r])
        implies r.succeeded = 0
}

/**
 * FIFO and LIFO may select different lots when dates differ.
 */
assert fifoLifoMayDiffer {
    some inv: Inventory, r1, r2: Reduction, l1, l2: Lot |
        l1 != l2 and
        l1 in inv.lots and l2 in inv.lots and
        dateLt[l1.acquiredOn, l2.acquiredOn] and
        r1.inventory = inv and r2.inventory = inv and
        r1.method = FIFO and r2.method = LIFO and
        r1.spec = r2.spec and isEmptySpec[r1.spec] and
        applyBooking[r1] and applyBooking[r2] and
        l1 in r1.matchedLots and l2 in r2.matchedLots
}

-- =============================================================================
-- EXAMPLE SCENARIOS
-- =============================================================================

/**
 * Example: Two lots, FIFO should select the older one.
 */
pred exampleFifoTwoLots {
    some inv: Inventory, r: Reduction, l1, l2: Lot |
        -- Setup: two lots with different dates
        l1 != l2
        inv.lots = l1 + l2
        dateLt[l1.acquiredOn, l2.acquiredOn]  -- l1 is older

        -- FIFO reduction with empty spec
        r.method = FIFO
        r.inventory = inv
        isEmptySpec[r.spec]
        applyBooking[r]

        -- Should select l1 (older)
        l1 in r.matchedLots
        r.succeeded = 1
}

/**
 * Example: Specific lot selection in STRICT mode.
 */
pred exampleStrictSpecificLot {
    some inv: Inventory, r: Reduction, l1, l2: Lot |
        -- Setup: two lots with different costs
        l1 != l2
        inv.lots = l1 + l2
        l1.cost != l2.cost

        -- STRICT reduction specifying l1's cost
        r.method = STRICT
        r.inventory = inv
        r.spec.specCost = l1.cost
        no r.spec.specDate
        no r.spec.specLabel
        applyBooking[r]

        -- Should match only l1
        r.matchedLots = l1
        r.succeeded = 1
}

/**
 * Example: STRICT fails with ambiguous empty spec.
 */
pred exampleStrictAmbiguousFails {
    some inv: Inventory, r: Reduction, l1, l2: Lot |
        -- Setup: two lots
        l1 != l2
        inv.lots = l1 + l2

        -- STRICT reduction with empty spec
        r.method = STRICT
        r.inventory = inv
        isEmptySpec[r.spec]
        applyBooking[r]

        -- Should fail
        r.succeeded = 0
}

-- =============================================================================
-- RUN COMMANDS
-- =============================================================================

run exampleFifoTwoLots for 4 but 2 Lot, 2 Date
run exampleStrictSpecificLot for 4 but 2 Lot
run exampleStrictAmbiguousFails for 4 but 2 Lot

check strictEmptySpecMultipleLotsFails for 5
check noneAlwaysSucceeds for 5
check noMatchingLotsFails for 5
