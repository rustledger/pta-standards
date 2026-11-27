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

-- Assertions
assert BalanceSheetBalances {
  all bs: BalanceSheet |
    ValidBalanceSheet[bs] implies AccountingEquation[bs]
}

assert AssetsArePositive {
  all bs: BalanceSheet |
    ValidBalanceSheet[bs] implies bs.totalAssets >= 0
}

assert LiabilitiesAreNegative {
  all bs: BalanceSheet |
    ValidBalanceSheet[bs] implies bs.totalLiabilities <= 0
}

check BalanceSheetBalances for 5
check AssetsArePositive for 5
check LiabilitiesAreNegative for 5

-- Example: simple balanced balance sheet
pred SimpleBalanceSheet {
  some bs: BalanceSheet |
  some disj cash, property: Account |
  some disj loan, equity: Account |
  some c: Currency |
    cash.type = Assets and cash.balance.value = 10000 and cash.balance.currency = c and
    property.type = Assets and property.balance.value = 100000 and property.balance.currency = c and
    loan.type = Liabilities and loan.balance.value = -60000 and loan.balance.currency = c and
    equity.type = Equity and equity.balance.value = -50000 and equity.balance.currency = c and
    bs.assets = cash + property and
    bs.liabilities = loan and
    bs.equity = equity and
    ValidBalanceSheet[bs] and
    AccountingEquation[bs]
}

run SimpleBalanceSheet for 5
