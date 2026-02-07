# hledger Compliance Testing

This document describes how to verify implementation compliance with the hledger format specification.

## Overview

Compliance testing ensures implementations correctly parse and process hledger journal files according to the specification.

## Compliance Levels

### Level 1: Core Syntax

Basic parsing requirements:

- [ ] Parse dates (YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD)
- [ ] Parse transaction headers
- [ ] Parse postings with amounts
- [ ] Handle amount elision
- [ ] Support basic commodities

### Level 2: Directives

Directive support:

- [ ] `account` directive
- [ ] `commodity` directive
- [ ] `include` directive
- [ ] `decimal-mark` directive
- [ ] `payee` directive
- [ ] `tag` directive

### Level 3: Advanced Features

Extended functionality:

- [ ] Balance assertions
- [ ] Balance assignments
- [ ] Auto postings
- [ ] Periodic transactions
- [ ] Multi-commodity transactions
- [ ] Price annotations

### Level 4: Full Compatibility

Complete feature support:

- [ ] All account types
- [ ] All query expressions
- [ ] Forecasting
- [ ] Budget reports
- [ ] CSV rules

## Test Suites

### Location

```
tests/hledger/v1/
├── syntax/
│   ├── valid/
│   └── invalid/
├── validation/
├── queries/
└── edge-cases/
```

### Running Tests

```bash
# Using the test harness
python tests/harness/runners/python/runner.py \
    --manifest tests/hledger/v1/manifest.json

# Using hledger directly
for f in tests/hledger/v1/syntax/valid/*.hledger; do
    hledger -f "$f" check
done
```

## Test Case Format

### Structure

```json
{
  "id": "hledger-basic-001",
  "description": "Basic two-posting transaction",
  "input": "2024-01-15 Grocery\n    expenses:food  $50\n    assets:cash",
  "expected": {
    "parse": true,
    "validate": true,
    "transactions": 1
  }
}
```

### Expected Fields

| Field | Description |
|-------|-------------|
| `parse` | Should parse successfully |
| `validate` | Should validate successfully |
| `error_contains` | Expected error substring |
| `transactions` | Expected transaction count |
| `accounts` | Expected account list |

## Compliance Matrix

| Feature | Required | Level |
|---------|----------|-------|
| Basic transactions | Yes | 1 |
| Amount elision | Yes | 1 |
| Comments | Yes | 1 |
| Account directive | No | 2 |
| Commodity directive | No | 2 |
| Balance assertions | No | 3 |
| Auto postings | No | 3 |
| Forecasting | No | 4 |

## Reporting Results

### Format

```json
{
  "implementation": "my-hledger",
  "version": "1.0.0",
  "test_date": "2024-01-15",
  "compliance_level": 3,
  "results": {
    "passed": 142,
    "failed": 3,
    "skipped": 10
  }
}
```

### Submission

To report compliance:

1. Run the test suite
2. Generate results JSON
3. Submit via pull request to compliance registry

## Known Differences

### From Ledger

- Stricter date parsing
- Different virtual posting syntax
- Different default precision

### From Beancount

- Different date format (- vs /)
- Different directive syntax
- No booking methods

## See Also

- [hledger Specification](v1/)
- [Test Harness](../../tests/harness/)
- [Ledger Compliance](../ledger/compliance.md)
