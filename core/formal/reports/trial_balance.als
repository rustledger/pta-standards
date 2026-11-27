/*
 * Trial Balance Formal Model
 *
 * Specifies the invariants of a trial balance report.
 * The fundamental property: Total Debits = Total Credits
 */

module core/formal/reports/trial_balance

open core/formal/balance_equation
open util/integer

-- Bounded magnitudes (see balance_equation's BoundedMagnitudes): the checks
-- below assume account balances of at most |2| so that, at scope 3, no sum
-- of balances, debits or credits can wrap around Alloy's 4-bit integers.
pred BoundedBalances {
  all a: Account | a.balance.value >= -2 and a.balance.value <= 2
}

-- Trial balance lists all accounts with debit/credit columns
sig TrialBalance {
  asOf: Int,  -- Date as ordinal
  accounts: set TrialBalanceEntry
}

sig TrialBalanceEntry {
  account: Account,
  debit: Int,   -- Positive or zero
  credit: Int   -- Positive or zero
}

-- Entry constraints
pred ValidEntry[entry: TrialBalanceEntry] {
  -- Debit and credit are non-negative
  entry.debit >= 0
  entry.credit >= 0

  -- Only one of debit or credit is non-zero
  entry.debit > 0 implies entry.credit = 0
  entry.credit > 0 implies entry.debit = 0

  -- Entry reflects account balance based on type
  let bal = entry.account.balance.value |
  entry.account.type in (Assets + Expenses) implies (
    -- Debit normal balance
    bal >= 0 implies (entry.debit = bal and entry.credit = 0)
    else (entry.debit = 0 and entry.credit = negate[bal])
  ) else (
    -- Credit normal balance
    bal <= 0 implies (entry.credit = negate[bal] and entry.debit = 0)
    else (entry.debit = bal and entry.credit = 0)
  )
}

-- Trial balance is valid
pred ValidTrialBalance[tb: TrialBalance] {
  -- All entries are valid
  all entry: tb.accounts | ValidEntry[entry]

  -- Each account appears exactly once
  all disj e1, e2: tb.accounts | e1.account != e2.account
}

-- The fundamental trial balance property: debits equal credits
pred DebitsEqualCredits[tb: TrialBalance] {
  (sum entry: tb.accounts | entry.debit) = (sum entry: tb.accounts | entry.credit)
}

-- Compute totals
fun totalDebits[tb: TrialBalance]: Int {
  sum entry: tb.accounts | entry.debit
}

fun totalCredits[tb: TrialBalance]: Int {
  sum entry: tb.accounts | entry.credit
}

-- Trial balance difference (should be zero if balanced)
fun trialBalanceDifference[tb: TrialBalance]: Int {
  sub[totalDebits[tb], totalCredits[tb]]
}

-- Trial balance derived from balanced transactions must balance
pred DerivedFromBalancedTransactions[tb: TrialBalance, txns: set Transaction] {
  -- All transactions are balanced
  all t: txns | TransactionBalanced[t]

  -- A trial balance is reported in a single currency
  lone txns.postings.amount.currency

  -- It lists every account the transactions post to
  txns.postings.account in tb.accounts.account

  -- Trial balance entries derived from transactions
  -- Each posting belongs to exactly one of the transactions
  all p: txns.postings | one (postings.p & txns)

  all entry: tb.accounts |
    entry.account.balance.value =
      (sum p: txns.postings & account.(entry.account) | p.amount.value)
}

-- Assertions
assert BalancedTransactionsGiveBalancedTrialBalance {
  all tb: TrialBalance, txns: set Transaction |
    (BoundedBalances and DerivedFromBalancedTransactions[tb, txns] and ValidTrialBalance[tb]) implies
    DebitsEqualCredits[tb]
}

-- A trial balance over accounts that satisfy the accounting equation
-- (balances sum to zero) has equal debit and credit columns.
assert TrialBalanceReflectsAccountingEquation {
  all tb: TrialBalance |
    (BoundedBalances and ValidTrialBalance[tb] and BalanceEquation[tb.accounts.account]) implies
    DebitsEqualCredits[tb]
}

check BalancedTransactionsGiveBalancedTrialBalance for 3
check TrialBalanceReflectsAccountingEquation for 3

-- Example: simple trial balance
pred SimpleTrialBalance {
  some tb: TrialBalance |
  some disj e1, e2, e3: TrialBalanceEntry |
  some disj cash, expense, income: Account |
  some c: Currency |
    -- (amounts in units of 500, to fit Alloy's 4-bit integers)
    -- Cash (asset): debit balance of 2 (1000)
    cash.type = Assets and cash.balance.value = 2 and cash.balance.currency = c and
    e1.account = cash and e1.debit = 2 and e1.credit = 0 and

    -- Expense: debit balance of 1 (500)
    expense.type = Expenses and expense.balance.value = 1 and expense.balance.currency = c and
    e2.account = expense and e2.debit = 1 and e2.credit = 0 and

    -- Income: credit balance of 3 (1500)
    income.type = Income and income.balance.value = -3 and income.balance.currency = c and
    e3.account = income and e3.debit = 0 and e3.credit = 3 and

    tb.accounts = e1 + e2 + e3 and
    ValidTrialBalance[tb] and
    DebitsEqualCredits[tb]
}

run SimpleTrialBalance for 5

-- Non-vacuity: the premise of BalancedTransactionsGiveBalancedTrialBalance
-- holds for a trial balance derived from a non-empty set of transactions.
run DerivedTrialBalanceExample {
  some tb: TrialBalance, txns: set Transaction |
    some txns.postings and BoundedBalances and DerivedFromBalancedTransactions[tb, txns] and ValidTrialBalance[tb]
} for 3
