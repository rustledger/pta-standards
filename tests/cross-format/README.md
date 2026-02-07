# Cross-Format Conversion Tests

This directory contains tests for verifying format conversion accuracy between Beancount, Ledger, and hledger.

## Overview

Cross-format tests verify that:
1. Conversion preserves semantic meaning
2. Round-trip conversion is possible where supported
3. Known information loss is documented

## Test Structure

```
cross-format/
├── README.md
├── manifest.json
├── beancount-to-ledger/
│   └── tests.json
├── beancount-to-hledger/
│   └── tests.json
├── ledger-to-hledger/
│   └── tests.json
├── ledger-to-beancount/
│   └── tests.json
├── hledger-to-ledger/
│   └── tests.json
├── hledger-to-beancount/
│   └── tests.json
└── fixtures/
    └── ...
```

## Test Case Format

```json
{
  "id": "simple-transaction",
  "description": "Basic transaction converts correctly",
  "source": {
    "format": "beancount",
    "content": "2024-01-15 * \"Test\"\n  Assets:A  100 USD\n  Assets:B"
  },
  "target": {
    "format": "ledger",
    "content": "2024/01/15 * Test\n    Assets:A  $100.00\n    Assets:B"
  },
  "equivalence": {
    "accounts": ["Assets:A", "Assets:B"],
    "balance": {
      "Assets:A": {"USD": "100.00"}
    }
  }
}
```

## Equivalence Checking

Tests can verify equivalence in multiple ways:

### Syntactic Equivalence
The output matches expected text exactly.

### Semantic Equivalence
The output, when parsed, produces equivalent:
- Account balances
- Transaction structure
- Metadata (where preserved)

### Behavioral Equivalence
Running reports on both produces the same results.

## Information Loss Matrix

Some information is lost during conversion:

| Feature | Bean→Led | Bean→HL | Led→HL | Led→Bean |
|---------|----------|---------|--------|----------|
| Tags | ✓ | ✓ | ✓ | ~ |
| Links | ~ | ~ | N/A | N/A |
| Booking | ~ | ~ | N/A | ✓ |
| Virtual | N/A | N/A | ✓ | N/A |

Legend: ✓ = preserved, ~ = partial, N/A = not applicable

## Running Tests

```bash
# Run all cross-format tests
python harness/runners/python/runner.py --manifest cross-format/manifest.json

# Run specific conversion pair
python harness/runners/python/runner.py --manifest cross-format/manifest.json --suite beancount-to-ledger
```
