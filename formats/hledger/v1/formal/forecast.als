/*
 * hledger Forecast Transactions Formal Model
 *
 * Specifies hledger's periodic and forecast transaction generation:
 * - ~ (tilde) periodic transactions for budgeting
 * - Forecast flag for future transaction generation
 */

module formats/hledger/v1/formal/forecast

open util/integer
open util/ordering[Date]

sig Date {
  ordinal: Int
}

sig Currency {}
sig Amount {
  value: Int,
  currency: Currency
}

sig Account {}

sig Posting {
  account: Account,
  amount: Amount
}

-- Regular transaction
sig Transaction {
  date: Date,
  postings: set Posting
}

-- Periodic transaction template (~ syntax)
sig PeriodicTransaction {
  period: Period,
  postings: set Posting
}

-- Period specification
abstract sig Period {}
sig Daily extends Period {}
sig Weekly extends Period {}
sig Monthly extends Period {}
sig Quarterly extends Period {}
sig Yearly extends Period {}

-- Custom period with interval
sig EveryN extends Period {
  n: Int,
  unit: Period
}

-- Date range for forecast generation
sig DateRange {
  startDate: Date,
  endDate: Date
}

-- Period interval in days (simplified)
fun periodDays[p: Period]: Int {
  p = Daily implies 1
  else p = Weekly implies 7
  else p = Monthly implies 30
  else p = Quarterly implies 90
  else p = Yearly implies 365
  else p in EveryN implies mul[p.n, periodDays[p.unit]]
  else 0
}

-- Generate dates for a periodic transaction within a range
pred GenerateDates[pt: PeriodicTransaction, range: DateRange, dates: set Date] {
  all d: dates |
    gte[d.ordinal, range.startDate.ordinal] and
    lte[d.ordinal, range.endDate.ordinal] and
    -- Date is on the period boundary
    rem[sub[d.ordinal, range.startDate.ordinal], periodDays[pt.period]] = 0
}

-- Generate transactions from periodic template
pred GenerateForecast[pt: PeriodicTransaction, range: DateRange, txns: set Transaction] {
  some dates: set Date |
    GenerateDates[pt, range, dates] and
    -- Each date gets a transaction with the same postings
    all d: dates | one t: txns |
      t.date = d and
      t.postings = pt.postings
}

-- Forecast mode: only generate if --forecast flag is set
sig ForecastMode {
  enabled: Bool,
  range: DateRange
}

abstract sig Bool {}
one sig True, False extends Bool {}

-- Transactions are only generated when forecast is enabled
pred ForecastGeneration[pt: PeriodicTransaction, mode: ForecastMode, txns: set Transaction] {
  mode.enabled = True implies GenerateForecast[pt, mode.range, txns]
  mode.enabled = False implies no txns
}

-- Periodic transactions for budgeting
-- ~ monthly
--   expenses:food  $400
--   budget:food
pred BudgetAllocation[pt: PeriodicTransaction] {
  all p: pt.postings |
    -- Budget postings should balance
    true
  (sum p: pt.postings | p.amount.value) = 0
}

-- Example: monthly budget transaction
pred MonthlyBudgetExample {
  some pt: PeriodicTransaction |
  some disj p1, p2: Posting |
  some disj expense, budget: Account |
  some c: Currency |
    pt.period = Monthly and
    p1.account = expense and p1.amount.value = 400 and p1.amount.currency = c and
    p2.account = budget and p2.amount.value = -400 and p2.amount.currency = c and
    pt.postings = p1 + p2 and
    BudgetAllocation[pt]
}

-- Forecast generates correct number of transactions
assert ForecastCountCorrect {
  all pt: PeriodicTransaction, range: DateRange, txns: set Transaction |
    GenerateForecast[pt, range, txns] implies
    let days = sub[range.endDate.ordinal, range.startDate.ordinal] |
    let interval = periodDays[pt.period] |
    interval > 0 implies #txns <= add[div[days, interval], 1]
}

check ForecastCountCorrect for 5

run MonthlyBudgetExample for 3
