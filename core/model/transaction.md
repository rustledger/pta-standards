# Transactions

This document specifies the transaction model for plain text accounting systems.

## Definition

A **Transaction** is a balanced collection of postings that records a financial event. Every transaction maintains the fundamental accounting equation: debits equal credits.

## Transaction Structure

```
Transaction = {
  date: Date,
  flag: Flag,
  payee: String?,
  narration: String,
  tags: Set[Tag],
  links: Set[Link],
  metadata: Metadata,
  postings: List[Posting]
}
```

## Components

### Date

The date when the transaction occurred:

```
2024-01-15
2024/01/15    ; Alternative format
```

### Flag

Transaction status indicator:

| Flag | Meaning | Description |
|------|---------|-------------|
| `*` | Cleared | Complete, verified transaction |
| `!` | Pending | Incomplete or unverified |
| `txn` | Cleared | Verbose form of `*` |

### Payee (Optional)

The other party in the transaction:

```
"Whole Foods"
"Amazon"
"John Smith"
```

### Narration

Description of the transaction:

```
"Weekly groceries"
"Monthly subscription"
"Salary deposit"
```

### Tags

Categorical labels starting with `#`:

```
#groceries
#trip-2024-europe
#tax-deductible
```

### Links

Document/transaction links starting with `^`:

```
^invoice-2024-001
^receipt-amazon-123
^trip-2024-europe
```

### Metadata

Key-value annotations:

```
order-id: "12345"
category: "essential"
```

### Postings

List of account changes (see [posting.md](posting.md)):

```
  Assets:Checking   -100.00 USD
  Expenses:Food      100.00 USD
```

## Basic Syntax

### Minimal Transaction

```
2024-01-15 * "Description"
  Account1  100 USD
  Account2 -100 USD
```

### Full Transaction

```
2024-01-15 * "Whole Foods" "Weekly groceries" #groceries ^receipt-001
  order-id: "12345"
  Assets:Checking   -85.50 USD
  Expenses:Food:Groceries  85.50 USD
    category: "essential"
```

## Transaction Flags

### Cleared (`*`)

Indicates a complete, verified transaction:

```
2024-01-15 * "Verified purchase"
  Assets:Checking  -50 USD
  Expenses:Food
```

### Pending (`!`)

Indicates an incomplete or unverified transaction:

```
2024-01-15 ! "Awaiting confirmation"
  Assets:Checking  -50 USD
  Expenses:Food
```

### Flag Progression

Typical workflow:

```
; Initial import (pending)
2024-01-15 ! "AMZN MKTP"
  Assets:Checking  -50 USD
  Expenses:Unknown

; After review (cleared, categorized)
2024-01-15 * "Amazon" "Office supplies"
  Assets:Checking  -50 USD
  Expenses:Office
```

## Payee and Narration

### Both Payee and Narration

```
2024-01-15 * "Payee" "Narration"
  ...
```

### Narration Only

```
2024-01-15 * "Narration only"
  ...
```

### Empty Narration

```
2024-01-15 * "Payee" ""
  ...
```

## Tags and Links

### Tags

Tags categorize transactions:

```
2024-01-15 * "Lunch" #work #reimbursable
  Expenses:Meals  25 USD
  Assets:Checking
```

Use cases:
- Filtering reports
- Categorization
- Project tracking

### Links

Links connect related transactions:

```
2024-01-15 * "Invoice payment" ^invoice-001
  Assets:Receivable  -1000 USD
  Assets:Checking     1000 USD

2024-01-01 * "Service rendered" ^invoice-001
  Assets:Receivable   1000 USD
  Income:Consulting
```

Use cases:
- Invoice tracking
- Trip expense grouping
- Multi-leg transactions

### Tag Stacks

Tags can be pushed for a section:

```
pushtag #trip-2024

2024-01-15 * "Flight"
  Expenses:Travel  500 USD    ; Gets #trip-2024
  Assets:Checking

2024-01-16 * "Hotel"
  Expenses:Travel  200 USD    ; Gets #trip-2024
  Assets:Checking

poptag #trip-2024
```

## Transaction Metadata

### Syntax

```
2024-01-15 * "Purchase"
  order-id: "12345"
  receipt: "path/to/receipt.pdf"
  Assets:Checking  -100 USD
  Expenses:Shopping
```

### Common Metadata Keys

| Key | Purpose | Example |
|-----|---------|---------|
| `filename` | Source file | `"ledger.beancount"` |
| `lineno` | Source line | `42` |
| `time` | Transaction time | `"14:30"` |
| `check` | Check number | `"1234"` |
| `confirmation` | Confirmation number | `"ABC123"` |

## Balance Invariant

### Fundamental Rule

Every transaction MUST balance:

```
sum(posting.weight for posting in transaction.postings) == 0
```

### Tolerance

Small rounding differences within tolerance are acceptable:

```
tolerance = 0.5 × 10^(-precision)
```

### Balance Error

```
ERROR: Transaction does not balance
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 * "Unbalanced"
43 |   Assets:Checking  100 USD
44 |   Expenses:Food     50 USD
   |
   = residual: 150 USD (expected 0)
```

## Multi-Leg Transactions

### Simple Two-Leg

```
2024-01-15 * "Deposit"
  Assets:Checking   1000 USD
  Income:Salary    -1000 USD
```

