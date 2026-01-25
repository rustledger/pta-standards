# Beancount Query Language (BQL) Specification

## Overview

BQL is a specialized SQL-like query engine designed for financial data analysis.
It operates on transaction postings while respecting double-entry bookkeeping constraints.

## Query Structure

```sql
SELECT <target1>, <target2>, ...
[FROM <entry-filter-expression>]
[WHERE <posting-filter-expression>]
[GROUP BY <columns>]
[ORDER BY <columns>]
[LIMIT <n>];
```

### Two-Level Filtering

- **FROM clause**: Filters entire transactions (preserving accounting equation)
- **WHERE clause**: Filters postings from matching transactions

This distinction is critical: FROM preserves transaction integrity while WHERE selects specific postings.

## Data Types

| Type | Description | Example |
|------|-------------|---------|
| String | Text values | `"payee name"` |
| Date | ISO date format | `2024-01-15` |
| Integer | Whole numbers | `42` |
| Boolean | Truth values | `TRUE`, `FALSE` |
| Number | Decimal precision | `123.45` |
| Set of Strings | Collections | tags, links |
| NULL | Absence of value | `NULL` |
| Position | Single lot with optional cost | Units + cost |
| Inventory | Aggregated positions | Multiple lots |

## Operators

### Comparison Operators

| Operator | Meaning |
|----------|---------|
| `=` | Equals |
| `!=` | Not equals |
| `<` | Less than |
| `<=` | Less than or equal |
| `>` | Greater than |
| `>=` | Greater than or equal |

### Logical Operators

| Operator | Meaning |
|----------|---------|
| `AND` | Logical and |
| `OR` | Logical or |
| `NOT` | Logical negation |

### Special Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `IN` | Set membership | `account IN ("Assets:Cash", "Assets:Bank")` |
| `~` | Regular expression match | `account ~ "Expenses:"` |

### NULL Handling

Unlike standard SQL, BQL uses binary NULL logic:

```sql
NULL = NULL  -- yields TRUE (not NULL)
```

This simplifies queries when comparing optional values.

## Column Types

### Posting Columns (SELECT/WHERE)

| Column | Type | Description |
|--------|------|-------------|
| `date` | Date | Transaction date |
| `account` | String | Account name |
| `position` | Position | Full position with cost |
| `units` | Amount | Units only |
| `cost` | Amount | Cost basis |
| `weight` | Amount | Balancing weight |
| `narration` | String | Transaction narration |
| `payee` | String | Payee |
| `tags` | Set | Transaction tags |
| `links` | Set | Transaction links |
| `flag` | String | Transaction flag (`*` or `!`) |
| `balance` | Inventory | Running balance after posting |

### Entry Columns (FROM clause)

| Column | Type | Description |
|--------|------|-------------|
| `date` | Date | Directive date |
| `flag` | String | Transaction flag |
| `payee` | String | Payee |
| `narration` | String | Narration |
| `tags` | Set | Tags |
| `links` | Set | Links |
| `id` | String | Unique stable hash |
| `type` | String | Directive type name |

## Functions

See [functions.md](functions.md) for the complete function reference.

### Position/Amount Functions

| Function | Description |
|----------|-------------|
| `COST(pos)` | Total cost (units × per-unit cost) |
| `UNITS(pos)` | Units only (strips cost) |
| `NUMBER(amt)` | Numeric value from amount |
| `CURRENCY(amt)` | Currency from amount |
| `WEIGHT(pos)` | Balancing weight |
| `VALUE(pos[, currency])` | Market value at last price |

### Date Functions

| Function | Description |
|----------|-------------|
| `DAY(date)` | Day of month (1-31) |
| `MONTH(date)` | Month (1-12) |
| `YEAR(date)` | Year |
| `QUARTER(date)` | Quarter (1-4) |
| `WEEKDAY(date)` | Day of week (0=Monday) |

### String Functions

| Function | Description |
|----------|-------------|
| `LENGTH(s)` | String length |
| `UPPER(s)` | Uppercase |
| `LOWER(s)` | Lowercase |

### Account Functions

