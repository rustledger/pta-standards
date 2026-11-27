/*
 * Balance Sheet Formal Model
 *
 * Specifies the invariants and properties of a balance sheet report.
 * The fundamental property: Assets = Liabilities + Equity
 */

module core/formal/reports/balance_sheet

open core/formal/balance_equation
open util/integer

-- Balance sheet as a snapshot at a point in time
sig BalanceSheet {
  asOf: Int,  -- Date as ordinal

  -- Account categories
  assets: set Account,
  liabilities: set Account,
  equity: set Account,

  -- Computed totals
  totalAssets: Int,
  totalLiabilities: Int,
  totalEquity: Int
}

-- Account type constraints
pred ValidBalanceSheet[bs: BalanceSheet] {
  -- Assets must be Asset-type accounts
  all a: bs.assets | a.type = Assets

  -- Liabilities must be Liability-type accounts
  all l: bs.liabilities | l.type = Liabilities

  -- Equity must be Equity-type accounts
  all e: bs.equity | e.type = Equity

  -- No overlap between categories
  no bs.assets & bs.liabilities
  no bs.assets & bs.equity
  no bs.liabilities & bs.equity

  -- Totals are sums of balances
  bs.totalAssets = (sum a: bs.assets | a.balance.value)
  bs.totalLiabilities = (sum l: bs.liabilities | l.balance.value)
  bs.totalEquity = (sum e: bs.equity | e.balance.value)
}

-- The fundamental accounting equation
-- Assets = Liabilities + Equity
-- In signed form: Assets + Liabilities + Equity = 0
-- (because liabilities and equity have negative normal balances)
pred AccountingEquation[bs: BalanceSheet] {
  add[add[bs.totalAssets, bs.totalLiabilities], bs.totalEquity] = 0
}

-- Retained earnings from income statement
-- This connects balance sheet to income statement
pred RetainedEarningsIncluded[bs: BalanceSheet, incomeAccounts: set Account, expenseAccounts: set Account] {
  -- Net income = -(Income + Expenses)
  let netIncome = negate[add[(sum i: incomeAccounts | i.balance.value),
                             (sum e: expenseAccounts | e.balance.value)]] |
  -- This should be reflected in equity
  some retainedEarnings: bs.equity |
    retainedEarnings.balance.value = netIncome
}

-- Current vs non-current classification
abstract sig AssetClass {}
one sig CurrentAsset, FixedAsset extends AssetClass {}

abstract sig LiabilityClass {}
one sig CurrentLiability, LongTermLiability extends LiabilityClass {}

sig ClassifiedAccount extends Account {
  assetClass: lone AssetClass,
  liabilityClass: lone LiabilityClass
}

-- Working capital calculation
fun workingCapital[bs: BalanceSheet]: Int {
  let currentAssets = (sum a: bs.assets |
    a in ClassifiedAccount and a.assetClass = CurrentAsset implies a.balance.value else 0) |
  let currentLiabilities = (sum l: bs.liabilities |
    l in ClassifiedAccount and l.liabilityClass = CurrentLiability implies l.balance.value else 0) |
  add[currentAssets, currentLiabilities]  -- liabilities are negative
}

-- Bounded magnitudes (see balance_equation's BoundedMagnitudes): the checks
-- assume account balances of at most |2| so that, at scope 3, no sum of
-- balances can wrap around Alloy's 4-bit integers.
pred BoundedBalances {
  all a: Account | a.balance.value >= -2 and a.balance.value <= 2
}

-- The balance sheet is drawn from a whole single-currency ledger after the
-- books are closed: it lists every Asset, Liability and Equity account,
-- Income and Expenses have been closed into Equity (shown as "Retained
-- Earnings" in reports/model/balance-sheet.md), and the ledger satisfies the
-- balance equation of core/formal/balance_equation.
pred ClosedLedger[bs: BalanceSheet] {
  lone Account.balance.currency
  bs.assets = type.Assets
  bs.liabilities = type.Liabilities
  bs.equity = type.Equity
  all a: type.(Income + Expenses) | a.balance.value = 0
  BalanceEquation[Account]
}

-- Assertions
assert BalanceSheetBalances {
  all bs: BalanceSheet |
    (BoundedBalances and ValidBalanceSheet[bs] and ClosedLedger[bs]) implies
    AccountingEquation[bs]
}

-- The sign of a category total is NOT an invariant. "Normal balance"
-- (Assets debit/positive, Liabilities credit/negative) is a presentation
-- convention (see core/model/account.md): an overdrawn checking account
-- leaves Assets negative and an over-paid credit card leaves Liabilities
-- positive, and both are valid ledgers (beancount, hledger, ledger and
-- GnuCash all accept them). The runs below pin that: if a later change made
-- either state unrepresentable, they would stop finding an instance.

check BalanceSheetBalances for 3

-- An overdrawn asset account is a valid, balanced, closed ledger.
run OverdrawnAssetIsValid {
  some bs: BalanceSheet |
    BoundedBalances and ValidBalanceSheet[bs] and ClosedLedger[bs] and
    bs.totalAssets < 0
} for 3

-- An over-paid liability is a valid, balanced, closed ledger.
run OverpaidLiabilityIsValid {
  some bs: BalanceSheet |
    BoundedBalances and ValidBalanceSheet[bs] and ClosedLedger[bs] and
    bs.totalLiabilities > 0
} for 3

-- Example: simple balanced balance sheet
pred SimpleBalanceSheet {
  some bs: BalanceSheet |
  some disj cash, property: Account |
  some disj loan, owners: Account |
  some c: Currency |
    -- (amounts in units of 10000, to fit Alloy's integers)
    cash.type = Assets and cash.balance.value = 1 and cash.balance.currency = c and
    property.type = Assets and property.balance.value = 10 and property.balance.currency = c and
    loan.type = Liabilities and loan.balance.value = -6 and loan.balance.currency = c and
    owners.type = Equity and owners.balance.value = -5 and owners.balance.currency = c and
    bs.assets = cash + property and
    bs.liabilities = loan and
    bs.equity = owners and
    ValidBalanceSheet[bs] and
    AccountingEquation[bs]
}

run SimpleBalanceSheet for 5 but 6 Int

-- Non-vacuity: the premise of BalanceSheetBalances holds for a closed ledger
-- with an asset, a liability and an equity account.
run ClosedLedgerExample {
  some bs: BalanceSheet |
    BoundedBalances and ValidBalanceSheet[bs] and ClosedLedger[bs] and
    some bs.assets and some bs.liabilities and some bs.equity
} for 3
