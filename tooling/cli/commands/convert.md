# convert Command

Convert between plain text accounting formats.

## Synopsis

```
pta convert [options] --from=<format> --to=<format> <file>
pta convert [options] --from=<format> --to=<format> --stdin
```

## Description

The `convert` command transforms ledger files between different plain text accounting formats (Beancount, Ledger, hledger).

## Arguments

### file

Input file to convert.

```bash
pta convert --from=beancount --to=ledger input.beancount
```

## Options

### --from, -f

Source format: `beancount`, `ledger`, `hledger`.

```bash
pta convert --from=beancount ...
```

### --to, -t

Target format: `beancount`, `ledger`, `hledger`.

```bash
pta convert --to=ledger ...
```

### --output, -o

Output file (default: stdout).

```bash
pta convert -o output.ledger --from=beancount --to=ledger input.beancount
```

### --stdin

Read from stdin.

```bash
cat input.beancount | pta convert --stdin --from=beancount --to=ledger
```

### --strict

Fail on lossy conversions.

```bash
pta convert --strict --from=beancount --to=ledger input.beancount
```

### --warnings

Show conversion warnings.

```bash
pta convert --warnings --from=beancount --to=ledger input.beancount
```

### --mapping

Use custom account/commodity mapping file.

```bash
pta convert --mapping=mappings.yaml --from=beancount --to=ledger input.beancount
```

### --preserve-metadata

Keep metadata in target format (when possible).

```bash
pta convert --preserve-metadata --from=beancount --to=ledger input.beancount
```

## Supported Conversions

| From | To | Support |
|------|-----|---------|
| Beancount | Ledger | Full |
| Beancount | hledger | Full |
| Ledger | Beancount | Partial |
| Ledger | hledger | Full |
| hledger | Beancount | Partial |
| hledger | Ledger | Full |

### Conversion Matrix Legend

- **Full**: Most features convert without loss
- **Partial**: Some features may not convert or require approximation

## Conversion Rules

### Beancount to Ledger

| Beancount | Ledger | Notes |
|-----------|--------|-------|
| `2024-01-15` | `2024/01/15` | Date format |
| `* "Payee" "Narration"` | `* Payee` | Narration in comment |
| `100.00 USD` | `$100.00` or `100.00 USD` | Amount format |
| `{100 USD}` | `{=$100}` | Cost syntax |
| `@ 1.08 USD` | `@ $1.08` | Price syntax |
| `#tag` | `:tag:` | Tag syntax |
| `^link` | (comment) | No direct equivalent |
| `key: "value"` | `; key: value` | Metadata |
| `open Account` | `account Account` | Account declaration |
| `balance` | `= assertion` | Balance assertion |

**Example:**

Beancount:
```beancount
2024-01-15 * "Whole Foods" "Weekly groceries" #food
  receipt: "receipts/001.pdf"
  Assets:Checking  -85.50 USD
  Expenses:Food:Groceries
```

Ledger:
```ledger
2024/01/15 * Whole Foods
    ; Weekly groceries
    ; :food:
    ; receipt: receipts/001.pdf
    Expenses:Food:Groceries         $85.50
    Assets:Checking
```

### Ledger to Beancount

| Ledger | Beancount | Notes |
|--------|-----------|-------|
| `2024/01/15` | `2024-01-15` | Date format |
| `* Payee` | `* "Payee" ""` | Payee/narration |
| `$100.00` | `100.00 USD` | Currency code |
| `{=$100}` | `{100 USD}` | Cost syntax |
| `:tag:` | `#tag` | Tag syntax |
| `; key: value` | `key: "value"` | Metadata |
| Expressions | (evaluated) | No expressions in Beancount |

**Example:**

Ledger:
```ledger
2024/01/15 * Grocery Store
    ; :groceries:
    Expenses:Food              $85.50
    Assets:Checking
```

Beancount:
```beancount
2024-01-15 * "Grocery Store" "" #groceries
  Expenses:Food          85.50 USD
  Assets:Checking       -85.50 USD
```

### Known Limitations

#### Beancount → Ledger

- Links (`^link`) have no direct equivalent (converted to comments)
- Plugin behavior cannot be converted
- Some metadata types may lose structure

#### Ledger → Beancount

- Expressions are evaluated, not preserved
- Automated transactions not supported
- Virtual postings require approximation
- Some date formats need interpretation

#### hledger Specifics

- Timedot format is hledger-only
- CSV rules are hledger-only
- Some directives differ from Ledger

## Mapping Files

### Account Mapping

```yaml
# mappings.yaml
accounts:
  # Ledger → Beancount
  "Expenses:Food": "Expenses:Food:Groceries"
  "Assets:Bank:*": "Assets:Bank:Checking"

commodities:
  # Symbol → Code
  "$": "USD"
  "€": "EUR"
  "£": "GBP"
```

### Usage

```bash
pta convert --mapping=mappings.yaml --from=ledger --to=beancount input.ledger
```

## Output

### Success

```bash
$ pta convert --from=beancount --to=ledger input.beancount
; Converted from Beancount
; Date: 2024-01-15

2024/01/15 * Whole Foods
    Expenses:Food:Groceries         $85.50
    Assets:Checking
```

### With Warnings

```bash
$ pta convert --warnings --from=beancount --to=ledger input.beancount
warning: Link ^invoice-001 converted to comment (line 42)
warning: Plugin 'auto_accounts' behavior not converted (line 5)

2024/01/15 * ...
```

### Strict Mode Failure

```bash
$ pta convert --strict --from=beancount --to=ledger input.beancount
error: Cannot convert link ^invoice-001 without loss
  --> input.beancount:42:25
   |
42 | 2024-01-15 * "Purchase" ^invoice-001
   |                         ^^^^^^^^^^^^
   |
   = hint: use --warnings to convert with loss, or remove links
$ echo $?
1
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Conversion successful |
| 1 | Conversion completed with warnings (without --strict) |
| 1 | Lossy conversion rejected (with --strict) |
| 2 | Invalid command-line usage |
| 3 | Input file not found |
| 10 | Parse error in input |
| 42 | Write error |

## Examples

### Basic Conversion

```bash
$ pta convert --from=beancount --to=ledger ledger.beancount > ledger.dat
```

### With Output File

```bash
$ pta convert -o ledger.dat --from=beancount --to=ledger ledger.beancount
```

### Pipeline

```bash
$ cat ledger.beancount \
  | pta convert --stdin --from=beancount --to=ledger \
  | ledger -f - balance
```

### Batch Conversion

```bash
for f in *.beancount; do
  pta convert --from=beancount --to=ledger "$f" > "${f%.beancount}.ledger"
done
```

### Round-Trip Test

```bash
$ pta convert --from=beancount --to=ledger input.beancount \
  | pta convert --stdin --from=ledger --to=beancount \
  | diff input.beancount -
```

## See Also

- [Conversion Specs](../../../conversions/README.md) - Detailed conversion rules
- [Format Differences](../../../reference/comparison/syntax.md) - Syntax comparison
- [Loss Matrix](../../../conversions/loss-matrix.md) - What can't be converted
