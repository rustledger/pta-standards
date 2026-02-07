# Error Specification

This document specifies the standard format for errors and diagnostics in plain text accounting tools.

## Overview

Standardized error formats enable:
- Consistent user experience across tools
- IDE integration via standard protocols
- Automated error processing and analysis
- Cross-tool error comparison

## Error Structure

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Unique error identifier |
| `severity` | enum | error, warning, info, hint |
| `message` | string | Human-readable description |
| `location` | Location | Source position |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Tool/component name |
| `related` | Location[] | Related source positions |
| `fixes` | Fix[] | Suggested fixes |
| `tags` | string[] | Error categories |

## Location Format

```json
{
  "file": "ledger.beancount",
  "range": {
    "start": {"line": 42, "character": 5},
    "end": {"line": 42, "character": 15}
  }
}
```

- Lines are 0-indexed
- Characters are 0-indexed
- End is exclusive

## Severity Levels

| Level | Code | Use Case |
|-------|------|----------|
| Error | 1 | Prevents successful processing |
| Warning | 2 | Potential problem, processing continues |
| Info | 3 | Informational message |
| Hint | 4 | Suggestion for improvement |

## Error Codes

### Code Format

```
E<format><category><number>
```

| Component | Description | Example |
|-----------|-------------|---------|
| E | Error prefix | `E` |
| format | 0=common, 1=beancount, 2=ledger, 3=hledger | `1` |
| category | 0=syntax, 1=semantic, 2=query | `1` |
| number | Sequential within category | `001` |

### Examples

| Code | Meaning |
|------|---------|
| E0001 | Common syntax error |
| E1001 | Beancount semantic error |
| E1101 | Beancount account error |
| E2001 | Ledger syntax error |

See [codes/](codes/) for complete catalog.

## Text Output Format

### Standard Format

```
ERROR[E1101]: Account not opened
  --> ledger.beancount:42:3
   |
42 |   Assets:Unknown  100 USD
   |   ^^^^^^^^^^^^^^
   |
   = hint: add 'open' directive before this transaction
```

### Components

| Part | Description |
|------|-------------|
| Level[Code] | Severity and error code |
| Message | Primary error description |
| Location | File:line:column |
| Source | Relevant source line |
| Indicator | Underline at error position |
| Hint | Suggested fix or explanation |

### Multi-Location Errors

```
ERROR[E1102]: Transaction does not balance
  --> ledger.beancount:42:1
   |
42 | 2024-01-15 * "Purchase"
   | ^^^^^^^^^^^^^^^^^^^^^^^^
...
45 |   Expenses:Food  50 USD
   |   ^^^^^^^^^^^^^^^^^^^^^ this posting
   |
   = residual: 50 USD (expected 0)
```

## JSON Output Format

```json
{
  "diagnostics": [
    {
      "code": "E1101",
      "severity": "error",
      "message": "Account not opened",
      "source": "beancount",
      "location": {
        "file": "ledger.beancount",
        "range": {
          "start": {"line": 41, "character": 2},
          "end": {"line": 41, "character": 16}
        }
      },
      "relatedInformation": [
        {
          "location": {
            "file": "ledger.beancount",
            "range": {
              "start": {"line": 0, "character": 0},
              "end": {"line": 0, "character": 0}
            }
          },
          "message": "Add 'open' directive here"
        }
      ],
      "tags": ["account", "lifecycle"]
    }
  ]
}
```

## SARIF Output Format

For CI/CD integration, errors MAY be output in SARIF format:

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "beancount",
          "version": "3.0.0",
          "rules": [
            {
              "id": "E1101",
              "shortDescription": {"text": "Account not opened"},
              "helpUri": "https://pta-spec.org/errors/E1101"
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "E1101",
          "level": "error",
          "message": {"text": "Account 'Assets:Unknown' not opened"},
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {"uri": "ledger.beancount"},
                "region": {
                  "startLine": 42,
                  "startColumn": 3,
                  "endColumn": 17
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## LSP Diagnostic Format

For editor integration, errors map to LSP diagnostics:

```json
{
  "uri": "file:///path/to/ledger.beancount",
  "diagnostics": [
    {
      "range": {
        "start": {"line": 41, "character": 2},
        "end": {"line": 41, "character": 16}
      },
      "severity": 1,
      "code": "E1101",
      "source": "beancount",
      "message": "Account not opened",
      "relatedInformation": []
    }
  ]
}
```

## Error Aggregation

### Grouping

Errors SHOULD be grouped by:
1. File
2. Line number
3. Error code

### Deduplication

Duplicate errors (same code, location) SHOULD be deduplicated.

### Limits

Implementations MAY limit errors:
- Per file: 100 errors
- Total: 1000 errors
- After limit: "... and N more errors"

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (no errors) |
| 1 | Errors found |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Internal error |

## See Also

- [Error Codes](codes/)
- [Message Style Guide](messages.md)
- [SARIF Schema](sarif.schema.json)
