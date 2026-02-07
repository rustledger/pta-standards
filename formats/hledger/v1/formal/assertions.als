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

sig Account {
  name: String,
  parent: lone Account
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
     (p.account = acct or p.account.^parent = acct) and
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

-- Check if a total assertion passes (all commodities)
pred TotalAssertionPasses[p: Posting, txns: set Transaction, txnDate: Int] {
  p.assertion in TotalAssertion implies
    -- For simplicity, check single currency; full impl would check all
    let expected = p.assertion.expectedAmount |
    accountBalance[p.account, expected.currency, txns, txnDate] = expected.value
}

-- All assertions in a transaction must pass
pred TransactionAssertionsPass[t: Transaction, allTxns: set Transaction] {
  all p: t.postings |
    some p.assertion implies (
      SingleAssertionPasses[p, allTxns, t.date] and
      SubaccountAssertionPasses[p, allTxns, t.date] and
      TotalAssertionPasses[p, allTxns, t.date]
    )
}

-- Assertions are checked after the posting is applied
pred AssertionTimingCorrect[t: Transaction, allTxns: set Transaction] {
  TransactionAssertionsPass[t, allTxns + t]  -- Include current transaction
}

-- Example: valid balance assertion
pred ValidAssertionExample {
  some t1, t2: Transaction, p1, p2, p3: Posting |
  some acct: Account, c: Currency, a: SingleCommodityAssertion |
    t1.date = 1 and t2.date = 2 and
    -- First transaction: deposit 100
    p1.account = acct and p1.amount.value = 100 and p1.amount.currency = c and no p1.assertion and
    t1.postings = p1 and
    -- Second transaction: withdraw 30 with assertion that balance is 70
    p2.account = acct and p2.amount.value = -30 and p2.amount.currency = c and
    a.expectedAmount.value = 70 and a.expectedAmount.currency = c and
    p2.assertion = a and
    t2.postings = p2 and
    AssertionTimingCorrect[t2, t1]
}

-- Assertions
assert AssertionFailsOnWrongBalance {
  all t: Transaction, p: t.postings, allTxns: set Transaction |
    (some p.assertion and p.assertion in SingleCommodityAssertion) implies
    let actual = accountBalance[p.account, p.assertion.expectedAmount.currency, allTxns + t, t.date] |
    actual != p.assertion.expectedAmount.value implies
    not SingleAssertionPasses[p, allTxns + t, t.date]
}

check AssertionFailsOnWrongBalance for 4

run ValidAssertionExample for 4
