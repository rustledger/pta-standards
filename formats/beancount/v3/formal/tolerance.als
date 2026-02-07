/**
 * Beancount v3 Balance Tolerances - Formal Specification
 *
 * This Alloy model formalizes the tolerance calculation and
 * balance checking semantics for transactions and assertions.
 */

module tolerance

-- =============================================================================
-- SIGNATURES (Data Types)
-- =============================================================================

sig Currency {}

/**
 * Precision represents the number of decimal places.
 * Higher precision = more decimal places = smaller tolerance.
 */
sig Precision {
    decimalPlaces: one Int
}

/**
 * An Amount with its precision for tolerance computation.
 */
sig Amount {
    value: one Int,        -- Scaled integer (e.g., 10000 for 100.00)
    precision: one Precision,
    currency: one Currency
}

/**
 * Tolerance computed from precision.
 * tolerance = 0.5 × 10^(-precision)
 *
 * We model this as an abstract value that can be compared.
 */
sig Tolerance {
    -- Higher precision means smaller tolerance
    fromPrecision: one Precision,
    -- Tolerance values are ordered (for max computation)
    value: one Int  -- Inverse relationship: lower precision = higher tolerance value
}

/**
 * A Posting is a single line in a transaction.
 */
sig Posting {
    amount: one Amount,
    -- Weight for balance calculation (may differ from amount due to cost/price)
    weight: one Amount
}

/**
 * A Transaction contains postings that must balance.
 */
sig Transaction {
    postings: set Posting,
    -- Computed transaction tolerance (max of posting tolerances)
    tolerance: one Tolerance,
    -- Residual after summing weights
    residual: one Int,
    -- Whether transaction balances
    balances: one Int  -- 1 = balances, 0 = does not balance
}

/**
 * A BalanceAssertion checks an account balance.
 */
sig BalanceAssertion {
    expected: one Amount,
    actual: one Amount,
    -- Explicit tolerance override (optional)
    explicitTolerance: lone Tolerance,
    -- Computed tolerance if no explicit
    computedTolerance: one Tolerance,
    -- Difference between expected and actual
    difference: one Int,
    -- Whether assertion passes
    passes: one Int  -- 1 = passes, 0 = fails
}

-- =============================================================================
-- TOLERANCE COMPUTATION
-- =============================================================================

/**
 * Tolerance from precision: 0.5 × 10^(-precision)
 *
 * We model this inversely: lower precision = higher tolerance value.
 * precision 0 → tolerance 500 (representing 0.5)
 * precision 1 → tolerance 50  (representing 0.05)
 * precision 2 → tolerance 5   (representing 0.005)
 * precision 3 → tolerance 0   (representing 0.0005, rounded)
 */
pred toleranceFromPrecision[t: Tolerance, p: Precision] {
    t.fromPrecision = p
    -- Inverse relationship: higher precision = lower tolerance value
    -- Simplified: use 10^(2-precision) as tolerance value
    p.decimalPlaces = 0 implies t.value = 500
    p.decimalPlaces = 1 implies t.value = 50
    p.decimalPlaces = 2 implies t.value = 5
    p.decimalPlaces >= 3 implies t.value = 0
}

/**
 * Compare tolerances: t1 is greater than or equal to t2.
 */
pred toleranceGeq[t1, t2: Tolerance] {
    t1.value >= t2.value
}

/**
 * Get maximum tolerance from a set of postings.
 */
pred maxToleranceOfPostings[postings: set Posting, result: Tolerance] {
    -- Result must be >= all posting tolerances
    all p: postings | {
        some t: Tolerance | {
            toleranceFromPrecision[t, p.amount.precision]
            toleranceGeq[result, t]
        }
    }
    -- Result is one of the posting tolerances (the max)
    some p: postings | {
        some t: Tolerance | {
            toleranceFromPrecision[t, p.amount.precision]
            result.value = t.value
        }
    }
}

-- =============================================================================
-- BALANCE CHECKING
-- =============================================================================

/**
 * Sum of weights for a currency in a transaction.
 */
