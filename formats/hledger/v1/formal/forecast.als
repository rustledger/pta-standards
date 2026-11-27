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

-- Day ordinals follow the date ordering (distinct dates, distinct days)
fact DateOrdinals {
  all d: Date - last | d.ordinal < d.next.ordinal
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
abstract sig BasePeriod extends Period {}
one sig Daily, Weekly, Monthly, Quarterly, Yearly extends BasePeriod {}

-- Custom period with interval ("every 2 weeks"). The unit is a base period:
-- Alloy functions cannot recurse, and nested intervals ("every 2 (every 3
-- days)") are not hledger syntax.
sig EveryN extends Period {
  n: Int,
  unit: BasePeriod
}

-- Date range for forecast generation
sig DateRange {
  startDate: Date,
  endDate: Date
}

-- Base period interval in days (simplified)
fun baseDays[p: BasePeriod]: Int {
  p = Daily implies 1
  else p = Weekly implies 7
  else p = Monthly implies 30
  else p = Quarterly implies 90
  else 365
}

-- Period interval in days (simplified)
fun periodDays[p: Period]: Int {
  p in BasePeriod implies baseDays[p]
  else mul[p.n, baseDays[p.unit]]
}

-- Generate dates for a periodic transaction within a range: exactly the
-- dates in the range that lie on a period boundary
pred GenerateDates[pt: PeriodicTransaction, range: DateRange, dates: set Date] {
  all d: Date | d in dates iff (
    gte[d.ordinal, range.startDate.ordinal] and
    lte[d.ordinal, range.endDate.ordinal] and
    -- Date is on the period boundary
    rem[sub[d.ordinal, range.startDate.ordinal], periodDays[pt.period]] = 0)
}

-- Generate transactions from periodic template: one transaction per
-- generated date, each with the template's postings, and nothing else
pred GenerateForecast[pt: PeriodicTransaction, range: DateRange, txns: set Transaction] {
  some dates: set Date |
    GenerateDates[pt, range, dates] and
    txns.date = dates and
    (all d: dates | one t: txns | t.date = d) and
    (all t: txns | t.postings = pt.postings)
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
  -- Budget postings should balance
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

-- A range whose start does not come after its end
pred ValidRange[range: DateRange] {
  lte[range.startDate.ordinal, range.endDate.ordinal]
}

-- Forecast generates correct number of transactions
-- (for a reversed range, days < 0 and the bound is meaningless: nothing is
-- generated, but the bound goes negative, so the range must be valid)
assert ForecastCountCorrect {
  all pt: PeriodicTransaction, range: DateRange, txns: set Transaction |
    (ValidRange[range] and GenerateForecast[pt, range, txns]) implies
    let days = sub[range.endDate.ordinal, range.startDate.ordinal] |
    let interval = periodDays[pt.period] |
    interval > 0 implies #txns <= add[div[days, interval], 1]
}

-- 10-bit integers so the 365-day year fits (smaller widths would silently
-- drop quarterly and yearly periods, whose lengths would wrap negative)
check ForecastCountCorrect for 3 but 10 Int, 1 PeriodicTransaction, 1 DateRange, 1 EveryN, 1 ForecastMode

run MonthlyBudgetExample for 3 but 10 Int
