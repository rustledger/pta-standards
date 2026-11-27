/*
 * Balance Equation - Fundamental Accounting Identity
 *
 * This module formally specifies the core accounting equation:
 * Assets = Liabilities + Equity
 *
 * In signed-balance form (as used in PTA):
 * Assets + Expenses + Equity + Liabilities + Income = 0
 */

module core/formal/balance_equation

open util/integer

-- Basic types
sig Currency {}

sig Amount {
  value: Int,
  currency: Currency
}

abstract sig AccountType {}
one sig Assets, Liabilities, Equity, Income, Expenses extends AccountType {}

-- Account names are opaque atoms. (A `String` field would leave Account
-- uninhabited: Alloy has no String atoms beyond the literals a model names.)
sig AccountName {}

sig Account {
  name: AccountName,
  type: AccountType,
  balance: Amount
}

sig Posting {
  account: Account,
  amount: Amount
}

sig Transaction {
  date: Int,
  postings: set Posting
}

-- Bounded magnitudes. Alloy integers are fixed-width two's complement, and
-- its overflow guard (-n) does not reliably reject an instance whose sum
-- wraps around inside a nested quantifier: two postings of -8 "sum" to 0 at
-- 4-bit width. Capping each posting at |2| with at most 3 postings keeps every
-- sum within the 4-bit range the checks below use, so no wrap-around can
-- masquerade as a balanced transaction or as a counterexample.
fact BoundedMagnitudes {
  all p: Posting | p.amount.value >= -2 and p.amount.value <= 2
}

-- The fundamental balance equation
-- Sum of all account balances must equal zero
pred BalanceEquation[accounts: set Account] {
  let total = (sum a: accounts | a.balance.value) |
    total = 0
}

-- A transaction must be balanced
-- Sum of all postings in a transaction equals zero
pred TransactionBalanced[t: Transaction] {
  all c: Currency |
    let postingsInCurrency = { p: t.postings | p.amount.currency = c } |
    (sum p: postingsInCurrency | p.amount.value) = 0
}

-- Debits equal credits (alternative view)
-- For accounts with positive normal balance (Assets, Expenses):
--   Increases are debits (positive)
-- For accounts with negative normal balance (Liabilities, Equity, Income):
--   Increases are credits (negative)
pred DebitsEqualCredits[postings: set Posting] {
  all c: Currency |
    let postingsInCurrency = { p: postings | p.amount.currency = c } |
    let debits = (sum p: postingsInCurrency | p.amount.value > 0 implies p.amount.value else 0) |
    let credits = (sum p: postingsInCurrency | p.amount.value < 0 implies negate[p.amount.value] else 0) |
    debits = credits
}

-- Account type determines normal balance sign
fun normalBalanceSign[t: AccountType]: Int {
  t in (Assets + Expenses) implies 1 else -1
}

-- A ledger: every posting belongs to exactly one transaction, every account
-- holds a single currency, and each account's balance is the sum of the
-- postings made to it.
pred LedgerDerived {
  all p: Posting | one postings.p
  all p: Posting | p.amount.currency = p.account.balance.currency
  all a: Account | a.balance.value = (sum p: account.a | p.amount.value)
}

-- A valid ledger: derived balances, and every transaction balanced.
pred ValidLedger {
  LedgerDerived
  all t: Transaction | TransactionBalanced[t]
}

-- Verify the accounting equation after all transactions: in a valid ledger
-- the balances of all accounts held in a currency sum to zero.
assert AccountingEquationHolds {
  ValidLedger implies
    all c: Currency | BalanceEquation[{ a: Account | a.balance.currency = c }]
}

-- Every transaction maintains balance, stated in its debit/credit form:
-- a transaction balances exactly when its debits equal its credits.
-- (That all transactions balance is the premise ValidLedger, not a theorem.)
assert AllTransactionsBalanced {
  all t: Transaction |
    TransactionBalanced[t] iff DebitsEqualCredits[t.postings]
}

-- Check assertions
check AccountingEquationHolds for 3
check AllTransactionsBalanced for 3

-- Example: valid simple transaction
pred ValidSimpleTransaction {
  some disj a1, a2: Account, p1, p2: Posting, t: Transaction, c: Currency |
    a1.type = Assets and
    a2.type = Expenses and
    p1.account = a1 and p1.amount.value = -2 and p1.amount.currency = c and
    p2.account = a2 and p2.amount.value = 2 and p2.amount.currency = c and
    t.postings = p1 + p2 and
    TransactionBalanced[t]
}

run ValidSimpleTransaction for 3

-- Non-vacuity: the premise of AccountingEquationHolds is satisfiable by a
-- ledger with postings in two accounts.
run ValidLedgerExample { ValidLedger and #Account > 1 and some Transaction.postings } for 3
