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
  -- Virtual postings can be any amount
  true
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
    (p.account = acct and p.amount.currency = c and p.postingType = Real)
    implies p.amount.value else 0
}

-- Include virtual for full picture
fun totalBalance[acct: Account, cur: Currency, txns: set Transaction]: Int {
  sum t: txns, p: t.postings |
    (p.account = acct and p.amount.currency = c)
    implies p.amount.value else 0
}

-- Budget envelope pattern using balanced virtual
pred BudgetEnvelopePattern[t: Transaction] {
  some disj real1, real2, bv1, bv2: Posting |
  some disj checking, expense, budgetFrom, budgetTo: Account |
  some c: Currency |
    -- Real: money flows from checking to expense
    real1.postingType = Real and real1.account = checking and real1.amount.value = -50 and
    real2.postingType = Real and real2.account = expense and real2.amount.value = 50 and
    -- Balanced virtual: budget tracking
    bv1.postingType = BalancedVirtual and bv1.account = budgetFrom and bv1.amount.value = -50 and
    bv2.postingType = BalancedVirtual and bv2.account = budgetTo and bv2.amount.value = 50 and
    t.postings = real1 + real2 + bv1 + bv2 and
    ValidTransaction[t]
}

-- Savings goal tracking with unbalanced virtual
pred SavingsGoalPattern[t: Transaction] {
  some disj real1, real2, virtual: Posting |
  some disj checking, savings, goalTracker: Account |
  some c: Currency |
    -- Real: transfer to savings
    real1.postingType = Real and real1.account = checking and real1.amount.value = -100 and
    real2.postingType = Real and real2.account = savings and real2.amount.value = 100 and
    -- Virtual: track progress toward goal (doesn't balance)
    virtual.postingType = Virtual and virtual.account = goalTracker and virtual.amount.value = 100 and
    t.postings = real1 + real2 + virtual and
    ValidTransaction[t]
}

-- Assertions
assert RealAlwaysBalances {
  all t: Transaction |
    ValidTransaction[t] implies RealPostingsBalance[t]
}

assert BalancedVirtualAlwaysBalances {
  all t: Transaction |
    ValidTransaction[t] implies BalancedVirtualBalance[t]
}

check RealAlwaysBalances for 5
check BalancedVirtualAlwaysBalances for 5

run BudgetEnvelopePattern for 5
run SavingsGoalPattern for 5
