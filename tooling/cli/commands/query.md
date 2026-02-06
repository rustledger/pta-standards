# query Command

Execute queries against ledger data.

## Synopsis

```
pta query [options] <file> <query>
pta query [options] <file> --file=<query-file>
pta query [options] <file>  # Interactive mode
```

## Description

The `query` command executes BQL (Beancount Query Language) or similar queries against ledger data, producing tabular results.

## Arguments

### file

The ledger file to query.

```bash
pta query ledger.beancount "SELECT ..."
```

### query

The query string (BQL syntax).

```bash
pta query ledger.beancount "SELECT account, sum(position) GROUP BY account"
```

## Options

### --format, -f

Output format: `text` (default), `csv`, `json`, `html`.

```bash
pta query --format=csv ledger.beancount "SELECT ..."
```

### --output, -o

Write output to file instead of stdout.

```bash
pta query -o results.csv ledger.beancount "SELECT ..."
```

### --file, -F

Read query from file.

```bash
pta query --file=query.bql ledger.beancount
```

### --interactive, -i

Start interactive query shell.

```bash
pta query --interactive ledger.beancount
```

### --header/--no-header

Include/exclude column headers.

```bash
pta query --no-header --format=csv ledger.beancount "SELECT ..."
```

### --delimiter

CSV delimiter (default: comma).

```bash
pta query --format=csv --delimiter='\t' ledger.beancount "SELECT ..."
```

### --limit

Limit number of results.

```bash
pta query --limit=10 ledger.beancount "SELECT ..."
```

### --explain

Show query execution plan.

```bash
pta query --explain ledger.beancount "SELECT ..."
```

## Query Language

### Basic SELECT

```sql
SELECT date, narration, account, position
FROM transactions
WHERE account ~ 'Assets:Checking'
```

### Aggregation

```sql
SELECT account, sum(position), count(*)
FROM postings
GROUP BY account
ORDER BY sum(position) DESC
```

### Date Filtering

```sql
SELECT *
FROM transactions
WHERE date >= 2024-01-01 AND date < 2024-02-01
```

### Account Patterns

```sql
SELECT account, sum(position)
FROM postings
WHERE account ~ 'Expenses:.*'
GROUP BY account
```

### Built-in Tables

| Table | Description |
|-------|-------------|
| `transactions` | All transactions |
| `postings` | All postings |
| `balances` | Account balances |
| `open` | Open directives |
| `close` | Close directives |
| `prices` | Price entries |

### Built-in Functions

| Function | Description |
|----------|-------------|
| `sum(position)` | Sum amounts |
| `count(*)` | Count rows |
| `first(x)` | First value |
| `last(x)` | Last value |
| `min(x)` | Minimum |
| `max(x)` | Maximum |
| `root(account, n)` | First n account components |
| `leaf(account)` | Last account component |
| `parent(account)` | Parent account |
| `year(date)` | Extract year |
| `month(date)` | Extract month |
| `day(date)` | Extract day |

## Output Formats

### Text (Default)

```
account              sum_position
──────────────────────────────────
Assets:Checking        1,234.56 USD
Assets:Savings         5,000.00 USD
Expenses:Food           -500.00 USD
```

### CSV

```csv
account,sum_position
Assets:Checking,1234.56 USD
Assets:Savings,5000.00 USD
Expenses:Food,-500.00 USD
```

### JSON

```json
{
  "columns": ["account", "sum_position"],
  "rows": [
    {"account": "Assets:Checking", "sum_position": "1234.56 USD"},
    {"account": "Assets:Savings", "sum_position": "5000.00 USD"}
  ]
}
```

### HTML

```html
<table>
  <thead>
    <tr><th>account</th><th>sum_position</th></tr>
  </thead>
  <tbody>
    <tr><td>Assets:Checking</td><td>1,234.56 USD</td></tr>
    ...
  </tbody>
</table>
```

## Interactive Mode

```bash
$ pta query --interactive ledger.beancount
pta> SELECT account FROM open LIMIT 5;
account
──────────────────────
Assets:Checking
Assets:Savings
Expenses:Food
Income:Salary
Liabilities:CreditCard

pta> SELECT sum(position) FROM postings WHERE account ~ 'Assets:.*';
sum_position
──────────────
6,234.56 USD

pta> .help
Commands:
  .help       Show this help
  .tables     List available tables
  .schema     Show table schema
  .quit       Exit interactive mode

pta> .quit
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Query executed successfully |
| 1 | Query returned no results |
| 2 | Invalid command-line usage |
| 3 | Input file not found |
| 10 | Parse error in ledger |
| 31 | Query syntax error |
| 32 | Query semantic error |
| 33 | Query execution error |

## Examples

### Account Balances

```bash
$ pta query ledger.beancount "
  SELECT account, sum(position)
  FROM postings
  GROUP BY account
  ORDER BY account
"
```

### Monthly Expenses

```bash
$ pta query ledger.beancount "
  SELECT year(date), month(date), sum(position)
  FROM postings
  WHERE account ~ 'Expenses:.*'
  GROUP BY year(date), month(date)
  ORDER BY year(date), month(date)
"
```

### Export to CSV

```bash
$ pta query --format=csv -o expenses.csv ledger.beancount "
  SELECT date, payee, narration, position
  FROM postings
  WHERE account ~ 'Expenses:.*'
"
```

### Top Payees

```bash
$ pta query ledger.beancount "
  SELECT payee, count(*), sum(position)
  FROM transactions
  GROUP BY payee
  ORDER BY count(*) DESC
  LIMIT 10
"
```

### Query from File

```sql
-- queries/monthly-summary.bql
SELECT
  root(account, 1) as category,
  sum(position) as total
FROM postings
WHERE date >= 2024-01-01 AND date < 2024-02-01
GROUP BY root(account, 1)
ORDER BY total DESC
```

```bash
$ pta query --file=queries/monthly-summary.bql ledger.beancount
```

### Pipeline Integration

```bash
# Export and process with other tools
$ pta query --format=csv --no-header ledger.beancount \
    "SELECT date, amount FROM postings" \
  | awk -F, '{sum += $2} END {print sum}'
```

## Comparison with Other Tools

| Feature | pta query | bean-query | hledger |
|---------|-----------|------------|---------|
| BQL syntax | Yes | Yes | Different |
| CSV export | Yes | Yes | Yes |
| JSON export | Yes | No | Yes |
| Interactive | Yes | Yes | No |
| Query files | Yes | No | No |

## See Also

- [BQL Specification](../../../formats/beancount/v3/bql/spec.md) - Query language spec
- [BQL Functions](../../../formats/beancount/v3/bql/functions.md) - Function reference
