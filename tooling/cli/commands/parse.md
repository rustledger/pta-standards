# parse Command

Parse ledger file and output AST or tokens.

## Synopsis

```
pta parse [options] <file>
pta parse [options] --stdin
```

## Description

The `parse` command parses a ledger file and outputs its internal representation. This is useful for debugging, tooling development, and understanding how files are interpreted.

## Arguments

### file

Ledger file to parse.

```bash
pta parse ledger.beancount
```

## Options

### --format, -f

Output format: `json` (default), `yaml`, `sexpr`, `debug`.

```bash
pta parse --format=json ledger.beancount
pta parse --format=yaml ledger.beancount
```

### --output, -o

Output file (default: stdout).

```bash
pta parse -o ast.json ledger.beancount
```

### --stdin

Read from stdin.

```bash
cat ledger.beancount | pta parse --stdin
```

### --tokens

Output tokens instead of AST.

```bash
pta parse --tokens ledger.beancount
```

### --pretty

Pretty-print output.

```bash
pta parse --pretty ledger.beancount
```

### --compact

Compact output (no whitespace).

```bash
pta parse --compact ledger.beancount
```

### --include-locations

Include source locations in output.

```bash
pta parse --include-locations ledger.beancount
```

### --include-trivia

Include comments and whitespace in output.

```bash
pta parse --include-trivia ledger.beancount
```

### --directive-types

Filter by directive types.

```bash
pta parse --directive-types=transaction,open ledger.beancount
```

### --no-resolve-includes

Don't resolve include directives.

```bash
pta parse --no-resolve-includes ledger.beancount
```

## Output Formats

### JSON (Default)

```bash
$ pta parse --format=json ledger.beancount
```

```json
{
  "directives": [
    {
      "type": "open",
      "date": "2024-01-01",
      "account": "Assets:Checking",
      "currencies": ["USD"],
      "location": {
        "file": "ledger.beancount",
        "line": 1,
        "column": 1
      }
    },
    {
      "type": "transaction",
      "date": "2024-01-15",
      "flag": "*",
      "payee": "Whole Foods",
      "narration": "Weekly groceries",
      "tags": ["food"],
      "links": [],
      "metadata": {},
      "postings": [
        {
          "account": "Assets:Checking",
          "amount": {
            "number": "-85.50",
            "currency": "USD"
          },
          "cost": null,
          "price": null
        },
        {
          "account": "Expenses:Food:Groceries",
          "amount": null
        }
      ],
      "location": {
        "file": "ledger.beancount",
        "line": 3,
        "column": 1
      }
    }
  ]
}
```

### YAML

```bash
$ pta parse --format=yaml ledger.beancount
```

```yaml
directives:
  - type: open
    date: "2024-01-01"
    account: Assets:Checking
    currencies:
      - USD
  - type: transaction
    date: "2024-01-15"
    flag: "*"
    payee: Whole Foods
    narration: Weekly groceries
    tags:
      - food
    postings:
      - account: Assets:Checking
        amount:
          number: "-85.50"
          currency: USD
      - account: Expenses:Food:Groceries
```

### S-Expression

```bash
$ pta parse --format=sexpr ledger.beancount
```

```lisp
(directives
  (open
    (date "2024-01-01")
    (account "Assets:Checking")
    (currencies "USD"))
  (transaction
    (date "2024-01-15")
    (flag "*")
    (payee "Whole Foods")
    (narration "Weekly groceries")
    (tags "food")
    (postings
      (posting
        (account "Assets:Checking")
        (amount "-85.50" "USD"))
      (posting
        (account "Expenses:Food:Groceries")))))
```

### Debug

```bash
$ pta parse --format=debug ledger.beancount
```

```
Open {
    date: 2024-01-01,
    account: "Assets:Checking",
    currencies: ["USD"],
    booking: None,
    meta: {},
    location: ledger.beancount:1:1
}
Transaction {
    date: 2024-01-15,
    flag: Cleared,
    payee: Some("Whole Foods"),
    narration: "Weekly groceries",
    tags: {"food"},
    links: {},
    meta: {},
    postings: [
        Posting { account: "Assets:Checking", units: Some(-85.50 USD), ... },
        Posting { account: "Expenses:Food:Groceries", units: None, ... }
    ],
    location: ledger.beancount:3:1
}
```

