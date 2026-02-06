# import Command

Import transactions from external sources.

## Synopsis

```
pta import [options] --importer=<name> <source>
pta import [options] --config=<config> <source>
```

## Description

The `import` command converts data from external sources (bank exports, financial institutions) into plain text accounting format.

## Arguments

### source

Input file or directory to import from.

```bash
pta import --importer=chase bank-statement.csv
pta import --config=importers.yaml ~/Downloads/
```

## Options

### --importer, -I

Use specific importer.

```bash
pta import --importer=chase statement.csv
pta import --importer=ofx export.ofx
```

### --config, -c

Use importer configuration file.

```bash
pta import --config=importers.yaml statement.csv
```

### --output, -o

Output file (default: stdout).

```bash
pta import -o transactions.beancount --importer=chase statement.csv
```

### --format

Output format: `beancount` (default), `ledger`, `hledger`.

```bash
pta import --format=ledger --importer=chase statement.csv
```

### --account

Default account for imported transactions.

```bash
pta import --account=Assets:Checking --importer=csv statement.csv
```

### --currency

Default currency.

```bash
pta import --currency=USD --importer=csv statement.csv
```

### --date-format

Date format in source.

```bash
pta import --date-format="%m/%d/%Y" --importer=csv statement.csv
```

### --dry-run

Show what would be imported without writing.

```bash
pta import --dry-run --importer=chase statement.csv
```

### --deduplicate

Skip transactions that appear to be duplicates.

```bash
pta import --deduplicate --existing=ledger.beancount --importer=chase statement.csv
```

### --existing

Existing ledger to check for duplicates.

```bash
pta import --deduplicate --existing=ledger.beancount ...
```

### --interactive

Interactively categorize transactions.

```bash
pta import --interactive --importer=chase statement.csv
```

## Built-in Importers

### csv

Generic CSV importer with configurable columns.

```bash
pta import --importer=csv \
  --csv-date=0 \
  --csv-description=1 \
  --csv-amount=2 \
  statement.csv
```

### ofx

OFX/QFX format (common bank export).

```bash
pta import --importer=ofx export.ofx
```

### qif

Quicken Interchange Format.

```bash
pta import --importer=qif export.qif
```

### Institution-Specific

```bash
pta import --importer=chase statement.csv
pta import --importer=amex statement.csv
pta import --importer=paypal report.csv
```

## Configuration File

### Format

```yaml
# importers.yaml
importers:
  - name: chase-checking
    type: csv
    account: Assets:Chase:Checking
    currency: USD
    patterns:
      - "Chase*.csv"
    columns:
      date: 0
      description: 2
      amount: 3
    date_format: "%m/%d/%Y"
    rules:
      - match: "WHOLE FOODS"
        payee: "Whole Foods"
        account: Expenses:Food:Groceries
      - match: "AMAZON"
        payee: "Amazon"
        account: Expenses:Shopping

  - name: amex-gold
    type: csv
    account: Liabilities:Amex:Gold
    currency: USD
    patterns:
      - "amex*.csv"
    columns:
      date: 0
      description: 1
      amount: 2
    negate_amounts: true  # Amex shows charges as positive
```

### Auto-Detection

With a config file, importers are auto-detected by filename patterns:

```bash
# Matches "Chase*.csv" pattern → uses chase-checking importer
pta import --config=importers.yaml Chase1234_Activity.csv
```

## Categorization Rules

### Pattern Matching

```yaml
rules:
  - match: "SPOTIFY"
    payee: "Spotify"
    account: Expenses:Entertainment:Music
    tags: [subscription]

  - match: "UBER|LYFT"
    regex: true
    payee: "Rideshare"
    account: Expenses:Transport

  - match: "TRANSFER"
    skip: true  # Don't import transfers
```

### Machine Learning (Optional)

```bash
pta import --categorize=ml --model=categories.model statement.csv
```

Requires training on existing ledger:

```bash
pta train-categorizer --ledger=ledger.beancount -o categories.model
```

## Output

### Default Output

```beancount
; Imported from: Chase1234_Activity.csv
; Date: 2024-01-20
; Importer: chase-checking

2024-01-15 * "WHOLE FOODS #1234" ""
  import-id: "chase-2024-01-15-001"
  Assets:Chase:Checking  -85.50 USD
  Expenses:Unknown

2024-01-16 * "SPOTIFY USA" ""
  import-id: "chase-2024-01-16-001"
  Assets:Chase:Checking  -9.99 USD
  Expenses:Unknown
```

### With Categorization

```beancount
2024-01-15 * "Whole Foods" "Groceries"
  import-id: "chase-2024-01-15-001"
  Assets:Chase:Checking  -85.50 USD
  Expenses:Food:Groceries

2024-01-16 * "Spotify" "Monthly subscription"
  import-id: "chase-2024-01-16-001"
  Assets:Chase:Checking  -9.99 USD
  Expenses:Entertainment:Music
```

## Interactive Mode

```bash
$ pta import --interactive --importer=chase statement.csv

Transaction 1/25:
  Date: 2024-01-15
  Description: WHOLE FOODS #1234 NEW YORK
  Amount: -85.50 USD

  Payee [Whole Foods]:
  Narration []: Weekly groceries
  Account [Expenses:Unknown]: Expenses:Food:Groceries

  Saved rule? (y/N): y
  Pattern: WHOLE FOODS

Transaction 2/25:
  ...
```

## Deduplication

### Import ID

Each imported transaction gets a unique ID:

```beancount
2024-01-15 * "Whole Foods"
  import-id: "chase-2024-01-15-a1b2c3"
  ...
```

### Duplicate Detection

```bash
$ pta import --deduplicate --existing=ledger.beancount statement.csv
Skipping 5 duplicate transactions (already in ledger)
Importing 12 new transactions
```

### Manual Resolution

```bash
$ pta import --deduplicate=prompt --existing=ledger.beancount statement.csv
Possible duplicate:
  Existing (line 142): 2024-01-15 * "Whole Foods"
  New import: WHOLE FOODS #1234 -85.50

  [S]kip, [I]mport anyway, [M]ark as duplicate?
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Import successful |
| 1 | Some transactions failed to import |
| 2 | Invalid command-line usage |
| 3 | Source file not found |
| 10 | Parse error in source |
| 50 | Configuration error |

## Examples

### Basic Import

```bash
$ pta import --importer=ofx export.ofx >> ledger.beancount
```

### With Configuration

```bash
$ pta import --config=importers.yaml ~/Downloads/*.csv >> ledger.beancount
```

### Dry Run

```bash
$ pta import --dry-run --importer=chase statement.csv
Would import 25 transactions:
  2024-01-15 WHOLE FOODS #1234     -85.50 USD
  2024-01-16 SPOTIFY USA            -9.99 USD
  ...
```

### Batch Import

```bash
$ for f in ~/Downloads/Chase*.csv; do
    pta import --config=importers.yaml "$f" >> ledger.beancount
    mv "$f" ~/Downloads/imported/
  done
```

### CI Pipeline

```bash
# Import and validate
pta import --config=importers.yaml new-statement.csv > new-transactions.beancount
cat ledger.beancount new-transactions.beancount | pta check -
```

## See Also

- [Import Formats](../../../imports/README.md) - Supported import formats
- [CSV Rules](../../../imports/csv/README.md) - CSV import configuration
- [OFX Spec](../../../imports/ofx/README.md) - OFX import details
