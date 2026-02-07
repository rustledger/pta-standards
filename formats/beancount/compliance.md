# Beancount Compliance Testing

This document describes compliance testing for Beancount implementations.

## Overview

Compliance testing ensures implementations correctly parse and validate Beancount files according to the specification.

## Compliance Levels

### Level 1: Core Syntax

- [ ] Parse dates (YYYY-MM-DD)
- [ ] Parse transactions
- [ ] Parse amounts with commodities
- [ ] Handle basic directives

### Level 2: Full Directives

- [ ] `open` and `close` accounts
- [ ] `commodity` declaration
- [ ] `balance` assertions
- [ ] `pad` entries
- [ ] `note` and `document`
- [ ] `price` declarations
- [ ] `event` entries
- [ ] `query` entries
- [ ] `custom` directives

### Level 3: Validation

- [ ] Account not opened
- [ ] Account closed
- [ ] Balance assertion failures
- [ ] Transaction balancing
- [ ] Booking method enforcement

### Level 4: Advanced Features

- [ ] Plugin execution
- [ ] BQL query support
- [ ] Options handling
- [ ] Include processing

## Test Suites

### Location

```
tests/beancount/
├── v2/
│   ├── syntax/
│   ├── validation/
│   └── queries/
└── v3/
    ├── syntax/
    ├── validation/
    └── queries/
```

### Running Tests

```bash
# Using test harness
python tests/harness/runners/python/runner.py \
    --manifest tests/beancount/v3/manifest.json

# Using bean-check
bean-check test-file.beancount
```

## Test Case Format

### Structure

```json
{
  "id": "beancount-open-001",
  "description": "Open account directive",
  "input": "2024-01-01 open Assets:Bank USD",
  "expected": {
    "parse": true,
    "validate": true,
    "accounts": ["Assets:Bank"]
  }
}
```

### Expected Fields

| Field | Description |
|-------|-------------|
| `parse` | Should parse successfully |
| `validate` | Should validate successfully |
| `error_contains` | Expected error substring |
| `accounts` | Expected account list |
| `directives` | Expected directive count |

## Reference Implementation

Python beancount is the reference implementation:

```bash
pip install beancount
bean-check file.beancount
```

## Compliance Matrix

| Feature | Required | Level |
|---------|----------|-------|
| Basic transactions | Yes | 1 |
| Open/close | Yes | 2 |
| Balance assertions | Yes | 2 |
| Pad entries | No | 2 |
| Booking methods | No | 3 |
| Plugins | No | 4 |
| BQL | No | 4 |

## Known Implementation Differences

### vs Python beancount

- Reference implementation
- Full plugin support
- Complete BQL

### vs Rust implementations

- May have performance differences
- Plugin support varies
- BQL coverage varies

## Reporting Results

### Format

```json
{
  "implementation": "my-beancount",
  "version": "1.0.0",
  "test_date": "2024-01-15",
  "compliance_level": 3,
  "results": {
    "passed": 200,
    "failed": 5,
    "skipped": 12
  }
}
```

## See Also

- [Beancount v3 Specification](v3/)
- [Test Harness](../../tests/harness/)
- [Plugin Specification](plugins/spec.md)
