# Ledger Compliance Testing

This document describes compliance testing for Ledger implementations.

## Overview

Compliance testing ensures implementations correctly parse and process Ledger journal files.

## Compliance Levels

### Level 1: Core Syntax

Basic parsing:

- [ ] Parse dates (YYYY/MM/DD, YYYY-MM-DD, YYYY.MM.DD)
- [ ] Parse transaction headers
- [ ] Parse postings with amounts
- [ ] Handle amount elision
- [ ] Support commodities

### Level 2: Directives

- [ ] `account` directive
- [ ] `commodity` directive
- [ ] `include` directive
- [ ] `alias` directive
- [ ] `tag` directive
- [ ] `payee` directive

### Level 3: Advanced Features

- [ ] Balance assertions
- [ ] Automated transactions
- [ ] Periodic transactions
- [ ] Virtual postings
- [ ] Value expressions

### Level 4: Full Compatibility

- [ ] All expression functions
- [ ] All command-line options
- [ ] Report formatting
- [ ] Full query language

## Test Suites

### Location

```
tests/ledger/v1/
├── syntax/
│   ├── valid/
│   └── invalid/
├── validation/
├── expressions/
└── edge-cases/
```

### Running Tests

```bash
# Using test harness
python tests/harness/runners/python/runner.py \
    --manifest tests/ledger/v1/manifest.json

# Using ledger directly
ledger -f test.ledger bal
```

## Test Case Format

```json
{
  "id": "ledger-txn-001",
  "description": "Basic transaction",
  "input": "2024/01/15 Payee\n    Expenses:A  $50\n    Assets:B",
  "expected": {
    "parse": true,
    "validate": true
  }
}
```

## Compliance Matrix

| Feature | Required | Level |
|---------|----------|-------|
| Basic transactions | Yes | 1 |
| Amount elision | Yes | 1 |
| Virtual postings | No | 3 |
| Expressions | No | 3 |
| Automated txns | No | 3 |

## See Also

- [Ledger Specification](v1/)
- [Test Harness](../../tests/harness/)