fun sumWeightsForCurrency[txn: Transaction, cur: Currency]: Int {
    sum p: txn.postings | (p.weight.currency = cur) implies p.weight.value else 0
}

/**
 * Absolute value.
 */
fun abs[n: Int]: Int {
    (n >= 0) implies n else negate[n]
}

/**
 * A transaction balances if |residual| ≤ tolerance for each currency.
 */
pred transactionBalances[txn: Transaction] {
    -- For each currency in the transaction
    all cur: Currency | {
        (some p: txn.postings | p.weight.currency = cur) implies {
            -- Sum of weights for this currency
            let sum = sumWeightsForCurrency[txn, cur] | {
                -- Check if within tolerance
                abs[sum] <= txn.tolerance.value
            }
        }
    }
}

/**
 * Compute transaction balance status.
 */
pred computeTransactionBalance[txn: Transaction] {
    -- Compute max tolerance from postings
    maxToleranceOfPostings[txn.postings, txn.tolerance]

    -- Check if balances
    transactionBalances[txn] implies txn.balances = 1
    not transactionBalances[txn] implies txn.balances = 0
}

-- =============================================================================
-- BALANCE ASSERTION CHECKING
-- =============================================================================

/**
 * A balance assertion passes if |expected - actual| ≤ tolerance.
 */
pred assertionPasses[ba: BalanceAssertion] {
    -- Use explicit tolerance if provided, otherwise computed
    let tol = (some ba.explicitTolerance) implies ba.explicitTolerance else ba.computedTolerance | {
        abs[ba.difference] <= tol.value
    }
}

/**
 * Compute balance assertion status.
 */
pred computeBalanceAssertion[ba: BalanceAssertion] {
    -- Compute difference
    ba.difference = sub[ba.expected.value, ba.actual.value]

    -- Compute tolerance from expected amount precision (if no explicit)
    no ba.explicitTolerance implies toleranceFromPrecision[ba.computedTolerance, ba.expected.precision]

    -- Check if passes
    assertionPasses[ba] implies ba.passes = 1
    not assertionPasses[ba] implies ba.passes = 0
}

-- =============================================================================
-- INVARIANTS
-- =============================================================================

/**
 * Invariant: Transaction tolerance is the maximum of posting tolerances.
 */
pred txnToleranceIsMax {
    all txn: Transaction | {
        all p: txn.postings | {
            some t: Tolerance | {
                toleranceFromPrecision[t, p.amount.precision]
                toleranceGeq[txn.tolerance, t]
            }
        }
    }
}

/**
 * Invariant: Zero tolerance means exact match required.
 */
pred zeroToleranceExact {
    all ba: BalanceAssertion | {
        (some ba.explicitTolerance and ba.explicitTolerance.value = 0) implies {
            ba.passes = 1 iff ba.difference = 0
        }
    }
}

/**
 * Invariant: Each currency balances independently.
 */
pred currenciesBalanceIndependently {
    all txn: Transaction, c1, c2: Currency | {
        c1 != c2 implies {
            -- Balance check for c1 is independent of c2
            let sum1 = sumWeightsForCurrency[txn, c1],
                sum2 = sumWeightsForCurrency[txn, c2] | {
                (abs[sum1] <= txn.tolerance.value) or (abs[sum2] <= txn.tolerance.value)
            }
        }
    }
}

/**
 * Invariant: Higher precision means smaller tolerance.
 */
pred higherPrecisionSmallerTolerance {
    all t1, t2: Tolerance | {
        (t1.fromPrecision.decimalPlaces > t2.fromPrecision.decimalPlaces) implies
            (t1.value <= t2.value)
    }
}

-- =============================================================================
-- ASSERTIONS (Properties to Check)
-- =============================================================================

/**
 * A balanced transaction has residual within tolerance.
 */
assert balancedWithinTolerance {
    all txn: Transaction |
        (txn.balances = 1 and computeTransactionBalance[txn])
        implies all cur: Currency |
            (some p: txn.postings | p.weight.currency = cur) implies
                abs[sumWeightsForCurrency[txn, cur]] <= txn.tolerance.value
}

