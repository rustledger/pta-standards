/*
 * Ledger Virtual Postings Formal Model
 *
 * Specifies Ledger's virtual posting semantics:
 * - (Account) - virtual posting, excluded from balance
 * - [Account] - balanced virtual posting
 */

module formats/ledger/v1/formal/virtual

open util/integer

sig Currency {}
sig Amount {
  value: Int,
  currency: Currency
}

sig Account {}

-- Posting types
abstract sig PostingType {}
one sig Real extends PostingType {}           -- Normal posting
one sig Virtual extends PostingType {}        -- (Account) - unbalanced virtual
one sig BalancedVirtual extends PostingType {}  -- [Account] - balanced virtual

sig Posting {
  account: Account,
  amount: Amount,
  postingType: PostingType
}

sig Transaction {
  date: Int,
  postings: set Posting
}

-- Real postings must balance
pred RealPostingsBalance[t: Transaction] {
  all c: Currency |
    let realPostings = { p: t.postings | p.postingType = Real and p.amount.currency = c } |
    (sum p: realPostings | p.amount.value) = 0
}

-- Balanced virtual postings must balance among themselves
pred BalancedVirtualBalance[t: Transaction] {
  all c: Currency |
    let bvPostings = { p: t.postings | p.postingType = BalancedVirtual and p.amount.currency = c } |
    (sum p: bvPostings | p.amount.value) = 0
}

-- Unbalanced virtual postings don't need to balance
-- (They're typically used for tracking/budgeting)
pred VirtualPostingsAllowed[t: Transaction] {
  -- Virtual postings can be any amount: ValidTransaction places no
  -- constraint on them (see UnbalancedVirtualUnconstrained below)
  some t.postings or no t.postings
}

-- Transaction is valid if real and balanced-virtual portions balance
pred ValidTransaction[t: Transaction] {
  RealPostingsBalance[t]
  BalancedVirtualBalance[t]
}

-- Account balance computation
-- Virtual postings are typically excluded from balance reports
fun realBalance[acct: Account, cur: Currency, txns: set Transaction]: Int {
  sum t: txns, p: t.postings |
    (p.account = acct and p.amount.currency = cur and p.postingType = Real)
    implies p.amount.value else 0
}

-- Real plus balanced-virtual postings (the [] view); excludes () postings
fun balancedBalance[acct: Account, cur: Currency, txns: set Transaction]: Int {
  sum t: txns, p: t.postings |
    (p.account = acct and p.amount.currency = cur and p.postingType in Real + BalancedVirtual)
    implies p.amount.value else 0
}

-- Include virtual for full picture
fun totalBalance[acct: Account, cur: Currency, txns: set Transaction]: Int {
  sum t: txns, p: t.postings |
    (p.account = acct and p.amount.currency = cur)
    implies p.amount.value else 0
}

-- Budget envelope pattern using balanced virtual
pred BudgetEnvelopePattern[t: Transaction] {
  some disj real1, real2, bv1, bv2: Posting |
  some disj checking, expense, budgetFrom, budgetTo: Account |
  some c: Currency |
    -- Real: money flows from checking to expense
    -- (amounts scaled from $50 to 5 to fit Alloy's small integers)
    real1.postingType = Real and real1.account = checking and real1.amount.value = -5 and
    real2.postingType = Real and real2.account = expense and real2.amount.value = 5 and
    -- Balanced virtual: budget tracking
    bv1.postingType = BalancedVirtual and bv1.account = budgetFrom and bv1.amount.value = -5 and
    bv2.postingType = BalancedVirtual and bv2.account = budgetTo and bv2.amount.value = 5 and
    (real1 + real2 + bv1 + bv2).amount.currency = c and
    t.postings = real1 + real2 + bv1 + bv2 and
    ValidTransaction[t]
}

-- Savings goal tracking with unbalanced virtual
pred SavingsGoalPattern[t: Transaction] {
  some disj real1, real2, virtual: Posting |
  some disj checking, savings, goalTracker: Account |
  some c: Currency |
    -- Real: transfer to savings
    -- (amounts scaled from $100 to 10 to fit Alloy's small integers)
    real1.postingType = Real and real1.account = checking and real1.amount.value = -10 and
    real2.postingType = Real and real2.account = savings and real2.amount.value = 10 and
    -- Virtual: track progress toward goal (doesn't balance)
    virtual.postingType = Virtual and virtual.account = goalTracker and virtual.amount.value = 10 and
    (real1 + real2 + virtual).amount.currency = c and
    t.postings = real1 + real2 + virtual and
    ValidTransaction[t]
}

-- Sum over every account of the balance restricted to `types`: since each
-- posting has exactly one account, this is the sum of all such postings
-- (written posting-wise because a nested per-account sum is far slower to
-- solve). With types = Real it is sum[realBalance], with Real+BalancedVirtual
-- it is sum[balancedBalance].
fun ledgerTotal[types: set PostingType, cur: Currency, txns: set Transaction]: Int {
  sum t: txns, p: t.postings |
    (p.postingType in types and p.amount.currency = cur) implies p.amount.value else 0
}

-- Amounts small enough that no ledger total in the check scopes below
-- (3 transactions x 3 postings, |value| <= 2, so |total| <= 18) can overflow
-- 6-bit integers. Without it, an overflowing sum makes the analyzer's
-- no-overflow mode report a spurious counterexample.
pred NoOverflowAmounts {
  all a: Amount | a.value >= -2 and a.value <= 2
}

-- Assertions
--
-- Across a ledger of valid transactions, the real postings sum to zero in
-- every currency, so real balances obey the accounting equation no matter
-- what () virtual postings say.
assert RealAlwaysBalances {
  all txns: set Transaction, cur: Currency |
    (NoOverflowAmounts and all t: txns | ValidTransaction[t]) implies
    ledgerTotal[Real, cur, txns] = 0
}

-- The [] view (real + balanced virtual, excluding ()) also sums to zero:
-- balanced virtual postings never unbalance the ledger.
assert BalancedVirtualAlwaysBalances {
  all txns: set Transaction, cur: Currency |
    (NoOverflowAmounts and all t: txns | ValidTransaction[t]) implies
    ledgerTotal[Real + BalancedVirtual, cur, txns] = 0
}

-- Unbalanced () postings are unconstrained: a valid transaction may carry a
-- non-zero virtual total (an instance is the point).
run UnbalancedVirtualUnconstrained {
  some t: Transaction, c: Currency |
    ValidTransaction[t] and
    (sum p: { p: t.postings | p.postingType = Virtual and p.amount.currency = c } | p.amount.value) != 0
} for 4 but 5 Int

check RealAlwaysBalances for 3 but 6 Int
check BalancedVirtualAlwaysBalances for 3 but 6 Int

run BudgetEnvelopePattern for 5 but 5 Int
run SavingsGoalPattern for 5 but 5 Int
