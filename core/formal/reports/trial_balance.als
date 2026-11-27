/*
 * Trial Balance Formal Model
 *
 * Specifies the invariants of a trial balance report.
 * The fundamental property: Total Debits = Total Credits
 */

module core/formal/reports/trial_balance

open core/formal/balance_equation
open util/integer

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

  -- Trial balance entries derived from transactions
  all entry: tb.accounts |
    entry.account.balance.value =
      (sum t: txns, p: t.postings |
        p.account = entry.account implies p.amount.value else 0)
}

-- Assertions
assert BalancedTransactionsGiveBalancedTrialBalance {
  all tb: TrialBalance, txns: set Transaction |
    (DerivedFromBalancedTransactions[tb, txns] and ValidTrialBalance[tb]) implies
    DebitsEqualCredits[tb]
}

assert TrialBalanceReflectsAccountingEquation {
  all tb: TrialBalance |
    ValidTrialBalance[tb] implies DebitsEqualCredits[tb]
}

check BalancedTransactionsGiveBalancedTrialBalance for 4
check TrialBalanceReflectsAccountingEquation for 5

-- Example: simple trial balance
pred SimpleTrialBalance {
  some tb: TrialBalance |
  some disj e1, e2, e3: TrialBalanceEntry |
  some disj cash, expense, income: Account |
  some c: Currency |
    -- Cash (asset): debit balance of 1000
    cash.type = Assets and cash.balance.value = 1000 and cash.balance.currency = c and
    e1.account = cash and e1.debit = 1000 and e1.credit = 0 and

    -- Expense: debit balance of 500
    expense.type = Expenses and expense.balance.value = 500 and expense.balance.currency = c and
    e2.account = expense and e2.debit = 500 and e2.credit = 0 and

    -- Income: credit balance of 1500
    income.type = Income and income.balance.value = -1500 and income.balance.currency = c and
    e3.account = income and e3.debit = 0 and e3.credit = 1500 and

    tb.accounts = e1 + e2 + e3 and
    ValidTrialBalance[tb] and
    DebitsEqualCredits[tb]
}

run SimpleTrialBalance for 5