## Token Output

### Token List

```bash
$ pta parse --tokens ledger.beancount
```

```json
{
  "tokens": [
    { "type": "DATE", "value": "2024-01-01", "line": 1, "column": 1 },
    { "type": "KEYWORD", "value": "open", "line": 1, "column": 12 },
    { "type": "ACCOUNT", "value": "Assets:Checking", "line": 1, "column": 17 },
    { "type": "CURRENCY", "value": "USD", "line": 1, "column": 33 },
    { "type": "NEWLINE", "value": "\n", "line": 1, "column": 36 },
    { "type": "NEWLINE", "value": "\n", "line": 2, "column": 1 },
    { "type": "DATE", "value": "2024-01-15", "line": 3, "column": 1 },
    { "type": "FLAG", "value": "*", "line": 3, "column": 12 },
    { "type": "STRING", "value": "Whole Foods", "line": 3, "column": 14 },
    ...
  ]
}
```

### With Trivia

```bash
$ pta parse --tokens --include-trivia ledger.beancount
```

Includes comments and whitespace tokens.

## Filtering

### By Directive Type

```bash
$ pta parse --directive-types=transaction ledger.beancount
```

Only outputs transaction directives.

### Multiple Types

```bash
$ pta parse --directive-types=transaction,balance ledger.beancount
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Parse successful |
| 2 | Invalid command-line usage |
| 3 | Input file not found |
| 10 | Parse error |

## Examples

### Basic Parse

```bash
$ pta parse ledger.beancount > ast.json
```

### Pretty-Printed

```bash
$ pta parse --pretty ledger.beancount | less
```

### Extract Transactions Only

```bash
$ pta parse --directive-types=transaction ledger.beancount \
  | jq '.directives[]'
```

### Count Directives by Type

```bash
$ pta parse ledger.beancount \
  | jq '.directives | group_by(.type) | map({type: .[0].type, count: length})'
```

### Validate JSON Output

```bash
$ pta parse ledger.beancount | jq -e '.' > /dev/null && echo "Valid JSON"
```

### Token Analysis

```bash
$ pta parse --tokens ledger.beancount \
  | jq '.tokens | group_by(.type) | map({type: .[0].type, count: length})'
```

### Debug Parse Errors

```bash
$ pta parse --format=debug problematic.beancount 2>&1 | head -50
```

### Pipeline Processing

```bash
# Extract all accounts mentioned
$ pta parse ledger.beancount \
  | jq -r '.directives[] | select(.type=="transaction") | .postings[].account' \
  | sort -u
```

### Round-Trip Test

```bash
# Parse → unparse → parse should be equivalent
$ pta parse ledger.beancount > ast1.json
$ pta unparse ast1.json | pta parse --stdin > ast2.json
$ diff ast1.json ast2.json
```

## Use Cases

### Tooling Development

Build tools that process ledger files:

```python
import subprocess
import json

result = subprocess.run(
    ['pta', 'parse', '--format=json', 'ledger.beancount'],
    capture_output=True, text=True
)
ast = json.loads(result.stdout)

for directive in ast['directives']:
    if directive['type'] == 'transaction':
        process_transaction(directive)
```

### Editor Integration

Provide IDE features:

```javascript
// VS Code extension
const ast = JSON.parse(execSync('pta parse --format=json file.beancount'));
const accounts = new Set();
ast.directives
  .filter(d => d.type === 'open')
  .forEach(d => accounts.add(d.account));
// Use for autocomplete
```

### Migration

Convert between internal representations:

```bash
pta parse --format=json old-format.beancount \
  | my-transformer \
  | pta unparse --format=beancount > new-format.beancount
```

## See Also

- [AST Schema](../../schema/README.md) - AST structure documentation
- [JSON Schema](../../../formats/beancount/v3/schema/ast.schema.json) - AST validation schema