| Function | Description |
|----------|-------------|
| `PARENT(account)` | Parent account name |
| `LEAF(account)` | Last component |
| `ROOT(account, n)` | First n components |

### Aggregate Functions

| Function | Description |
|----------|-------------|
| `COUNT(*)` | Count of postings |
| `FIRST(x)` | First value in group |
| `LAST(x)` | Last value in group |
| `MIN(x)` | Minimum value |
| `MAX(x)` | Maximum value |
| `SUM(x)` | Sum (works on amounts, positions, inventories) |

## Query Types

### Simple Query

One result row per matching posting:

```sql
SELECT date, account, narration, position
WHERE account ~ "Expenses:";
```

### Aggregate Query

One result row per group:

```sql
SELECT account, SUM(position)
WHERE account ~ "Expenses:"
GROUP BY account;
```

Group keys MAY reference:
- Column names
- Ordinal indices (1, 2, ...)
- Expressions

## Result Control

### DISTINCT

Remove duplicate result rows:

```sql
SELECT DISTINCT account;
```

### ORDER BY

Sort results:

```sql
ORDER BY date DESC, account ASC;
```

Default is `ASC`. Multiple columns supported.

### LIMIT

Restrict output:

```sql
LIMIT 100;
```

## Statement Operators

These transform transactions before posting projection.

### OPEN ON \<date\>

Summarizes all entries before the date:

- Asset/Liability balances → booked to Equity:Opening-Balances
- Income/Expense balances → cleared to Equity:Earnings:Previous

```sql
SELECT * FROM has_account("Invest") OPEN ON 2024-01-01;
```

### CLOSE [ON \<date\>]

Truncates entries after the date:

```sql
SELECT * FROM condition CLOSE ON 2024-12-31;
```

### CLEAR

Transfers income and expense balances to equity:

```sql
SELECT account, SUM(position)
FROM OPEN ON 2023-01-01 CLOSE ON 2024-01-01 CLEAR
WHERE account ~ "^(Assets|Liabilities)"
GROUP BY 1;
```

## High-Level Query Shortcuts

### JOURNAL

Generate account statement:

```sql
JOURNAL <account-regexp> [AT <function>] [FROM ...]
```

Example:
```sql
JOURNAL "Assets:Checking" AT cost
```

### BALANCES

Produce account balance table:

```sql
BALANCES [AT <function>] [FROM ...]
```

Example:
```sql
BALANCES AT units FROM year = 2024
```

### PRINT

Output filtered transactions in Beancount syntax:

```sql
PRINT [FROM ...]
```

## Wildcard Selection

```sql
SELECT *;
```

Selects sensible default columns for the query type.

## FROM Clause Filters

Special predicates for transaction-level filtering:

| Predicate | Description |
|-----------|-------------|
| `has_account(pattern)` | Transaction has posting matching account pattern |
| `year = N` | Transaction year equals N |
| `month = N` | Transaction month equals N |
| `date >= D` | Transaction date comparison |

## Grammar Summary

```
query       := select_stmt | journal_stmt | balances_stmt | print_stmt

select_stmt := SELECT [DISTINCT] targets
               [FROM from_expr]
               [WHERE where_expr]
               [GROUP BY group_exprs]
               [ORDER BY order_exprs]
               [LIMIT n]

targets     := target ("," target)*
target      := expr [AS name]

from_expr   := [OPEN ON date] [CLOSE ON date] [CLEAR] [filter_expr]
filter_expr := predicate (AND predicate)*

where_expr  := condition (AND|OR condition)*
condition   := expr op expr | NOT condition | "(" where_expr ")"

group_exprs := expr ("," expr)*
order_exprs := expr [ASC|DESC] ("," expr [ASC|DESC])*

expr        := column | function(args) | literal | expr op expr
```

## Key Distinctions from SQL

1. **Two-level filtering**: FROM filters transactions, WHERE filters postings
2. **Native inventory types**: Position and Inventory are first-class types
3. **Cost operations**: Built-in functions for cost basis calculations
4. **Accounting equation preservation**: Transaction-level filtering maintains balance
5. **Running balance column**: `balance` without window functions
6. **Simplified NULL**: Binary logic (NULL = NULL is TRUE)
