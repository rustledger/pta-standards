# format Command

Format and pretty-print ledger files.

## Synopsis

```
pta format [options] <file>...
pta format [options] --stdin
```

## Description

The `format` command reformats ledger files according to consistent style rules, improving readability and ensuring consistent formatting across a project.

## Arguments

### file

Ledger files to format.

```bash
pta format ledger.beancount
pta format *.beancount
```

## Options

### --in-place, -i

Modify files in place.

```bash
pta format --in-place ledger.beancount
```

Without `--in-place`, formatted output goes to stdout.

### --check

Check if files are formatted (no output).

```bash
pta format --check ledger.beancount
```

Exit code 0 if formatted, 1 if changes needed.

### --diff

Show diff of changes.

```bash
pta format --diff ledger.beancount
```

### --stdin

Read from stdin, write to stdout.

```bash
cat ledger.beancount | pta format --stdin
```

### --output, -o

Write to specific file.

```bash
pta format -o formatted.beancount ledger.beancount
```

### --config

Use specific configuration file.

```bash
pta format --config=.formatrc ledger.beancount
```

## Style Options

### --indent

Indentation width (default: 2).

```bash
pta format --indent=4 ledger.beancount
```

### --indent-style

Indentation style: `space` (default) or `tab`.

```bash
pta format --indent-style=tab ledger.beancount
```

### --align-amounts

Align amounts in postings.

```bash
pta format --align-amounts ledger.beancount
```

### --align-column

Column for amount alignment (default: 50).

```bash
pta format --align-amounts --align-column=60 ledger.beancount
```

### --sort-accounts

Sort account directives.

```bash
pta format --sort-accounts ledger.beancount
```

### --sort-transactions

Sort transactions by date.

```bash
pta format --sort-transactions ledger.beancount
```

### --normalize-whitespace

Normalize blank lines and trailing whitespace.

```bash
pta format --normalize-whitespace ledger.beancount
```

### --trailing-newline

Ensure file ends with newline.

```bash
pta format --trailing-newline ledger.beancount
```

## Configuration File

### Format

```yaml
# .formatrc or .pta-format.yaml
indent: 2
indent_style: space
align_amounts: true
align_column: 50
sort_accounts: false
sort_transactions: false
normalize_whitespace: true
trailing_newline: true

# Per-section overrides
metadata:
  indent: 4

postings:
  indent: 2
  align_amounts: true
```

### Discovery

Configuration is searched in order:

1. `--config` option
2. `.formatrc` in file's directory
3. `.pta-format.yaml` in file's directory
4. `.formatrc` in parent directories (up to root)
5. `~/.config/pta/format.yaml`

## Formatting Rules

### Transaction Formatting

**Before:**
```beancount
2024-01-15  *  "Store"   "Purchase"
 Assets:Checking -100 USD
    Expenses:Food    100 USD
```

**After:**
```beancount
2024-01-15 * "Store" "Purchase"
  Assets:Checking   -100.00 USD
  Expenses:Food      100.00 USD
```

### Amount Alignment

**Before:**
```beancount
2024-01-15 * "Multiple items"
  Assets:Checking  -1234.56 USD
  Expenses:Food  50 USD
  Expenses:Transport  1184.56 USD
```

**After (aligned):**
```beancount
2024-01-15 * "Multiple items"
  Assets:Checking                         -1234.56 USD
  Expenses:Food                              50.00 USD
  Expenses:Transport                       1184.56 USD
```

### Metadata Formatting

**Before:**
```beancount
2024-01-15 * "Purchase"
 receipt: "receipt.pdf"
     category: "food"
  Assets:Checking  -100 USD
  Expenses:Food
```

**After:**
```beancount
2024-01-15 * "Purchase"
  receipt: "receipt.pdf"
  category: "food"
  Assets:Checking  -100.00 USD
  Expenses:Food
```

### Directive Ordering

With `--sort-accounts`:

**Before:**
```beancount
2024-01-01 open Expenses:Food
2024-01-01 open Assets:Checking
2024-01-01 open Income:Salary
```

**After:**
```beancount
2024-01-01 open Assets:Checking
2024-01-01 open Expenses:Food
2024-01-01 open Income:Salary
```

### Blank Lines

- One blank line between directives
- Two blank lines between sections (configurable)
- No trailing blank lines (or one, configurable)

## Output

### Default (stdout)

```bash
$ pta format ledger.beancount
2024-01-15 * "Store" "Purchase"
  Assets:Checking  -100.00 USD
  Expenses:Food     100.00 USD
```

### Diff Output

```bash
$ pta format --diff ledger.beancount
--- ledger.beancount
+++ ledger.beancount (formatted)
@@ -1,4 +1,4 @@
-2024-01-15  *  "Store"   "Purchase"
- Assets:Checking -100 USD
-    Expenses:Food    100 USD
+2024-01-15 * "Store" "Purchase"
+  Assets:Checking  -100.00 USD
+  Expenses:Food     100.00 USD
```

### Check Output

```bash
$ pta format --check ledger.beancount
ledger.beancount: needs formatting
$ echo $?
1

$ pta format --check formatted.beancount
$ echo $?
0
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (or file already formatted with --check) |
| 1 | File needs formatting (with --check) |
| 2 | Invalid command-line usage |
| 3 | Input file not found |
| 10 | Parse error |
| 42 | Write error |

## Examples

### Format to stdout

```bash
$ pta format ledger.beancount > formatted.beancount
```

### Format in Place

```bash
$ pta format --in-place ledger.beancount
```

### Format Multiple Files

```bash
$ pta format --in-place *.beancount
```

### Check in CI

```bash
$ pta format --check ledger.beancount || {
    echo "Files need formatting. Run: pta format --in-place"
    exit 1
  }
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.beancount$')
if [ -n "$files" ]; then
  if ! pta format --check $files; then
    echo "Please format files before committing:"
    echo "  pta format --in-place $files"
    exit 1
  fi
fi
```

### Custom Style

```bash
$ pta format --indent=4 --align-column=60 ledger.beancount
```

### Format from stdin

```bash
$ echo '2024-01-15 * "Test"
 Assets:A 100 USD
  Expenses:B' | pta format --stdin
2024-01-15 * "Test"
  Assets:A     100.00 USD
  Expenses:B
```

## Comparison with Other Tools

| Feature | pta format | bean-format | hledger |
|---------|------------|-------------|---------|
| In-place edit | Yes | Yes | No |
| Check mode | Yes | No | No |
| Diff output | Yes | No | No |
| Configurable | Yes | Limited | No |
| Sort options | Yes | No | No |

## See Also

- [Canonical Format](../../canonical/README.md) - Canonical formatting rules
- [Style Guide](../../canonical/style-guide.md) - Recommended style
