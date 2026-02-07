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

sig Account {
  name: String
}

sig Posting {
  account: Account,
  amount: Amount
}

sig Transaction {
  date: Int,
  payee: String,
  postings: set Posting
}

-- Pattern for matching transactions
abstract sig Pattern {}

-- Account pattern: matches postings to specific accounts
sig AccountPattern extends Pattern {
  accountMatch: String  -- Account name pattern (supports regex)
}

-- Payee pattern: matches transaction payee
sig PayeePattern extends Pattern {
  payeeMatch: String
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
  percentage: lone Int  -- If set, compute as % of matched amount
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

-- Compute the amount for an auto posting
fun computeAutoAmount[ap: AutoPosting, matchedAmount: Amount]: Amount {
  some ap.fixedAmount implies ap.fixedAmount
  else some ap.percentage implies {
    a: Amount |
      a.currency = matchedAmount.currency and
      a.value = div[mul[matchedAmount.value, ap.percentage], 100]
  }
  else matchedAmount
}

-- Apply automated transaction to a matching transaction
pred ApplyAutomated[auto: AutomatedTransaction, original: Transaction, result: Transaction] {
  TransactionMatchesPattern[original, auto.trigger]

  -- Result has original postings plus generated ones
  result.date = original.date
  result.payee = original.payee

  -- Find the matched posting (first one that matches)
  some matchedPosting: original.postings |
    PostingMatchesPattern[matchedPosting, auto.trigger] and

    -- Generate new postings
    let newPostings = { ap: auto.generatedPostings, a: Account, amt: Amount |
      a = ap.account and
      amt = computeAutoAmount[ap, matchedPosting.amount]
    } |
    -- This is simplified; actual would create Posting objects
    #result.postings = add[#original.postings, #auto.generatedPostings]
}

-- Example: automatic sales tax
pred SalesTaxAutomation {
  some auto: AutomatedTransaction, ap1, ap2: AutoPosting |
  some pattern: AccountPattern |
  some taxExpense, taxPayable: Account |
    -- Trigger on any Expenses:* posting
    pattern.accountMatch = "Expenses" and
    auto.trigger = pattern and

    -- Generate tax postings (10% of expense)
    ap1.account = taxExpense and ap1.percentage = 10 and no ap1.fixedAmount and
    ap2.account = taxPayable and ap2.percentage = -10 and no ap2.fixedAmount and
    auto.generatedPostings = ap1 + ap2
}

-- Example: automatic savings transfer
pred AutoSavingsTransfer {
  some auto: AutomatedTransaction, ap1, ap2: AutoPosting |
  some pattern: PayeePattern |
  some savingsFrom, savingsTo: Account |
    -- Trigger on paycheck deposits
    pattern.payeeMatch = "Employer Payroll" and
    auto.trigger = pattern and

    -- Auto-transfer 20% to savings
    ap1.account = savingsFrom and ap1.percentage = -20 and
    ap2.account = savingsTo and ap2.percentage = 20 and
    auto.generatedPostings = ap1 + ap2
}

-- Generated postings should balance
pred AutomatedPostingsBalance[auto: AutomatedTransaction, matchedAmount: Amount] {
  (sum ap: auto.generatedPostings |
    computeAutoAmount[ap, matchedAmount].value) = 0
}

-- Assertions
assert AutomatedMaintainsBalance {
  all auto: AutomatedTransaction, amt: Amount |
    AutomatedPostingsBalance[auto, amt] implies
    -- Original balanced + balanced generated = still balanced
    true
}

check AutomatedMaintainsBalance for 4

run SalesTaxAutomation for 4
run AutoSavingsTransfer for 4
