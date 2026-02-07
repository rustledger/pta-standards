# Test Format Specification

This document specifies the format for PTA Standards conformance tests.

## Overview

Conformance tests are defined in JSON files that specify:
- Input: The PTA content to parse
- Expected: The expected outcome (success, error, specific values)
- Metadata: Tags, skip conditions, descriptions

## File Structure

### Manifest File

Each format version has a `manifest.json`:

```json
{
  "$schema": "../../harness/manifest.schema.json",
  "format": "beancount",
  "version": "3",
  "description": "Conformance tests for Beancount v3",
  "test_directories": [
    "syntax/valid",
    "syntax/invalid",
    "validation",
    "booking",
    "bql",
    "regression"
  ],
  "metadata": {
    "created": "2024-02-07",
    "spec_version": "draft",
    "reference_implementation": "beancount 3.2.0"
  }
}
```

### Test Suite File

Each test directory contains a `tests.json`:

```json
{
  "$schema": "../../../harness/test-case.schema.json",
  "suite": "syntax-valid",
  "description": "Valid syntax that should parse successfully",
  "tests": [
    {
      "id": "test-id",
      "description": "What this tests",
      "input": {...},
      "expected": {...}
    }
  ]
}
```

## Test Case Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, hyphens) |
| `description` | string | Human-readable description |
| `input` | object | Test input specification |
| `expected` | object | Expected outcome |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `spec_ref` | string | Reference to spec section |
| `tags` | array | Tags for filtering |
| `skip` | boolean | Skip this test |
| `skip_reason` | string | Why test is skipped |

## Input Specification

### Inline Content

```json
{
  "input": {
    "inline": "2024-01-01 open Assets:Bank USD"
  }
}
```

Inline content is the PTA source code as a string. Use `\n` for newlines.

### File Reference

```json
{
  "input": {
    "file": "fixtures/complex.beancount"
  }
}
```

File paths are relative to the test directory.

### Multiple Files

```json
{
  "input": {
    "files": {
      "main.beancount": "include \"other.beancount\"",
      "other.beancount": "2024-01-01 open Assets:Bank"
    }
  }
}
```

For testing include behavior.

## Expected Outcomes

### Parse Result

```json
{
  "expected": {
    "parse": "success"
  }
}
```

| Value | Meaning |
|-------|---------|
| `"success"` | Must parse without errors |
| `"error"` | Must produce parse error |

### Validation Result

```json
{
  "expected": {
    "parse": "success",
    "validate": "error"
  }
}
```

| Value | Meaning |
|-------|---------|
| `"success"` | Must validate without errors |
| `"error"` | Must produce validation error |
| `"skip"` | Skip validation check |

### Directive Count

```json
{
  "expected": {
    "parse": "success",
    "directives": 5
  }
}
```

### Error Details

```json
{
  "expected": {
    "parse": "error",
    "error_count": 1,
    "error_contains": ["balance", "failed"]
  }
}
```

- `error_count`: Exact number of errors
- `error_contains`: Substrings in error message

### Balance Check

```json
{
  "expected": {
    "validate": "success",
    "balance": {
      "Assets:Bank": {
        "USD": "1000.00",
        "EUR": "500.00"
      }
    }
  }
}
```

### Query Results

For BQL tests:

```json
{
  "expected": {
    "query": "success",
    "row_count": 10,
    "columns": ["account", "balance"]
  }
}
```

## Tags

Tags enable filtering tests by category:

```json
{
  "tags": ["transaction", "multi-currency", "edge-case"]
}
```

### Standard Tags

| Tag | Meaning |
|-----|---------|
| `minimal` | Minimal valid examples |
| `edge-case` | Boundary conditions |
| `unicode` | Unicode handling |
| `regression` | Bug fixes |
| `booking` | Cost basis tracking |
| `fifo`, `lifo` | Specific booking methods |

## Skip Conditions

```json
{
  "skip": true,
  "skip_reason": "Requires optional feature X"
}
```

Use skip for:
- Implementation-specific behavior
- Optional features
- Known issues under investigation

## Fixtures

Large or complex test files go in `fixtures/`:

```
tests/beancount/v3/
├── fixtures/
│   ├── large-ledger.beancount
│   └── multi-file/
│       ├── main.beancount
│       └── accounts.beancount
└── validation/
    └── tests.json  # References fixtures
```

## Test ID Conventions

| Pattern | Example | Usage |
|---------|---------|-------|
| `{feature}-{variant}` | `open-minimal` | Basic tests |
| `{feature}-{edge}` | `date-leap-year` | Edge cases |
| `error-{type}` | `error-unbalanced` | Error tests |
| `regression-{issue}` | `regression-123` | Bug fixes |

## Versioning

Tests specify the spec version they target:

```json
{
  "metadata": {
    "spec_version": "1.0.0"
  }
}
```

When the spec changes:
- Add new tests for new behavior
- Update existing tests if behavior changes
- Mark obsolete tests with skip

## Best Practices

1. **One concept per test**: Test a single behavior
2. **Minimal examples**: Use smallest input that demonstrates the point
3. **Clear descriptions**: Explain what and why
4. **Tag appropriately**: Enable useful filtering
5. **Document skips**: Always explain skip_reason
6. **Test both success and failure**: Cover error cases
