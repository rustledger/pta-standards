# PTA Linting Specification

This document specifies linting rules for PTA journals.

## Overview

Linting checks for:
- Style consistency
- Common errors
- Best practices
- Potential problems

## Rule Categories

### Correctness

Errors that affect validity:
- Unbalanced transactions
- Invalid dates
- Undeclared accounts

### Style

Formatting preferences:
- Indentation
- Alignment
- Naming conventions

### Consistency

Cross-journal consistency:
- Date format
- Amount format
- Account naming

## Rule Format

### Identifier

```
CATEGORY-NNN
```

Examples: `STYLE-001`, `CORRECT-005`

### Severity

| Level | Meaning |
|-------|---------|
| error | Must fix |
| warning | Should fix |
| info | Suggestion |
| hint | Preference |

### Configuration

```yaml
rules:
  STYLE-001:
    enabled: true
    severity: warning
    options:
      indent: 4
```

## Linting Output

### Text Format

```
journal.beancount:42:5: warning[STYLE-001]: Inconsistent indentation
    Expected 4 spaces, found 2
journal.beancount:50:1: error[CORRECT-001]: Transaction does not balance
    Difference: 0.01 USD
```

### JSON Format

```json
{
  "file": "journal.beancount",
  "issues": [
    {
      "rule": "STYLE-001",
      "severity": "warning",
      "line": 42,
      "column": 5,
      "message": "Inconsistent indentation"
    }
  ]
}
```

### SARIF Format

For IDE integration.

## Configuration

### File Locations

```
.ptalint.yaml
.ptalint.json
ptalint.config.js
```

### Format

```yaml
extends: recommended
rules:
  STYLE-001: warning
  STYLE-002: off
  CORRECT-001: error
ignore:
  - "*.generated.journal"
```

### Rule Sets

- `recommended`: Common rules
- `strict`: All rules as errors
- `minimal`: Essential rules only

## Commands

### Check

```bash
pta lint journal.beancount
pta lint --format json *.journal
```

### Fix

```bash
pta lint --fix journal.beancount
```

### List Rules

```bash
pta lint --list-rules
```

## IDE Integration

### LSP Diagnostics

```json
{
  "diagnostics": [
    {
      "range": {"start": {"line": 41, "character": 4}},
      "severity": 2,
      "code": "STYLE-001",
      "source": "pta-lint",
      "message": "Inconsistent indentation"
    }
  ]
}
```

### Quick Fixes

```json
{
  "title": "Fix indentation",
  "kind": "quickfix",
  "edit": {
    "changes": {
      "journal.beancount": [
        {"range": {...}, "newText": "    "}
      ]
    }
  }
}
```

## Disabling Rules

### Inline

```beancount
2024-01-15 * "Test"  ; ptalint-disable STYLE-001
  Account  50.00 USD
```

### Block

```beancount
; ptalint-disable
2024-01-15 * "Test"
  Account  50.00 USD
; ptalint-enable
```

### File Level

```beancount
; ptalint-disable-file STYLE-001
```

## See Also

- [Style Rules](rules/style.md)
- [Correctness Rules](rules/correctness.md)
- [Consistency Rules](rules/consistency.md)
