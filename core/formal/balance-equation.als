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

sig Account {
  name: String,
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

-- Verify the accounting equation after all transactions
assert AccountingEquationHolds {
  all accounts: set Account |
    BalanceEquation[accounts]
}

-- Every transaction maintains balance
assert AllTransactionsBalanced {
  all t: Transaction |
    TransactionBalanced[t]
}

-- Check assertions
check AccountingEquationHolds for 5
check AllTransactionsBalanced for 5

-- Example: valid simple transaction
pred ValidSimpleTransaction {
  some disj a1, a2: Account, p1, p2: Posting, t: Transaction, c: Currency |
    a1.type = Assets and
    a2.type = Expenses and
    p1.account = a1 and p1.amount.value = -100 and p1.amount.currency = c and
    p2.account = a2 and p2.amount.value = 100 and p2.amount.currency = c and
    t.postings = p1 + p2 and
    TransactionBalanced[t]
}

run ValidSimpleTransaction for 3
