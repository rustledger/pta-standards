# validate Command

Perform detailed validation with custom rules.

## Synopsis

```
pta validate [options] <file>...
```

## Description

The `validate` command extends `check` with support for custom validation rules, detailed reporting, and validation profiles. Use this when you need more control over validation than `check` provides.

## Difference from check

| Feature | check | validate |
|---------|-------|----------|
| Standard validation | Yes | Yes |
| Custom rules | No | Yes |
| Validation profiles | No | Yes |
| Performance focus | Yes | No |
| Detailed reports | Basic | Comprehensive |

## Arguments

### file

Ledger files to validate.

```bash
pta validate ledger.beancount
```

## Options

### --rules

Load custom validation rules.

```bash
pta validate --rules=company-rules.yaml ledger.beancount
```

### --profile

Use a validation profile.

```bash
pta validate --profile=strict ledger.beancount
pta validate --profile=personal ledger.beancount
```

### --report

Generate validation report.

```bash
pta validate --report=report.html ledger.beancount
pta validate --report=report.json ledger.beancount
```

### --explain

Show detailed explanation for errors.

```bash
pta validate --explain ledger.beancount
```

### --fix

Suggest or apply automatic fixes.

```bash
pta validate --fix=suggest ledger.beancount
pta validate --fix=apply ledger.beancount
```

### --severity

Minimum severity to report.

```bash
pta validate --severity=warning ledger.beancount
pta validate --severity=error ledger.beancount
```

### Standard Options

All options from `check` are also available:

- `--strict`
- `--quiet`, `-q`
- `--verbose`, `-v`
- `--format`
- `--max-errors`
- `--ignore`
- `--only`

## Custom Rules

### Rule File Format

```yaml
# company-rules.yaml
rules:
  - id: CUSTOM001
    name: require-receipt
    description: All expenses over $25 must have a receipt
    severity: warning
    match:
      directive: transaction
      account: Expenses:*
      amount: "> 25 USD"
    require:
      metadata: receipt

  - id: CUSTOM002
    name: approved-vendors
    description: Only approved vendors allowed
    severity: error
    match:
      directive: transaction
      payee: "*"
    condition: |
      payee in approved_vendors
    data:
      approved_vendors:
        - "Amazon"
        - "Whole Foods"
        - "Office Depot"
```

### Built-in Rule Sets

```bash
# Use built-in rule sets
pta validate --rules=builtin:expenses ledger.beancount
pta validate --rules=builtin:investments ledger.beancount
```

## Validation Profiles

### Profile Definition

```yaml
# profiles/strict.yaml
name: strict
description: Strict validation for production ledgers
extends: default
settings:
  treat_warnings_as_errors: true
  require_narration: true
  require_payee: true
  max_posting_amount: 100000 USD
rules:
  - builtin:standard
  - builtin:best-practices
disabled:
  - W1005  # Allow unused commodities
```

### Built-in Profiles

| Profile | Description |
|---------|-------------|
| `default` | Standard validation |
| `strict` | Warnings as errors |
| `personal` | Relaxed for personal use |
| `business` | Business accounting rules |
| `audit` | Maximum strictness |

## Output

### Text Format

```
=== Validation Report ===
File: ledger.beancount
Profile: strict

ERRORS (2):

[E1001] Account not opened
  --> ledger.beancount:42:3
  |
  | 42 |   Assets:Unknown  100 USD
  |    |   ^^^^^^^^^^^^^^
  |
  Explanation: Every account must be opened with an 'open' directive
  before it can be used in transactions.

  Fix: Add the following before line 42:
    2024-01-01 open Assets:Unknown

[CUSTOM001] Missing receipt for large expense
  --> ledger.beancount:85:1
  |
  | 85 | 2024-03-15 * "Office Supplies"
  | 86 |   Expenses:Office  150.00 USD
  |    |   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |
  Explanation: Company policy requires receipts for expenses over $25.

  Fix: Add metadata:
    receipt: "path/to/receipt.pdf"

WARNINGS (1):

[W1002] Large transaction amount
  --> ledger.beancount:100:1

=== Summary ===
Errors:   2
Warnings: 1
Status:   FAILED
```

### JSON Format

```json
{
  "file": "ledger.beancount",
  "profile": "strict",
  "results": [
    {
      "id": "E1001",
      "level": "error",
      "category": "account",
      "message": "Account not opened",
      "explanation": "Every account must be opened...",
      "location": { "line": 42, "column": 3 },
      "fix": {
        "type": "insert",
        "line": 41,
        "content": "2024-01-01 open Assets:Unknown"
      }
    }
  ],
  "summary": {
    "errors": 2,
    "warnings": 1,
    "passed": false
  }
}
```

### HTML Report

```bash
pta validate --report=report.html ledger.beancount
```

Generates a standalone HTML report with:

- Summary statistics
- Error details with source context
- Navigation and filtering
- Export options

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Validation errors found |
| 2 | Invalid command-line usage |
| 3 | Input file not found |
| 10 | Parse error |
| 52 | Invalid rules file |

## Examples

### Basic Validation

```bash
$ pta validate ledger.beancount
Validating ledger.beancount...
✓ 0 errors, 0 warnings
```

### With Custom Rules

```bash
$ pta validate --rules=company.yaml ledger.beancount
Validating with profile: default + company.yaml

[CUSTOM001] Missing receipt for expense over $25
  --> ledger.beancount:85:1

1 custom rule violation, 0 standard errors
```

### Generate Report

```bash
$ pta validate --report=validation-report.html ledger.beancount
Validation complete. Report written to validation-report.html
```

### Auto-Fix Mode

```bash
$ pta validate --fix=suggest ledger.beancount
2 issues found with suggested fixes:

1. [E1001] Account not opened
   Fix: Insert at line 41:
   + 2024-01-01 open Assets:Unknown

2. [W1003] Inconsistent indentation
   Fix: Change line 50:
   -    Assets:Cash  100 USD
   +  Assets:Cash  100 USD

Apply fixes? [y/N]
```

### Strict Profile

```bash
$ pta validate --profile=strict ledger.beancount
Using profile: strict (warnings treated as errors)

[W1002] Deprecated account name format
  --> ledger.beancount:15:1

Validation FAILED (1 warning treated as error)
```

## See Also

- [check](check.md) - Basic validation
- [Error Codes](../../errors/README.md) - Standard error codes
- [Linting Rules](../../linting/README.md) - Additional linting
