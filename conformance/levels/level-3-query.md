# Level 3: Query Conformance

Level 3 conformance requires Level 2 validation plus BQL (Beancount Query Language) execution.

## Requirements

### Level 2 Prerequisites

All Level 1 and Level 2 requirements MUST be met.

### Query Parsing

The implementation MUST parse BQL syntax:

| Clause | Support |
|--------|---------|
| SELECT | Required |
| FROM | Required |
| WHERE | Required |
| GROUP BY | Required |
| ORDER BY | Required |
| LIMIT | Required |
| HAVING | Optional |

### Data Sources

The implementation MUST support FROM clauses:

| Source | Description |
|--------|-------------|
| `postings` | All postings |
| `transactions` | All transactions |
| `balances` | Current balances |
| `entries` | All directives |

### Column Access

The implementation MUST support columns:

| Column | Type | Description |
|--------|------|-------------|
| `account` | string | Account name |
| `date` | date | Transaction date |
| `narration` | string | Transaction description |
| `payee` | string | Transaction payee |
| `position` | position | Posting amount with cost |
| `balance` | inventory | Running balance |
| `number` | decimal | Amount number |
| `currency` | string | Amount currency |

### Operators

The implementation MUST support:

| Category | Operators |
|----------|-----------|
| Comparison | `=`, `!=`, `<`, `>`, `<=`, `>=` |
| Logical | `AND`, `OR`, `NOT` |
| Pattern | `~` (regex match) |
| Null | `IS NULL`, `IS NOT NULL` |
| Membership | `IN` |

### Aggregate Functions

The implementation MUST support:

| Function | Description |
|----------|-------------|
| `SUM()` | Sum of values |
| `COUNT()` | Count of rows |
| `FIRST()` | First value |
| `LAST()` | Last value |
| `MIN()` | Minimum value |
| `MAX()` | Maximum value |

### Scalar Functions

The implementation SHOULD support:

| Function | Description |
|----------|-------------|
| `ABS()` | Absolute value |
| `LENGTH()` | String length |
| `YEAR()` | Year from date |
| `MONTH()` | Month from date |
| `DAY()` | Day from date |
| `ROOT()` | Account root |
| `LEAF()` | Account leaf |
| `PARENT()` | Parent account |

### Amount Functions

The implementation MUST support:

| Function | Description |
|----------|-------------|
| `UNITS()` | Extract units from position |
| `COST()` | Extract cost from position |
| `NUMBER()` | Number from amount |
| `CURRENCY()` | Currency from amount |
| `CONVERT()` | Currency conversion |

## Test Suite

### Required Tests

| Suite | Purpose | Minimum Pass Rate |
|-------|---------|-------------------|
| All Level 2 tests | Prerequisites | 100% of L2 |
| `bql` | Query execution | 95% |

### Query Test Categories

- Basic SELECT queries
- WHERE filtering
- GROUP BY aggregation
- ORDER BY sorting
- Complex expressions
- Error handling

## Example Queries

### Basic Query

```sql
SELECT account, SUM(position)
FROM postings
WHERE account ~ 'Expenses'
GROUP BY account
ORDER BY SUM(position) DESC
```

### Date Filtering

```sql
SELECT date, narration, position
FROM postings
WHERE date >= 2024-01-01 AND date < 2024-02-01
  AND account = 'Assets:Checking'
```

### Account Hierarchy

```sql
SELECT ROOT(account, 2) AS category, SUM(position)
FROM postings
WHERE account ~ 'Expenses:'
GROUP BY ROOT(account, 2)
```

## Query Execution Model

```
Parse Query → Plan → Execute → Format Results
```

### Execution Steps

1. Parse BQL into AST
2. Validate column/function references
3. Load required data
4. Apply WHERE filters
5. Perform GROUP BY
6. Apply HAVING filters
7. Sort by ORDER BY
8. Apply LIMIT
9. Format output

## Error Handling

Query errors MUST include:

| Error Type | Information |
|------------|-------------|
| Syntax error | Location in query |
| Unknown column | Available columns |
| Type mismatch | Expected vs actual |
| Invalid function | Available functions |

## Example Implementation

```python
def execute_query(query: str, journal: Journal) -> QueryResult:
    """
    Level 3 compliant query executor.
    """
    ast = parse_query(query)
    validate_query(ast, journal)

    # Get data source
    if ast.from_clause == 'postings':
        rows = get_postings(journal)
    elif ast.from_clause == 'balances':
        rows = get_balances(journal)

    # Filter
    rows = filter(lambda r: evaluate(ast.where, r), rows)

    # Group
    if ast.group_by:
        rows = group_and_aggregate(rows, ast)

    # Sort
    if ast.order_by:
        rows = sorted(rows, key=lambda r: evaluate(ast.order_by, r))

    # Limit
    if ast.limit:
        rows = rows[:ast.limit]

    return QueryResult(columns=ast.columns, rows=list(rows))
```

## Certification

To achieve Level 3:

1. Achieve Level 2 certification
2. Run BQL test suite
3. Achieve 95% pass rate
4. Document query limitations
5. Submit certification

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| Inventory summation | Handle multi-currency |
| NULL handling | Use SQL NULL semantics |
| Regex escaping | Use proper regex syntax |
| Date comparisons | Use consistent date handling |

## Non-Requirements

Level 3 does NOT require:
- FLATTEN clause
- PIVOT operations
- Subqueries
- Plugin support
- Booking methods

## See Also

- [Test Suite](/tests/beancount/v3/bql/)
- [BQL Specification](/formats/beancount/v3/bql/spec.md)
- [BQL Functions](/formats/beancount/v3/bql/functions.md)
