# Query Directive

## Overview

The `query` directive embeds a named BQL (Beancount Query Language) query within the ledger file. This allows frequently-used queries to be stored alongside the data.

## Syntax

```ebnf
query = date WHITESPACE "query" WHITESPACE name WHITESPACE query_string
        (NEWLINE metadata)*

name         = string
query_string = string
```

## Components

### Date

The date associated with the query. This can represent:
- When the query was created
- The default date context for the query
- A logical grouping date

### Name

A string identifier for the query. Used to reference and execute the query.

### Query String

A BQL query enclosed in quotes.

## Examples

### Basic Query

```beancount
2024-01-01 query "balance" "
  SELECT account, sum(position)
  GROUP BY account
  ORDER BY account
"
```

### Income Statement

```beancount
2024-01-01 query "income-statement" "
  SELECT account, sum(position)
  WHERE account ~ 'Income|Expenses'
  GROUP BY account
  ORDER BY account
"
```

### Monthly Expenses

```beancount
2024-01-01 query "monthly-expenses" "
  SELECT month, sum(position)
  WHERE account ~ 'Expenses'
  GROUP BY month
  ORDER BY month
"
```

### Account Register

```beancount
2024-01-01 query "checking-register" "
  SELECT date, narration, position, balance
  WHERE account = 'Assets:Checking'
  ORDER BY date
"
```

### With Metadata

```beancount
2024-01-01 query "tax-expenses" "
  SELECT account, sum(position)
  WHERE account ~ 'Expenses' AND 'tax-deductible' IN tags
  GROUP BY account
"
  description: "Tax-deductible expenses for filing"
  category: "tax"
```

## Query Execution

Embedded queries can be run by name:

```bash
# Run a named query
bean-query ledger.beancount --query "balance"

# Run with date filter
bean-query ledger.beancount --query "monthly-expenses" --from 2024-01-01 --to 2024-12-31
```

Or in interactive mode:

```
beancount> run balance
beancount> run income-statement
```

## Query Library

Organize queries as a library in the ledger:

```beancount
; ============================================
; QUERY LIBRARY
; ============================================

2024-01-01 query "net-worth" "
  SELECT sum(position)
  WHERE account ~ 'Assets|Liabilities'
"

2024-01-01 query "cash-flow" "
  SELECT month, sum(position)
  WHERE account ~ 'Assets:.*:Checking'
  GROUP BY month
"

2024-01-01 query "spending-by-category" "
  SELECT root(account, 2) AS category, sum(position)
  WHERE account ~ 'Expenses'
  GROUP BY category
  ORDER BY sum(position) DESC
"

2024-01-01 query "investment-performance" "
  SELECT account,
         sum(units(position)) AS units,
         sum(cost(position)) AS cost,
         sum(value(position)) AS value
  WHERE account ~ 'Assets:Investments'
  GROUP BY account
"
```

## Parameterized Queries

While BQL doesn't support parameters directly, conventions can be used:

```beancount
; Use a specific account pattern
2024-01-01 query "account-detail" "
  SELECT date, narration, position, balance
  WHERE account ~ '{ACCOUNT}'
  ORDER BY date
"
  parameter: "ACCOUNT"
  default: "Assets:Checking"
```

Implementations may support substitution:

```bash
bean-query ledger.beancount --query "account-detail" --param ACCOUNT="Liabilities:CreditCard"
```

## Common Queries

### Balance Sheet

```beancount
2024-01-01 query "balance-sheet" "
  SELECT account, sum(position) AS balance
  WHERE account ~ 'Assets|Liabilities|Equity'
  GROUP BY account
  ORDER BY account
"
```

### Trial Balance

```beancount
2024-01-01 query "trial-balance" "
  SELECT account,
         sum(position) FILTER (WHERE number > 0) AS debits,
         sum(position) FILTER (WHERE number < 0) AS credits
  GROUP BY account
  ORDER BY account
"
```

### Expense Breakdown

```beancount
2024-01-01 query "expense-breakdown" "
  SELECT
    root(account, 2) AS category,
    sum(position) AS total,
    count(*) AS transactions
  WHERE account ~ 'Expenses'
  GROUP BY category
  ORDER BY total DESC
"
```

### Uncleared Transactions

```beancount
2024-01-01 query "uncleared" "
  SELECT date, narration, position
  WHERE flag = '!'
  ORDER BY date
"
```

## Validation

Query directives have minimal validation:
- Name must be a valid string
- Query string must be a valid string

Query syntax errors are detected at execution time, not parse time.

## Listing Queries

Get all defined queries:

```bash
bean-query ledger.beancount --list-queries
```

Output:
```
balance              2024-01-01  Balance by account
income-statement     2024-01-01  Income and expenses summary
monthly-expenses     2024-01-01  Expenses by month
checking-register    2024-01-01  Checking account transactions
```

## Use Cases

### Personal Finance Dashboard

```beancount
2024-01-01 query "dashboard-networth" "SELECT sum(position) WHERE account ~ 'Assets|Liabilities'"
2024-01-01 query "dashboard-monthly-spend" "SELECT sum(position) WHERE account ~ 'Expenses' AND year = 2024 AND month = MONTH(today())"
2024-01-01 query "dashboard-savings-rate" "SELECT 1 - (sum(position) FILTER (WHERE account ~ 'Expenses') / sum(position) FILTER (WHERE account ~ 'Income'))"
```

### Reporting Templates

```beancount
2024-01-01 query "report-annual" "
  SELECT
    root(account, 1) AS type,
    sum(position) AS total
  WHERE year = YEAR(today()) - 1
  GROUP BY type
"
  output-format: "csv"
  schedule: "annually"
```

## Implementation Notes

1. Store queries indexed by name
2. Parse query string at execution time (not load time)
3. Date provides context but doesn't filter by default
4. Support listing all defined queries
5. Queries don't affect financial calculations
