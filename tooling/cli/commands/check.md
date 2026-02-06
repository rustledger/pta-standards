# check Command

Validate a ledger file for errors.

## Synopsis

```
pta check [options] <file>...
```

## Description

The `check` command parses and validates a ledger file, reporting any errors or warnings found. This is the primary command for verifying ledger correctness.

## Arguments

### file

One or more ledger files to check. Multiple files are merged before validation.

```bash
pta check ledger.beancount
pta check main.beancount accounts.beancount
pta check *.beancount
```

Use `-` to read from stdin:

```bash
cat ledger.beancount | pta check -
```

## Options

### --strict

Treat warnings as errors.

```bash
pta check --strict ledger.beancount
```

Exit code 1 if any warnings are present.

### --quiet, -q

Suppress output except errors.

```bash
pta check --quiet ledger.beancount
```

### --verbose, -v

Show additional information.

```bash
pta check --verbose ledger.beancount
```

### --format

Output format: `text` (default), `json`, `github`.

```bash
pta check --format=json ledger.beancount
```

### --max-errors

Stop after N errors.

```bash
pta check --max-errors=10 ledger.beancount
```

### --ignore

Ignore specific error codes.

```bash
pta check --ignore=W1001,W1002 ledger.beancount
```

### --only

Report only specific error codes.

```bash
pta check --only=E1001,E2001 ledger.beancount
```

### --no-plugins

Skip plugin execution.

```bash
pta check --no-plugins ledger.beancount
```

### --plugin

Load additional plugin.

```bash
pta check --plugin=my_plugin ledger.beancount
```

## Output

### Text Format (Default)

```
error: Account not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
   |
   = hint: add 'open' directive before this transaction

warning: Unused account
  --> ledger.beancount:10:1
   |
10 | 2024-01-01 open Assets:Unused
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ledger.beancount: 1 error, 1 warning
```

### JSON Format

```json
{
  "file": "ledger.beancount",
  "errors": [
    {
      "level": "error",
      "code": "E1001",
      "message": "Account not opened",
      "location": {
        "file": "ledger.beancount",
        "line": 42,
        "column": 3,
        "end_line": 42,
        "end_column": 17
      },
      "source": "  Assets:Unknown  100 USD",
      "hint": "add 'open' directive before this transaction"
    }
  ],
  "warnings": [
    {
      "level": "warning",
      "code": "W1001",
      "message": "Unused account",
      "location": {
        "file": "ledger.beancount",
        "line": 10,
        "column": 1
      }
    }
  ],
  "summary": {
    "errors": 1,
    "warnings": 1
  }
}
```

### GitHub Actions Format

```bash
pta check --format=github ledger.beancount
```

```
::error file=ledger.beancount,line=42,col=3::Account not opened
::warning file=ledger.beancount,line=10,col=1::Unused account
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No errors (warnings may be present) |
| 1 | Validation errors found |
| 2 | Invalid command-line usage |
| 3 | Input file not found |
| 10 | Parse error |

## Examples

### Basic Check

```bash
$ pta check ledger.beancount
ledger.beancount: OK
$ echo $?
0
```

### Check with Errors

```bash
$ pta check ledger.beancount
error: Transaction does not balance
  --> ledger.beancount:50:1
   |
50 | 2024-01-15 * "Unbalanced"
51 |   Assets:Checking  100 USD
52 |   Expenses:Food     50 USD
   |
   = residual: 50 USD

ledger.beancount: 1 error
$ echo $?
1
```

### Strict Mode

```bash
$ pta check --strict ledger.beancount
warning: Unused account 'Assets:Deprecated'
ledger.beancount: 0 errors, 1 warning (treated as error)
$ echo $?
1
```

### CI Integration

```bash
# In CI script
pta check --format=json --strict ledger.beancount > results.json
if [ $? -ne 0 ]; then
  cat results.json | jq '.errors[] | .message'
  exit 1
fi
```

### Multiple Files

```bash
$ pta check accounts.beancount transactions/*.beancount
accounts.beancount: OK
transactions/2024-01.beancount: OK
transactions/2024-02.beancount: 2 errors
```

### Ignoring Warnings

```bash
$ pta check --ignore=W1001 ledger.beancount
ledger.beancount: OK
```

## Validation Checks

The `check` command performs:

### Parse Validation

- Syntax correctness
- Valid directives
- Proper structure

### Account Validation

- Accounts opened before use
- Accounts not used after close
- Valid account names

### Transaction Validation

- Transactions balance
- Valid posting structure
- Currency constraints

### Balance Assertions

- Balance assertions match computed balance
- Within specified tolerance

### Inventory Validation

- Sufficient inventory for reductions
- Valid booking operations

## Comparison with Other Tools

| Feature | pta check | bean-check | hledger check |
|---------|-----------|------------|---------------|
| JSON output | Yes | No | No |
| Error codes | Detailed | Basic | Basic |
| --strict | Yes | No | --strict |
| --ignore | Yes | No | No |
| Plugin control | Yes | Limited | No |

## See Also

- [validate](validate.md) - Detailed validation with custom rules
- [Exit Codes](../exit-codes.md) - Complete exit code reference
- [Error Codes](../../errors/README.md) - Validation error codes
