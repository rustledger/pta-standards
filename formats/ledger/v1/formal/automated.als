/*
 * Ledger Automated Transactions Formal Model
 *
 * Specifies Ledger's automated transaction feature:
 * - = PATTERN triggers on matching transactions
 * - Adds computed postings to matching transactions
 */

module formats/ledger/v1/formal/automated

open util/integer

sig Currency {}
sig Amount {
  value: Int,
  currency: Currency
}

-- Names (account names, payees, patterns). Alloy has no String atoms unless
-- they are written as literals, so names are modelled as atoms; the two
-- names the examples need are distinguished singletons.
abstract sig Name {}
one sig ExpensesName, EmployerPayrollName extends Name {}
sig OtherName extends Name {}

sig Account {
  name: Name
}

sig Posting {
  account: Account,
  amount: Amount
}

sig Transaction {
  date: Int,
  payee: Name,
  postings: set Posting
}

-- Pattern for matching transactions
abstract sig Pattern {}

-- Account pattern: matches postings to specific accounts
sig AccountPattern extends Pattern {
  accountMatch: Name  -- Account name pattern (supports regex)
}

-- Payee pattern: matches transaction payee
sig PayeePattern extends Pattern {
  payeeMatch: Name
}

-- Automated transaction rule
sig AutomatedTransaction {
  trigger: Pattern,
  generatedPostings: set AutoPosting
}

-- Auto-generated posting (can use expressions)
sig AutoPosting {
  account: Account,
  -- Amount can be fixed or computed from matched posting
  fixedAmount: lone Amount,
  -- If set, compute as ratioNum/ratioDen of the matched amount. This is
  -- Ledger's multiplier form (`-1`, `0.22` = 22/100, `(amount * 0.10)`); a
  -- percentage p is p/100. Kept as a fraction rather than a percentage so no
  -- literal 100 has to fit in the analyzer's small integers.
  ratioNum: lone Int,
  ratioDen: lone Int
}

fact WellFormedRatio {
  all ap: AutoPosting |
    (some ap.ratioNum iff some ap.ratioDen) and
    (some ap.ratioDen implies ap.ratioDen > 0)
}

-- Check if a posting matches a pattern
pred PostingMatchesPattern[p: Posting, pattern: Pattern] {
  pattern in AccountPattern implies
    -- Simplified: exact match (real impl uses regex)
    p.account.name = pattern.accountMatch
}

-- Check if a transaction matches a pattern
pred TransactionMatchesPattern[t: Transaction, pattern: Pattern] {
  pattern in PayeePattern implies
    t.payee = pattern.payeeMatch
  pattern in AccountPattern implies
    some p: t.postings | PostingMatchesPattern[p, pattern]
}

-- The value of an auto posting: fixed, a fraction of the matched amount,
-- or (by default) the matched amount itself
fun autoValue[ap: AutoPosting, matchedAmount: Amount]: Int {
  some ap.fixedAmount implies ap.fixedAmount.value
  else some ap.ratioNum implies div[mul[matchedAmount.value, ap.ratioNum], ap.ratioDen]
  else matchedAmount.value
}

-- The currency of an auto posting: a fixed amount carries its own,
-- otherwise the matched amount's currency is used
fun autoCurrency[ap: AutoPosting, matchedAmount: Amount]: Currency {
  some ap.fixedAmount implies ap.fixedAmount.currency else matchedAmount.currency
}

-- Apply automated transaction to a matching transaction. `matchedPosting` is
-- the posting that triggered the rule; every generated AutoPosting becomes
-- exactly one new Posting of the result.
pred ApplyAutomated[auto: AutomatedTransaction, original: Transaction, matchedPosting: Posting, result: Transaction] {
  TransactionMatchesPattern[original, auto.trigger]
  matchedPosting in original.postings
  PostingMatchesPattern[matchedPosting, auto.trigger]

  -- Result has original postings plus generated ones
  result.date = original.date
  result.payee = original.payee

  some gen: auto.generatedPostings lone -> one Posting |
    no original.postings & AutoPosting.gen and
    result.postings = original.postings + AutoPosting.gen and
    (all ap: auto.generatedPostings |
      ap.gen.account = ap.account and
      ap.gen.amount.value = autoValue[ap, matchedPosting.amount] and
      ap.gen.amount.currency = autoCurrency[ap, matchedPosting.amount])
}

