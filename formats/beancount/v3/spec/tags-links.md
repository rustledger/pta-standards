# Tags and Links

## Overview

Tags and links provide lightweight categorization and cross-referencing for transactions. Tags group related transactions by category, while links connect specific transactions across time.

## Syntax

```ebnf
tag  = "#" identifier
link = "^" identifier

identifier = (letter | digit | "-" | "_" | "/" | ".")+
```

Note: Periods (`.`) are allowed in tag and link identifiers.

## Tags

### Basic Usage

Tags categorize transactions:

```beancount
2024-01-15 * "Flight to Berlin" #travel #berlin-trip
  Expenses:Travel:Flights  450 USD
  Liabilities:CreditCard

2024-01-16 * "Hotel" #travel #berlin-trip
  Expenses:Travel:Lodging  200 USD
  Liabilities:CreditCard
```

### Tag Format

- Start with `#`
- Contain letters, digits, hyphens, underscores, slashes
- Case-sensitive

### Valid Tags

```
#travel
#berlin-trip
#2024/q1
#tax_deductible
#Project-Alpha
```

### Invalid Tags

```
#travel trip    ; Space not allowed
#               ; Empty tag
travel          ; Missing #
```

## Links

### Basic Usage

Links connect related transactions:

```beancount
2024-01-15 * "Invoice #1234" ^invoice-1234
  Income:Consulting  -5000 USD
  Assets:Receivable

2024-02-01 * "Payment received" ^invoice-1234
  Assets:Checking   5000 USD
  Assets:Receivable
```

### Link Format

- Start with `^`
- Same character rules as tags
- Case-sensitive

### Valid Links

```
^invoice-1234
^project/phase-1
^ref_2024_001
```

## Tags vs Links

| Aspect | Tags | Links |
|--------|------|-------|
| Prefix | `#` | `^` |
| Purpose | Categorization | Cross-reference |
| Cardinality | Many transactions | Few transactions |
| Query | Filter by category | Find related items |
| Example | `#travel` | `^invoice-123` |

## Placement

Tags and links appear after the transaction strings:

```beancount
2024-01-15 * "Description" #tag1 #tag2 ^link1 ^link2
  Account  100 USD
  Other
```

Order doesn't matter:

```beancount
; Both equivalent
2024-01-15 * "Desc" #travel ^trip-123
2024-01-15 * "Desc" ^trip-123 #travel
```

## Tag Stack

### pushtag / poptag

Apply tags to multiple transactions:

```beancount
pushtag #berlin-trip

2024-04-23 * "Flight"
  ; Automatically tagged #berlin-trip
  Expenses:Travel:Flights  500 USD
  Liabilities:CreditCard

2024-04-24 * "Hotel"
  ; Also tagged #berlin-trip
  Expenses:Travel:Lodging  150 USD
  Liabilities:CreditCard

2024-04-25 * "Dinner"
  Expenses:Travel:Meals  45 USD
  Liabilities:CreditCard

poptag #berlin-trip
```

### Nested Stacks

```beancount
pushtag #travel
pushtag #business

2024-03-15 * "Conference"
  ; Has both #travel and #business
  Expenses:Conference  500 USD
  Assets:Checking

poptag #business

2024-03-20 * "Vacation flight"
  ; Has only #travel
  Expenses:Vacation  300 USD
  Assets:Checking

poptag #travel
```

### Stack + Explicit Tags

```beancount
pushtag #2024

2024-01-15 * "Expense" #tax-deductible
  ; Has both #2024 (from stack) and #tax-deductible (explicit)
  Expenses:Office  100 USD
  Assets:Checking

poptag #2024
```

## Common Tag Patterns

### Time-Based

```beancount
#2024
#2024/q1
#january
#fiscal-2024
```

### Category-Based

```beancount
#travel
#business
#personal
#tax-deductible
#reimbursable
```

### Project-Based

```beancount
#project-alpha
#client/acme
#website-redesign
```

### Status-Based

```beancount
#pending-review
#needs-receipt
#reconciled
```

## Common Link Patterns

### Invoice Lifecycle

```beancount
2024-01-15 * "Send invoice" ^inv-2024-001
  Income:Consulting  -5000 USD
  Assets:Receivable

2024-02-01 * "Partial payment" ^inv-2024-001
  Assets:Checking   2500 USD
  Assets:Receivable

2024-02-15 * "Final payment" ^inv-2024-001
  Assets:Checking   2500 USD
  Assets:Receivable
```

### Purchase Order

```beancount
2024-01-10 * "Order equipment" ^po-2024-005
  Expenses:Equipment  2000 USD
  Liabilities:Payable

2024-01-25 * "Pay for equipment" ^po-2024-005
  Liabilities:Payable  2000 USD
  Assets:Checking
```

### Transfer Tracking

```beancount
2024-01-15 * "Initiate transfer" ^transfer-001
  Assets:BankA  -1000 USD
  Assets:InTransit

2024-01-17 * "Transfer complete" ^transfer-001
  Assets:InTransit  -1000 USD
  Assets:BankB   1000 USD
```

## Querying

### By Tag

```sql
-- All travel expenses
SELECT date, narration, sum(position)
FROM postings
WHERE #travel IN tags
GROUP BY date, narration

-- Multiple tags (AND)
SELECT * FROM transactions
WHERE #business IN tags AND #travel IN tags

-- Multiple tags (OR)
SELECT * FROM transactions
WHERE #business IN tags OR #personal IN tags
```

### By Link

```sql
-- All transactions for an invoice
SELECT date, narration, position
FROM postings
WHERE ^invoice-1234 IN links

-- Find all links
SELECT DISTINCT link FROM transactions
```

## Tags on Other Directives

Tags can appear on some non-transaction directives:

### Document

```beancount
2024-01-15 document Assets:Checking "statement.pdf" #monthly #2024
```

### Custom

```beancount
2024-01-01 custom "budget" Expenses:Food 500 USD #2024
```

## Validation

Tags and links have no semantic validation—any valid identifier is accepted. Implementations may warn about:

- Unused links (link appears only once)
- Very long tag/link names
- Inconsistent naming conventions

## Best Practices

### Tags

1. Use consistent naming conventions
2. Prefer lowercase with hyphens
3. Create a tag taxonomy for your ledger
4. Use hierarchical tags for subcategories (`#travel/flight`)

### Links

1. Use unique, descriptive identifiers
2. Include reference numbers when available
3. Link all related transactions
4. Document link meanings in comments

## Implementation Notes

1. Parse `#` as tag, `^` as link
2. Store as sets on transactions
3. Merge stack tags with explicit tags
4. Enable efficient tag/link queries
5. Support both inclusion and exclusion filters