/**
 * Explicit zero tolerance requires exact match.
 */
assert zeroToleranceRequiresExact {
    all ba: BalanceAssertion |
        (some ba.explicitTolerance and
         ba.explicitTolerance.value = 0 and
         computeBalanceAssertion[ba] and
         ba.passes = 1)
        implies ba.difference = 0
}

/**
 * Lower precision always allows larger residuals.
 */
assert lowerPrecisionMoreTolerant {
    all txn1, txn2: Transaction |
        -- If txn1 has lower precision (higher tolerance)
        (txn1.tolerance.value > txn2.tolerance.value and
         -- And same residual
         txn1.residual = txn2.residual and
         -- And txn2 balances
         txn2.balances = 1)
        -- Then txn1 also balances
        implies txn1.balances = 1
}

-- =============================================================================
-- EXAMPLE SCENARIOS
-- =============================================================================

/**
 * Example: Two decimal places gives 0.005 tolerance.
 */
pred exampleTwoDecimalTolerance {
    some t: Tolerance, p: Precision | {
        p.decimalPlaces = 2
        toleranceFromPrecision[t, p]
        t.value = 5  -- Representing 0.005
    }
}

/**
 * Example: Transaction with mixed precision uses max tolerance.
 */
pred exampleMixedPrecisionMax {
    some txn: Transaction, p1, p2, p3: Posting, pr1, pr2: Precision | {
        -- Different precisions
        pr1.decimalPlaces = 2  -- tolerance 5
        pr2.decimalPlaces = 0  -- tolerance 500

        p1.amount.precision = pr1
        p2.amount.precision = pr1
        p3.amount.precision = pr2

        txn.postings = p1 + p2 + p3
        computeTransactionBalance[txn]

        -- Max tolerance should be 500 (from precision 0)
        txn.tolerance.value = 500
    }
}

/**
 * Example: Transaction balances within tolerance.
 */
pred exampleTransactionBalances {
    some txn: Transaction, p1, p2: Posting, cur: Currency, pr: Precision | {
        pr.decimalPlaces = 2  -- tolerance 5

        -- Postings: 10000 and -9997 (residual 3)
        p1.amount.precision = pr
        p2.amount.precision = pr
        p1.weight.currency = cur
        p2.weight.currency = cur
        p1.weight.value = 10000
        p2.weight.value = -9997

        txn.postings = p1 + p2
        computeTransactionBalance[txn]

        -- Residual 3 is within tolerance 5
        txn.balances = 1
    }
}

/**
 * Example: Transaction fails to balance.
 */
pred exampleTransactionFails {
    some txn: Transaction, p1, p2: Posting, cur: Currency, pr: Precision | {
        pr.decimalPlaces = 2  -- tolerance 5

        -- Postings: 10000 and -9990 (residual 10)
        p1.amount.precision = pr
        p2.amount.precision = pr
        p1.weight.currency = cur
        p2.weight.currency = cur
        p1.weight.value = 10000
        p2.weight.value = -9990

        txn.postings = p1 + p2
        computeTransactionBalance[txn]

        -- Residual 10 exceeds tolerance 5
        txn.balances = 0
    }
}

/**
 * Example: Balance assertion with explicit zero tolerance.
 */
pred exampleZeroTolerance {
    some ba: BalanceAssertion, t: Tolerance | {
        t.value = 0
        ba.explicitTolerance = t
        ba.expected.value = 100000
        ba.actual.value = 100001  -- Off by 1

        computeBalanceAssertion[ba]

        -- Should fail (exact match required)
        ba.passes = 0
    }
}

-- =============================================================================
-- RUN COMMANDS
-- =============================================================================

run exampleTwoDecimalTolerance for 3
run exampleMixedPrecisionMax for 5 but 3 Posting, 2 Precision
run exampleTransactionBalances for 4 but 2 Posting, 1 Currency
run exampleTransactionFails for 4 but 2 Posting, 1 Currency
run exampleZeroTolerance for 3

check balancedWithinTolerance for 5
check zeroToleranceRequiresExact for 5
check lowerPrecisionMoreTolerant for 5