### Complex Multi-Leg

```
2024-01-15 * "Paycheck with deductions"
  Assets:Checking     4000.00 USD
  Expenses:Tax:Federal 800.00 USD
  Expenses:Tax:State   200.00 USD
  Assets:401k          500.00 USD
  Income:Salary      -5500.00 USD
```

### Split Transaction

```
2024-01-15 * "Grocery store"
  Assets:Checking     -100.00 USD
  Expenses:Food:Groceries  80.00 USD
  Expenses:Household       15.00 USD
  Expenses:Pet              5.00 USD
```

## Currency Conversion

### Explicit Price

```
2024-01-15 * "Currency exchange"
  Assets:USD    108 USD
  Assets:EUR   -100 EUR @ 1.08 USD
```

### Total Price

```
2024-01-15 * "Currency exchange"
  Assets:USD    108 USD
  Assets:EUR   -100 EUR @@ 108 USD
```

### Multi-Currency with Cost

```
2024-01-15 * "Buy foreign stock"
  Assets:Brokerage    10 NESN {85 CHF}
  Assets:CHF        -850 CHF
```

## Stock Transactions

### Purchase

```
2024-01-15 * "Buy Apple stock"
  Assets:Brokerage   100 AAPL {150.00 USD}
  Expenses:Fees        9.95 USD
  Assets:Cash      -15009.95 USD
```

### Sale

```
2024-03-15 * "Sell Apple stock"
  Assets:Brokerage  -100 AAPL {150.00 USD} @ 175.00 USD
  Assets:Cash       17490.05 USD
  Expenses:Fees         9.95 USD
  Income:Gains       -2500.00 USD
```

### Dividend

```
2024-03-01 * "Apple dividend"
  Assets:Cash         24.00 USD
  Income:Dividends   -24.00 USD
```

## Special Transactions

### Opening Balance

```
2024-01-01 * "Opening balance"
  Assets:Checking      5000.00 USD
  Equity:Opening-Balances
```

### Transfer

```
2024-01-15 * "Transfer to savings"
  Assets:Checking  -1000 USD
  Assets:Savings    1000 USD
```

### Reimbursement

```
2024-01-15 * "Work expense reimbursement" ^expense-001
  Assets:Checking     200 USD
  Assets:Receivable  -200 USD
```

## Ordering and Timing

### Date-Based Ordering

Transactions are sorted by date:

```
2024-01-14 * "First"    ; Processed first
2024-01-15 * "Second"   ; Processed second
```

### Same-Date Ordering

Same-date transactions use file order:

```
; Line 10
2024-01-15 * "Morning purchase"

; Line 20
2024-01-15 * "Afternoon purchase"
```

### No Sub-Day Timing

PTA systems typically don't track time within a day. Use metadata if needed:

```
2024-01-15 * "Purchase"
  time: "14:30"
  ...
```

## Implementation Model

```python
@dataclass
class Transaction:
    date: date
    flag: str
    payee: Optional[str]
    narration: str
    tags: Set[str]
    links: Set[str]
    metadata: Dict[str, Any]
    postings: List[Posting]

    def balance_residual(self) -> Dict[str, Decimal]:
        """Calculate balance residual by currency."""
        residuals: Dict[str, Decimal] = {}
        for posting in self.postings:
            if posting.units:
                weight = posting.weight
                currency = weight.commodity
                residuals[currency] = residuals.get(currency, 0) + weight.number
        return residuals

    def is_balanced(self, tolerance: Decimal = Decimal('0.005')) -> bool:
        """Check if transaction balances within tolerance."""
        for residual in self.balance_residual().values():
            if abs(residual) > tolerance:
                return False
        return True
```

## Validation

### Missing Postings

```
ERROR: Transaction has no postings
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 * "Empty"
   | ^^^^^^^^^^^^^^^^^^^^
```

### Single Posting

```
ERROR: Transaction has only one posting
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 * "Single"
43 |   Assets:Checking  100 USD
   |
   = hint: transactions need at least two postings
```

### Invalid Date

```
ERROR: Invalid date
  --> ledger.beancount:42:1
   |
42 | 2024-13-45 * "Bad date"
   | ^^^^^^^^^^
   |
   = month must be 1-12, day must be valid for month
```

## Serialization

### Text Format

```
2024-01-15 * "Payee" "Narration" #tag ^link
  key: "value"
  Assets:Checking  -100 USD
  Expenses:Food
```

### JSON Format

```json
{
  "date": "2024-01-15",
  "flag": "*",
  "payee": "Payee",
  "narration": "Narration",
  "tags": ["tag"],
  "links": ["link"],
  "metadata": {"key": "value"},
  "postings": [
    {"account": "Assets:Checking", "amount": {"number": "-100", "commodity": "USD"}},
    {"account": "Expenses:Food", "amount": null}
  ]
}
```

## Cross-Format Notes

| Feature | Beancount | Ledger | hledger |
|---------|-----------|--------|---------|
| Flags | `*`, `!` | None (or custom) | `*`, `!` |
| Payee | Quoted | Unquoted | Either |
| Tags | `#tag` | `:tag:` | `tag:` |
| Links | `^link` | Not standard | Not standard |
| Metadata | `key: value` | `; key: value` | `; key: value` |