-- A transaction balances when its postings sum to zero in every currency
pred TransactionBalanced[t: Transaction] {
  all c: Currency |
    (sum p: { p: t.postings | p.amount.currency = c } | p.amount.value) = 0
}

-- Generated postings should balance
pred AutomatedPostingsBalance[auto: AutomatedTransaction, matchedAmount: Amount] {
  all c: Currency |
    (sum ap: { ap: auto.generatedPostings | autoCurrency[ap, matchedAmount] = c } |
      autoValue[ap, matchedAmount]) = 0
}

-- Example: automatic sales tax
-- (amounts scaled from dollars to small integers to fit Alloy's bitwidth)
pred SalesTaxAutomation {
  some auto: AutomatedTransaction, disj ap1, ap2: AutoPosting |
  some pattern: AccountPattern |
  some disj taxExpense, taxPayable, food, checking: Account |
  some disj original, result: Transaction, disj p1, p2: Posting, c: Currency |
    -- Trigger on any Expenses:* posting
    pattern.accountMatch = ExpensesName and
    auto.trigger = pattern and

    -- Generate tax postings (10% of expense)
    ap1.account = taxExpense and ap1.ratioNum = 1 and ap1.ratioDen = 10 and no ap1.fixedAmount and
    ap2.account = taxPayable and ap2.ratioNum = -1 and ap2.ratioDen = 10 and no ap2.fixedAmount and
    auto.generatedPostings = ap1 + ap2 and

    -- Expenses:Food 20 / Assets:Checking -20 gains Tax 2 / Payable -2
    food.name = ExpensesName and checking.name != ExpensesName and
    p1.account = food and p1.amount.value = 20 and p1.amount.currency = c and
    p2.account = checking and p2.amount.value = -20 and p2.amount.currency = c and
    original.postings = p1 + p2 and
    ApplyAutomated[auto, original, p1, result] and
    TransactionBalanced[result] and
    (some tax: result.postings | tax.account = taxExpense and tax.amount.value = 2)
}

-- Example: automatic savings transfer
pred AutoSavingsTransfer {
  some auto: AutomatedTransaction, disj ap1, ap2: AutoPosting |
  some pattern: PayeePattern |
  some disj savingsFrom, savingsTo, checking, salary: Account |
  some disj original, result: Transaction, disj p1, p2: Posting, c: Currency |
    -- Trigger on paycheck deposits
    pattern.payeeMatch = EmployerPayrollName and
    auto.trigger = pattern and

    -- Auto-transfer 20% to savings
    ap1.account = savingsFrom and ap1.ratioNum = -1 and ap1.ratioDen = 5 and no ap1.fixedAmount and
    ap2.account = savingsTo and ap2.ratioNum = 1 and ap2.ratioDen = 5 and no ap2.fixedAmount and
    auto.generatedPostings = ap1 + ap2 and

    -- Paycheck of 10 moves 2 to savings
    original.payee = EmployerPayrollName and
    p1.account = checking and p1.amount.value = 10 and p1.amount.currency = c and
    p2.account = salary and p2.amount.value = -10 and p2.amount.currency = c and
    original.postings = p1 + p2 and
    ApplyAutomated[auto, original, p1, result] and
    (some s: result.postings | s.account = savingsTo and s.amount.value = 2)
}

-- Amounts and ratios small enough that no sum or product in the check scope
-- overflows (|value| <= 3, |ratioNum| <= 10, so |value*num| <= 30 and sums of
-- <= 6 postings stay inside 6-bit integers). Without it an overflowing sum
-- makes the analyzer's no-overflow mode report a spurious counterexample.
pred NoOverflow {
  all a: Amount | a.value >= -3 and a.value <= 3
  all ap: AutoPosting | some ap.ratioNum implies (ap.ratioNum >= -10 and ap.ratioNum <= 10)
}

-- Assertions
-- Original balanced + balanced generated = still balanced
assert AutomatedMaintainsBalance {
  all auto: AutomatedTransaction, original, result: Transaction, matched: Posting |
    (NoOverflow and
     TransactionBalanced[original] and
     ApplyAutomated[auto, original, matched, result] and
     AutomatedPostingsBalance[auto, matched.amount]) implies
    TransactionBalanced[result]
}

check AutomatedMaintainsBalance for 3 but 6 Int

run SalesTaxAutomation for 4 but 6 Int
run AutoSavingsTransfer for 4 but 6 Int
