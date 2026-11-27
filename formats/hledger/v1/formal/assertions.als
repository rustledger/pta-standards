/*
 * hledger Balance Assertions Formal Model
 *
 * Specifies hledger's balance assertion semantics:
 * - Single-commodity assertions: =AMOUNT
 * - Multi-commodity assertions: ==AMOUNT
 * - Subaccount-inclusive assertions: =* or ==*
 */

module formats/hledger/v1/formal/assertions

open util/integer

sig Currency {}
sig Amount {
  value: Int,
  currency: Currency
}

-- Account names are atoms: Alloy has no String atoms unless they are
-- written as literals, so a String field would leave Account uninhabitable.
sig Name {}

sig Account {
  name: Name,
  parent: lone Account
}

-- The account tree has no cycles
fact AccountTree {
  no a: Account | a in a.^parent
}

sig Posting {
  account: Account,
  amount: Amount,
  assertion: lone BalanceAssertion
}

sig Transaction {
  date: Int,
  postings: set Posting
}

-- Balance assertion types
abstract sig BalanceAssertion {
  expectedAmount: Amount
}

-- = AMOUNT: assert single commodity balance
sig SingleCommodityAssertion extends BalanceAssertion {}

-- == AMOUNT: assert total balance (all commodities must match)
sig TotalAssertion extends BalanceAssertion {}

-- =* AMOUNT: assert including subaccounts
sig SubaccountInclusiveAssertion extends BalanceAssertion {}

-- ==* AMOUNT: total including subaccounts
sig TotalSubaccountAssertion extends BalanceAssertion {}

-- Compute account balance at a point
fun accountBalance[acct: Account, cur: Currency, txns: set Transaction, asOf: Int]: Int {
  sum t: txns, p: t.postings |
    (t.date <= asOf and p.account = acct and p.amount.currency = cur)
    implies p.amount.value else 0
}

-- Compute balance including subaccounts
fun accountBalanceWithSubs[acct: Account, cur: Currency, txns: set Transaction, asOf: Int]: Int {
  sum t: txns, p: t.postings |
    (t.date <= asOf and
     (p.account = acct or acct in p.account.^parent) and
     p.amount.currency = cur)
    implies p.amount.value else 0
}

-- Check if a single-commodity assertion passes
pred SingleAssertionPasses[p: Posting, txns: set Transaction, txnDate: Int] {
  p.assertion in SingleCommodityAssertion implies
    let expected = p.assertion.expectedAmount |
    accountBalance[p.account, expected.currency, txns, txnDate] = expected.value
}

-- Check if a subaccount-inclusive assertion passes
pred SubaccountAssertionPasses[p: Posting, txns: set Transaction, txnDate: Int] {
  p.assertion in SubaccountInclusiveAssertion implies
    let expected = p.assertion.expectedAmount |
    accountBalanceWithSubs[p.account, expected.currency, txns, txnDate] = expected.value
}

-- Check if a total assertion passes (all commodities): the asserted
-- commodity has the expected balance and every other commodity is zero
pred TotalAssertionPasses[p: Posting, txns: set Transaction, txnDate: Int] {
  p.assertion in TotalAssertion implies
    let expected = p.assertion.expectedAmount |
    accountBalance[p.account, expected.currency, txns, txnDate] = expected.value and
    (all c: Currency - expected.currency | accountBalance[p.account, c, txns, txnDate] = 0)
}

-- Check if a total subaccount-inclusive assertion (==*) passes
pred TotalSubaccountAssertionPasses[p: Posting, txns: set Transaction, txnDate: Int] {
  p.assertion in TotalSubaccountAssertion implies
    let expected = p.assertion.expectedAmount |
    accountBalanceWithSubs[p.account, expected.currency, txns, txnDate] = expected.value and
    (all c: Currency - expected.currency | accountBalanceWithSubs[p.account, c, txns, txnDate] = 0)
}

-- All assertions in a transaction must pass
pred TransactionAssertionsPass[t: Transaction, allTxns: set Transaction] {
  all p: t.postings |
    some p.assertion implies (
      SingleAssertionPasses[p, allTxns, t.date] and
      SubaccountAssertionPasses[p, allTxns, t.date] and
      TotalAssertionPasses[p, allTxns, t.date] and
      TotalSubaccountAssertionPasses[p, allTxns, t.date]
    )
}

-- Assertions are checked after the posting is applied
pred AssertionTimingCorrect[t: Transaction, allTxns: set Transaction] {
  TransactionAssertionsPass[t, allTxns + t]  -- Include current transaction
}

-- Example: valid balance assertion
-- (amounts scaled from 100/-30/70 to 10/-3/7 to fit Alloy's small integers)
pred ValidAssertionExample {
  some t1, t2: Transaction, p1, p2, p3: Posting |
  some acct: Account, c: Currency, a: SingleCommodityAssertion |
    t1.date = 1 and t2.date = 2 and
    -- First transaction: deposit 10
    p1.account = acct and p1.amount.value = 10 and p1.amount.currency = c and no p1.assertion and
    t1.postings = p1 and
    -- Second transaction: withdraw 3 with assertion that balance is 7
    p2.account = acct and p2.amount.value = -3 and p2.amount.currency = c and
    a.expectedAmount.value = 7 and a.expectedAmount.currency = c and
    p2.assertion = a and
    t2.postings = p2 and
    AssertionTimingCorrect[t2, t1]
}

-- Posting amounts small enough that no balance in the check scopes below can
-- overflow 5-bit integers (2 transactions x 3 postings, |value| <= 2, so
-- |balance| <= 12). Without it an overflowing sum makes the analyzer's
-- no-overflow mode report spurious results.
pred NoOverflow {
  all a: Amount | a.value >= -2 and a.value <= 2
}

-- Assertions

-- Assertions check the balance AFTER the posting (spec: "Assertion Timing"):
-- an assertion that states the balance as it was *before* a non-zero
-- posting to that account fails.
assert AssertionFailsOnWrongBalance {
  all t: Transaction, p: t.postings, allTxns: set Transaction |
    (NoOverflow and
     p.assertion in SingleCommodityAssertion and
     t not in allTxns and (all u: allTxns | u.date < t.date) and
     p.amount.currency = p.assertion.expectedAmount.currency and
     p.amount.value != 0 and
     -- p is t's only posting to that account
     (all q: t.postings - p | q.account != p.account) and
     p.assertion.expectedAmount.value =
       accountBalance[p.account, p.amount.currency, allTxns, t.date]) implies
    not AssertionTimingCorrect[t, allTxns]
}

-- An account with no subaccounts: =* means the same as =
assert SubaccountInclusiveMatchesExactOnLeaf {
  all acct: Account, cur: Currency, txns: set Transaction, d: Int |
    (NoOverflow and no parent.acct) implies
    accountBalanceWithSubs[acct, cur, txns, d] = accountBalance[acct, cur, txns, d]
}

check AssertionFailsOnWrongBalance for 3 but 5 Int, 2 Transaction
check SubaccountInclusiveMatchesExactOnLeaf for 3 but 5 Int, 2 Transaction

run ValidAssertionExample for 4 but 5 Int
